import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
from app.core.database import Base, engine
from app.api import auth, agent, documents, conversations, memory, tools, dashboard

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables if not present
    Base.metadata.create_all(bind=engine)
    print(f"[{settings.PROJECT_NAME}] Service initialized on database {settings.DATABASE_URL.split('///')[-1]}")
    yield
    print(f"[{settings.PROJECT_NAME}] Service shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise AI Research & Automation Agent - Production Portfolio Platform",
    lifespan=lifespan
)

# CORS configuration: strict allowed origins from configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Include API Routers
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
        "environment": "production" if os.getenv("ENV") == "production" else "development"
    }

@app.get("/", tags=["Root"])
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs_url": "/docs",
        "health_check": "/health"
    }

# Mount Elysia AI static application assets if installed in environment
elysia_static = Path(__file__).resolve().parent.parent.parent / ".venv/lib/python3.11/site-packages/elysia/api/static"
if elysia_static.exists():
    _next_dir = elysia_static / "_next"
    if _next_dir.exists():
        app.mount("/_next", StaticFiles(directory=str(_next_dir)), name="elysia-next-assets")
    app.mount("/elysia-static", StaticFiles(directory=str(elysia_static)), name="elysia-static")

    @app.get("/elysia", tags=["Elysia AI Studio"])
    @app.get("/elysia/", tags=["Elysia AI Studio"])
    def serve_elysia():
        index_file = elysia_static / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"status": "error", "message": "Elysia index.html not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
