# numerology/features/relationship_report.py
from __future__ import annotations
from typing import Any, Dict, Tuple, List
from numerology.core import mystical_triangle_values_image, combine_two_triangles, _collect_used_numbers
from numerology.reads import build_reads
from numerology.traits import meaning, COMPOUND_TRAITS, F_TRAIT, num_traits
from numerology.traits import COMPOUND_ALERTS, ALERT_TAG_ORDER, element_of, DEFAULT_ELEMENT_PRESET

# 🔹 NEW imports
from numerology.traits import summarize_polarity
from numerology.features.special_numbers import scan_special_signals


# ───────────────────────── constants (new, centralized) ─────────────────────────
MIRROR_PAIRS: set[int] = {18, 81, 27, 72, 36, 63, 45, 54}


# ───────────────────────── helpers (unchanged) ─────────────────────────
def _reads_contains(reads: Dict[str, int], targets: List[int]) -> bool:
    tset = set(targets)
    return any(isinstance(v, int) and v in tset for v in reads.values())


def _any_digit_is(values: Dict[str, Any], target: int) -> bool:
    for section in ("inputs", "layer1", "second_layer", "third_layer"):
        block = values.get(section, {})
        if isinstance(block, dict):
            for v in block.values():
                if isinstance(v, int) and v == target:
                    return True
    return False


def _bond_assessment(vals_combined: Dict[str, Any], reads: Dict[str, int]) -> Dict[str, Any]:
    has_27_link = _reads_contains(reads, [27, 72])
    lucky_any_9 = _any_digit_is(vals_combined, 9)
    qr_val = reads.get("QR")
    qr_linked = qr_val in MIRROR_PAIRS
    g_is_9 = vals_combined.get("layer1", {}).get("G") == 9

    score = 0
    if has_27_link: score += 2
    if g_is_9: score += 2
    if lucky_any_9: score += 1
    if qr_linked: score -= 1

    if score >= 4:
        bucket = "Highest Possibility"
    elif score == 3:
        bucket = "Stronger"
    elif score == 2:
        bucket = "Strong"
    else:
        bucket = "Fair"

    return {
        "has_27_link": has_27_link,
        "lucky_any_9": lucky_any_9,
        "qr_linked": qr_linked,
        "g_is_9": g_is_9,
        "score": score,
        "bucket": bucket,
        "notes": [
            "Bond is strong if 27/72 linked" if has_27_link else "",
            "Any one is 9 → Lucky" if lucky_any_9 else "",
            "Q & R linked → Complicated" if qr_linked else "",
            "G is 9 (amplifies harmony/closure)" if g_is_9 else "",
        ],
    }


def _issue_flags_from_reads(reads: Dict[str, int]) -> Dict[str, List[str]]:
    buckets: Dict[str, List[str]] = {}
    for read_code, value in reads.items():
        alerts = COMPOUND_ALERTS.get(read_code)
        if not alerts:
            if read_code == "EF" and "EFCORE" in COMPOUND_ALERTS:
                alerts = COMPOUND_ALERTS["EFCORE"]
            else:
                continue
        for tag, enabled in alerts.items():
            if not enabled:
                continue
            buckets.setdefault(tag, []).append(read_code)

    ordered = {tag: buckets[tag] for tag in ALERT_TAG_ORDER if tag in buckets}
    for tag in buckets:
        if tag not in ordered:
            ordered[tag] = buckets[tag]
    return ordered


def _elements_summary(vals_combined: Dict[str, Any], preset: str | None = None) -> Dict[str, Any]:
    counts = {"water": 0, "wood": 0, "fire": 0, "earth": 0, "metal": 0}
    detail: Dict[str, List[Tuple[str, int]]] = {k: [] for k in counts}

    for section in ("inputs", "layer1", "second_layer", "third_layer"):
        block = vals_combined.get(section, {})
        if not isinstance(block, dict):
            continue
        for k, v in block.items():
            if not isinstance(v, int) or v < 1 or v > 9:
                continue
            el = element_of(v, preset=preset)
            if el in counts:
                counts[el] += 1
                detail[el].append((k, v))

    dominant = max(counts, key=lambda e: counts[e]) if counts else None
    return {
        "preset": preset or DEFAULT_ELEMENT_PRESET,
        "counts": counts,
        "dominant": dominant,
        "detail": detail,
    }


