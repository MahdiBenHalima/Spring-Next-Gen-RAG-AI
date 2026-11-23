# Spring Next Gen — Hybrid RAG & AI for RFP Analysis

**Independent, open portfolio reconstruction** of selected AI engineering concepts implemented during a two-month Spring Next Gen internship (2026). This repository **does not contain the complete internship platform**, customer tenders, private business rules, Angular UI, or Spring Boot code. It was authored anew as a small, inspectable Python demonstration after examining the architecture of the private project. The actual original implementation is not open sourced here.

## Engineering scope and CV correspondence

| CV capability | Confirmed in private Python project | Public representation |
|---|---|---|
| RFP document processing and chunking | PDF/text extraction and RecursiveCharacterTextSplitter with 1,200-character chunks/200 overlap | Independent text/PDF ingestion and overlapping source-aware chunks |
| Hybrid RAG | PGVector semantic retrieval + BM25 candidate retrieval + CrossEncoder reranking | BM25, injectable vector retrieval, reciprocal-rank fusion and injectable reranking |
| Local LLMs | Ollama ChatOllama, Qwen3:8b configured, mxbai-embed-large embeddings configured | Optional adapters for Ollama/PGVector; not required for offline demo |
| Requirements extraction | Dedicated requirements module, prompt and JSON validation | Demonstrated concept in architecture; lightweight heuristic example is **not** equivalent |
| Technical, risk and resource analysis | Private `app/agents/technical`, `risk_analysis`, `resource_estimation` modules | Documented architecture and evidence-based example; proprietary logic excluded |
| Financial estimation and Go/No-Go | Private financial and Go/No-Go scoring services | Transparent cost arithmetic; decision stays `HUMAN_REVIEW_REQUIRED` |
| FastAPI integration | Private FastAPI routes and backend integrations | Independent `/health` and `/demo/analyze` endpoints |
| PDF reporting | Private PDF report generator | Documented; **not implemented** in this minimal public reconstruction |

**Terminology:** The private code uses `agents/` as modules for task-specific analysis. No LangGraph orchestration or autonomous tool-using multi-agent system is claimed for this internship project.

## Architecture

```text
Original private project (verified high-level components)
PDF/text --> parsing --> chunking --> Ollama embeddings --> PostgreSQL / pgvector
                                               |                  |
User query --------------------------- BM25 retrieval      vector search
                                               \                  /
                                                CrossEncoder reranking
                                                         |
                                               Context + Ollama LLM
                                                         |
                                  Requirement / Technical / Risk / Resources
                                                         |
                                        Business rules / Financial / Go-No-Go
                                                         |
                                                 FastAPI / PDF report

This PUBLIC repository (independent implementation)
text/PDF --> chunking --> BM25 ----+--> rank fusion --> optional reranker
                     optional pgvector search -------+
                                               |
                                     evidence + heuristic review
                                               |
                                         FastAPI / CLI demo
```

The optional adapters connect to Ollama and PGVector when services are configured. **The default CLI/API demo runs BM25 only**, does not invoke a language model, and is not a production procurement decision system.

## Quick start (Python 3.10+)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m rfp_ai.demo
pytest -q
uvicorn rfp_ai.api:app --reload
```

Then visit `http://127.0.0.1:8000/docs`.

### Example request

```bash
curl -X POST http://127.0.0.1:8000/demo/analyze \
  -H "Content-Type: application/json" \
  -d '{"tender_id":"SYNTHETIC-001","document_text":"A fictional customer requires REST API integration and a security audit.","question":"What integration is required?","person_days":20,"daily_rate":400}'
```

The response includes evidence chunk IDs and the explicitly non-automated outcome `HUMAN_REVIEW_REQUIRED`.

## Optional real hybrid retrieval

```bash
python -m pip install -e ".[rag,pdf,dev]"
cp .env.example .env
# Set DATABASE_URL in your environment (local PostgreSQL with pgvector enabled)
# Start Ollama and pull compatible models:
ollama pull qwen3:8b
ollama pull mxbai-embed-large
```

The `rfp_ai.adapters` module exposes `index_in_pgvector`, `search_pgvector`, `cross_encoder_scoring` and `answer_with_ollama`. Combine the adapters with `rfp_ai.pipeline.retrieve` for a real service-backed hybrid run. These optional integrations are **not validated by offline GitHub Actions**; they require PostgreSQL, pgvector, Ollama and external model artifacts. A separate integration test environment is required for reproducible end-to-end validation.

## Tests and safety

- Offline pytest tests cover chunk metadata, retrieval isolation, RRF deduplication, reranking, costs, API validation and human-review status.
- `.github/workflows/ci.yml` executes the package installation, compilation and tests without network model calls.
- All demo inputs are fictional. Do **not** add customer tenders, private PDFs, database dumps, passwords or production model caches.
- The published repository is **not** an exact copy of internship code, not a validated production deployment, and not an autonomous bidding agent.

See [TRACEABILITY.md](TRACEABILITY.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), and [docs/SECURITY.md](docs/SECURITY.md).

**Keywords:** Python · Hybrid RAG · Retrieval-Augmented Generation · BM25 · pgvector · Ollama · CrossEncoder · LLM · FastAPI · RFP Analysis · Go/No-Go
