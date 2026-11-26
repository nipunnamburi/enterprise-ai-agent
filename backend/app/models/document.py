import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Integer,
    Text,
    ForeignKey,
    Index,
    Computed,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, default="default", index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False, default="pdf")
    file_size = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
    checksum = Column(String(64), nullable=True)
    status = Column(String(32), nullable=False, default="PENDING")  # PENDING | PROCESSING | COMPLETED | FAILED
    error_message = Column(Text, nullable=True)
    doc_metadata = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, default="default", index=True)
    document_id = Column(
        UUID(as_uuid=False),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content = Column(Text, nullable=False)
    chunk_metadata = Column("metadata", JSONB, default=dict)
    embedding = Column(Vector(1536), nullable=True)
    search_vector = Column(
        TSVECTOR,
        Computed("to_tsvector('english', content)", persisted=True),
    )
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    document = relationship("Document", back_populates="chunks")

    __table_args__ = (
        Index(
            "ix_document_chunks_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
        Index(
            "ix_document_chunks_search_vector_gin",
            "search_vector",
            postgresql_using="gin",
        ),
    )
