"""Reciprocal rank fusion and injectable CrossEncoder-style reranking."""
from collections.abc import Callable
from .models import Chunk, Hit


def reciprocal_rank_fusion(
    vector_hits: list[Hit], lexical_hits: list[Hit], *, k: int = 60
) -> list[Hit]:
    if k <= 0:
        raise ValueError("k must be > 0")
    documents: dict[str, Chunk] = {}
    combined: dict[str, float] = {}
    for hits in (vector_hits, lexical_hits):
        seen: set[str] = set()
        for rank, hit in enumerate(hits, start=1):
            key = hit.chunk.chunk_id
            if key in seen:
                continue
            seen.add(key)
            documents[key] = hit.chunk
            combined[key] = combined.get(key, 0.0) + 1.0 / (k + rank)
    return [
        Hit(chunk=documents[key], score=score, source="rrf")
        for key, score in sorted(combined.items(), key=lambda item: (-item[1], item[0]))
    ]


def rerank(
    question: str, candidates: list[Hit], scoring: Callable[[str, list[str]], list[float]],
    *, top_k: int = 5,
) -> list[Hit]:
    if top_k <= 0 or not candidates:
        return []
    scores = scoring(question, [hit.chunk.text for hit in candidates])
    if len(scores) != len(candidates):
        raise ValueError("Reranker must return one score per candidate")
    ranked = [
        Hit(chunk=hit.chunk, score=float(score), source="cross_encoder")
        for hit, score in zip(candidates, scores)
    ]
    return sorted(ranked, key=lambda h: (-h.score, h.chunk.chunk_id))[:top_k]
