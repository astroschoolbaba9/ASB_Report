# numerology/pdf.py
from __future__ import annotations
from io import BytesIO
from typing import Any, Dict
from datetime import date
import os  # ← added

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, PageBreak

# Narrative generators — provider chosen via settings; tests will monkeypatch to "mock"
from AI.ai import (
    generate_interpretation,
    generate_relationship_interpretation,
    generate_yearly_interpretation,
    generate_monthly_interpretation,
    generate_daily_interpretation,
    generate_health_interpretation,
    generate_health_daily_interpretation,
    generate_health_monthly_interpretation,
    generate_health_yearly_interpretation,
    get_last_used,
)
from AI.swot import generate_swot_from_interpretation

# Triangle image + structured single-person report
from numerology.viz import (
    build_triangle_png_bytes,
    plot_three_triangles,
    plot_yearly_triptych,
    plot_monthly_triptych,   # ← use viz monthly (no combined drawing)
    plot_daily_triptych,     # ← use viz daily   (no combined drawing)
)
from numerology.features.single_person_report import mystical_triangle_report

# NEW: Mulank/Bhagyank + pair rating (same as UI API)
from numerology.mulank_bhagyank import mulank_bhagyank_profile

# NEW: Profession / career mapping (same as /numerology/profession.report.json)
from numerology.features.profession_report import profession_report

# Optional plotting helpers (used for triptychs)
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "asb_logo.jpg")   # updated to your logo file

# PDF decorative images (drop your files into /assets)
COVER_IMAGE_PATH = os.path.join(ASSETS_DIR, "cover_page.png")
REMEDIES_IMAGE_PATH = os.path.join(ASSETS_DIR, "remedies_image.png")
INLINE_HALF_IMAGE_PATH = os.path.join(ASSETS_DIR, "inline_half.png")


