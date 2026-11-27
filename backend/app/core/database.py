from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.sync_database_url,
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async_engine = create_async_engine(
    settings.async_database_url,
    echo=False,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session


async def ensure_pgvector_extension():
    """Ensure the pgvector extension is enabled in PostgreSQL using the unpooled/direct connection."""
    try:
        unpooled_engine = create_async_engine(settings.unpooled_async_database_url, echo=False)
        async with unpooled_engine.begin() as conn:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await unpooled_engine.dispose()
    except Exception as exc:
        print(
            f"[Database Warning] Could not run 'CREATE EXTENSION IF NOT EXISTS vector;' ({exc}). "
            "If using a managed Postgres provider (Neon, Supabase, RDS), enable the 'vector' extension via your dashboard."
        )
