"""Whitespace-aware overlapping text segmentation with source identifiers."""
from .models import Chunk


def chunk_text(
    text: str, *, tender_id: str, document_id: str,
    chunk_size: int = 1200, overlap: int = 200,
) -> list[Chunk]:
    if not 0 <= overlap < chunk_size:
        raise ValueError("overlap must be nonnegative and smaller than chunk_size")
    if not tender_id or not document_id:
        raise ValueError("tender_id and document_id are required")
    text = " ".join(text.split())
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            boundary = text.rfind(" ", start + max(chunk_size // 2, 1), end)
            if boundary > start:
                end = boundary
        segment = text[start:end].strip()
        if segment:
            index = len(chunks)
            chunks.append(Chunk(
                chunk_id=f"{tender_id}:{document_id}:{index}",
                tender_id=tender_id,
                document_id=document_id,
                index=index,
                text=segment,
            ))
        if end == len(text):
            break
        start = max(start + 1, end - overlap)
    return chunks
