import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.core.config import settings
from app.core.database import Base, engine, ensure_pgvector_extension
from app.core.seed import seed_database
from app.core.telemetry import configure_telemetry
from app.agents.graph import build_enterprise_agent_graph
from app.tools.registry import tool_registry
from app.api import auth, agent, documents, conversations, memory, tools, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    pg_pool = None
    try:
        await ensure_pgvector_extension()
        Base.metadata.create_all(bind=engine)
        seed_database()
    except Exception as e:
        print(f"[Startup DB/Seed Warning]: {e}")

    try:
        pg_pool = AsyncConnectionPool(
            conninfo=settings.checkpointer_dsn,
            max_size=10,
            kwargs={"autocommit": True, "prepare_threshold": 0},
            open=False,
        )
        await pg_pool.open()
        checkpointer = AsyncPostgresSaver(pg_pool)
        await checkpointer.setup()
        app.state.pg_pool = pg_pool
        app.state.agent_graph = build_enterprise_agent_graph(checkpointer=checkpointer)
    except Exception as e:
        print(f"[Startup Checkpointer Warning]: Falling back to stateless graph ({e})")
        app.state.agent_graph = build_enterprise_agent_graph()

    try:
        await tool_registry.load_external_mcp_tools()
    except Exception as e:
        print(f"[Startup MCP Warning]: {e}")

    print(f"[{settings.PROJECT_NAME}] Service initialized.")
    yield

    if pg_pool is not None:
        await pg_pool.close()
    print(f"[{settings.PROJECT_NAME}] Service shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise AI Research & Automation Agent - Production Platform",
    lifespan=lifespan,
)

configure_telemetry(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Versioned API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(agent.router, prefix=settings.API_V1_STR)
app.include_router(documents.router, prefix=settings.API_V1_STR)
app.include_router(conversations.router, prefix=settings.API_V1_STR)
app.include_router(memory.router, prefix=settings.API_V1_STR)
app.include_router(tools.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)

# Top-level direct routes for convenience
app.include_router(auth.router)
app.include_router(agent.router)
app.include_router(documents.router)
app.include_router(conversations.router)
app.include_router(memory.router)
app.include_router(tools.router)
app.include_router(dashboard.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": "production" if os.getenv("ENV") == "production" else "development",
    }


@app.get("/", tags=["Root"])
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs_url": "/docs",
        "health_check": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
