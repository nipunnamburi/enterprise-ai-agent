import asyncio
from typing import List, Dict, Any, Optional
from openai import OpenAI, AsyncOpenAI
from sqlalchemy import text
from app.core.config import settings
from app.core.database import AsyncSessionLocal


class HybridRetriever:
    """PostgreSQL pgvector + GIN tsvector hybrid retriever with Reciprocal Rank Fusion (RRF)."""

    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k
        self._sync_openai: Optional[OpenAI] = None
        self._async_openai: Optional[AsyncOpenAI] = None

    @property
    def sync_client(self) -> Optional[OpenAI]:
        if self._sync_openai is None and settings.OPENAI_API_KEY:
            self._sync_openai = OpenAI(api_key=settings.OPENAI_API_KEY)
        return self._sync_openai

    @property
    def async_client(self) -> Optional[AsyncOpenAI]:
        if self._async_openai is None and settings.OPENAI_API_KEY:
            self._async_openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        return self._async_openai

    async def embed_query(self, query: str) -> Optional[List[float]]:
        if not self.async_client:
            return None
        resp = await self.async_client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=query,
        )
        return resp.data[0].embedding

    async def retrieve(
        self,
        query: str,
        tenant_id: str = "default",
        top_k: int = 4,
        document_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Execute tenant-scoped semantic + lexical search and merge via RRF."""
        if not query or not query.strip():
            return []

        candidate_k = max(top_k * 3, 12)
        query_embedding = await self.embed_query(query)

        filter_clause = ""
        params: Dict[str, Any] = {
            "tenant_id": tenant_id,
            "query": query,
            "candidate_k": candidate_k,
        }
        if document_filter:
            filter_clause = "AND (dc.metadata->>'filename' = :doc_filter OR d.filename = :doc_filter)"
            params["doc_filter"] = document_filter

        semantic_rows = []
        lexical_rows = []

        async with AsyncSessionLocal() as session:
            if query_embedding is not None:
                vec_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
                params["query_embedding"] = vec_str
                sem_sql = text(f"""
                    SELECT dc.id, dc.document_id, dc.content, dc.metadata, d.filename,
                           (1.0 - (dc.embedding <=> CAST(:query_embedding AS vector))) AS semantic_score
                    FROM document_chunks dc
                    JOIN documents d ON d.id = dc.document_id
                    WHERE dc.tenant_id = :tenant_id
                      AND dc.embedding IS NOT NULL
                      {filter_clause}
                    ORDER BY dc.embedding <=> CAST(:query_embedding AS vector)
                    LIMIT :candidate_k
                """)
                res = await session.execute(sem_sql, params)
                semantic_rows = res.mappings().all()

            lex_sql = text(f"""
                SELECT dc.id, dc.document_id, dc.content, dc.metadata, d.filename,
                       ts_rank_cd(dc.search_vector, plainto_tsquery('english', :query)) AS lexical_score
                FROM document_chunks dc
                JOIN documents d ON d.id = dc.document_id
                WHERE dc.tenant_id = :tenant_id
                  AND dc.search_vector @@ plainto_tsquery('english', :query)
                  {filter_clause}
                ORDER BY lexical_score DESC
                LIMIT :candidate_k
            """)
            res = await session.execute(lex_sql, params)
            lexical_rows = res.mappings().all()

        # Reciprocal Rank Fusion (RRF)
        fused: Dict[str, Dict[str, Any]] = {}
        for rank, row in enumerate(semantic_rows, start=1):
            cid = str(row["id"])
            meta = dict(row["metadata"] or {})
            filename = meta.get("filename") or row["filename"]
            fused[cid] = {
                "chunk_id": cid,
                "document_id": str(row["document_id"]),
                "content": row["content"],
                "metadata": meta,
                "source_citation": meta.get("source_citation") or f"[Source: {filename}]",
                "semantic_score": round(float(row["semantic_score"] or 0.0), 4),
                "lexical_score": 0.0,
                "rrf_score": 1.0 / (self.rrf_k + rank),
            }

        for rank, row in enumerate(lexical_rows, start=1):
            cid = str(row["id"])
            meta = dict(row["metadata"] or {})
            filename = meta.get("filename") or row["filename"]
            rrf_add = 1.0 / (self.rrf_k + rank)
            if cid in fused:
                fused[cid]["lexical_score"] = round(float(row["lexical_score"] or 0.0), 4)
                fused[cid]["rrf_score"] += rrf_add
            else:
                fused[cid] = {
                    "chunk_id": cid,
                    "document_id": str(row["document_id"]),
                    "content": row["content"],
                    "metadata": meta,
                    "source_citation": meta.get("source_citation") or f"[Source: {filename}]",
                    "semantic_score": 0.0,
                    "lexical_score": round(float(row["lexical_score"] or 0.0), 4),
                    "rrf_score": rrf_add,
                }

        ranked = sorted(fused.values(), key=lambda x: x["rrf_score"], reverse=True)[:top_k]
        for item in ranked:
            item["similarity_score"] = round(item["rrf_score"], 4)
        return ranked

    def search(
        self,
        query: str,
        top_k: int = 4,
        filter_metadata: Optional[Dict[str, Any]] = None,
        tenant_id: str = "default",
    ) -> List[Dict[str, Any]]:
        """Synchronous convenience wrapper for tools and non-async callers."""
        doc_filter = (filter_metadata or {}).get("filename")
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # Run in a separate thread if called inside an active event loop
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(
                    lambda: asyncio.run(
                        self.retrieve(query=query, tenant_id=tenant_id, top_k=top_k, document_filter=doc_filter)
                    )
                ).result()
        return asyncio.run(
            self.retrieve(query=query, tenant_id=tenant_id, top_k=top_k, document_filter=doc_filter)
        )


hybrid_retriever = HybridRetriever()
