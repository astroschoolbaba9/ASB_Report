# AI/ai_api.py  (TOP OF FILE)
from __future__ import annotations
from io import BytesIO
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse

from feature_gate import ensure_allowed


from AI.ai import (generate_interpretation,
                   generate_relationship_interpretation,
                   generate_health_interpretation ,
                   get_last_used ,
                   generate_yearly_interpretation,
                   generate_monthly_interpretation,
                   generate_daily_interpretation,
                   generate_health_daily_interpretation,
                   generate_health_monthly_interpretation,
                   generate_health_yearly_interpretation,
                   generate_profession_interpretation,
                )
from AI.swot import generate_swot_from_interpretation
from numerology.features.relationship_report import relationship_triangle_report
from numerology.viz import build_triangle_png_bytes  # if needed anywhere
from numerology.pdf import build_ai_master_report_pdf ,build_ai_report_pdf



router = APIRouter(prefix="/ai", tags=["AI"])


@router.get("/summary")
def ai_summary(
    dob: str = Query(
        ...,
        description="Date of birth in DD-MM-YYYY",
        min_length=8,
        max_length=10,
    )
):
    ensure_allowed("single") 
    """
    Return a single-paragraph LLM interpretation in plain human language.

    Shape:
      { "interpretation": "<paragraph>" }
    """
    try:
        result = generate_interpretation(dob)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {e}")

    # Normalize result (pydantic model / dict / string) to { "interpretation": "..." }
    payload: dict
    interpretation_text = None

    # Try pydantic v2 .model_dump()
    try:
        payload = result.model_dump()  # type: ignore[attr-defined]
    except Exception:
        if isinstance(result, dict):
            payload = result
        elif isinstance(result, str):
            interpretation_text = result
            payload = {}
        else:
            interpretation_text = str(result)
            payload = {}

    if interpretation_text is None:
        if "interpretation" in payload and isinstance(payload["interpretation"], str):
            interpretation_text = payload["interpretation"]
        elif "summary" in payload and isinstance(payload["summary"], str):
            # Back-compat if anything still returns "summary"
            interpretation_text = payload["summary"]

    if not interpretation_text:
        raise HTTPException(
            status_code=500,
            detail="AI returned an unexpected shape; no interpretation text was found.",
        )

    used = get_last_used()
    headers = {
        "X-AI-Provider": used.get("provider") or "",
        "X-AI-Model": used.get("model") or "",
    }
    return JSONResponse({"interpretation": interpretation_text}, headers=headers)


@router.get("/report.pdf")
def ai_report_pdf(
    dob: str = Query(..., description="Date of birth in DD-MM-YYYY", min_length=8, max_length=10)
):
    ensure_allowed("single")
    """
    Return an inline PDF that includes the triangle image and the AI narrative.

    URL (with numerology prefix from the parent router):
      GET /numerology/ai/report.pdf?dob=DD-MM-YYYY
    """
    try:
        pdf_bytes = build_ai_report_pdf(dob)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build PDF: {e}")

    # The PDF builder calls generate_interpretation() internally,
    # so we can expose which provider/model was used.
    used = get_last_used()
    headers = {
        "Content-Disposition": f'inline; filename="mystical-triangle-{dob}.pdf"',
        "X-AI-Provider": used.get("provider") or "",
        "X-AI-Model": used.get("model") or "",
    }

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers=headers,
    )


@router.get("/relationship-triangle.ai.json")
def relationship_ai_summary(
    left: str = Query(..., description="Left person's DOB (DD-MM-YYYY or YYYY-MM-DD)"),
    right: str = Query(..., description="Right person's DOB (DD-MM-YYYY or YYYY-MM-DD)"),
):
    ensure_allowed("relationship")
    try:
        # One-paragraph AI narrative (relationship tone)
        result = generate_relationship_interpretation(left, right)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Relationship AI failed: {e}")

    # Normalize the AI result to { "interpretation": "..." }
    payload: dict
    interpretation_text = None
    try:
        payload = result.model_dump()  # type: ignore[attr-defined]
    except Exception:
        if isinstance(result, dict):
            payload = result
        elif isinstance(result, str):
            interpretation_text = result
            payload = {}
        else:
            interpretation_text = str(result)
            payload = {}

    if interpretation_text is None:
        if "interpretation" in payload and isinstance(payload["interpretation"], str):
            interpretation_text = payload["interpretation"]
        elif "summary" in payload and isinstance(payload["summary"], str):
            interpretation_text = payload["summary"]

    if not interpretation_text:
        raise HTTPException(
            status_code=500,
            detail="AI returned an unexpected shape; no interpretation text was found.",
        )

    used = get_last_used()
    headers = {
        "X-AI-Provider": used.get("provider") or "",
        "X-AI-Model": used.get("model") or "",
    }
    return JSONResponse({ "interpretation": interpretation_text}, headers=headers)




