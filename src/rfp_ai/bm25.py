"""Lexical retrieval across the complete in-memory corpus, filtered by tender."""
import re
from rank_bm25 import BM25Okapi
from .models import Chunk, Hit


def tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.casefold(), flags=re.UNICODE)


class BM25Index:
    def __init__(self, chunks: list[Chunk]):
        self.chunks = list(chunks)
        self._bm25 = BM25Okapi([tokenize(c.text) for c in chunks]) if chunks else None

    def search(self, question: str, *, tender_id: str, k: int = 10) -> list[Hit]:
        if not self._bm25 or k <= 0:
            return []
        scores = self._bm25.get_scores(tokenize(question))
        ranked = sorted(
            ((chunk, float(score)) for chunk, score in zip(self.chunks, scores)
             if chunk.tender_id == tender_id and set(tokenize(question)) & set(tokenize(chunk.text))),
            key=lambda item: (-item[1], item[0].chunk_id),
        )
        return [Hit(chunk=chunk, score=score, source="bm25") for chunk, score in ranked[:k]]
