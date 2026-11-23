"""Small self-contained FastAPI portfolio surface; no database required."""
from fastapi import FastAPI
from pydantic import BaseModel, Field
from .analysis import assess
from .chunking import chunk_text
from .pipeline import retrieve


app = FastAPI(title="RFP Hybrid RAG Portfolio Demo", version="0.1.0")


class AnalysisRequest(BaseModel):
    tender_id: str = Field(min_length=1, max_length=100)
    document_text: str = Field(min_length=1, max_length=100_000)
    question: str = Field(min_length=1, max_length=2000)
    person_days: int | None = Field(default=None, ge=0)
    daily_rate: float | None = Field(default=None, ge=0)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/demo/analyze")
def analyze(request: AnalysisRequest) -> dict:
    """Keyword/BM25 demonstration; no LLM or PGVector implied for this endpoint."""
    chunks = chunk_text(
        request.document_text,
        tender_id=request.tender_id,
        document_id="request_text",
    )
    hits = retrieve(request.question, tender_id=request.tender_id, chunks=chunks)
    assessment = assess(
        request.tender_id, hits,
        person_days=request.person_days,
        daily_rate=request.daily_rate,
    )
    return {
        "mode": "bm25_only",
        "evidence": [
            {"chunk_id": h.chunk.chunk_id, "excerpt": h.chunk.text}
            for h in hits
        ],
        "assessment": assessment.to_dict(),
    }


# Portfolio workflow additions. These endpoints use independent, fictional demo rules.
from io import BytesIO
from fastapi.responses import StreamingResponse
from .workflow import analyze_workflow


class WorkflowRequest(BaseModel):
    tender_id: str = Field(min_length=1, max_length=100)
    document_text: str = Field(min_length=1, max_length=100_000)
    daily_rates: dict[str, float] = Field(default_factory=dict)
    available_skills: list[str] | None = None
    budget_cap: float | None = Field(default=None, ge=0)


@app.post("/api/v1/workflow/analyze")
def workflow_analysis(request: WorkflowRequest) -> dict:
    return analyze_workflow(
        request.document_text,
        request.tender_id,
        daily_rates=request.daily_rates,
        available_skills=request.available_skills,
        budget_cap=request.budget_cap,
    ).as_dict()


@app.post("/api/v1/workflow/report.pdf")
def workflow_pdf(request: WorkflowRequest) -> StreamingResponse:
    from .reports import pdf_report
    result = workflow_analysis(request)
    output = pdf_report(result)
    return StreamingResponse(
        BytesIO(output),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="rfp-review-demo.pdf"'},
    )
