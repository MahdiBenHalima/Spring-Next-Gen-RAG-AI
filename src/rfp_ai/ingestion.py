"""Local text/PDF extraction; no customer documents are shipped with this repository."""
from pathlib import Path
from .chunking import chunk_text
from .models import Chunk


def read_document(path: str | Path) -> str:
    path = Path(path)
    if path.suffix.lower() in {".txt", ".md"}:
        return path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".pdf":
        try:
            import fitz
        except ImportError as exc:
            raise RuntimeError("Install the PDF extra: pip install -e '.[pdf]'") from exc
        with fitz.open(path) as pdf:
            return "\n".join(page.get_text() for page in pdf)
    if path.suffix.lower() == ".docx":
        try:
            from docx import Document
        except ImportError as exc:
            raise RuntimeError("Install the PDF/document extra: pip install -e '.[pdf]'") from exc
        doc = Document(path)
        return "\\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip())
    if path.suffix.lower() == ".pptx":
        try:
            from pptx import Presentation
        except ImportError as exc:
            raise RuntimeError("Install the PDF/document extra: pip install -e '.[pdf]'") from exc
        presentation = Presentation(path)
        return "\\n".join(
            shape.text for slide in presentation.slides for shape in slide.shapes
            if shape.has_text_frame and shape.text.strip()
        )
    raise ValueError("Supported formats: .txt, .md, .pdf, .docx and .pptx")


def prepare_document(path: str | Path, *, tender_id: str) -> list[Chunk]:
    path = Path(path)
    return chunk_text(read_document(path), tender_id=tender_id, document_id=path.stem)