@router.get("/yearly-prediction.ai.json")
def ai_yearly_prediction(
    dob: str = Query(..., description="Date of birth (DD-MM-YYYY or YYYY-MM-DD)"),
    year: int = Query(..., description="Target year for yearly prediction"),
):
    ensure_allowed("yearly") 
    """
    Generate a one-paragraph AI interpretation of the combined yearly pattern (DOB ⊕ Year).
    """
    try:
        result = generate_yearly_interpretation(dob, year)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI yearly generation failed: {e}")

    # normalize pydantic or dict
    try:
        payload = result.model_dump()
        interpretation_text = payload.get("interpretation", "")
    except Exception:
        interpretation_text = getattr(result, "interpretation", str(result))

    used = get_last_used()
    headers = {
        "X-AI-Provider": used.get("provider") or "",
        "X-AI-Model": used.get("model") or "",
    }
    return JSONResponse({"interpretation": interpretation_text}, headers=headers)



# AI/ai_api.py

@router.get("/monthly-prediction.ai.json")
def ai_monthly_prediction(
    dob: str = Query(..., description="DOB DD-MM-YYYY or YYYY-MM-DD"),
    year: int = Query(..., description="Target year"),
    month: int = Query(..., ge=1, le=12, description="Target month (1-12)")
):
    result = generate_monthly_interpretation(dob, year, month)
    try:
        payload = result.model_dump()
        interpretation_text = payload.get("interpretation", "")
    except Exception:
        interpretation_text = getattr(result, "interpretation", str(result))
    used = get_last_used()
    headers = {"X-AI-Provider": used.get("provider") or "", "X-AI-Model": used.get("model") or ""}
    return JSONResponse({"interpretation": interpretation_text}, headers=headers)


@router.get("/daily-interpretation.ai.json")
def ai_daily_interpretation(
    dob: str = Query(..., description="DOB (DD-MM-YYYY or YYYY-MM-DD)"),
    day: str | None = Query(None, description="Optional specific date DD-MM-YYYY or YYYY-MM-DD"),
):
    try:
        result = generate_daily_interpretation(dob, day=day)  # ⬅ pass through
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI daily generation failed: {e}")
    ...

    # Normalize to { "interpretation": "..." }
    try:
        payload = result.model_dump()  # type: ignore[attr-defined]
        interpretation_text = payload.get("interpretation", "")
    except Exception:
        interpretation_text = getattr(result, "interpretation", str(result))

    used = get_last_used()
    headers = {
        "X-AI-Provider": used.get("provider") or "",
        "X-AI-Model": used.get("model") or "",
    }

    return JSONResponse({"interpretation": interpretation_text}, headers=headers)



@router.get("/health-summary")
def ai_health_summary(
    dob: str = Query(..., description="Date of birth in DD-MM-YYYY", min_length=8, max_length=10),
    gender: str | None = Query(None, description="Optional: male/female for a specific heuristic")
):
    """
    Return a single-paragraph *health-focused* LLM interpretation in plain language.
    """
    try:
        result = generate_health_interpretation(dob, gender=gender)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {e}")

    # normalize to { interpretation: "..." } just like your other endpoints
    payload: dict
    interpretation_text = None
    try:
        payload = result.model_dump()  # type: ignore[attr-defined]
    except Exception:
        if isinstance(result, dict):
            payload = result
        elif isinstance(result, str):
            interpretation_text = result
            payload = {}
        else:
            interpretation_text = str(result)
            payload = {}

    if interpretation_text is None:
        if "interpretation" in payload and isinstance(payload["interpretation"], str):
            interpretation_text = payload["interpretation"]
        elif "summary" in payload and isinstance(payload["summary"], str):
            interpretation_text = payload["summary"]

    if not interpretation_text:
        raise HTTPException(status_code=500, detail="AI returned an unexpected shape; no interpretation text was found.")

    used = get_last_used()
    headers = {"X-AI-Provider": used.get("provider") or "", "X-AI-Model": used.get("model") or ""}
    return JSONResponse({"interpretation": interpretation_text}, headers=headers)


