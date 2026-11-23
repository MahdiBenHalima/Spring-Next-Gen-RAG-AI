from fastapi.testclient import TestClient
from rfp_ai.api import app

client = TestClient(app)


def example_request():
    return {
        "tender_id": "PUBLIC-DEMO-1",
        "document_text": "REST API integration and security audit. Deadline December 20.",
        "daily_rates": {
            "Backend engineer": 450.0,
            "Security engineer": 550.0,
        },
        "available_skills": ["Backend engineer", "Security engineer"],
        "budget_cap": 15000.0,
    }


def test_workflow_endpoint_exposes_reviewable_stages():
    result = client.post("/api/v1/workflow/analyze", json=example_request())
    assert result.status_code == 200
    data = result.json()
    assert data["status"] == "INTERNAL_DEMONSTRATION"
    assert data["technical"]["requirement_count"] > 0
    assert data["resources"] and data["financial"]["illustrative_total"] > 0
    assert data["go_no_go"]["decision"] == "HUMAN_REVIEW_REQUIRED"


def test_workflow_request_validation():
    result = client.post("/api/v1/workflow/analyze", json={
        "tender_id": "T-1", "document_text": "Hello", "budget_cap": -100,
    })
    assert result.status_code == 422


def test_pdf_endpoint():
    result = client.post("/api/v1/workflow/report.pdf", json=example_request())
    assert result.status_code == 200
    assert result.headers["content-type"] == "application/pdf"
    assert result.content.startswith(b"%PDF")
