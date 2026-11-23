# Spring Next Gen — Intelligent RFP Analysis Platform

**Hybrid RAG • Local LLMs • AI-Powered Tender Analysis • Decision Support • FastAPI**

[![Python CI](https://github.com/MahdiBenHalima/Spring-Next-Gen-RAG-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/MahdiBenHalima/Spring-Next-Gen-RAG-AI/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)
![RAG](https://img.shields.io/badge/AI-Hybrid%20RAG-purple)
![LLMs](https://img.shields.io/badge/LLM-Ollama-orange)

> **Project overview:** An AI engineering project for transforming unstructured request-for-proposal (RFP) documents into searchable evidence, structured requirements, technical and risk observations, resource and financial estimates, and reviewable Go/No-Go recommendations.
>
> Developed in the context of an **AI & LLM Engineering internship at Spring Next Gen (2026)**. This repository provides an **independently implemented, public technical showcase** of the methods and workflow. Certain original application components, internal rules, datasets and business integrations remain private to the organization.

## Project highlights

- **Document Intelligence:** extract information from PDF, DOCX, PPTX or plain-text documents, then segment text into identifiable chunks.
- **Hybrid Retrieval-Augmented Generation:** combine lexical BM25 and semantic pgvector retrieval, merge candidates and optionally rerank with a CrossEncoder.
- **Local LLMs:** Ollama integration for context-grounded question answering; optional structured JSON extraction with Pydantic validation and evidence-ID checking.
- **RFP Analysis:** a modular workflow for requirements identification, technical observations, resource estimation, financial calculations and risk flags.
- **Go/No-Go Decision Support:** explainable recommendations designed for **human approval**, not autonomous tender submission.
- **PDF Reporting:** an optional review report generated from the public workflow.
- **API & Testing:** FastAPI endpoints, synthetic examples, isolated unit/API tests and automated CI.

## Architecture

```text
               RFP / Tender Documents
                 PDF · DOCX · PPTX
                         │
               Document Intelligence
             extraction + text chunking
                         │
                Evidence / Metadata
                         │
          ┌──────────────┴──────────────┐
          │                             │
       BM25 Search              Semantic Search
     (keyword matching)       (Ollama embeddings)
          │                             │
          │                       PostgreSQL + pgvector
          │                             │
          └──────────────┬──────────────┘
                         │
               Hybrid Retrieval / Fusion
                         │
                CrossEncoder Reranking
                         │
                 Evidence Context
                         │
              Local LLM / Structured JSON
                         │
            ┌────────────┴────────────┐
            │                         │
     Requirement Extraction     Technical Evaluation
            │                         │
            ├── Resource Estimation    │
            ├── Financial Estimation   │
            └── Risk Analysis ─────────┘
                         │
              Go / No-Go Review
                         │
               PDF / FastAPI Outputs
                         │
               Human Validation
```

**Implementation note:** The architecture above describes the overall internship solution and the independently reconstructed public modules. The **offline demo** uses BM25 plus transparent example business logic; LLM, vector database and CrossEncoder integrations are optional and require local services. No private prompts, company data or internal pricing logic are reproduced.

## Technology stack

| Layer | Technologies | Purpose |
|---|---|---|
| Backend / API | Python, FastAPI, Pydantic | Typed requests and service endpoints |
| RAG orchestration | LangChain-compatible adapters | Query routing and evidence retrieval |
| Lexical retrieval | BM25 / `rank-bm25` | Exact-term relevance |
| Semantic retrieval | Ollama embeddings, PostgreSQL / pgvector | Contextual similarity search |
| Reranking | Sentence Transformers CrossEncoder | Context-specific candidate ranking |
| LLM | Ollama (e.g., Qwen3) | Grounded answers and structured extraction |
| Document processing | PyMuPDF, python-docx, python-pptx | PDF, Word and PowerPoint text extraction |
| Reports | ReportLab | PDF review report generation |
| Quality | pytest, GitHub Actions | Reproducible offline tests |

## Repository layout

```text
Spring-Next-Gen-RAG-AI/
├── src/rfp_ai/
│   ├── ingestion.py       # Local document extraction
│   ├── chunking.py        # Document segmentation and chunk metadata
│   ├── bm25.py            # Lexical retrieval
│   ├── fusion.py          # Hybrid result fusion and reranking
│   ├── adapters.py        # Ollama, pgvector and CrossEncoder adapters
│   ├── pipeline.py        # Retrieval orchestration
│   ├── hybrid.py          # Optional service-backed RAG QA
│   ├── structured_llm.py  # Typed LLM requirement extraction
│   ├── llm_workflow.py    # Structured LLM technical/resource/risk review
│   ├── workflow.py        # End-to-end fictional RFP review workflow
│   ├── analysis.py        # Lightweight analysis helpers
│   ├── reports.py         # PDF review report
│   ├── api.py             # FastAPI routes
│   ├── cli.py             # Full synthetic workflow CLI
│   └── demo.py            # Standalone retrieval demo
├── tests/                 # Offline unit and API tests
├── docs/                  # Architecture and security notes
├── .github/workflows/     # CI validation
├── .env.example
├── pyproject.toml
└── README.md
```

## Getting started

Requirements: **Python 3.10+**. The basic demo runs without an LLM, PostgreSQL or model downloads.

```bash
git clone https://github.com/MahdiBenHalima/Spring-Next-Gen-RAG-AI.git
cd Spring-Next-Gen-RAG-AI
python -m venv .venv
```

Activate the environment:

- **Windows PowerShell:** `.venv\Scripts\Activate.ps1`
- **Linux/macOS:** `source .venv/bin/activate`

Install and run:

```bash
python -m pip install -e ".[dev,reports]"
python -m rfp_ai.cli --pdf outputs/synthetic-review.pdf
python -m pytest -q
uvicorn rfp_ai.api:app --reload
```

The CLI uses fictional procurement text and user-specified example rates. It prints a JSON analysis and saves a PDF under `outputs/` (ignored by Git). API documentation is available at **http://127.0.0.1:8000/docs**.

### API endpoints

| Method | Endpoint | Behavior |
|---|---|---|
| `GET` | `/health` | Health status |
| `POST` | `/demo/analyze` | BM25 evidence search and lightweight demonstration |
| `POST` | `/api/v1/workflow/analyze` | Synthetic end-to-end RFP review (requirements, technical, resources, finance, risks, human decision) |
| `POST` | `/api/v1/workflow/report.pdf` | Download a PDF report for the public workflow |
| `POST` | `/api/v1/llm/review` | Optional Ollama-backed structured technical/resource/risk analysis from evidence |

Example:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/workflow/analyze \
  -H "Content-Type: application/json" \
  -d '{"tender_id":"DEMO-001","document_text":"REST API integration, security audit and documentation. Deadline December 20.","daily_rates":{"Backend engineer":400,"Security engineer":500,"Technical writer":200},"available_skills":["Backend engineer","Security engineer","Technical writer"],"budget_cap":20000}'
```

The workflow returns evidence-linked requirements, transparent effort/cost computations, observed risk flags and `HUMAN_REVIEW_REQUIRED`. **Rates, roles and efforts are invented demonstration assumptions, not real company estimates.**

## Enabling the optional Hybrid RAG + LLM stack

```bash
python -m pip install -e ".[rag,pdf,reports,dev]"
ollama pull qwen3:8b
ollama pull mxbai-embed-large
```

Configure PostgreSQL with the **pgvector extension**, set `DATABASE_URL` and any relevant `OLLAMA_*` variables (see `.env.example`), then use:

- `rfp_ai.adapters.index_in_pgvector` — embed and store permitted documents.
- `rfp_ai.adapters.search_pgvector` — tenant-filtered semantic retrieval.
- `rfp_ai.pipeline.retrieve` — combine semantic and BM25 candidates.
- `rfp_ai.adapters.cross_encoder_scoring` — optional CrossEncoder reranking.
- `rfp_ai.adapters.answer_with_ollama` — grounded question answering.
- `rfp_ai.hybrid.index_text` and `rfp_ai.hybrid.ask_hybrid` — opt-in service-backed ingestion and hybrid retrieval + LLM response.
- `rfp_ai.structured_llm.extract_structured_tender` — schema-validated extraction using a caller-provided LLM function.
- `rfp_ai.llm_workflow.analyze_with_ollama` — optional multi-stage structured LLM review with evidence-ID validation and human approval.

These are **integration components, not an automatically deployed service**. They require an external database and models and are not exercised by the offline CI matrix. An evaluation dataset and system-level integration tests are needed before claiming retrieval or decision accuracy.

## Quality and reproducibility

GitHub Actions checks **Python 3.10, 3.11 and 3.12**, compiling the package and executing offline tests with no credentials or AI model downloads. Tests cover evidence IDs, tender isolation, BM25 retrieval, hybrid rank fusion, reranker injection, schema validation, synthetic workflow estimates, safety guards and API behavior.

[View CI runs](https://github.com/MahdiBenHalima/Spring-Next-Gen-RAG-AI/actions)

## Project scope and confidentiality

The implementation demonstrates the **engineering approach** used in a wider tender-analysis platform. Some original modules, organization-specific knowledge, pricing policies, internal business data, documents, prompts and Angular/Spring Boot integrations are not available publicly because they belong to the project organization. The code here is intentionally **reconstructed**, not copied from the internal repository.

The public analysis is a **technical portfolio demonstration** and must not be treated as a production decision engine or proof of accuracy. All procurement decisions require human review.

---

**Focus areas:** AI Engineering · Hybrid RAG · Local LLMs · Document Intelligence · Semantic Search · Technical and Risk Analysis · FastAPI · Explainable Decision Support

**Author:** [Mahdi Ben Halima](https://github.com/MahdiBenHalima) · **Project:** Spring Next Gen, 2026