@router.get("/health/daily.ai.json")
def ai_health_daily(
    dob: str = Query(..., description="DOB (DD-MM-YYYY or YYYY-MM-DD)"),
    day: str | None = Query(None, description="Optional date DD-MM-YYYY or YYYY-MM-DD; omit for today"),
    gender: str | None = Query(None, description="Optional: male/female"),
):
    """
    One-paragraph *health* interpretation for the combined DAILY triangle (DOB ⊕ Day).
    """
    try:
        result = generate_health_daily_interpretation(dob, day=day, gender=gender)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI daily health failed: {e}")

    try:
        payload = result.model_dump()  # type: ignore[attr-defined]
        interpretation_text = payload.get("interpretation", "")
    except Exception:
        interpretation_text = getattr(result, "interpretation", str(result))

    used = get_last_used()
    headers = {"X-AI-Provider": used.get("provider") or "", "X-AI-Model": used.get("model") or ""}
    return JSONResponse({"interpretation": interpretation_text}, headers=headers)


@router.get("/health/monthly.ai.json")
def ai_health_monthly(
    dob: str = Query(..., description="DOB (DD-MM-YYYY or YYYY-MM-DD)"),
    year: int = Query(..., description="Target year, e.g., 2025"),
    gender: str | None = Query(None, description="Optional: male/female"),
):
    """
    One-paragraph *health* interpretation for the MONTHLY driver (DOB ⊕ Month–Year driver).
    """
    try:
        result = generate_health_monthly_interpretation(dob, year, gender=gender)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI monthly health failed: {e}")

    try:
        payload = result.model_dump()  # type: ignore[attr-defined]
        interpretation_text = payload.get("interpretation", "")
    except Exception:
        interpretation_text = getattr(result, "interpretation", str(result))

    used = get_last_used()
    headers = {"X-AI-Provider": used.get("provider") or "", "X-AI-Model": used.get("model") or ""}
    return JSONResponse({"interpretation": interpretation_text}, headers=headers)


@router.get("/health/yearly.ai.json")
def ai_health_yearly(
    dob: str = Query(..., description="DOB (DD-MM-YYYY or YYYY-MM-DD)"),
    year: int = Query(..., description="Target year, e.g., 2025"),
    gender: str | None = Query(None, description="Optional: male/female"),
):
    """
    One-paragraph *health* interpretation for the YEARLY triangle (DOB ⊕ Year).
    """
    try:
        result = generate_health_yearly_interpretation(dob, year, gender=gender)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI yearly health failed: {e}")

    try:
        payload = result.model_dump()  # type: ignore[attr-defined]
        interpretation_text = payload.get("interpretation", "")
    except Exception:
        interpretation_text = getattr(result, "interpretation", str(result))

    used = get_last_used()
    headers = {"X-AI-Provider": used.get("provider") or "", "X-AI-Model": used.get("model") or ""}
    return JSONResponse({"interpretation": interpretation_text}, headers=headers)



@router.get("/profession.ai.json")
def ai_profession_summary(
    dob: str = Query(
        ...,
        description="Date of birth (DD-MM-YYYY or YYYY-MM-DD)",
        min_length=8,
        max_length=10,
    )
):
    """
    Return a single-paragraph *profession/career-style* interpretation
    based on Mulank + Bhagyank mapping only.

    Shape:
      { "interpretation": "<paragraph>" }
    """
    ensure_allowed("profession")  # 👈 feature gate

    try:
        result = generate_profession_interpretation(dob)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI profession generation failed: {e}")

    # Normalize to { "interpretation": "..." }
    payload: dict
    interpretation_text = None
    try:
        payload = result.model_dump()  # type: ignore[attr-defined]
    except Exception:
        if isinstance(result, dict):
            payload = result
        elif isinstance(result, str):
            interpretation_text = result
            payload = {}
        else:
            interpretation_text = str(result)
            payload = {}

    if interpretation_text is None:
        if "interpretation" in payload and isinstance(payload["interpretation"], str):
            interpretation_text = payload["interpretation"]
        elif "summary" in payload and isinstance(payload["summary"], str):
            interpretation_text = payload["summary"]

    if not interpretation_text:
        raise HTTPException(
            status_code=500,
            detail="AI returned an unexpected shape; no interpretation text was found.",
        )

    used = get_last_used()
    headers = {
        "X-AI-Provider": used.get("provider") or "",
        "X-AI-Model": used.get("model") or "",
    }
    return JSONResponse({"interpretation": interpretation_text}, headers=headers)



