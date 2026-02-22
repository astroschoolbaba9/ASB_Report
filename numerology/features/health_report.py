from __future__ import annotations
from typing import Any, Dict, List, Tuple, Set, Optional

# ⬇️ added imports for combined triangles
from numerology.core import (
    mystical_triangle_values_image,
    _collect_used_numbers,
    daily_combined_triangle,
    monthly_combined_triangle,
    yearly_combined_triangle,
)

from numerology.reads import build_reads
from numerology.traits import num_traits, COMPOUND_TRAITS, F_TRAIT
from numerology.traits import (
    HEALTH_MEANINGS, ELEMENT_TABLE, TRIPLE_ROWS, CANCER_TRIPLES,
    HEART_ATTACK_COMPOUNDS, NERVOUS_ISSUE_READS, MENTAL_DISORDER_TRIPLE,
    CRITICAL_NINE_PAIRS,
)

# 🔹 NEW imports for special scanner and polarity
from numerology.features.special_numbers import scan_special_signals
from numerology.traits import summarize_polarity

#-------------------------------
#  Helper function for health.py
#-------------------------------
def _values_flat(vals: Dict[str, Dict[str, int]]) -> Dict[str, int]:
    """Flatten the triangle dict to a single label->value map."""
    out: Dict[str, int] = {}
    for section in ("inputs", "layer1", "second_layer", "third_layer"):
        out.update({k: int(v) for k, v in vals[section].items()})
    return out


def _scan_triples(flat: Dict[str, int]) -> Dict[str, str]:
    """Return triplet strings like 'ABC': '369' for configured rows."""
    found: Dict[str, str] = {}
    for name, cols in TRIPLE_ROWS:
        s = "".join(str(flat[c]) for c in cols)
        found[name] = s
    return found


def _count_element_presence(used_nums: List[int]) -> Dict[str, Dict[str, Any]]:
    """Compute count of element numbers present from the table."""
    present: Dict[str, Dict[str, Any]] = {}
    for elem, meta in ELEMENT_TABLE.items():
        nums = meta["numbers"]
        count = sum(1 for n in used_nums if n in nums)
        present[elem] = {
            "numbers": nums,
            "organs": meta["organs"],
            "count": count,
            "status": (
                "Missing" if count == 0 else
                "Balanced" if count == 1 else
                "Excessive"  # 2 or more
            ),
        }
    return present


def _organ_flags(flat: Dict[str, int],
                 reads: Dict[str, int],
                 triples: Dict[str, str]) -> Dict[str, Any]:
    """Deterministic flags derived from the user's screenshots."""
    flags: Dict[str, Any] = {}

    # Legs: N (left) and O (right) == 7
    if flat.get("N") == 7:
        flags["Left leg issue"] = {"where": "N", "reason": "N=7"}
    if flat.get("O") == 7:
        flags["Right leg issue"] = {"where": "O", "reason": "O=7"}

    # Lung cancer patterns
    if triples.get("EGN") == "369" or triples.get("FGO") == "369":
        flags["Lung cancer pattern"] = {"triples": {k: v for k, v in triples.items() if v == "369"}}
    # Stronger generic patterns
    if any(t == "666" for t in triples.values()):
        flags["Severe respiratory pattern (666)"] = True
    if any(t == "222" for t in triples.values()):
        flags["Gallbladder/Kidney pattern (222)"] = True

    # Hospital number: set {1,5,6} inside any configured triple
    for tname, tstr in triples.items():
        if set(tstr) == set("156"):
            flags.setdefault("Hospital number (156)", []).append(tname)

    # Cancer number presence (triple repeats)
    cancer_hits = [name for name, t in triples.items() if t in CANCER_TRIPLES]
    if cancer_hits:
        flags["Cancer numbers"] = cancer_hits

    # Nervous system issues if any read is 15 or 51
    if any(v in NERVOUS_ISSUE_READS for v in reads.values()):
        flags["Nerve issues (15/51)"] = True

    # Mental disorder cue if any triple equals 685
    if any(t == MENTAL_DISORDER_TRIPLE for t in triples.values()):
        flags["Mental disorder pattern (685)"] = True

    return flags


