"""Hybrid retrieval orchestration. Vector retrieval and reranker are injectable."""
from collections.abc import Callable
from .bm25 import BM25Index
from .fusion import reciprocal_rank_fusion, rerank
from .models import Chunk, Hit


def retrieve(
    question: str, *, tender_id: str, chunks: list[Chunk],
    vector_search: Callable[[str, str, int], list[Hit]] | None = None,
    reranker: Callable[[str, list[str]], list[float]] | None = None,
    candidate_k: int = 10, top_k: int = 5,
) -> list[Hit]:
    if not question.strip() or not tender_id.strip():
        raise ValueError("Question and tender_id must be nonempty")
    bm25 = BM25Index(chunks).search(question, tender_id=tender_id, k=candidate_k)
    vector = vector_search(question, tender_id, candidate_k) if vector_search else []
    # Defense in depth: an external vector store may return a different tender.
    vector = [hit for hit in vector if hit.chunk.tender_id == tender_id]
    fused = reciprocal_rank_fusion(vector, bm25)
    if reranker is not None:
        return rerank(question, fused, reranker, top_k=top_k)
    return fused[:max(0, top_k)]