def _brand_page(canvas: Canvas, doc):
    """
    Draws ASB logo, header/footer and light logo watermark on every page.
    """
    w, h = A4

    # Header with logo + text
    canvas.saveState()
    if LOGO_PATH and os.path.exists(LOGO_PATH):
        try:
            canvas.drawImage(
                LOGO_PATH,
                36,
                h - 60,
                width=40,
                height=40,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception:
            pass  # fail silently if logo missing/invalid

    canvas.setFont("Helvetica-Bold", 11)
    canvas.setFillColor(colors.HexColor("#5E35B1"))  # violet tone from your brand
    canvas.drawString(90, h - 28, "")
    canvas.restoreState()

    # Footer page number
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawRightString(w - 36, 20, f"Page {doc.page}")
    canvas.restoreState()

    # Light diagonal watermark using logo image
    if LOGO_PATH and os.path.exists(LOGO_PATH):
        canvas.saveState()
        try:
            # Some backends expose setFillAlpha; if not, just rely on light color
            if hasattr(canvas, "setFillAlpha"):
                canvas.setFillAlpha(0.06)

            # Scale watermark
            wm_width = w * 0.55
            wm_height = h * 0.55

            canvas.translate(w / 2.0, h / 2.0)
            canvas.drawImage(
                LOGO_PATH,
                -wm_width / 2,
                -wm_height / 2,
                width=wm_width,
                height=wm_height,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception:
            pass
        finally:
            canvas.restoreState()


def _draw_full_page_image(canvas: Canvas, img_path: str):
    """Draw an image to cover the full A4 page (aspect preserved, centered).

    If the file is missing/invalid, it fails silently.
    """
    if not img_path or not os.path.exists(img_path):
        return
    w, h = A4
    try:
        reader = ImageReader(img_path)
        iw, ih = reader.getSize()
        if not iw or not ih:
            return
        scale = min(w / float(iw), h / float(ih))
        dw, dh = iw * scale, ih * scale
        x = (w - dw) / 2.0
        y = (h - dh) / 2.0
        canvas.drawImage(reader, x, y, width=dw, height=dh, preserveAspectRatio=True, mask='auto')
    except Exception:
        return


def _cover_page(canvas: Canvas, doc):
    """First page: full-bleed cover image (no header/footer/watermark)."""
    canvas.saveState()
    _draw_full_page_image(canvas, COVER_IMAGE_PATH)
    canvas.restoreState()


# ─────────────────────────── Helpers ───────────────────────────

def _normalize_interpretation(result: Any) -> str:
    """
    Accepts whatever generate_* function returns and extracts a single
    plain-language paragraph. Supports:
      - string (already the paragraph)
      - dict with "interpretation" or legacy "summary"
      - Pydantic model (v2 .model_dump()), or attributes .interpretation/.summary
    """
    if isinstance(result, str):
        return result.strip()

    if isinstance(result, dict):
        text = result.get("interpretation") or result.get("summary")
        if isinstance(text, str):
            return text.strip()

    try:
        data: Dict[str, Any] = result.model_dump()  # type: ignore[attr-defined]
        text = data.get("interpretation") or data.get("summary")
        if isinstance(text, str):
            return text.strip()
    except Exception:
        pass

    for attr in ("interpretation", "summary"):
        if hasattr(result, attr):
            text = getattr(result, attr)
            if isinstance(text, str):
                return text.strip()

    return str(result).strip()


def _fig_to_png_bytes(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=170, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()


def _scaled_image_from_bytes(png_bytes: bytes, max_height_ratio: float = 0.6) -> Image:
    """
    Return a ReportLab Image flowable scaled to the SAME bounding box
    used for the base triangle image above Personality Traits.
    """
    img = Image(BytesIO(png_bytes))
    max_w = A4[0] - (36 + 36)          # same left/right margins as SimpleDocTemplate
    max_h = max_w * 0.65               # same aspect-bound as main triangle image
    img._restrictSize(max_w, max_h)
    return img

def _scaled_image_from_path(img_path: str, *, max_height_ratio: float = 0.5) -> Image | None:
    """Scaled Image flowable from a local path.

    max_height_ratio is relative to the *full A4 height* inside margins.
    """
    if not img_path or not os.path.exists(img_path):
        return None
    try:
        img = Image(img_path)
        max_w = A4[0] - (36 + 36)
        max_h = (A4[1] - (72 + 48)) * max_height_ratio
        img._restrictSize(max_w, max_h)
        return img
    except Exception:
        return None


def _format_for_pdf(text: str) -> str:
    """
    Roughly mirror the UI bullet formatting:

    • Treat lines starting with '•' as bullet lines
    • Preserve line breaks using <br/>
    """
    if not isinstance(text, str):
        return ""
    raw_lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in raw_lines if ln]
    if not lines:
        return ""
    has_bullet = any(ln.startswith("•") for ln in lines)
    out: list[str] = []
    for ln in lines:
        if has_bullet and ln.startswith("•"):
            content = ln.lstrip("•").strip()
            out.append(f"• {content}")
        else:
            if out:
                out.append("<br/>" + ln)
            else:
                out.append(ln)
    return "<br/>".join(out)


# NEW: AI SWOT helper (same source as UI /ai/swot.ai.json)
def _get_swot_for_pdf(dob: str) -> Dict[str, Any] | None:
    """
    Build SWOT using the SAME logic as /ai/swot.ai.json:
      1) Use generate_interpretation(dob) to get plain text.
      2) Pass that text into generate_swot_from_interpretation().
    Returns dict like:
      { "Strengths": [...], "Weaknesses": [...], ... }
    or None if anything fails.
    """
    try:
        # 1) get the same interpretation as the Personality section
        raw = generate_interpretation(dob)
        text = _normalize_interpretation(raw)
        if not isinstance(text, str) or not text.strip():
            return None

        # 2) run SWOT classifier (LLM or heuristic, depending on settings)
        swot = generate_swot_from_interpretation(text)
        if isinstance(swot, dict):
            return swot
        return None
    except Exception:
        return None


# NEW: AI Profession helper (to mirror /ai/profession.ai.json)
def _get_profession_ai_text(dob: str) -> str | None:
    """
    Try to pull AI profession interpretation from AI.ai.
    Looks for one of:
      • generate_profession_interpretation
      • generate_profession
      • generate_profession_ai
    Returns normalized string or None.
    """
    try:
        import AI.ai as ai_module
        for cand in (
            "generate_profession_interpretation",
            "generate_profession",
            "generate_profession_ai",
        ):
            fn = getattr(ai_module, cand, None)
            if callable(fn):
                raw = fn(dob)
                return _normalize_interpretation(raw)
    except Exception:
        return None
    return None


# ───────────────────── Single-person Report PDF (kept for tests) ─────────────────────

def build_ai_report_pdf(dob: str) -> bytes:
    """
    Build a concise PDF with the Mystical Triangle image, a quick-glance row,
    and a single-paragraph interpretation in simple, human language.

    • Works with the configured generator; tests will monkeypatch to "mock".
    """
    report = mystical_triangle_report(dob)
    raw_interp = generate_interpretation(dob)
    interpretation = _normalize_interpretation(raw_interp)

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=72,   # more space for logo header
        bottomMargin=48,
    )

    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        name="Title",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#5E35B1"),  # brand violet
        spaceAfter=10,
    )
    h2 = ParagraphStyle(
        name="H2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#333399"),
        spaceBefore=10,
        spaceAfter=6,
    )
    small = ParagraphStyle(
        name="Small",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#555555"),
        spaceAfter=4,
    )
    body = ParagraphStyle(
        name="Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#222222"),
        spaceAfter=8,
    )
    # NEW: subheading — bigger than body, smaller than H2
    subheading = ParagraphStyle(
        name="Subheading",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#444444"),
        spaceBefore=4,
        spaceAfter=4,
    )

    story = []
    story.append(Paragraph("ASB", title))
    # DOB as subheading (bigger than paragraph)
    story.append(Paragraph(f"DOB: <b>{dob}</b>", subheading))

    # Triangle image
    img_bytes = build_triangle_png_bytes(dob)
    img = Image(BytesIO(img_bytes))
    max_w = A4[0] - (36 + 36)
    img._restrictSize(max_w, max_w * 0.65)
    story += [Spacer(1, 10), img, Spacer(1, 10)]

    # Interpretation
    story.append(Spacer(1, 4))
    story.append(Paragraph("Interpretation", h2))
    story.append(Paragraph(_format_for_pdf(interpretation), body))

    story += [
        Spacer(1, 14),
        Paragraph(
            "Note: Interpretations are grounded in deterministic triangle values and your meanings library.",
            small,
        ),
    ]

    # ───────────── Closing: Remedies (text + image at end) ─────────────
    story.append(PageBreak())
    # Push content towards the bottom so the Remedies block appears near the end of the page
    story.append(Spacer(1, 250))
    story.append(Paragraph("Remedies : https://www.instagram.com/astroschoolbaba/", h2))
    story.append(Spacer(1, 10))
    rem_img = _scaled_image_from_path(REMEDIES_IMAGE_PATH, max_height_ratio=0.45)
    if rem_img is not None:
        story.append(rem_img)

    doc.build(story, onFirstPage=_cover_page, onLaterPages=_brand_page)
    return buf.getvalue()