def _neoplasm_probability(E: int, F: int, reads: Dict[str, int]) -> Dict[str, Any]:
    """
    Simple probability aggregator per the sheet:
    - EF == 33 contributes 50%
    - Any compound read in CRITICAL_NINE_PAIRS adds 10% each (cap 100)
    """
    prob = 0
    reasons: List[str] = []
    if int(f"{E}{F}") == 33:
        prob += 50
        reasons.append("EF=33 (+50%)")

    nine_hits = sorted({v for v in reads.values() if v in CRITICAL_NINE_PAIRS})
    if nine_hits:
        add = min(50, 10 * len(nine_hits))
        prob += add
        reasons.append(f"critical pairs with 9: {nine_hits} (+{add}%)")

    return {"percent": min(100, prob), "reasons": reasons}


def _abdominal_block(I: int, J: int, K: int, L: int) -> Dict[str, Any]:
    """
    From screenshot: if 1,5,6,7 appear in I,J,K,L and any 3 are present => abdominal area issue.
    If subset contains 1,5,6 together -> C-section/IVF likelihood note.
    """
    window = [I, J, K, L]
    target = {1, 5, 6, 7}
    present = sorted(n for n in set(window) if n in target)
    risk = len([n for n in window if n in target]) >= 3
    csec = all(x in window for x in (1, 5, 6))
    note = []
    if risk:
        note.append("≥3 of {1,5,6,7} present")
    if csec:
        note.append("stomach has 1,5,6 ⇒ C-section/IVF chance high")
    return {"present": present, "risk": risk or csec, "notes": note}


def _element_summary(used_nums: List[int]) -> Dict[str, Any]:
    table = _count_element_presence(used_nums)
    # Quick guide: more than 2 is 'excessive' (per sheet note)
    return table


