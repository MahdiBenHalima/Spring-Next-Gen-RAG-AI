"""Deterministic tests of the public reconstructed end-to-end demo."""
import json
import pytest

from rfp_ai.workflow import analyze_workflow
from rfp_ai.structured_llm import (
    extract_structured_tender, parse_structured_response,
)
from rfp_ai.cli import main as cli_main


def test_workflow_has_all_stages():
    output = analyze_workflow(
        "REST API integration, security audit and documentation. Deadline December 20.",
        "SYN-10",
        daily_rates={"Backend engineer": 400, "Security engineer": 500,
                     "Technical writer": 200},
        available_skills=["Backend engineer", "Security engineer", "Technical writer"],
        budget_cap=20000,
    ).as_dict()
    assert len(output["requirements"]) >= 2
    assert output["technical"]["requirement_count"] >= 2
    assert output["financial"]["rate_status"] == "COMPLETE"
    assert output["financial"]["illustrative_total"] > 0
    assert output["resources"]
    assert output["go_no_go"]["decision"] == "HUMAN_REVIEW_REQUIRED"
    assert output["status"] == "INTERNAL_DEMONSTRATION"


def test_missing_rates_are_not_invented():
    output = analyze_workflow("REST API integration", "SYN-11").as_dict()
    assert output["financial"]["illustrative_total"] is None
    assert output["financial"]["rate_status"] == "MISSING_RATES"
    assert any(r["category"] == "Estimation" for r in output["risks"])


def test_missing_capability_risk():
    output = analyze_workflow(
        "Security audit", "SYN-12",
        available_skills=["Backend engineer"],
        daily_rates={"Security engineer": 500},
    ).as_dict()
    assert any(r["category"] == "Capability" for r in output["risks"])


def test_bad_rates_and_empty_input_rejected():
    with pytest.raises(ValueError):
        analyze_workflow("x", "A", daily_rates={"Backend engineer": -1})
    with pytest.raises(ValueError):
        analyze_workflow("", "A")


def test_fenced_json_validation():
    obj = parse_structured_response(
        '```json\n{"summary":"ok","requirements":[]}\n```'
    )
    assert obj.summary == "ok"


def test_injected_generator_is_deterministic_and_schema_checked():
    def fake_llm(prompt):
        assert "UNTRUSTED" in prompt
        return json.dumps({
            "summary": "A fictional example",
            "requirements": [{
                "title": "API", "kind": "technical", "evidence_ids": ["doc:0"]
            }],
        })
    result = extract_structured_tender(
        "Extract requirements", "[doc:0] REST API required", generate=fake_llm
    )
    assert result.requirements[0].evidence_ids == ["doc:0"]


def test_hallucinated_citation_rejected():
    with pytest.raises(ValueError, match="absent"):
        extract_structured_tender(
            "Summarize", "[doc:0] Example",
            generate=lambda prompt: json.dumps({
                "summary": "x",
                "requirements": [{"title": "x", "kind": "technical",
                                  "evidence_ids": ["fake:100"]}],
            }),
        )


def test_cli_json_output(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["rfp_ai.cli"])
    cli_main()
    obj = json.loads(capsys.readouterr().out)
    assert obj["go_no_go"]["decision"] == "HUMAN_REVIEW_REQUIRED"
