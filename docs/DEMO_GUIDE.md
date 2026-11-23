# Portfolio demonstration guide

This guide shows how to demonstrate the publicly reproducible AI workflow without exposing internal documents.

## Quick presentation (3 minutes)

1. Explain the problem: procurement teams receive unstructured technical requirements and need an evidence-based review workflow.
2. Show the hybrid retrieval architecture: BM25 for exact terms, PGVector for semantic similarity and optional CrossEncoder reranking.
3. Run the synthetic workflow end to end (requirements, technical observations, resource estimate, financial estimate, risk flags, Go/No-Go human review).
4. Open the FastAPI OpenAPI docs and demonstrate JSON inputs and outputs.
5. Generate a PDF review report and show the GitHub Actions validation.
6. Clarify that original company data, internal prompts and pricing logic are not published.

## Reproducible commands

```bash
python -m pip install -e ".[dev,reports]"
python -m rfp_ai.cli --pdf outputs/synthetic-review.pdf
python -m pytest -q
uvicorn rfp_ai.api:app --reload
```

The CLI shows a fictional RFP containing API integration, a security audit, documentation and a deadline. All default effort assumptions are purely illustrative and not employer-based.

## Interview discussion points

**What makes it RAG?** The optional service-backed path retrieves document evidence through lexical and vector search and sends bounded context to a local LLM. The offline demo tests the retrieval and deterministic workflow without model downloads.

**Why hybrid retrieval?** Procurement documents often include exact technical strings and paraphrased requirements. Lexical and semantic methods cover different retrieval needs.

**Why reranking?** A CrossEncoder can score query–chunk pairs more precisely after a first-stage candidate search, at extra latency.

**Why typed schemas?** Structured requirement extraction has predictable fields. Pydantic validation catches malformed output and evidence-ID checks reject unsupported citations.

**Why human review?** Costing, legal compliance, organization capabilities and bid decisions involve real-world risk and business policy not represented in the synthetic demo.

## Limitations to disclose

This public code is a fresh technical showcase, not the complete company application. The default workflow's rule-based technical/risk/financial analysis is illustrative and different from the original LLM-supported modules. Optional real RAG components are not covered by the offline CI suite.