@router.get("/master-report.pdf", summary="Generate a combined AI PDF report")
def ai_master_report_pdf(
    dob: str = Query(..., description="Date of birth (DD-MM-YYYY or YYYY-MM-DD)"),
    name: str | None = Query(
        None, description="Optional name to show on the PDF front page"
    ),
    mobile: str | None = Query(
        None, description="Optional mobile number to show on the PDF front page"
    ),
    report_date: str | None = Query(
        None, description="Optional report date (DD-MM-YYYY) to show on the PDF front page"
    ),
    partner: str | None = Query(
        None, description="Optional partner DOB for relationship section"
    ),
    year: int | None = Query(
        None, description="Target year (defaults to current year)"
    ),
    day: str | None = Query(
        None, description="Specific day (defaults to today; DD-MM-YYYY or YYYY-MM-DD)"
    ),
    month: int | None = Query(
        None,
        ge=1,
        le=12,
        description="Target month (1–12, defaults to January in the report)",
    ),
    gender: str | None = Query(
        None, description="Optional: male/female for health analysis"
    ),
    include_images: bool = Query(
        True, description="Include triangle diagrams in the PDF"
    ),
):
    """
    Return a combined AI report as a single PDF:
      • Single-person + Daily + Monthly + Yearly + Health (overall/daily/monthly/yearly)
      • Relationship section if partner DOB is provided.
      • Monthly section can be focused on a specific month (1–12) if provided.
    """
    # 🔐 Feature gate: deny if 'ai' not enabled
    ensure_allowed("ai")

    # First try: full master report
    try:
        pdf_bytes = build_ai_master_report_pdf(
            dob=dob,
            name=name,
            mobile=mobile,
            report_date=report_date,
            partner_dob=partner,
            year=year,
            day=day,
            month=month,
            gender=gender,
            include_images=include_images,
        )
    except Exception as e:
        # Log full stacktrace for debugging in console
        logger.exception("build_ai_master_report_pdf failed for dob=%s", dob)

        # Optional fallback: simple 1-page AI report so the endpoint still returns *something*
        try:
            fallback_bytes = build_ai_report_pdf(dob)
            pdf_bytes = fallback_bytes
            # Expose that we had to fall back, so you can see it from headers
            used = get_last_used() or {}
            headers = {
                "Content-Disposition": f'inline; filename="master-report-fallback-{dob}.pdf"',
                "X-AI-Provider": used.get("provider") or "",
                "X-AI-Model": used.get("model") or "",
                "X-Master-Report-Fallback": f"{e}",
            }
            return StreamingResponse(
                BytesIO(pdf_bytes),
                media_type="application/pdf",
                headers=headers,
            )
        except Exception as e2:
            # If even fallback fails, bubble up with full context
            raise HTTPException(
                status_code=500,
                detail=f"Failed to build master PDF: {e} (fallback failed: {e2})",
            )

    # Normal success path
    used = get_last_used() or {}
    headers = {
        "Content-Disposition": f'inline; filename="master-report-{dob}.pdf"',
        "X-AI-Provider": used.get("provider") or "",
        "X-AI-Model": used.get("model") or "",
    }

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers=headers,
    )


@router.get("/swot.ai.json")
def swot_analysis(
    dob: str = Query(..., description="Date of birth (DD-MM-YYYY or YYYY-MM-DD)")
):
    """
    Build a SWOT analysis from the SAME interpretation used in /ai/summary.
    Returns:
      {
        "interpretation": "<same text as /ai/summary>",
        "swot": {
          "Strengths": [...],
          "Weaknesses": [...],
          "Opportunities": [...],
          "Threats": [...]
        }
      }
    """
    # 🔐 Use the same feature gate as Personality Traits
    ensure_allowed("single")

    try:
        # 1) Call the same generator used by /ai/summary
        raw = generate_interpretation(dob=dob)

        # 2) Normalize to plain interpretation text (same style as /summary)
        try:
            payload = raw.model_dump()  # pydantic v2
            interp = payload.get("interpretation", "") or payload.get("summary", "")
        except Exception:
            interp = getattr(raw, "interpretation", "") or getattr(raw, "summary", "")

        if not isinstance(interp, str) or not interp.strip():
            raise HTTPException(
                status_code=500,
                detail="SWOT: no interpretation text returned from generate_interpretation().",
            )

        # 3) Run SWOT generator (LLM + heuristic fallback as in AI/swot.py)
        swot = generate_swot_from_interpretation(interp)

    except HTTPException:
        # Re-raise clean FastAPI HTTP errors
        raise
    except Exception as e:
        # General safety net
        raise HTTPException(status_code=500, detail=f"SWOT generation failed: {e}")

    # 4) Mirror provider/model headers like other AI endpoints
    used = get_last_used() or {}
    headers = {
        "X-AI-Provider": used.get("provider") or "",
        "X-AI-Model": used.get("model") or "",
    }

    return JSONResponse({"interpretation": interp, "swot": swot}, headers=headers)
