"""Offline test suite: no Ollama, PostgreSQL, model downloads, or business data."""
import pytest
from fastapi.testclient import TestClient

from rfp_ai.analysis import assess
from rfp_ai.api import app
from rfp_ai.bm25 import BM25Index
from rfp_ai.chunking import chunk_text
from rfp_ai.demo import run_demo
from rfp_ai.fusion import reciprocal_rank_fusion, rerank
from rfp_ai.models import Chunk, Hit
from rfp_ai.pipeline import retrieve


def corpus():
    return [
        Chunk("1", "A", "d1", "REST API integration and documentation"),
        Chunk("2", "A", "d1", "Security audit and compliance requirements"),
        Chunk("3", "B", "d2", "API integration for another customer"),
    ]


def test_chunking_preserves_metadata_and_overlap():
    data = chunk_text("some meaningful words " * 30, tender_id="A", document_id="d")
    assert len(data) > 1
    assert all(x.tender_id == "A" and x.document_id == "d" for x in data)
    assert len({x.chunk_id for x in data}) == len(data)


def test_invalid_overlap_rejected():
    with pytest.raises(ValueError):
        chunk_text("some text", tender_id="A", document_id="d", overlap=1200)


def test_empty_text():
    assert chunk_text(" \n ", tender_id="A", document_id="d") == []


def test_bm25_tender_isolation():
    hits = BM25Index(corpus()).search("API integration", tender_id="A")
    assert hits and all(hit.chunk.tender_id == "A" for hit in hits)


def test_bm25_empty_corpus():
    assert BM25Index([]).search("x", tender_id="A") == []


def test_fusion_deduplicates():
    chunk = corpus()[0]
    fused = reciprocal_rank_fusion(
        [Hit(chunk, 0.1, "vector")], [Hit(chunk, 1.0, "bm25")]
    )
    assert len(fused) == 1 and fused[0].score > 0


def test_fusion_is_stable():
    items = [Hit(c, 1.0, "v") for c in corpus()[:2]]
    assert [h.chunk.chunk_id for h in reciprocal_rank_fusion(items, [])] == ["1", "2"]


def test_reranker_reorders():
    hits = [Hit(c, 1.0, "bm25") for c in corpus()[:2]]
    result = rerank("security", hits, lambda _, texts: [float("Security" in t) for t in texts])
    assert result[0].chunk.chunk_id == "2"


def test_reranker_bad_scores():
    with pytest.raises(ValueError):
        rerank("x", [Hit(corpus()[0], 1.0, "bm25")], lambda q, t: [])


def test_pipeline_filters_vector_cross_tender():
    other = Hit(corpus()[2], 1.0, "pgvector")
    hits = retrieve(
        "API integration", tender_id="A", chunks=corpus(),
        vector_search=lambda q, t, k: [other],
    )
    assert hits and all(h.chunk.tender_id == "A" for h in hits)


def test_missing_query_rejected():
    with pytest.raises(ValueError):
        retrieve(" ", tender_id="A", chunks=corpus())


def test_assessment_requires_review():
    result = assess("A", [Hit(corpus()[0], 1.0, "bm25")], person_days=5, daily_rate=200)
    assert result.go_no_go == "HUMAN_REVIEW_REQUIRED"
    assert result.estimated_cost == 1000


def test_assessment_rejects_incomplete_cost_inputs():
    with pytest.raises(ValueError):
        assess("A", [], daily_rate=100)


def test_demo_uses_only_synthetic_data():
    result = run_demo()
    assert result["dataset"] == "fictional_synthetic_example"
    assert result["assessment"]["go_no_go"] == "HUMAN_REVIEW_REQUIRED"


def test_health():
    response = TestClient(app).get("/health")
    assert response.status_code == 200


def test_demo_api():
    response = TestClient(app).post("/demo/analyze", json={
        "tender_id": "TEST-1",
        "document_text": "Security audit and REST API integration required.",
        "question": "What security requirements?",
        "person_days": 3,
        "daily_rate": 150,
    })
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "bm25_only"
    assert body["assessment"]["estimated_cost"] == 450
    assert body["assessment"]["go_no_go"] == "HUMAN_REVIEW_REQUIRED"


def test_invalid_request():
    response = TestClient(app).post("/demo/analyze", json={
        "tender_id": "A", "document_text": "Hello", "question": "",
    })
    assert response.status_code == 422
