import os
import math
import hashlib
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings

class EmbeddingService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except Exception:
                self.client = None

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        
        if self.client:
            try:
                response = self.client.embeddings.create(
                    input=texts,
                    model=settings.EMBEDDING_MODEL
                )
                return [item.embedding for item in response.data]
            except Exception as e:
                print(f"[VectorStore] OpenAI embedding failed, using semantic fallback: {e}")

        # Deterministic 128-dimensional hashed-word token projection fallback
        # (MD5 bit-projection with inverse-length weighting for zero-API-key local testing)
        return [self._generate_fallback_embedding(t) for t in texts]

    def _generate_fallback_embedding(self, text: str) -> List[float]:
        dim = 128
        vec = [0.0] * dim
        words = text.lower().split()
        for word in words:
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            for i in range(dim):
                bit = (h >> (i % 64)) & 1
                weight = 1.0 if bit == 1 else -1.0
                vec[i] += weight / (math.log(len(word) + 2))
        
        # Normalize
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]

class ChromaVectorStore:
    def __init__(self):
        os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.embedding_service = EmbeddingService()
        self.collection = self.chroma_client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        if not chunks:
            return 0

        ids = [c["chunk_id"] for c in chunks]
        documents = [c["content"] for c in chunks]
        metadatas = []
        for c in chunks:
            meta = {}
            for k, v in c["metadata"].items():
                if isinstance(v, (str, int, float, bool)):
                    meta[k] = v
                else:
                    meta[k] = str(v)
            metadatas.append(meta)

        embeddings = self.embedding_service.get_embeddings(documents)

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )
        return len(ids)

    def search(
        self, 
        query: str, 
        top_k: int = 4, 
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        query_embedding = self.embedding_service.get_embeddings([query])[0]
        
        where_clause = None
        if filter_metadata:
            # Format Chroma where clause
            conditions = [{k: {"$eq": v}} for k, v in filter_metadata.items()]
            if len(conditions) == 1:
                where_clause = conditions[0]
            elif len(conditions) > 1:
                where_clause = {"$and": conditions}

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause,
            include=["documents", "metadatas", "distances"]
        )

        formatted_results = []
        if results and results["ids"] and len(results["ids"][0]) > 0:
            for i in range(len(results["ids"][0])):
                chunk_id = results["ids"][0][i]
                doc_text = results["documents"][0][i] if results["documents"] else ""
                meta = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 1.0
                similarity_score = round(1.0 - (distance / 2.0), 4)

                formatted_results.append({
                    "chunk_id": chunk_id,
                    "content": doc_text,
                    "metadata": meta,
                    "similarity_score": similarity_score,
                    "source_citation": f"[Source: {meta.get('filename', 'Unknown')}, page {meta.get('page_number', 1)}]"
                })

        return formatted_results

    def delete_document(self, document_id: str) -> int:
        # Delete all chunks belonging to document_id
        try:
            self.collection.delete(where={"document_id": {"$eq": document_id}})
            return 1
        except Exception as e:
            print(f"[VectorStore] Error deleting doc {document_id}: {e}")
            return 0

    def delete_by_filename(self, filename: str) -> int:
        try:
            self.collection.delete(where={"filename": {"$eq": filename}})
            return 1
        except Exception as e:
            print(f"[VectorStore] Error deleting file {filename}: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        count = self.collection.count()
        return {
            "collection_name": settings.CHROMA_COLLECTION_NAME,
            "total_chunks": count,
            "persist_dir": settings.CHROMA_PERSIST_DIR
        }

vector_store = ChromaVectorStore()
