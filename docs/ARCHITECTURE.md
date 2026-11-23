# System design and tradeoffs

## Original workflow (architecture verified from inspected private source)

Documents are extracted and split, Ollama embeddings are stored using LangChain's PGVector integration, and questions are retrieved using both vector similarity and BM25. A CrossEncoder reorders the combined candidates before an Ollama chat model is prompted with context. Separate analysis modules perform requirements, technical, risk and resource analysis, followed by financial and Go/No-Go services. FastAPI routes integrate the components with a wider Angular/Spring Boot system.

## Public workflow (new implementation)

```
             synthetic text or approved local PDF
                           |
                     chunk_text()
                           |
       +-------------------+------------------+
       |                                      |
  BM25Index.search()                  search_pgvector()*
       |                                      |
       +-------------------+------------------+
                           |
                  reciprocal_rank_fusion()
                           |
                  CrossEncoder rerank()*
                           |
                      evidence hits
                           |
                    assess() / API
                           |
                 HUMAN_REVIEW_REQUIRED
```

`*` Optional adapters require external infrastructure; offline tests use deterministic stub functions where needed.

## Design choices

- **Tenant filter:** every retrieval query specifies a tender ID, and external vector results are filtered again at the orchestration boundary.
- **Evidence:** every chunk has a stable ID and document reference. Responses include evidence snippets.
- **Lexical + semantic:** lexical retrieval handles exact terminology; semantic retrieval can capture paraphrases. RRF avoids requiring comparable score scales.
- **Reranking:** a CrossEncoder can improve candidate ordering at additional compute cost. It is loaded only when explicitly requested.
- **LLM isolation:** Ollama invocation is opt-in, separated from the deterministic CI path.
- **Human review:** financial figures are user-supplied example arithmetic; no tender acceptance decision is made automatically.

## Known limitations

The public demo is not a fully integrated RFP lifecycle platform. It lacks authentication, rate limiting, evaluation datasets, complete LLM schema extraction, automated PDF proposals, and production authorization. It should be deployed only behind appropriate security controls. The PDF extraction example does not OCR scanned PDFs. Source-page citations and strict schema extraction would be required for a trustworthy production assessment.
