"""Reconstructed PDF report generator for fictional / approved portfolio inputs."""
from io import BytesIO
from xml.sax.saxutils import escape


def pdf_report(payload: dict) -> bytes:
    """Generate a review-only report in memory; do not write private files to disk."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    except ImportError as exc:
        raise RuntimeError("Install PDF support: pip install -e '.[reports]'") from exc

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title="RFP AI Review Report")
    styles = getSampleStyleSheet()
    story = [
        Paragraph("RFP AI — Review Report (Portfolio Demo)", styles["Title"]),
        Spacer(1, 14),
        Paragraph("Synthetic/approved inputs only. Not an approved bid.", styles["Italic"]),
        Spacer(1, 14),
    ]
    sections = (
        ("Tender", payload.get("tender_id", "N/A")),
        ("Requirements", payload.get("requirements", [])),
        ("Technical observations", payload.get("technical", {})),
        ("Resource estimation", payload.get("resources", [])),
        ("Financial estimation", payload.get("financial", {})),
        ("Risk analysis", payload.get("risks", [])),
        ("Go / No-Go review", payload.get("go_no_go", {})),
        ("Limitations", payload.get("limitations", [])),
    )
    for heading, value in sections:
        story.append(Paragraph(escape(heading), styles["Heading2"]))
        if isinstance(value, list):
            items = value or ["None documented"]
            for item in items:
                story.append(Paragraph(escape(str(item)), styles["BodyText"]))
        else:
            story.append(Paragraph(escape(str(value)), styles["BodyText"]))
        story.append(Spacer(1, 9))
    doc.build(story)
    return buffer.getvalue()
