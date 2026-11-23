"""Mock-only schema and evidence checks. Never download a model in CI."""
import json
import pytest
from rfp_ai.llm_workflow import analyze_rfp_with_llm

EXAMPLE = [{"chunk_id": "T1:doc:0", "excerpt": "REST API and security audit."}]


def example_output():
    return {
        "executive_summary": "Example",
        "technical": {"integrations": ["REST API"]},
        "resources": [{
            "role": "Backend engineer",
            "justification": "API integration",
            "estimated_person_days": None,
            "evidence_ids": ["T1:doc:0"],
        }],
        "risks": [{
            "category": "Security",
            "severity": "medium",
            "explanation": "Audit is required",
            "evidence_ids": ["T1:doc:0"],
        }],
        "decision": "HUMAN_REVIEW_REQUIRED",
    }


def test_mock_llm_structured_review():
    result = analyze_rfp_with_llm(EXAMPLE, generate=lambda p: json.dumps(example_output()))
    assert result.technical.integrations == ["REST API"]
    assert result.resources[0].estimated_person_days is None
    assert result.decision == "HUMAN_REVIEW_REQUIRED"


def test_no_automatic_go():
    obj = example_output()
    obj["decision"] = "GO"
    with pytest.raises(ValueError):
        analyze_rfp_with_llm(EXAMPLE, generate=lambda p: json.dumps(obj))


def test_unknown_evidence_rejected():
    obj = example_output()
    obj["risks"][0]["evidence_ids"] = ["unsupported"]
    with pytest.raises(ValueError, match="unsupported"):
        analyze_rfp_with_llm(EXAMPLE, generate=lambda p: json.dumps(obj))


def test_requires_evidence():
    with pytest.raises(ValueError):
        analyze_rfp_with_llm([], generate=lambda p: "{}")
