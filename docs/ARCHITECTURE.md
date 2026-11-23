# Technical architecture

## 1. System overview

The original Spring Next Gen project analyzed tender documents using Python AI services integrated into a broader application. Core AI techniques verified in the private implementation included document extraction, text segmentation, Ollama embeddings, PostgreSQL/pgvector semantic retrieval, BM25 keyword retrieval, CrossEncoder reranking, local LLM prompting, typed JSON extraction, technical evaluation, resources, costs, risk analysis, Go/No-Go support and PDF generation.

The public repository reproduces these capabilities through **newly written, independent Python components**. It contains no Angular/Spring Boot application sources, real customer documents, proprietary prompts or internal rules.

## 2. Data flow

```text
 PDF / DOCX / PPTX / TXT
           |
       Extraction
           |
    Text segmentation
           |
         Chunks + metadata (tender_id, document_id, chunk_id)
           |
      +----+----+
      |         |
  BM25 Index   Ollama embeddings --> PostgreSQL/pgvector
      |         |
      +----+----+
           |
   Reciprocal Rank Fusion
           |
     CrossEncoder* 
           |
     Evidence snippets
           |
     Ollama LLM* --> structured schema validation*
           |
       RFP workflow
      /     |      \
 Requirements  Technical/Risk  Resources/Finance
      \     |      /
      Go/No-Go review
           |
     PDF / FastAPI
           |
       Human review
```

`*` Optional: requires models and services not launched by the offline CI.

## 3. Public modules

| Module | Purpose |
|---|---|
| `ingestion.py` | Parse permitted local text, PDF, DOCX, PPTX |
| `chunking.py` | Source-aware overlapping chunks |
| `bm25.py` | Lexical retrieval with tenant filtering |
| `adapters.py` | Ollama, pgvector and CrossEncoder integrations |
| `fusion.py` | Reciprocal-rank fusion; injectable reranking |
| `pipeline.py` | Hybrid candidate retrieval orchestration |
| `hybrid.py` | Opt-in service-backed ingestion and question answering |
| `llm_workflow.py` | Opt-in Ollama-backed structured technical, resources and risk review |
| `structured_llm.py` | Pydantic JSON schema and evidence ID checks |
| `workflow.py` | Independent, explainable example analysis stages |
| `reports.py` | PDF review export |
| `api.py` | HTTP endpoints |
| `cli.py` | Reproducible synthetic full-workflow demo |

## 4. Demonstration vs real integrations

**Offline path:** synthetic text → chunking → BM25 → observed requirement categories → illustrative effort/cost → risk flags → human review → optional PDF. It is deterministic and covered by CI.

**Opt-in service-backed path:** approved documents → pgvector indexing with Ollama embeddings → combined BM25 and semantic retrieval → CrossEncoder reranking → evidence-grounded Ollama answer. This requires a PostgreSQL pgvector instance, compatible Ollama models, and integration testing on the user's own infrastructure. It is not automatically used by the offline API.

The public pipeline adds **reciprocal rank fusion** to its independent implementation; it must not be described as an exact reproduction of the original private ranking formula.

## 5. Reliability and production gaps

- Retrieval validation: document-to-tender isolation, source IDs and no cross-tender vector hits.
- LLM validation: JSON schema checks and rejection of citations not in the supplied context, with no guarantee of factual correctness.
- Risk flags are informational, not regulatory or financial advice.
- Automatic bid submission and binding Go/No-Go decisions are intentionally disabled.
- No private corpora or historical evaluation set are published, so benchmark accuracy is not claimed.
- Network-exposed deployments additionally require authentication, access control, rate limits, privacy controls, monitoring, prompt-injection defenses and audit logging.
