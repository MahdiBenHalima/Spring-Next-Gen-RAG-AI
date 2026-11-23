# Public-repository security and data boundaries

- The code here is **newly authored demonstration code**, not a wholesale release of private internship sources.
- Synthetic input only. Do not commit actual tenders, customer documents, company pricing, employee names, customer IDs, exported databases, model weights, API keys or JWT secrets.
- `.gitignore` excludes `.env`, local data directories, uploads and runtime outputs. This does **not** protect credentials hard-coded in source code: review every diff.
- Postgres connection URLs must be injected as `DATABASE_URL` at runtime; do not put credentials in commit history.
- The optional Ollama adapter sends provided context to the configured Ollama server; use only servers and documents you are authorized to process.
- The optional vector adapter persists document contents to the target database. Do not use customer content for demonstrations.
- The public FastAPI endpoint has no authentication; use only as a local learning demo. Never expose it to the internet with sensitive input.
- Prompts treat retrieved text as untrusted data; prompt injection and hallucination risk remain and require independent review.
- `HUMAN_REVIEW_REQUIRED` is intentionally returned instead of automating legal/commercial tender decisions.
- Publishing even rewritten project architecture can carry IP or confidentiality obligations; obtain approval as required by internship agreements.
