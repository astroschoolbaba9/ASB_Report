# numerology/features/daily_report.py
from __future__ import annotations
from typing import Dict, Any, List, Optional
from datetime import date

from numerology.core import (
    mystical_triangle_values_image,
    mystical_triangle_today,
    combine_two_triangles,
    _collect_used_numbers,
    _resolve_right_day,
)
from numerology.reads import build_reads
from numerology.traits import meaning, num_traits, F_TRAIT

# 🔹 NEW: imports for specials + polarity
from numerology.features.special_numbers import scan_special_signals
from numerology.traits import summarize_polarity


def _panel_core(vals: Dict[str, Dict[str, int]]) -> dict:
    e = vals["layer1"]["E"]; f = vals["layer1"]["F"]; g = vals["layer1"]["G"]
    p = vals["third_layer"]["P"]
    return {
        "EF_pair": int(f"{e}{f}"),
        "E": {"value": e, "meaning": meaning(e)},
        "F": {"value": f, "meaning": meaning(f)},
        "G": {"value": g, "meaning": meaning(g)},
        "P_outcome": {"value": p, "meaning": meaning(p)},
        "F_trait": F_TRAIT.get(f, ""),
    }


# time bands from your screenshot
_DAILY_BANDS: List[dict] = [
    {"start": "00:01", "end": "04:00", "codes": ["E"]},
    {"start": "04:01", "end": "08:00", "codes": ["F"]},
    {"start": "08:01", "end": "16:00", "codes": ["H", "I", "J", "K", "L", "M"]},
    {"start": "16:01", "end": "20:00", "codes": ["N", "O"]},
    {"start": "20:01", "end": "00:00", "codes": ["P", "Q", "R"]},
]

# optional quick tags
_QUICK_TAGS = {
    3: ["study", "speed"],
    4: ["strategies", "planning"],
    6: ["partner", "family"],
    8: ["workoholic"],
    9: ["energy"],
}


def _build_time_slots(vals: Dict[str, Dict[str, int]]) -> List[dict]:
    flat = {}
    for sec in ("inputs", "layer1", "second_layer", "third_layer"):
        flat.update(vals.get(sec, {}))

    slots = []
    for band in _DAILY_BANDS:
        blocks = []
        for code in band["codes"]:
            v = int(flat[code])
            blocks.append({
                "code": code,
                "value": v,
                "meaning": meaning(v),
                "tags": _QUICK_TAGS.get(v, []),
            })
        slots.append({
            "start": band["start"],
            "end": band["end"],
            "blocks": blocks,
        })
    return slots


def daily_triangle_report(dob_str: str, right_day: Optional[str] = None) -> Dict[str, Any]:
    """
    Daily report (DOB ⊕ Day):
      Left   = DOB triangle (normal mystical build)
      Right  = If right_day omitted/'today' → today's date triangle; else → the given date
      Combo  = combine_two_triangles(Left, Right)
    """
    # Left (DOB)
    left = mystical_triangle_values_image(dob_str)

    # Right (calendar day: today or manually provided)
    right, right_label = _resolve_right_day(right_day)  # new

    # Combined
    combo = combine_two_triangles(left, right)

    # Deterministic reads
    left_reads = build_reads(left)
    right_reads = build_reads(right)
    combo_reads = build_reads(combo)

    # Traits across the combined (active) panel
    used_nums = sorted(_collect_used_numbers(combo))
    traits_map = {n: num_traits(n) for n in used_nums}

    # Back-compat: keep "today" but set it to the chosen right date
    chosen_day_str = right_label

    right_panel = {
        "date": chosen_day_str,
        "values": right,
        "reads": right_reads,
        "core": _panel_core(right),
    }

    # 🔹 NEW: compute polarity + scan specials (feature-aware = "daily")
    polarity = summarize_polarity(combo)
    special_notes = scan_special_signals(
        feature_type="daily",
        final_values=combo,
        final_reads=combo_reads,
    )

    return {
        "type": "daily",
        "dob": dob_str,
        "day": chosen_day_str,   # Back-compat + clarity
        "today": chosen_day_str,
        "panels": {
            "left_dob": {
                "values": left,
                "reads": left_reads,
                "core": _panel_core(left),
            },
            "right_day": right_panel,         # New, correct key
            "right_today": right_panel,       # Back-compat alias (same data)
            "combined": {
                "values": combo,
                "reads": combo_reads,
                "core": _panel_core(combo),
                "time_slots": _build_time_slots(combo),
                "polarity": polarity,                                  # 🔹 NEW
                **({"special_notes": special_notes} if special_notes else {}),  # 🔹 NEW
            },
        },
        "traits": traits_map,
        "notes": {
            "priority": "Use the COMBINED panel for the day. G is the core driver; EF shows style; P is the day’s outcome.",
        },
    }
