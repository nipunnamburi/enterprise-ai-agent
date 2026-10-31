import os
import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models.document import Document
from app.schemas.document import DocumentOut, DocumentUploadResponse
from app.rag.document_loader import DocumentLoader
from app.rag.text_splitter import RecursiveTextSplitter
from app.rag.vector_store import vector_store

router = APIRouter(prefix="/documents", tags=["Documents & RAG"])

@router.get("", response_model=List[DocumentOut])
def list_documents(db: Session = Depends(get_db)):
    return db.query(Document).order_by(Document.created_at.desc()).all()

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)
    checksum = DocumentLoader.calculate_checksum(file_path)

    # Check if doc already exists in DB
    doc_entry = db.query(Document).filter(Document.filename == file.filename).first()
    if not doc_entry:
        doc_id = f"doc_{file.filename.replace('.', '_')}"
        doc_entry = Document(
            id=doc_id,
            filename=file.filename,
            file_type=file.filename.split(".")[-1].lower(),
            file_size=file_size,
            chunk_count=0,
            checksum=checksum,
            status="indexing"
        )
        db.add(doc_entry)
        db.commit()
        db.refresh(doc_entry)
    else:
        doc_id = doc_entry.id
        doc_entry.status = "indexing"
        db.commit()

    # Ingest and Chunk
    try:
        sections = DocumentLoader.load_file(file_path)
        splitter = RecursiveTextSplitter(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
        
        all_chunks = []
        for text_content, meta in sections:
            meta["document_id"] = doc_id
            chunks = splitter.create_chunks_with_metadata(text_content, meta)
            all_chunks.extend(chunks)

        # Index in Chroma
        vector_store.add_chunks(all_chunks)

        doc_entry.chunk_count = len(all_chunks)
        doc_entry.status = "indexed"
        doc_entry.doc_metadata = {"chunks": len(all_chunks), "type": doc_entry.file_type}
        db.commit()
        db.refresh(doc_entry)

        return {
            "document": doc_entry,
            "message": f"Successfully ingested and indexed {len(all_chunks)} chunks into Chroma vector database."
        }
    except Exception as e:
        doc_entry.status = "error"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Document ingestion failed: {str(e)}")

@router.delete("/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete from Chroma
    vector_store.delete_document(doc.id)
    vector_store.delete_by_filename(doc.filename)

    # Delete physical file if exists
    file_path = os.path.join(settings.UPLOAD_DIR, doc.filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass

    # Delete from DB
    db.delete(doc)
    db.commit()
    return {"success": True, "message": f"Document {doc.filename} deleted successfully from DB and Vector Store."}

@router.post("/reindex")
def reindex_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).all()
    reindexed_count = 0
    splitter = RecursiveTextSplitter(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)

    for doc in docs:
        file_path = os.path.join(settings.UPLOAD_DIR, doc.filename)
        if os.path.exists(file_path):
            try:
                sections = DocumentLoader.load_file(file_path)
                all_chunks = []
                for text_content, meta in sections:
                    meta["document_id"] = doc.id
                    chunks = splitter.create_chunks_with_metadata(text_content, meta)
                    all_chunks.extend(chunks)
                
                vector_store.add_chunks(all_chunks)
                doc.chunk_count = len(all_chunks)
                doc.status = "indexed"
                reindexed_count += 1
            except Exception as e:
                doc.status = "error"
                print(f"[Reindex] Error reindexing {doc.filename}: {e}")

    db.commit()
    return {
        "success": True,
        "reindexed_documents": reindexed_count,
        "chroma_stats": vector_store.get_stats()
    }
