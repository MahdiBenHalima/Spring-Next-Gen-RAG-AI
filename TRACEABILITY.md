# Engineering provenance and scope

This document explains which features of the original Spring Next Gen architecture were inspected and how they are represented in the independent public implementation. No private source file was copied verbatim into this repository.

| Capability in original private Python project | Public implementation | Scope |
|---|---|---|
| Multi-format document extraction | `src/rfp_ai/ingestion.py` | TXT, MD, PDF, DOCX and PPTX |
| Chunking with tender/document metadata | `src/rfp_ai/chunking.py` | Source-aware segmentation |
| BM25 lexical retrieval | `src/rfp_ai/bm25.py` | In-memory, tender-filtered search |
| Ollama embeddings + PGVector | `src/rfp_ai/adapters.py` | Optional external services |
| Combined vector/BM25 retrieval | `src/rfp_ai/pipeline.py`, `fusion.py` | Independent RRF fusion |
| CrossEncoder reranking | `src/rfp_ai/adapters.py`, `fusion.py` | Optional model |
| Ollama question answering | `src/rfp_ai/adapters.py`, `hybrid.py` | Optional evidence-grounded generation |
| LLM JSON extraction for requirements | `src/rfp_ai/structured_llm.py` | Independent typed extraction interface |
| Technical, risk and resource modules | `src/rfp_ai/workflow.py` | Explainable example logic, no private company rules |
| Financial estimation and Go/No-Go | `src/rfp_ai/workflow.py` | Illustrative inputs and mandatory human review |
| PDF generation | `src/rfp_ai/reports.py` | Reconstructed PDF report |
| FastAPI routes | `src/rfp_ai/api.py` | Standalone public API |

## Scope boundaries

The original intern project used dedicated analysis modules with LLM-generated structured results and organization-specific decision policies. In the public demonstration, workflow estimates and risk observations are **simplified example algorithms**. They are not the employer's algorithms, pricing policies, output schema or validated production results. The optional Ollama adapters and structured extraction provide technical integration points but have not been benchmarked against the private system.

Internal tender documents, private business data, application integrations, original prompts and other restricted assets remain unpublished because they are associated with the organization. This independent implementation is intended to demonstrate the engineering methods without revealing them.

## Evidence reviewed (private repository)

The original design was checked against `Next_Gen/app/retrieval/`, `Next_Gen/app/agents/`, `Next_Gen/app/api/`, `Next_Gen/app/common/report_generator.py` and the private dependency/configuration files. The private repository is not referenced by a public hyperlink. This statement records an architectural review, **not** permission to redistribute underlying materials.

## Reproducibility

- Offline workflows use synthetic text and fictional rate inputs.
- GitHub Actions runs Python package compilation, tests, a synthetic demonstration and PDF output checks.
- PostgreSQL, pgvector, Ollama and CrossEncoder require separate opt-in integration setup.
- No quantitative performance or commercial outcome parity with the private system is claimed.