# ───────────────────── Combined Master Report PDF (all features) ─────────────────────

def _safe_call(fn, *args, **kwargs) -> str | None:
    """Call a generator, normalize to text; return None if anything fails."""
    try:
        raw = fn(*args, **kwargs)
        return _normalize_interpretation(raw)
    except Exception:
        return None


def _add_section(story, title_style, body_style, heading: str, text: str | None):
    if not text:
        return
    story.append(Paragraph(heading, title_style))
    story.append(Paragraph(_format_for_pdf(text), body_style))
    story.append(Spacer(1, 8))


def build_ai_master_report_pdf(
    dob: str,
    *,
    name: str | None = None,
    mobile: str | None = None,
    report_date: str | None = None,
    partner_dob: str | None = None,     # optional — include relationship section
    year: int | None = None,            # e.g., 2025 (defaults to current if None)
    day: str | None = None,             # DD-MM-YYYY or YYYY-MM-YYYY (defaults to today)
    month: int | None = None,           # OPTIONAL: target month for monthly section
    gender: str | None = None,          # optional for health heuristics
    include_images: bool = True,        # include diagrams
) -> bytes:
    """
    Build a COMBINED PDF aggregating interpretations across all features:
      • Single (overall) • Daily • Monthly • Yearly
      • Health (overall, daily, monthly, yearly)
      • Relationship (optional)

    Notes:
      • Uses your configured generator/model (see settings).
      • Gracefully skips sections if a generator call or image build fails.
    """

    # NEW: Mulank/Bhagyank profile from the same source as UI
    mulank = bhagyank = None
    pair_rating = pair_meaning = None
    try:
        mb_profile = mulank_bhagyank_profile(dob)
        if isinstance(mb_profile, dict):
            mulank = mb_profile.get("mulank")
            bhagyank = mb_profile.get("bhagyank")
            pair = mb_profile.get("pair") or {}
            pair_rating = pair.get("rating_label")
            pair_meaning = pair.get("rating_meaning")
    except Exception:
        pass

    # NEW: Profession report (same logic as /numerology/profession.report.json)
    profession_data: Dict[str, Any] | None = None
    try:
        profession_data = profession_report(dob)
    except Exception:
        profession_data = None

    # NEW: SWOT from AI (if available)
    swot_dict: Dict[str, Any] | None = _get_swot_for_pdf(dob)

    if year is None:
        year = date.today().year
    if not day or str(day).strip().lower() == "today":
        day_label = date.today().strftime("%d-%m-%Y")
    else:
        day_label = day

    if month is None:
        month = 1  # default to January if not provided

    if report_date is None:
        report_date = date.today().strftime("%d-%m-%Y")

    # Collect texts
    single_text         = _safe_call(generate_interpretation, dob)
    daily_text          = _safe_call(generate_daily_interpretation, dob, day=day)
    monthly_text        = _safe_call(generate_monthly_interpretation, dob, year, month=month)
    yearly_text         = _safe_call(generate_yearly_interpretation, dob, year)
    health_text         = _safe_call(generate_health_interpretation, dob, gender=gender)
    health_daily_text   = _safe_call(generate_health_daily_interpretation, dob, day=day, gender=gender)
    health_monthly_text = _safe_call(generate_health_monthly_interpretation, dob, year, gender=gender)
    health_yearly_text  = _safe_call(generate_health_yearly_interpretation, dob, year, gender=gender)
    relationship_text   = _safe_call(generate_relationship_interpretation, dob, partner_dob) if partner_dob else None

    # Build PDF
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=72,   # room for header + logo
        bottomMargin=48,
    )

    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        name="Title",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#5E35B1"),
        spaceAfter=10,
    )
    h2 = ParagraphStyle(
        name="H2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#333399"),
        spaceBefore=10,
        spaceAfter=6,
    )
    small = ParagraphStyle(
        name="Small",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#555555"),
        spaceAfter=4,
    )
    body = ParagraphStyle(
        name="Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#222222"),
        spaceAfter=8,
    )
    # NEW: slightly larger footer text for closing note
    footer = ParagraphStyle(
        name="Footer",
        parent=small,
        fontSize=11,
        leading=15,
    )
    # NEW: subheading — bigger than body, smaller than H2
    subheading = ParagraphStyle(
        name="Subheading",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#444444"),
        spaceBefore=4,
        spaceAfter=4,
    )

    story = []

    # ───────────── Cover page (full page image) ─────────────
    # A tiny flowable is enough to create the first page; the actual image is drawn by _cover_page().
    story.append(Spacer(1, 1))
    story.append(PageBreak())

    # ───────────── Header: Name → DOB → Numbers → Current Date ─────────────
    story.append(Paragraph("ASB — Report", title))
    
    # -----------------------------------------------------------------------------
    # FRONT PAGE — Company About Section
    # -----------------------------------------------------------------------------
    story.append(Spacer(1, 10))
    story.append(
        Paragraph(
            "<b>ASB — Where Numbers Meet Destiny</b><br/>"
            "This report is crafted through ancient numerological principles and advanced analytical methods. "
            "Each section reflects the harmony of your personal energies — revealing insights about your personality, "
            "health cycles, and the rhythm of your destiny.<br/><br/>"
            "Every number carries a vibration, and every vibration shapes the life path ahead. "
            "May this guide bring clarity, balance, and purpose to your journey.<br/><br/>"
            "<i>For guidance or personal consultation, contact us at: "
            "<b>support@ocultscience.ai</b></i>",
            footer,
        )
    )
    story.append(Spacer(1, 20))
    # ----------------------------------------------------------------------------- 
    
    # -----------------------------------------------------------------------------
    # PAGE 2 — FULL DISCLAIMER PAGE
    # -----------------------------------------------------------------------------
    story.append(PageBreak())   # move to page 2

    story.append(Paragraph("<b>Disclaimer</b>", title))
    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "This report is created solely for self-reflection and personal insight. "
            "All interpretations are based on numerological principles and symbolic patterns, "
            "not on scientific or medical evidence.<br/><br/>"

            "<b>This document is NOT intended to:</b><br/>"
            "- Provide medical diagnosis or treatment<br/>"
            "- Offer financial or investment advice<br/>"
            "- Replace psychological counselling or therapy<br/>"
            "- Serve as legal or professional guidance<br/><br/>"

            "Numerology offers directional understanding, not fixed prediction. "
            "You are solely responsible for decisions taken based on this report.<br/><br/>"

            "<i>For professional concerns, always consult a certified specialist.</i>",
            body,
        )
    )

    story.append(PageBreak())

    story.append(Paragraph(f"{name} — Report ASB", title))

    # Name above DOB (subheading)
    if name:
        story.append(Paragraph(f"Name: <b>{name}</b>", subheading))

    # DOB (subheading)
    story.append(Paragraph(f"DOB: <b>{dob}</b>", subheading))

    # Optional mobile (subheading)
    if mobile:
        story.append(Paragraph(f"Mobile: <b>{mobile}</b>", subheading))

    # Current report date (subheading)
    if report_date:
        story.append(Paragraph(f"Report Date: <b>{report_date}</b>", subheading))

    story.append(Spacer(1, 6))

    # Mulank / Bhagyank block from Mulank-Bhagyank profile (same as UI)
    story.append(Paragraph("Features (Mulank & Bhagyank)", h2))
    if mulank is not None:
        story.append(Paragraph(f"Mulank (Birth Path): <b>{mulank}</b>", subheading))
    if bhagyank is not None:
        story.append(Paragraph(f"Bhagyank (Destiny Path): <b>{bhagyank}</b>", subheading))
    if pair_rating:
        story.append(Paragraph(f"Pair Rating: <b>{pair_rating}</b>", subheading))
    if pair_meaning:
        story.append(Paragraph(f"Pair Meaning: {pair_meaning}", subheading))
    story.append(Spacer(1, 10))

    # ───────────── Decorative image (half-page) ─────────────
    half_img = _scaled_image_from_path(INLINE_HALF_IMAGE_PATH, max_height_ratio=0.5)
    if half_img is not None:
        story += [half_img, Spacer(1, 10)]

    # ───────────── Base triangle image ─────────────
    if include_images:
        try:
            img_bytes = build_triangle_png_bytes(dob)
            img = Image(BytesIO(img_bytes))
            max_w = A4[0] - (36 + 36)
            img._restrictSize(max_w, max_w * 0.65)
            story += [Spacer(1, 10), img, Spacer(1, 10)]
        except Exception:
            pass

    # ───────────── Personality + SWOT ─────────────
    _add_section(story, h2, body, "Personality Traits", single_text)
    story.append(Spacer(1, 6))

    # SWOT: Use already generated single_text to derive SWOT (save one AI call)
    derived_swot = None
    if single_text:
        try:
            derived_swot = generate_swot_from_interpretation(single_text)
        except Exception:
            pass

    if isinstance(derived_swot, dict) and derived_swot:
        story.append(Paragraph("SWOT Analysis", h2))
        for key in ("Strengths", "Weaknesses", "Opportunities", "Threats"):
            items = derived_swot.get(key) or derived_swot.get(key.lower())
            if isinstance(items, list) and items:
                bullets = "\n".join(f"• {it}" for it in items)
                # key label as subheading
                story.append(Paragraph(key, subheading))
                story.append(Paragraph(_format_for_pdf(bullets), body))
                story.append(Spacer(1, 4))
    else:
        story.append(Paragraph("SWOT Snapshot", h2))
        story.append(
            Paragraph(
                _format_for_pdf(
                    "A detailed SWOT (Strengths, Weaknesses, Opportunities, Threats) "
                    "analysis is available in the interactive ASB application. "
                    "Use it to further map your core traits to practical life situations."
                ),
                body,
            )
        )
        story.append(PageBreak())

    # ───────────── Profession / Career Guidance (its own feature section) ─────────────
    if profession_data:
        story.append(Paragraph("Profession / Career Guidance", h2))

        # 🔁 profession_report() returns a nested "profession" dict
        if isinstance(profession_data, dict):
            prof_block = profession_data.get("profession") or profession_data
        else:
            prof_block = {}

        stars = prof_block.get("stars")
        rating_text = prof_block.get("rating_text")
        rating_short = prof_block.get("rating_short")
        rating_detail = prof_block.get("rating_detail")
        remark = prof_block.get("remark")
        professions = prof_block.get("professions") or []

        # Stars + rating (short + detail, same idea as UI)
        if stars or rating_text or rating_short or rating_detail:
            # main label: prefer short + stars
            if rating_short and stars:
                main = f"{rating_short} ({stars})"
            elif rating_short:
                main = rating_short
            elif stars:
                main = stars
            else:
                main = ""

            # description: prefer detail; else fall back to rating_text
            desc = rating_detail or (rating_text if not rating_detail else "")

            if main and desc:
                story.append(
                    Paragraph(
                        f"Suitability Rating: <b>{main}</b> — {desc}",
                        subheading,
                    )
                )
            elif main:
                story.append(
                    Paragraph(
                        f"Suitability Rating: <b>{main}</b>",
                        subheading,
                    )
                )
            elif desc:
                story.append(
                    Paragraph(
                        f"Suitability Rating: {desc}",
                        subheading,
                    )
                )

        if remark:
            story.append(Paragraph(_format_for_pdf(str(remark)), subheading))

        if professions:
            prof_lines = "<br/>" + "<br/>".join(f"• {p}" for p in professions)
            story.append(Paragraph(f"Suggested domains & roles:{prof_lines}", body))

        # ✅ AI Profession interpretation (same spirit as /ai/profession.ai.json)
        ai_prof_text = _get_profession_ai_text(dob)
        if ai_prof_text:
            story.append(Spacer(1, 6))
            story.append(Paragraph("Profession Interpretation", h2))
            story.append(Paragraph(_format_for_pdf(ai_prof_text), body))

        story.append(PageBreak())

    # ───────────── Time Cycles (Daily / Monthly / Yearly) ─────────────
    # Daily → image first, then interpretation
    if daily_text or include_images:
        story.append(Paragraph(f"Time Cycles — Daily (for {day_label})", h2))
        if include_images:
            try:
                d_fig, _d_vals = plot_daily_triptych(dob, day_label)
                d_png = _fig_to_png_bytes(d_fig)
                d_img = _scaled_image_from_bytes(d_png)
                story += [Spacer(1, 6), d_img, Spacer(1, 8)]
            except Exception:
                pass
        if daily_text:
            story.append(Paragraph(_format_for_pdf(daily_text), body))
            story.append(PageBreak())

    # Monthly → image first, then interpretation
    month_name = date(year, month, 1).strftime("%B")
    if monthly_text or include_images:
        story.append(Paragraph(f"Time Cycles — Monthly ({month_name} {year})", h2))
        if include_images:
            try:
                m_fig, _m_vals = plot_monthly_triptych(dob, year, month)
                m_png = _fig_to_png_bytes(m_fig)
                m_img = _scaled_image_from_bytes(m_png)
                story += [Spacer(1, 6), m_img, Spacer(1, 8)]
            except Exception:
                pass
        if monthly_text:
            story.append(Paragraph(_format_for_pdf(monthly_text), body))
            story.append(PageBreak())

    # Yearly → image first, then interpretation
    if yearly_text or include_images:
        story.append(Paragraph(f"Time Cycles — Yearly ({year})", h2))
        if include_images:
            try:
                y_fig, _y_vals = plot_yearly_triptych(dob, year)
                y_png = _fig_to_png_bytes(y_fig)
                y_img = _scaled_image_from_bytes(y_png)
                story += [Spacer(1, 6), y_img, Spacer(1, 8)]
            except Exception:
                pass
        if yearly_text:
            story.append(Paragraph(_format_for_pdf(yearly_text), body))
            story.append(Spacer(1, 6))

    # ───────────── Health block (shares its own pages) ─────────────
    story.append(PageBreak())
    _add_section(story, h2, body, "Health — Overall", health_text)
    _add_section(story, h2, body, f"Health — Daily (for {day_label})", health_daily_text)
    _add_section(story, h2, body, f"Health — Monthly (Year {year})", health_monthly_text)
    _add_section(story, h2, body, f"Health — Yearly (Year {year})", health_yearly_text)

    # Relationship (optional) on its own page block
    if partner_dob:
        story.append(PageBreak())
        _add_section(
            story,
            h2,
            body,
            f"Relationship with your Partner({partner_dob})",
            relationship_text,
        )
        if include_images:
            try:
                rel_fig, _rels = plot_three_triangles(
                    left_dob=dob,
                    right_dob_or_today=partner_dob,
                    left_title="Left",
                    right_title="Right",
                    combined_title="Combined (Relationship)",
                )
                rel_png = _fig_to_png_bytes(rel_fig)
                img = _scaled_image_from_bytes(rel_png)
                story += [Spacer(1, 6), img, Spacer(1, 8)]
            except Exception:
                pass


    # ───────────── Closing: Remedies (text + image at end) ─────────────
    story.append(PageBreak())
    # Push content towards the bottom so the Remedies block appears near the end of the page
    story.append(Spacer(1, 250))
    story.append(Paragraph("Remedies : https://www.instagram.com/astroschoolbaba/", h2))
    story.append(Spacer(1, 10))
    rem_img = _scaled_image_from_path(REMEDIES_IMAGE_PATH, max_height_ratio=0.45)
    if rem_img is not None:
        story.append(rem_img)

    doc.build(story, onFirstPage=_cover_page, onLaterPages=_brand_page)
    return buf.getvalue()
