"""Portable models intentionally independent of the private application database."""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    tender_id: str
    document_id: str
    text: str
    index: int = 0
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Hit:
    chunk: Chunk
    score: float
    source: str


@dataclass(frozen=True)
class Evidence:
    chunk_id: str
    document_id: str
    excerpt: str