# ───────────────────────── main function ─────────────────────────
def relationship_triangle_report(dob_left: str, dob_right: str) -> Dict[str, Any]:
    vL = mystical_triangle_values_image(dob_left)
    vR = mystical_triangle_values_image(dob_right)
    vals_combined = combine_two_triangles(vL, vR)

    E = vals_combined["layer1"]["E"]
    F = vals_combined["layer1"]["F"]
    G = vals_combined["layer1"]["G"]
    P = vals_combined["third_layer"]["P"]

    used_nums = sorted(_collect_used_numbers(vals_combined))
    traits = {n: num_traits(n) for n in used_nums}
    reads = build_reads(vals_combined)

    used_codes = sorted({v for v in reads.values() if v in COMPOUND_TRAITS})
    reads_traits = {code: COMPOUND_TRAITS[code] for code in used_codes}
    reads_explained = {
        k: {"value": v, "traits_ref": v} if v in COMPOUND_TRAITS else {"value": v}
        for k, v in reads.items()
    }

    sections = {
        "core": {
            "Union EF (emotional–mental blend)": {
                "value": int(f"{E}{F}"),
                "note": (
                    f"Together, your emotional side (E={E}, {meaning(E)}) and "
                    f"behavioral/mental side (F={F}, {meaning(F)}) shape the daily style."
                ),
                "E_details_ref": E,
                "F_details_ref": F,
            },
            "Shared G (relationship center)": {
                "value": G,
                "meaning": f"Foundation you project together — {meaning(G)}.",
                "details_ref": G,
            },
            "Outcome P (direction of bond)": {
                "value": P,
                "meaning": f"Long-term direction tends toward {meaning(P)}.",
                "details_ref": P,
            },
        },
        "relations": {
            "Hidden potential (H/I)": {
                "values": (
                    vals_combined["second_layer"]["H"],
                    vals_combined["second_layer"]["I"],
                ),
                "meaning": "Subconscious compatibility / blind spots.",
                "H_details_ref": vals_combined["second_layer"]["H"],
                "I_details_ref": vals_combined["second_layer"]["I"],
            },
            "Family ties (J/K)": {
                "values": (
                    vals_combined["second_layer"]["J"],
                    vals_combined["second_layer"]["K"],
                ),
                "meaning": "Maternal & paternal patterning that colors the bond.",
                "J_details_ref": vals_combined["second_layer"]["J"],
                "K_details_ref": vals_combined["second_layer"]["K"],
            },
            "Outlook & growth (L/M)": {
                "values": (
                    vals_combined["second_layer"]["L"],
                    vals_combined["second_layer"]["M"],
                ),
                "meaning": "How you appear outwardly and how you research/grow together.",
                "L_details_ref": vals_combined["second_layer"]["L"],
                "M_details_ref": vals_combined["second_layer"]["M"],
            },
        },
        "upper_cluster": {
            "N,O,Q,R": {
                "values": (
                    vals_combined["third_layer"]["N"],
                    vals_combined["third_layer"]["O"],
                    vals_combined["third_layer"]["Q"],
                    vals_combined["third_layer"]["R"],
                ),
                "meaning": "Evolutionary arc: balance, shared vision, growth, resilience.",
                "N_details_ref": vals_combined["third_layer"]["N"],
                "O_details_ref": vals_combined["third_layer"]["O"],
                "Q_details_ref": vals_combined["third_layer"]["Q"],
                "R_details_ref": vals_combined["third_layer"]["R"],
            }
        }
    }

    bond = _bond_assessment(vals_combined, reads)
    issues = _issue_flags_from_reads(reads)
    elements = _elements_summary(vals_combined)

    # 🔹 NEW: polarity + special notes (feature-aware = "relationship")
    polarity = summarize_polarity(vals_combined)
    special_notes = scan_special_signals(
        feature_type="relationship",
        final_values=vals_combined,
        final_reads=reads,
    )

    return {
        "relationship": f"{dob_left} + {dob_right}",
        "values": vals_combined,
        "reads": reads,
        "reads_explained": reads_explained,
        "reads_traits": reads_traits,
        "interpretations": sections,
        "traits": traits,
        "bond_assessment": bond,
        "issue_flags": issues,
        "elements": elements,
        "polarity": polarity,                                  # 🔹 NEW
        **({"special_notes": special_notes} if special_notes else {}),  # 🔹 NEW
        "core_notes": {
            "priority": "Shared G is the foundation; EF is style; P is direction.",
            "F_trait": F_TRAIT.get(F, ""),
        },
    }
