# numerology/num_api.py
from fastapi import APIRouter, Query, Response
import io
from datetime import date
from feature_gate import ensure_allowed
from numerology.features.profile_bulletins import build_profile_bulletins


# --- core math (pure) ---
from numerology import (  # top-level exports from package
    mystical_triangle_values_image,
    year_only_triangle, 
    yearly_combined_triangle,
    mystical_triangle_today,
    combine_two_triangles,
    F_TRAIT,
)

# --- reads helper (concat like EF, AB, etc.) ---
from numerology.reads import build_reads

# --- viz (PNG/PDF + triptych) ---
from numerology.viz import (
    plot_mystical_triangle_excel_exact,
    build_triangle_png_bytes,
    build_triangle_pdf_bytes,
    plot_three_triangles,
    plot_yearly_triptych,
    plot_monthly_triptych,
    plot_daily_triptych,
)
from numerology.mulank_bhagyank import mulank_bhagyank_profile

# --- reports (moved to features) ---
from numerology.features.single_person_report import mystical_triangle_report
from numerology.features.relationship_report import relationship_triangle_report
from numerology.features.yearly_report import yearly_triangle_report
from numerology.features.monthly_report import monthly_prediction_report
from numerology.features.daily_report import daily_triangle_report
from numerology.features.health_report import (
    health_triangle_report,      # existing single (DOB-only)
    health_daily_report,         # NEW: DOB ⊕ Day
    health_monthly_report,       # NEW: DOB ⊕ Month-Year driver
    health_yearly_report,        # NEW: DOB ⊕ Year-only
)
from numerology.features.profession_report import profession_report



router = APIRouter(prefix="/numerology", tags=["numerology"])

@router.get("/mystical-triangle.json")
async def triangle_json(dob: str = Query(..., description="Date of birth DD-MM-YYYY or YYYY-MM-DD")):
    ensure_allowed("single") 
    return mystical_triangle_values_image(dob)

@router.get("/mystical-triangle.report.json")
async def triangle_report_json(dob: str = Query(..., description="Date of birth DD-MM-YYYY or YYYY-MM-DD")):
    ensure_allowed("single") 
    return mystical_triangle_report(dob)

@router.get("/mystical-triangle.png")
async def triangle_png(dob: str = Query(..., description="Date of birth DD-MM-YYYY or YYYY-MM-DD")):
    ensure_allowed("single")
    img_bytes = build_triangle_png_bytes(dob)
    return Response(content=img_bytes, media_type="image/png")

@router.get("/mystical-triangle.pdf")
async def triangle_pdf(dob: str = Query(..., description="Date of birth DD-MM-YYYY or YYYY-MM-DD")):
    ensure_allowed("single")
    pdf_bytes = build_triangle_pdf_bytes(dob)
    return Response(content=pdf_bytes, media_type="application/pdf")

@router.get("/year-only-triangle.json")
async def year_only_triangle_json(year: int):
    ensure_allowed("yearly")
    return year_only_triangle(year)

@router.get("/yearly-combined-triangle.json")
async def yearly_combined_triangle_json(dob: str, year: int):
    ensure_allowed("yearly") 
    return yearly_combined_triangle(dob, year)

# ────────────────────────────────────────────────────────────────
# Triptych (PNG + JSON)
# ────────────────────────────────────────────────────────────────
@router.get("/mystical-triangle-triptych.png")
async def triangle_triptych_png(
    left: str = Query(..., description="Left person's DOB (DD-MM-YYYY or YYYY-MM-DD)"),
    right: str = Query("today", description="Right person's DOB or 'today'"),
    left_title: str = Query("Left", description="Title for the left triangle"),
    right_title: str = Query("Right", description="Title for the right triangle"),
    combined_title: str = Query("Combined", description="Title for the combined triangle"),
):
    ensure_allowed("single")
    fig, vals = plot_three_triangles(left, right, left_title, right_title, combined_title)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=170, bbox_inches="tight")
    return Response(content=buf.getvalue(), media_type="image/png")

@router.get("/mystical-triangle-triptych.json")
async def triangle_triptych_json(
    left: str = Query(..., description="Left person's DOB (DD-MM-YYYY or YYYY-MM-DD)"),
    right: str = Query("today", description="Right person's DOB or 'today'"),
):
    ensure_allowed("single") 
    # Left
    vals_left = mystical_triangle_values_image(left)
    left_reads = build_reads(vals_left)
    left_F = vals_left["layer1"]["F"]
    left_notes = {"priority": "G is most important core number; then E and F.", "F_trait": F_TRAIT.get(left_F, "")}

    # Right
    if right.lower() == "today":
        vals_right = mystical_triangle_today()
        right_label = f"Today ({date.today().strftime('%d-%m-%Y')})"
    else:
        vals_right = mystical_triangle_values_image(right)
        right_label = right
    right_reads = build_reads(vals_right)
    right_F = vals_right["layer1"]["F"]
    right_notes = {"priority": "G is most important core number; then E and F.", "F_trait": F_TRAIT.get(right_F, "")}

    # Combined
    vals_combined = combine_two_triangles(vals_left, vals_right)
    combined_reads = build_reads(vals_combined)
    combined_F = vals_combined["layer1"]["F"]
    combined_notes = {"priority": "G is most important core number; then E and F.", "F_trait": F_TRAIT.get(combined_F, "")}

    return {
        "left": {"dob": left, "values": vals_left, "reads": left_reads, "core_notes": left_notes},
        "right": {"dob": right_label, "values": vals_right, "reads": right_reads, "core_notes": right_notes},
        "combined": {"dob": f"{left} + {right_label}", "values": vals_combined, "reads": combined_reads, "core_notes": combined_notes},
    }

