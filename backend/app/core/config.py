import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="allow")

    PROJECT_NAME: str = "Enterprise AI Research & Automation Agent"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment & Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-enterprise-ai-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"
    ALLOW_DEMO_AUTH: bool = os.getenv("ALLOW_DEMO_AUTH", "true").lower() in ("true", "1", "yes")
    CORS_ALLOWED_ORIGINS: list = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ALLOWED_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001"
        ).split(",")
        if origin.strip()
    ]
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../enterprise_ai.db'))}"
    )
    
    # Chroma Vector DB
    CHROMA_PERSIST_DIR: str = os.getenv(
        "CHROMA_PERSIST_DIR",
        os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../data/chroma_db'))
    )
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "enterprise_knowledge_base")
    
    # LLM & Multi-Provider Architecture (Devo-inspired)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock")  # openai, anthropic, ollama, mock
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY", None)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o")
    FAST_LLM_MODEL: str = os.getenv("FAST_LLM_MODEL", "gpt-4o-mini")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    # RAG Settings
    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 100
    TOP_K_RESULTS: int = 4
    
    # Storage for uploaded documents
    UPLOAD_DIR: str = os.getenv(
        "UPLOAD_DIR",
        os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../data/documents'))
    )

settings = Settings()
