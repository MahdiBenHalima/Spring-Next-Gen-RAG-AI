"""Standalone public RFP workflow with transparent deterministic, reviewable outputs.

The original internship project used LLM-driven modules and internal business rules.
This workflow uses newly written example logic; it is not a copy or validation of them.
"""
from dataclasses import asdict, dataclass, field
import re

from .chunking import chunk_text
from .models import Hit
from .pipeline import retrieve


@dataclass(frozen=True)
class Requirement:
    category: str
    description: str
    evidence_id: str
    confidence: str = "keyword_observation"


@dataclass(frozen=True)
class Risk:
    category: str
    severity: str
    rationale: str
    evidence_id: str | None = None


@dataclass(frozen=True)
class ResourceLine:
    role: str
    person_days: int
    daily_rate: float
    amount: float


@dataclass(frozen=True)
class WorkflowResult:
    tender_id: str
    status: str
    requirements: list[Requirement]
    technical: dict
    resources: list[ResourceLine]
    financial: dict
    risks: list[Risk]
    go_no_go: dict
    evidence: list[dict] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return asdict(self)


# Fictional scenario defaults are editable and are NOT internal pricing rules.
DEMO_ROLES = {
    "API integration": ("Backend engineer", 12),
    "Security assessment": ("Security engineer", 8),
    "Data engineering": ("Data engineer", 10),
    "Documentation": ("Technical writer", 4),
}
TERMS = {
    "API integration": ("api", "rest", "integration", "interface"),
    "Security assessment": ("security", "audit", "pentest", "sécurité"),
    "Data engineering": ("etl", "data pipeline", "analytics", "données"),
    "Documentation": ("documentation", "livrable", "deliverable", "guide"),
}


def _observed(text: str, words: tuple[str, ...]) -> bool:
    return any(re.search(r"(?<!\w)" + re.escape(w) + r"(?!\w)", text, re.I) for w in words)


def analyze_workflow(
    document_text: str,
    tender_id: str,
    *,
    daily_rates: dict[str, float] | None = None,
    available_skills: list[str] | None = None,
    budget_cap: float | None = None,
    vector_search=None,
    reranker=None,
) -> WorkflowResult:
    """Analyze a fictional tender. Never automatically issue a binding GO decision."""
    if not document_text.strip() or not tender_id.strip():
        raise ValueError("document_text and tender_id are mandatory")
    if budget_cap is not None and budget_cap < 0:
        raise ValueError("budget_cap cannot be negative")
    rates = daily_rates or {}
    if any(rate < 0 for rate in rates.values()):
        raise ValueError("Daily rates cannot be negative")
    chunks = chunk_text(document_text, tender_id=tender_id, document_id="input")
    requirements: list[Requirement] = []
    evidence: dict[str, Hit] = {}
    for name, terms in TERMS.items():
        for chunk in chunks:
            if _observed(chunk.text, terms):
                requirements.append(Requirement(name, name + " mentioned in the supplied document", chunk.chunk_id))
                hits = retrieve(
                    " ".join(terms), tender_id=tender_id, chunks=chunks,
                    vector_search=vector_search, reranker=reranker,
                )
                if hits:
                    evidence[hits[0].chunk.chunk_id] = hits[0]
                break

    lines: list[ResourceLine] = []
    for item in requirements:
        role, days = DEMO_ROLES[item.category]
        if role not in rates:
            continue  # Missing rates are never fabricated.
        rate = float(rates[role])
        lines.append(ResourceLine(role, days, rate, round(days * rate, 2)))
    total_days = sum(line.person_days for line in lines)
    total_cost = round(sum(line.amount for line in lines), 2)
    expected_roles = [DEMO_ROLES[r.category][0] for r in requirements]
    missing_rates = [role for role in expected_roles if role not in rates]
    known_skills = {skill.casefold() for skill in (available_skills or [])}
    missing_skills = [
        role for role in expected_roles
        if available_skills is not None and role.casefold() not in known_skills
    ]

    risks: list[Risk] = []
    if missing_rates:
        risks.append(Risk("Estimation", "high", "Missing approved rates: " + ", ".join(missing_rates)))
    if missing_skills:
        risks.append(Risk("Capability", "high", "Required roles not evidenced: " + ", ".join(missing_skills)))
    if budget_cap is not None and total_cost > budget_cap and not missing_rates:
        risks.append(Risk("Budget", "high", "Illustrative cost exceeds provided budget cap"))
    if not requirements:
        risks.append(Risk("Evidence", "high", "No demonstration keyword categories detected"))
    if not _observed(document_text, ("deadline", "due date", "date limite", "échéance")):
        risks.append(Risk("Schedule", "medium", "Deadline not established by basic pattern matching"))

    return WorkflowResult(
        tender_id=tender_id,
        status="INTERNAL_DEMONSTRATION",
        requirements=requirements,
        technical={
            "detected_categories": [r.category for r in requirements],
            "requirement_count": len(requirements),
            "assessment_method": "explainable keyword evidence, not technical LLM scoring",
        },
        resources=lines,
        financial={
            "estimated_person_days_for_priced_roles": total_days,
            "illustrative_total": total_cost if not missing_rates else None,
            "currency": "USER_DEFINED",
            "rate_status": "COMPLETE" if not missing_rates else "MISSING_RATES",
            "budget_cap": budget_cap,
            "missing_rates": missing_rates,
        },
        risks=risks,
        go_no_go={
            "decision": "HUMAN_REVIEW_REQUIRED",
            "automatic_decision_enabled": False,
            "observations": [r.rationale for r in risks],
        },
        evidence=[
            {"chunk_id": hit.chunk.chunk_id, "document_id": hit.chunk.document_id,
             "excerpt": hit.chunk.text}
            for hit in evidence.values()
        ],
        limitations=[
            "Demo categories and default effort assumptions are illustrative, not employer rules.",
            "No LLM structured-extraction call is used by this deterministic workflow.",
            "No authoritative capability or commercial eligibility assessment is performed.",
            "An authorized reviewer must verify evidence, effort, rates and eligibility.",
        ],
    )