# ────────────────────────────────────────────────────────────────────────────
# NEW: Shared builder used by single / daily / monthly / yearly
# ────────────────────────────────────────────────────────────────────────────
def _build_health_report_from_values(
    dob_str: str,
    vals: Dict[str, Dict[str, int]],
    *,
    gender: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    EXACT same logic as your previous health_triangle_report(), but parameterized
    to accept a pre-computed triangle 'vals' (e.g., combined triangle).
    """
    flat = _values_flat(vals)
    used_nums = sorted(_collect_used_numbers(vals))
    traits = {n: num_traits(n) for n in used_nums}

    reads = build_reads(vals)
    triples = _scan_triples(flat)

    # 🔹 NEW additions
    polarity = summarize_polarity(vals)
    special_notes = scan_special_signals(
        feature_type="health",
        final_values=vals,
        final_reads=reads,
    )

    # Core references
    E = flat["E"]; F = flat["F"]; G = flat["G"]
    H = flat["H"]; I = flat["I"]; J = flat["J"]; K = flat["K"]; L = flat["L"]; M = flat["M"]
    N = flat["N"]; O = flat["O"]; P = flat["P"]; Q = flat["Q"]; R = flat["R"]

    # Sections (use health meanings instead of general meanings)
    sections = {
        "core_health": {
            "Vital Energy (G)": {
                "value": G,
                "meaning": HEALTH_MEANINGS.get(G, "—"),
                "details_ref": G,
            },
            "Balance (E+F)": {
                "value": int(f"{E}{F}"),
                "note": f"E⇒{HEALTH_MEANINGS.get(E,'—')}; F⇒{HEALTH_MEANINGS.get(F,'—')}",
                "E_details_ref": E,
                "F_details_ref": F,
            },
            "Healing Direction (P)": {
                "value": P,
                "meaning": HEALTH_MEANINGS.get(P, "—"),
                "details_ref": P,
            },
        },
        "zones": {
            "Mental Health Zone (N,O)": {
                "values": (N, O),
                "meaning": f"N⇒{HEALTH_MEANINGS.get(N,'—')}; O⇒{HEALTH_MEANINGS.get(O,'—')}",
            },
            "Physical Health Zone (H,I,J)": {
                "values": (H, I, J),
                "meaning": f"H⇒{HEALTH_MEANINGS.get(H,'—')}; I⇒{HEALTH_MEANINGS.get(I,'—')}; J⇒{HEALTH_MEANINGS.get(J,'—')}",
            },
            "Emotional Health Zone (K,L,M)": {
                "values": (K, L, M),
                "meaning": f"K⇒{HEALTH_MEANINGS.get(K,'—')}; L⇒{HEALTH_MEANINGS.get(L,'—')}; M⇒{HEALTH_MEANINGS.get(M,'—')}",
            },
            "Recovery Potential (Q,R)": {
                "values": (Q, R),
                "meaning": f"Q⇒{HEALTH_MEANINGS.get(Q,'—')}; R⇒{HEALTH_MEANINGS.get(R,'—')}",
            },
        },
    }

    # Organ/disease flags
    organ_flags = _organ_flags(flat, reads, triples)

    # Neoplasm risk scoring
    neoplasm = _neoplasm_probability(E, F, reads)

    # Breast cancer heuristic
    breast_note = None
    if gender and gender.lower().startswith("f") and flat.get("A") == 4 and flat.get("B") == 7:
        breast_note = "Higher tendency for breast-related issues (A=4, B=7)."

    # Abdominal block logic (I,J,K,L)
    abdomen = _abdominal_block(I, J, K, L)

    # Element presence table
    elements = _element_summary(used_nums)

    payload = {
        "dob": dob_str,
        "values": vals,
        "triples": triples,
        "reads": reads,
        "reads_traits": {c: COMPOUND_TRAITS[c] for c in sorted({v for v in reads.values() if v in COMPOUND_TRAITS})},
        "traits": traits,
        "sections": sections,
        "organ_flags": organ_flags,
        "neoplasm_probability": neoplasm,
        "abdomen": abdomen,
        "elements": elements,
        "polarity": polarity,                                # 🔹 NEW
        **({"special_notes": special_notes} if special_notes else {}),  # 🔹 NEW
        "core_notes": {
            "priority": "G=vitality; EF=balance; P=healing direction.",
            "F_trait": F_TRAIT.get(F, ""),
            "health_meanings_note": "Health meanings (1–9) are organ-centric (not personality meanings).",
            "breast_note": breast_note,
        },
    }
    if context:
        payload["context"] = context
    return payload


# ────────────────────────────────────────────────────────────────────────────
# ORIGINAL API (unchanged behavior)
# ────────────────────────────────────────────────────────────────────────────
def health_triangle_report(dob_str: str, *, gender: str | None = None) -> Dict[str, Any]:
    vals = mystical_triangle_values_image(dob_str)
    return _build_health_report_from_values(dob_str, vals, gender=gender, context={"mode": "single"})


# ────────────────────────────────────────────────────────────────────────────
# NEW convenience wrappers: daily / monthly / yearly via COMBINED triangles
# ────────────────────────────────────────────────────────────────────────────
def health_daily_report(
    dob_str: str, *, day: Optional[str] = None, gender: Optional[str] = None
) -> Dict[str, Any]:
    combo_vals = daily_combined_triangle(dob_str, day=day)
    return _build_health_report_from_values(
        dob_str, combo_vals, gender=gender,
        context={"mode": "daily", "day": day or "today", "note": "Combined: DOB ⊕ Day"}
    )


def health_monthly_report(
    dob_str: str, year: int, *, gender: Optional[str] = None
) -> Dict[str, Any]:
    combo_vals = monthly_combined_triangle(dob_str, year)
    return _build_health_report_from_values(
        dob_str, combo_vals, gender=gender,
        context={"mode": "monthly", "year": year, "note": "Combined: DOB ⊕ Month-Year driver"}
    )


def health_yearly_report(
    dob_str: str, year: int, *, gender: Optional[str] = None
) -> Dict[str, Any]:
    combo_vals = yearly_combined_triangle(dob_str, year)
    return _build_health_report_from_values(
        dob_str, combo_vals, gender=gender,
        context={"mode": "yearly", "year": year, "note": "Combined: DOB ⊕ Year-only"}
    )
