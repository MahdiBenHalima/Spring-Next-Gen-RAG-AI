"""Small, explicitly heuristic demonstration; not an LLM or a bid decision engine."""
from dataclasses import asdict, dataclass
from .models import Hit


@dataclass(frozen=True)
class Assessment:
    tender_id: str
    detected_requirements: list[str]
    evidence_ids: list[str]
    estimated_person_days: int | None
    estimated_cost: float | None
    go_no_go: str
    limitations: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


KEYWORDS = {
    "API integration": ("api", "integration", "rest"),
    "Security assessment": ("security", "security audit", "pentest", "sécurité"),
    "Data engineering": ("data pipeline", "etl", "data engineering"),
    "Documentation": ("documentation", "deliverable", "livrable"),
}


def assess(
    tender_id: str, evidence: list[Hit], *,
    person_days: int | None = None, daily_rate: float | None = None,
) -> Assessment:
    text = " ".join(item.chunk.text.casefold() for item in evidence)
    detected = [
        name for name, words in KEYWORDS.items()
        if any(word.casefold() in text for word in words)
    ]
    cost = None
    if person_days is not None or daily_rate is not None:
        if person_days is None or daily_rate is None:
            raise ValueError("person_days and daily_rate must be supplied together")
        if person_days < 0 or daily_rate < 0:
            raise ValueError("Costs and days must be nonnegative")
        cost = round(person_days * daily_rate, 2)
    return Assessment(
        tender_id=tender_id,
        detected_requirements=detected,
        evidence_ids=[hit.chunk.chunk_id for hit in evidence],
        estimated_person_days=person_days,
        estimated_cost=cost,
        go_no_go="HUMAN_REVIEW_REQUIRED",
        limitations=[
            "This is a keyword-based portfolio demonstration, not the private LLM workflow.",
            "No compliance, profitability, or company capability verification is performed.",
            "Do not use this result as an automatic submission decision.",
        ],
    )
