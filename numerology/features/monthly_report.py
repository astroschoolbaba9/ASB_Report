# numerology/features/monthly_report.py
from __future__ import annotations
from typing import Dict, Any

from numerology.core import (
    mystical_triangle_values_image,
    month_year_driver_triangle,   # A=0, B=month(M.M), C/D from year
    monthly_combined_triangle,    # combine(left, driver)
    _collect_used_numbers,
)
from numerology.traits import meaning, num_traits

# 🔹 NEW imports
from numerology.reads import build_reads
from numerology.traits import summarize_polarity
from numerology.features.special_numbers import scan_special_signals


# Month → triangle-position mapping (as per your screenshot)
_MONTH_POS: Dict[int, str] = {
     1: "E",  2: "E",      # Jan–Feb
     3: "F",  4: "F",      # Mar–Apr
     5: "H",  6: "I",  7: "J",  8: "K",  # May–Aug (row H–K)
     9: "N", 10: "O",      # Sept–Oct
    11: "Q", 12: "R",      # Nov–Dec
}


def _panel_core(vals: Dict[str, Dict[str, int]]) -> dict:
    """Small core section for UI/consumers (EF, G, P with meanings)."""
    e = vals["layer1"]["E"]; f = vals["layer1"]["F"]; g = vals["layer1"]["G"]
    p = vals["third_layer"]["P"]
    return {
        "EF_core": {
            "value": int(f"{e}{f}"),
            "E": e, "F": f,
            "E_meaning": meaning(e),
            "F_meaning": meaning(f),
        },
        "G": {"value": g, "meaning": meaning(g)},
        "P_outcome": {"value": p, "meaning": meaning(p)},
    }


def _extract_value(vals: Dict[str, Dict[str, int]], pos: str) -> int | None:
    """Fetch a position's value from the triangle dict."""
    if pos in ("E", "F", "G"):
        return vals["layer1"].get(pos)
    if pos in ("H", "I", "J", "K", "L", "M"):
        return vals["second_layer"].get(pos)
    if pos in ("N", "O", "P", "Q", "R"):
        return vals["third_layer"].get(pos)
    return None


def monthly_prediction_report(dob_str: str, year: int) -> Dict[str, Any]:
    """
    Deterministic monthly report for a given DOB and target year.

    Left   = DOB triangle
    Right  = Month-Year driver (A=0, B=M.M from DOB, C/D from year)
    Combo  = combine(left, right)  → active yearly pattern used for months

    Months mapped as:
      Jan–Feb: E
      Mar–Apr: F
      May–Aug: H, I, J, K (respectively)
      Sept–Oct: N, O
      Nov–Dec: Q, R
    """
    left = mystical_triangle_values_image(dob_str)
    right = month_year_driver_triangle(dob_str, year)
    combo = monthly_combined_triangle(dob_str, year)

    # Build per-month view from the COMBINED triangle
    months: Dict[str, Any] = {}
    for m in range(1, 13):
        pos = _MONTH_POS[m]
        val = _extract_value(combo, pos)
        months[str(m)] = {
            "position": pos,
            "value": val,
            "meaning": meaning(val) if isinstance(val, int) else None,
            "traits": num_traits(val) if isinstance(val, int) else None,
        }

    # Traits used anywhere in the combined triangle
    used_nums = sorted(_collect_used_numbers(combo))
    traits_map = {n: num_traits(n) for n in used_nums}

    # Core glance from combined
    E = combo["layer1"]["E"]; F = combo["layer1"]["F"]; G = combo["layer1"]["G"]
    P = combo["third_layer"]["P"]; EF = int(f"{E}{F}")

    # 🔹 NEW: compute reads (for scanner), polarity, and special notes (feature-aware="monthly")
    combo_reads = build_reads(combo)
    polarity = summarize_polarity(combo)
    special_notes = scan_special_signals(
        feature_type="monthly",
        final_values=combo,
        final_reads=combo_reads,
    )

    return {
        "dob": dob_str,
        "year": year,
        "panels": {
            "left_dob":   {"values": left,  "interpretations": {"core": _panel_core(left)}},
            "right_driver": {
                "values": right,
                "interpretations": {"core": _panel_core(right)},
                "note": "Monthly driver: A=0, B=M.M (from DOB), C/D from target year.",
            },
            "combined":   {
                "values": combo,
                "interpretations": {"core": _panel_core(combo)},
                "note": "Active pattern for months in this year (DOB ⊕ driver).",
                "polarity": polarity,                                   # 🔹 NEW
                **({"special_notes": special_notes} if special_notes else {}),  # 🔹 NEW
            },
        },
        "summary": {
            "glance": {"E": E, "F": F, "G": G, "EF": EF, "P": P},
            "meanings": {"E": meaning(E), "F": meaning(F), "G": meaning(G), "P": meaning(P)},
        },
        "months": months,      # month-by-month meanings/traits
        "traits": traits_map,  # digits used in combined
        "_mapping": _MONTH_POS # transparency/debugging
    }
