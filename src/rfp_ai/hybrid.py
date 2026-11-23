"""Service-backed Hybrid RAG pipeline (optional Ollama/PGVector/CE stack).

Calls real services only when explicitly invoked; not run by default CI.
"""
from .adapters import (
    answer_with_ollama, cross_encoder_scoring, index_in_pgvector,
    search_pgvector,
)
from .bm25 import BM25Index
from .chunking import chunk_text
from .models import Chunk
from .pipeline import retrieve


def index_text(text: str, *, tender_id: str, document_id: str) -> dict:
    chunks = chunk_text(text, tender_id=tender_id, document_id=document_id)
    count = index_in_pgvector(chunks)
    return {"tender_id": tender_id, "document_id": document_id, "indexed_chunks": count}


def ask_hybrid(
    question: str, *,
    tender_id: str,
    candidate_chunks: list[Chunk],
    use_reranker: bool = True,
) -> dict:
    """Requires Ollama and PostgreSQL/PGVector.

    BM25 operates on candidate_chunks supplied by the caller: for true corpus-wide
    lexical recall, provide the complete authorized tender chunk collection.
    """
    scoring = cross_encoder_scoring() if use_reranker else None
    hits = retrieve(
        question,
        tender_id=tender_id,
        chunks=candidate_chunks,
        vector_search=lambda q, t, k: search_pgvector(q, tender_id=t, k=k),
        reranker=scoring,
    )
    answer = answer_with_ollama(question, hits)
    return {
        "tender_id": tender_id,
        "question": question,
        "retrieval_mode": "hybrid_bm25_pgvector_crossencoder" if use_reranker
                          else "hybrid_bm25_pgvector_rrf",
        "answer": answer,
        "evidence": [
            {"chunk_id": hit.chunk.chunk_id, "document_id": hit.chunk.document_id,
             "excerpt": hit.chunk.text, "retrieval_score": hit.score}
            for hit in hits
        ],
        "requires_human_verification": True,
    }
