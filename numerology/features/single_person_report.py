# numerology/features/single_person_report.py
from typing import Any, Dict

from numerology.core import (
    mystical_triangle_values_image,
    _collect_used_numbers,
    mulank_bhagyank_from_dob,        # 🔹 NEW
)
from numerology.reads import build_reads
from numerology.traits import meaning, num_traits, COMPOUND_TRAITS, F_TRAIT
# 🔹 NEW imports
from numerology.traits import summarize_polarity
from numerology.features.special_numbers import scan_special_signals
from numerology.mulank_bhagyank_traits import PAIR_MEANINGS  # 🔹 NEW


# ── Report ────────────────────────────────────────────────────────────────────
def mystical_triangle_report(dob_str: str) -> Dict:
    vals = mystical_triangle_values_image(dob_str)
    A, B, C, D = [vals["inputs"][k] for k in ("A", "B", "C", "D")]
    E, F, G = [vals["layer1"][k] for k in ("E", "F", "G")]
    H = vals["second_layer"]["H"]; I = vals["second_layer"]["I"]
    J = vals["second_layer"]["J"]; K = vals["second_layer"]["K"]
    L = vals["second_layer"]["L"]; M = vals["second_layer"]["M"]
    N = vals["third_layer"]["N"];  O = vals["third_layer"]["O"]
    P = vals["third_layer"]["P"];  Q = vals["third_layer"]["Q"]
    R = vals["third_layer"]["R"]

    # Build a deduped traits map for all numbers that appear in this triangle
    used_nums = sorted(_collect_used_numbers(vals))
    traits = {n: num_traits(n) for n in used_nums}

    core_pair = int(f"{E}{F}")
    reads = build_reads(vals)
    used_codes = sorted({v for v in reads.values() if v in COMPOUND_TRAITS})
    reads_traits = {c: COMPOUND_TRAITS[c] for c in used_codes}
    reads_explained = {
        k: {"value": v, "traits_ref": v} if v in COMPOUND_TRAITS else {"value": v}
        for k, v in reads.items()
    }

    # 🔹 NEW: derive Mulank & Bhagyank + combined meaning
    mulank, bhagyank = mulank_bhagyank_from_dob(dob_str)
    pair_key = (mulank, bhagyank)
    pair_meaning = PAIR_MEANINGS.get(pair_key, None)

    sections = {
        "core": {
            "EF_core": {
                "value": core_pair,
                "note": f"E={E} ({meaning(E)}), F={F} ({meaning(F)})",
                "E_details_ref": E,
                "F_details_ref": F,
            },
            "G": {
                "value": G,
                "meaning": meaning(G),
                "details_ref": G,
            },
            "P_outcome": {
                "value": P,
                "meaning": meaning(P),
                "details_ref": P,
            },
        },
        "relations": {
            "H1 (Intuition / 3rd eye)": {"value": H, "meaning": meaning(H), "details_ref": H},
            "H2 (Hidden Potential / Blind spot)": {"value": I, "meaning": meaning(I), "details_ref": I},
            "H3 (Relationship with Mother)": {"value": J, "meaning": meaning(J), "details_ref": J},
            "H4 (Relationship with Father)": {"value": K, "meaning": meaning(K), "details_ref": K},
            "H5 (External outlook)": {"value": L, "meaning": meaning(L), "details_ref": L},
            "H6 (B+C+E+F — research)": {"value": M, "meaning": meaning(M), "details_ref": M},
        },
        "upper_cluster": {
            "N": {"value": N, "meaning": meaning(N), "details_ref": N},
            "O": {"value": O, "meaning": meaning(O), "details_ref": O},
            "Q": {"value": Q, "meaning": meaning(Q), "details_ref": Q},
            "R": {"value": R, "meaning": meaning(R), "details_ref": R},
        }
    }

    # 🔹 NEW: polarity + special notes for single-person feature
    polarity = summarize_polarity(vals)
    special_notes = scan_special_signals(
        feature_type="person",
        final_values=vals,
        final_reads=reads,
    )

    # Add-on info without removing existing structure:
    report: Dict[str, Any] = {
        "dob": dob_str,
        # 🔹 Mulank–Bhagyank block placed immediately after dob
        "mulank_bhagyank": {
            "mulank": mulank,
            "bhagyank": bhagyank,
            "pair_key": f"{mulank}-{bhagyank}",
            "pair_meaning": pair_meaning,
        },
        "values": vals,
        "reads": reads,
        "reads_explained": reads_explained,
        "reads_traits": reads_traits,
        "interpretations": sections,
        "traits": traits,
        "polarity": polarity,  # 🔹 existing NEW
        "core_notes": {
            "priority": "G is most important core number; then E and F.",
            "F_trait": F_TRAIT.get(F, ""),
        },
    }

    # preserve existing optional special_notes behaviour
    if special_notes:
        report["special_notes"] = special_notes

    return report
