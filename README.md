# Enterprise AI Research & Automation Agent

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-StateGraph-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![pgvector](https://img.shields.io/badge/PostgreSQL-pgvector-336791.svg)](https://github.com/pgvector/pgvector)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A production-grade, full-stack **Autonomous AI Agent Platform** architected for complex enterprise research, policy compliance verification, deterministic mathematical analysis, structured business data retrieval, and multi-step workflow automation.

This system runs natively with Python (`venv`) and Node.js, leveraging a **LangGraph StateGraph** with PostgreSQL checkpointing (`langgraph-checkpoint-postgres`), Human-in-the-Loop (HITL) `interrupt()` approval gates, **MCP tool adapters** (`langchain-mcp-adapters`), **PostgreSQL + `pgvector`** hybrid search (HNSW + GIN `tsvector` with RRF), **ARQ + Redis** async **Docling** ingestion, **OpenTelemetry / Langfuse** tracing, and **DeepEval** CI evaluations.

---

## 🛠️ Tech Stack & Directory Structure

```text
enterprise-ai-agent/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI entrypoint, lifespan, OTel instrumentation
│   │   ├── core/                       # Settings, async/sync DB, JWT/bcrypt, guardrails, rate limit, telemetry
│   │   ├── models/                     # SQLAlchemy ORM (User, Task, Memory, Order, Sale, Document, DocumentChunk)
│   │   ├── schemas/                    # Pydantic v2 structured schemas
│   │   ├── agents/                     # LangGraph StateGraph, nodes, HITL approval_gate, context manager
│   │   ├── agent/                      # MCP tool registry (langchain-mcp-adapters)
│   │   ├── tools/                      # Deterministic tools + ToolRegistry
│   │   ├── rag/                        # pgvector + tsvector HybridRetriever (RRF), TextSplitter
│   │   ├── workers/                    # ARQ async Docling ingestion worker
│   │   ├── memory/                     # Long-term selective extraction & short-term scratchpad
│   │   └── api/                        # REST API routers (/auth, /agent, /documents, /memory, /tools)
│   ├── tests/                          # Pytest unit tests + DeepEval RAG evals (tests/evals/)
│   ├── requirements-api.txt            # Lightweight FastAPI + LangGraph + OTel dependencies
│   ├── requirements-worker.txt         # API dependencies + Docling for async ingestion
│   └── requirements-dev.txt            # Pytest, DeepEval, Ruff, httpx
├── frontend/
│   ├── app/                            # Next.js 14 App Router (/, /chat, /documents, /memory, /tools)
│   ├── components/                     # React components, ActionApprovalCard (HITL), trace viewers
│   ├── lib/                            # API client & utility functions
│   └── types/                          # TypeScript interface definitions
├── mcp_servers.json                    # MCP server configuration for MultiServerMCPClient
├── scripts/
│   ├── setup.sh                        # Native venv + npm setup script
│   └── generate_sample_docs.py         # Sample policy PDF generator
├── .github/workflows/ci.yml            # GitHub Actions (backend-test, frontend-check, rag-evals)
└── .env.example
```

---

## ⚡ Quick Start (Native Local Setup)

### Prerequisites
- **Python 3.11+**
- **Node.js 20+**
- **PostgreSQL 15+ with `pgvector`** and **Redis 7+** (either installed locally or via free managed cloud tiers)

### 1. Configure Environment (`.env`)
```bash
cp .env.example .env
```

Point `.env` to **local services** or **managed cloud tiers**:

* **Local PostgreSQL + Redis**:
  ```env
  DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/enterprise_agent
  REDIS_URL=redis://localhost:6379/0
  UPLOAD_DIR=./data/uploads
  ```
* **Managed Cloud Free Tiers (Neon / Supabase + Upstash)**:
  * **Neon / Supabase (`pgvector`)**: Enable the `vector` extension in your provider dashboard, then set `DATABASE_URL` to your Neon/Supabase connection string (`postgresql+asyncpg://...`).
  * **Upstash (Redis)**: Set `REDIS_URL=rediss://default:<token>@<endpoint>.upstash.io:6379`.

### 2. Install Dependencies
```bash
# Backend virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-api.txt -r requirements-worker.txt

# Frontend dependencies
cd ../frontend
npm install
```

### 3. Run the 3 Native Processes (in separate terminals)

1. **FastAPI Backend** (Port `8000`):
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **ARQ Ingestion Worker** (Docling PDF/DOCX parsing & `pgvector` indexing):
   ```bash
   cd backend
   source venv/bin/activate
   arq app.workers.ingestion.WorkerSettings
   ```

3. **Next.js Frontend** (Port `3000`):
   ```bash
   cd frontend
   npm run dev
   ```

* **Frontend**: `http://localhost:3000`
* **FastAPI Backend**: `http://localhost:8000`
* **Interactive OpenAPI Docs**: `http://localhost:8000/docs`

---

## 🧪 Running Tests & Evaluations

```bash
cd backend
source venv/bin/activate

# Unit & API tests (excluding LLM-as-judge evals)
pytest -v -m "not eval"

# DeepEval RAG evaluation suite (requires OPENAI_API_KEY)
pytest -v tests/evals
```

---

## 🔒 Security & Guardrails
1. **PII & Prompt Injection Screening**: `EnterpriseComplianceGuardrails` redacts SSNs, Luhn-verified payment cards, API keys, and flags prompt-injection patterns before LLM execution.
2. **Human-in-the-Loop (HITL) Approval Gates**: Sensitive or mutating tools (`requires_approval=True`) pause via LangGraph `interrupt()` and render an inline `ActionApprovalCard` in Next.js before resuming via `Command(resume=...)`.
3. **Tenant Isolation**: `Document`, `DocumentChunk`, `HybridRetriever`, and Redis rate limiting are strictly scoped by `tenant_id`.

## 📜 License
MIT License.
