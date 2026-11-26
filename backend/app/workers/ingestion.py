import os
from typing import List, Dict, Any
from arq.connections import RedisSettings
from openai import AsyncOpenAI
from sqlalchemy import delete
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.document import Document, DocumentChunk
from app.rag.text_splitter import RecursiveTextSplitter


def _parse_with_docling(file_path: str) -> str:
    """Parse PDF/DOCX/etc. using Docling and export structured Markdown."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext in {".txt", ".md", ".csv", ".json"}:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    from docling.document_converter import DocumentConverter

    converter = DocumentConverter()
    result = converter.convert(file_path)
    return result.document.export_to_markdown()


async def _embed_texts(texts: List[str]) -> List[List[float]]:
    if not texts or not settings.OPENAI_API_KEY:
        return [[] for _ in texts]
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    embeddings: List[List[float]] = []
    batch_size = 64
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        resp = await client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=batch,
        )
        embeddings.extend([item.embedding for item in resp.data])
    return embeddings


async def ingest_document(ctx: Dict[str, Any], document_id: str, tenant_id: str, file_path: str) -> Dict[str, Any]:
    """ARQ background task: parse document with Docling, chunk, embed, and store in pgvector."""
    async with AsyncSessionLocal() as session:
        doc = await session.get(Document, document_id)
        if not doc:
            return {"status": "FAILED", "error": f"Document {document_id} not found"}
        doc.status = "PROCESSING"
        doc.error_message = None
        await session.commit()

    try:
        markdown_text = _parse_with_docling(file_path)
        splitter = RecursiveTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        filename = os.path.basename(file_path)
        base_meta = {
            "document_id": document_id,
            "tenant_id": tenant_id,
            "filename": filename,
            "source_citation": f"[Source: {filename}]",
        }
        chunks = splitter.create_chunks_with_metadata(markdown_text, base_meta)
        contents = [c["content"] for c in chunks]
        vectors = await _embed_texts(contents)

        async with AsyncSessionLocal() as session:
            # Remove any stale chunks for this document before re-inserting
            await session.execute(
                delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
            )

            db_chunks = []
            for idx, chunk in enumerate(chunks):
                vec = vectors[idx] if idx < len(vectors) and vectors[idx] else None
                db_chunks.append(
                    DocumentChunk(
                        tenant_id=tenant_id,
                        document_id=document_id,
                        content=chunk["content"],
                        chunk_metadata=chunk["metadata"],
                        embedding=vec,
                    )
                )
            session.add_all(db_chunks)

            doc = await session.get(Document, document_id)
            if doc:
                doc.status = "COMPLETED"
                doc.chunk_count = len(db_chunks)
                doc.doc_metadata = {"chunks": len(db_chunks), "parser": "docling"}
            await session.commit()

        return {"status": "COMPLETED", "document_id": document_id, "chunks": len(chunks)}
    except Exception as exc:
        async with AsyncSessionLocal() as session:
            doc = await session.get(Document, document_id)
            if doc:
                doc.status = "FAILED"
                doc.error_message = str(exc)
                await session.commit()
        return {"status": "FAILED", "document_id": document_id, "error": str(exc)}


class WorkerSettings:
    functions = [ingest_document]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    max_jobs = 4
    job_timeout = 600
