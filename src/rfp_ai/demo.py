"""Reproducible synthetic demo. No private tender PDFs or company data."""
import json
from .analysis import assess
from .chunking import chunk_text
from .pipeline import retrieve


SYNTHETIC_TENDER = (
    "Synthetic example request for proposal. The client requires an API integration "
    "with REST endpoints, security audit, project documentation and delivery "
    "within twelve weeks. All organization names and requirements are fictional. "
    "A detailed assessment needs technical and budget validation by a human."
)


def run_demo() -> dict:
    chunks = chunk_text(
        SYNTHETIC_TENDER,
        tender_id="SYNTHETIC-001",
        document_id="fictional-example",
        chunk_size=150,
        overlap=25,
    )
    hits = retrieve(
        "What API integration and security requirements are stated?",
        tender_id="SYNTHETIC-001", chunks=chunks,
    )
    assessment = assess("SYNTHETIC-001", hits, person_days=20, daily_rate=400.0)
    return {
        "dataset": "fictional_synthetic_example",
        "retrieval_mode": "bm25_only_without_optional_services",
        "retrieved_evidence": [
            {"chunk_id": h.chunk.chunk_id, "text": h.chunk.text}
            for h in hits
        ],
        "assessment": assessment.to_dict(),
    }


if __name__ == "__main__":
    print(json.dumps(run_demo(), ensure_ascii=False, indent=2))
