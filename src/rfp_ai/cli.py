"""End-to-end synthetic portfolio demonstration and optional PDF export."""
import argparse
import json
from pathlib import Path
from .demo import SYNTHETIC_TENDER
from .workflow import analyze_workflow


def main() -> None:
    parser = argparse.ArgumentParser(description="Public RFP AI workflow demo")
    parser.add_argument("--pdf", type=Path, help="Export a human-review PDF (optional reports extra)")
    args = parser.parse_args()
    result = analyze_workflow(
        SYNTHETIC_TENDER + " The deadline will be confirmed by the customer.",
        "SYNTHETIC-001",
        available_skills=["Backend engineer", "Security engineer", "Technical writer"],
        daily_rates={
            "Backend engineer": 400.0,
            "Security engineer": 500.0,
            "Technical writer": 250.0,
        },
        budget_cap=12000.0,
    )
    payload = result.as_dict()
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if args.pdf:
        from .reports import pdf_report
        args.pdf.parent.mkdir(parents=True, exist_ok=True)
        args.pdf.write_bytes(pdf_report(payload))
        print(f"Wrote: {args.pdf}")


if __name__ == "__main__":
    main()