@router.get("/mulank-bhagyank.profile.json")
async def mulank_bhagyank_profile_json(
    dob: str = Query(..., description="DOB in DD-MM-YYYY or YYYY-MM-DD"),
):
    """
    Return Mulank, Bhagyank and their star rating profile.

    Shape:
    {
      "dob": "29-10-2001",
      "mulank": 2,
      "bhagyank": 6,
      "pair": {
        "rating_label": "2.5star",
        "rating_meaning": "average"
      }
    }
    """
    ensure_allowed("single")  # or "profession" if you later gate it separately
    return mulank_bhagyank_profile(dob)


# Triptych PNG
@router.get("/yearly-triptych.png")
async def yearly_triptych_png(
    dob: str,
    year: int,
    left_title: str = "DOB",
    right_title: str | None = None,
    combined_title: str = "Combined (Yearly)",
):
    ensure_allowed("yearly") 
    fig, _ = plot_yearly_triptych(dob, year, left_title, right_title, combined_title)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=170, bbox_inches="tight")
    return Response(content=buf.getvalue(), media_type="image/png")

# ▼▼ ADDED: Monthly Triptych PNG
@router.get("/monthly-triptych.png")
async def monthly_triptych_png(
    dob: str,
    year: int,
    month: int,
    left_title: str = "DOB",
    right_title: str | None = None,
    combined_title: str = "Combined (Monthly)",
):
    fig, _ = plot_monthly_triptych(dob, year, month, left_title, right_title, combined_title)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=170, bbox_inches="tight")
    return Response(content=buf.getvalue(), media_type="image/png")
# ▲▲ ADDED

# ▼▼ ADDED: Daily Triptych PNG
@router.get("/daily-triptych.png")
async def daily_triptych_png(
    dob: str,
    day: str = Query("today", description="DD-MM-YYYY or 'today'"),
    left_title: str = "DOB",
    right_title: str | None = None,
    combined_title: str = "Combined (Daily)",
):
    fig, _ = plot_daily_triptych(dob, day, left_title, right_title, combined_title)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=170, bbox_inches="tight")
    return Response(content=buf.getvalue(), media_type="image/png")
# ▲▲ ADDED




@router.get("/relationship-triangle.report.json")
async def relationship_triangle_report_json(
    left: str = Query(..., description="Left person's DOB (DD-MM-YYYY or YYYY-MM-DD)"),
    right: str = Query(..., description="Right person's DOB (DD-MM-YYYY or YYYY-MM-DD)"),
):
    ensure_allowed("relationship")
    return relationship_triangle_report(left, right)


# JSON report
@router.get("/yearly-triangle.report.json")
async def yearly_triangle_report_json(
    dob: str,
    year: int
):
    ensure_allowed("yearly")
    return yearly_triangle_report(dob, year)



@router.get("/monthly.report.json")
async def monthly_report_json(dob: str, year: int):
    """
    Monthly prediction report (DOB ⊕ Year) with months mapped as per screenshot.
    """
    return monthly_prediction_report(dob, year)




@router.get("/features/daily-triangle.report.json")
async def daily_triangle_report_json(
    dob: str = Query(..., description="DOB in DD-MM-YYYY or YYYY-MM-DD")
):
    return daily_triangle_report(dob)



@router.get("/health-triangle.report.json")
async def health_triangle_report_json(
    dob: str = Query(..., description="DD-MM-YYYY or YYYY-MM-DD"),
    gender: str | None = Query(None, description="optional: male/female"),
):
    return health_triangle_report(dob, gender=gender)


@router.get("/health/daily.report.json")
async def health_daily_report_json(
    dob: str = Query(..., description="DOB in DD-MM-YYYY or YYYY-MM-DD"),
    day: str | None = Query(None, description="DD-MM-YYYY or YYYY-MM-DD; omit for 'today'"),
    gender: str | None = Query(None, description="optional: male/female"),
):
    return health_daily_report(dob, day=day, gender=gender)


@router.get("/health/monthly.report.json")
async def health_monthly_report_json(
    dob: str = Query(..., description="DOB in DD-MM-YYYY or YYYY-MM-DD"),
    year: int = Query(..., description="Target year (e.g., 2025)"),
    gender: str | None = Query(None, description="optional: male/female"),
):
    return health_monthly_report(dob, year, gender=gender)


@router.get("/health/yearly.report.json")
async def health_yearly_report_json(
    dob: str = Query(..., description="DOB in DD-MM-YYYY or YYYY-MM-DD"),
    year: int = Query(..., description="Target year (e.g., 2025)"),
    gender: str | None = Query(None, description="optional: male/female"),
):
    return health_yearly_report(dob, year, gender=gender)




# ────────────────────────────────────────────────────────────────
# Profession Report (Mulank + Bhagyank → profession mapping)
# ────────────────────────────────────────────────────────────────

@router.get("/profession.report.json")
async def profession_report_json(
    dob: str = Query(..., description="DOB in DD-MM-YYYY or YYYY-MM-DD")
):
    ensure_allowed("single")   # or "profession" if you create a new feature gate
    return profession_report(dob)

@router.get("/profile-bulletins.json")
async def profile_bulletins_json(
    dob: str = Query(..., description="DOB in DD-MM-YYYY or YYYY-MM-DD"),
    gender: str | None = Query(None, description="male/female/other (optional)"),
    year: int | None = Query(None, description="Target year (optional)"),
    month: int | None = Query(None, description="Target month 1..12 (optional)"),
    day: str | None = Query("today", description="DD-MM-YYYY or 'today'"),
):
    """
    Compact, decorative bulletins for Profile page:
    Personality + Profession + Health + Time cycles.
    Uses existing report logic; only aggregates.
    """
    return build_profile_bulletins(dob=dob, gender=gender, year=year, month=month, day=day)


