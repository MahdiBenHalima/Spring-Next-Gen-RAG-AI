# Traceability to the private Spring Next Gen implementation

This document records what was actually inspected in the connected private GitHub repository and how the portfolio reconstruction differs. It is **not** permission to redistribute employer-owned source code.

## Inspected original paths (private; not linked publicly)

| Original path under `Next_Gen/` | Observed mechanism | Public counterpart | Status |
|---|---|---|---|
| `app/retrieval/chunking_service.py` | Recursive character segmentation; 1200 size / 200 overlap; tender/document/chunk metadata | `src/rfp_ai/chunking.py` | Independently reimplemented |
| `app/retrieval/bm25_service.py` | `rank_bm25.BM25Okapi` and simple lexical tokenization | `src/rfp_ai/bm25.py` | Independently reimplemented |
| `app/retrieval/vector_service.py` | OllamaEmbeddings and PostgreSQL PGVector with tender-ID filtering | `src/rfp_ai/adapters.py` | Optional integration reconstructed |
| `app/retrieval/reranker_service.py` | CrossEncoder `ms-marco-MiniLM-L-6-v2` reranks de-duplicated candidates | `src/rfp_ai/fusion.py` and `adapters.py` | Optional integration reconstructed |
| `app/retrieval/rag_service.py` | BM25 + semantic retrieval, reranking and prompt context | `src/rfp_ai/pipeline.py` | Independently reimplemented; RRF is new |
| `app/retrieval/llm_extraction_service.py` | Local Ollama chat, prompt-based extraction and JSON parsing | `src/rfp_ai/adapters.py` | Context-answering adapter only; structured extraction not duplicated |
| `app/agents/requirements/service.py` | RAG context passed through LLM prompt and typed JSON schema | README and architecture docs | Documented, not ported |
| `app/agents/technical/analysis_service.py` | Ollama LLM, JSON output parser, normalization, Pydantic validation | README and architecture docs | Documented, not ported |
| `app/agents/go_no_go/service.py` | Combine technical, resource, budget and risk outputs, use business context/scoring and persist result | `src/rfp_ai/analysis.py` | Simplified, safe demo; no claim of decision parity |
| `app/main.py` | FastAPI application with route mounting | `src/rfp_ai/api.py` | Independent minimal endpoints |
| `requirements.txt` | Lists FastAPI, LangChain, pgvector and other dependencies | `pyproject.toml` | Reproducible package declaration updated for public demo |

## Explicit differences

1. The original retrieval workflow obtains the BM25 candidate pool from a limited vector-store similarity search; the public demo uses an in-memory BM25 corpus, and can optionally query pgvector. These are **not** equivalent retrieval experiments.
2. Reciprocal rank fusion (RRF) is a documented **public-demo addition**, not a claim about the private algorithm.
3. The demo's keyword detection is **not** the original LLM-driven requirements/technical analysis.
4. The public demonstration does not contain proprietary costing rules, customer rates, company profiles, SQL data, private prompts or PDF output templates.
5. No accuracy, precision, retrieval recall, decision quality or business ROI results are claimed because no comparable evaluation set was supplied.
6. The upstream private implementation was inspected for technical correspondence only; this public code was created independently for portfolio use and requires review of employer/IP obligations.

## What to validate before citing in a CV

The CV may accurately refer to internship work on hybrid RAG, LLM analysis, FastAPI integration and Go/No-Go support. Link this public repository as an **independent portfolio reconstruction** illustrating key methods, not as a complete public release of the production internship application.
