# numerology/features/yearly_report.py
from __future__ import annotations
from typing import Dict, Any
from numerology.core import (
    mystical_triangle_values_image,
    year_only_triangle,
    yearly_combined_triangle,
    _collect_used_numbers,
)
from numerology.reads import build_reads
from numerology.traits import meaning, num_traits, COMPOUND_TRAITS, F_TRAIT

# 🔹 NEW imports
from numerology.traits import summarize_polarity
from numerology.features.special_numbers import scan_special_signals


def _reads_details(vals: Dict[str, Dict[str, int]]) -> tuple[dict, dict]:
    """Build reads + (compact) traits mapping only for used compound codes."""
    reads = build_reads(vals)
    used_codes = sorted({v for v in reads.values() if v in COMPOUND_TRAITS})
    reads_traits = {code: COMPOUND_TRAITS[code] for code in used_codes}
    reads_explained = {
        k: {"value": v, "traits_ref": v} if v in COMPOUND_TRAITS else {"value": v}
        for k, v in reads.items()
    }
    return reads_explained, reads_traits


def yearly_triangle_report(dob_str: str, year: int) -> Dict[str, Any]:
    """
    Yearly report that mirrors your screenshot:
      Left   = DOB triangle
      Right  = Year-only triangle (A=0,B=0, C/D from target year)
      Combo  = combine_two_triangles(Left, Right)

    Returns one JSON with values, reads, and traits-driven notes.
    """
    left = mystical_triangle_values_image(dob_str)
    right = year_only_triangle(year)
    combo = yearly_combined_triangle(dob_str, year)

    # traits: collect from the combined triangle (what matters for the year’s effect)
    used_nums = sorted(_collect_used_numbers(combo))
    traits_map = {n: num_traits(n) for n in used_nums}

    # reads/traits per panel
    left_reads_explained, left_reads_traits = _reads_details(left)
    right_reads_explained, right_reads_traits = _reads_details(right)
    combo_reads_explained, combo_reads_traits = _reads_details(combo)

    # 🔹 NEW: compute polarity + special notes (feature-aware = "yearly")
    polarity = summarize_polarity(combo)
    special_notes = scan_special_signals(
        feature_type="yearly",
        final_values=combo,
        final_reads=build_reads(combo),
    )

    # Core glance (from combo)
    E = combo["layer1"]["E"]; F = combo["layer1"]["F"]; G = combo["layer1"]["G"]
    P = combo["third_layer"]["P"]; EF = int(f"{E}{F}")

    # Panel mini-sections with meanings (for UI hover / reference)
    def panel_core(vals: Dict[str, Dict[str, int]]) -> dict:
        e = vals["layer1"]["E"]; f = vals["layer1"]["F"]; g = vals["layer1"]["G"]
        p = vals["third_layer"]["P"]
        return {
            "EF_core": {
                "value": int(f"{e}{f}"),
                "note": f"E={e} ({meaning(e)}), F={f} ({meaning(f)})",
                "E_details_ref": e, "F_details_ref": f,
            },
            "G": {"value": g, "meaning": meaning(g), "details_ref": g},
            "P_outcome": {"value": p, "meaning": meaning(p), "details_ref": p},
        }

    report = {
        "dob": dob_str,
        "year": year,
        "panels": {
            "left_dob": {
                "values": left,
                "reads": left_reads_explained,
                "reads_traits": left_reads_traits,
                "interpretations": {"core": panel_core(left)},
                "core_notes": {
                    "priority": "G is most important core number; then E and F.",
                    "F_trait": F_TRAIT.get(left["layer1"]["F"], ""),
                },
            },
            "right_year": {
                "values": right,
                "reads": right_reads_explained,
                "reads_traits": right_reads_traits,
                "interpretations": {"core": panel_core(right)},
                "note": "Year-only driver: A=0, B=0; C/D from the target year.",
                "core_notes": {
                    "priority": "Driver panel for the year; used only for combination.",
                    "F_trait": F_TRAIT.get(right["layer1"]["F"], ""),
                },
            },
            "combined": {
                "values": combo,
                "reads": combo_reads_explained,
                "reads_traits": combo_reads_traits,
                "interpretations": {"core": panel_core(combo)},
                "core_notes": {
                    "priority": "This is the active yearly pattern (DOB ⊕ Year).",
                    "F_trait": F_TRAIT.get(combo["layer1"]["F"], ""),
                },
                "polarity": polarity,                                  # 🔹 NEW
                **({"special_notes": special_notes} if special_notes else {}),  # 🔹 NEW
            },
        },
        "summary": {
            "glance": {"G": G, "EF": EF, "P": P},
            "meanings": {
                "G": meaning(G),
                "E": meaning(E),
                "F": meaning(F),
                "P": meaning(P),
            },
        },
        "traits": traits_map,  # single-digit traits referenced by details_ref
    }
    return report
