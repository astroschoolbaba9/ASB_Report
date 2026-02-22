# numerology/features/special_numbers.py
from __future__ import annotations

from typing import Dict, Any, List, Tuple, Optional
from numerology.reads import build_reads

# ───────────────── helpers ─────────────────

LEFT_POS = {"A", "B", "E", "H", "K", "N", "Q"}
RIGHT_POS = {"C", "D", "F", "J", "M", "O", "R"}
MIDDLE_POS = {"G", "I", "L", "P"}

# ───────────── pairing groups for A↔D & B↔C rule ─────────────
# same OR in same group:
# {1,6} {2,7} {3,8} {4,9}
_PAIR_GROUPS = [
    {1, 6},
    {2, 7},
    {3, 8},
    {4, 9},
]


def _paired_or_equal(x: Optional[int], y: Optional[int]) -> bool:
    """True if x==y OR {x,y} is one of the pairing groups."""
    if x is None or y is None:
        return False
    x = int(x)
    y = int(y)
    if x == y:
        return True
    return any({x, y} == g for g in _PAIR_GROUPS)


# ───────────── leader pattern helper ─────────────
_LEADER_SET = {1, 2, 3}


def _leader_pattern(flat: Dict[str, int]) -> bool:
    """
    Leader pattern:
      (C,D) in {1,2,3} AND (F,G) in {1,2,3} AND (K,L) in {1,2,3}
    """
    C = flat.get("C")
    D = flat.get("D")
    F = flat.get("F")
    G = flat.get("G")
    K = flat.get("K")
    L = flat.get("L")

    if None in (C, D, F, G, K, L):
        return False

    return (
        int(C) in _LEADER_SET
        and int(D) in _LEADER_SET
        and int(F) in _LEADER_SET
        and int(G) in _LEADER_SET
        and int(K) in _LEADER_SET
        and int(L) in _LEADER_SET
    )


# ───────────── betrayal/back-stepping helper ─────────────
def _pair_has_one(x: Optional[int], y: Optional[int]) -> bool:
    """True if (x,y) is (1,anything 1..9) in any order."""
    if x is None or y is None:
        return False
    x = int(x)
    y = int(y)
    if x < 1 or x > 9 or y < 1 or y > 9:
        return False
    return x == 1 or y == 1


def _betrayal_flags(flat: Dict[str, int]) -> Tuple[bool, bool]:
    """
    Betrayal flags:
      front/direct pairs: AB, AE, BE
      back pairs:         CD, CF, DF
    Trigger if any pair contains 1 (1-x or x-1 including 1-1).
    Returns: (front, back)
    """
    A = flat.get("A")
    B = flat.get("B")
    C = flat.get("C")
    D = flat.get("D")
    E = flat.get("E")
    F = flat.get("F")

    front = _pair_has_one(A, B) or _pair_has_one(A, E) or _pair_has_one(B, E)
    back = _pair_has_one(C, D) or _pair_has_one(C, F) or _pair_has_one(D, F)
    return front, back


def _values_flat(vals: Dict[str, Dict[str, int]]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for sec in ("inputs", "layer1", "second_layer", "third_layer"):
        for k, v in (vals.get(sec) or {}).items():
            out[k] = int(v)
    return out


def _digits_on_side(flat: Dict[str, int], side: str) -> List[int]:
    if side == "left":
        pos = LEFT_POS
    elif side == "right":
        pos = RIGHT_POS
    else:
        pos = MIDDLE_POS
    return [int(flat[k]) for k in flat if k in pos]


def _scan_triples(flat: Dict[str, int]) -> Dict[str, str]:
    rows: List[Tuple[str, Tuple[str, ...]]] = [
        ("ABC", ("A", "B", "C")),
        ("BCD", ("B", "C", "D")),
        ("AEG", ("A", "E", "G")),
        ("DFG", ("D", "F", "G")),
        ("EGN", ("E", "G", "N")),
        ("FGO", ("F", "G", "O")),
        ("HIJ", ("H", "I", "J")),
        ("KLM", ("K", "L", "M")),
        ("NOP", ("N", "O", "P")),
    ]
    found: Dict[str, str] = {}
    for name, cols in rows:
        found[name] = "".join(str(flat[c]) for c in cols if c in flat)
    return found


def _is_sandwich_triple(s: str) -> bool:
    """
    Sandwich triple pattern: 1x1 / 2x2 / ... / 9x9
    i.e. a 3-digit string where first digit == last digit; middle can be anything.
    Examples: 101, 121, 191, 212, 272, 999
    """
    return isinstance(s, str) and len(s) == 3 and s[0].isdigit() and s[2].isdigit() and s[0] == s[2]


# ─────────────── Rules, partitioned by feature ───────────────

SPECIAL_RULES: List[Dict[str, Any]] = [
    # === Yearly / Monthly: movement, downfall, influence windows ===
    {
        "feature": ["yearly", "monthly"],
        "reads_any": [15, 16, 17],
        "tags": ["travel_or_relocation"],
        "note": "Travel, job change or relocation phase.",
    },
    {
        "feature": ["yearly"],
        "reads_any": [39, 93],
        "tags": ["major_downfall"],
        "note": "Major downfall marker; stay conservative in high-risk bets.",
    },
    {
        "feature": ["yearly", "monthly"],
        "reads_any": [57, 75],
        "tags": ["influence_circle"],
        "note": "Influence of powerful people; networking effects are strong.",
    },
    # === Relationship-centric patterns ===
    {
        "feature": ["relationship"],
        "reads_any": [48, 84, 88],
        "tags": ["separation"],
        "note": "Separation / chronic dissatisfaction tendency.",
    },
    {
        "feature": ["relationship"],
        "reads_any": [17, 27, 37, 45, 46, 56, 65, 79, 97, 33, 66],
        "tags": ["relationship_issue"],
        "note": "Relationship/marriage stress loop may surface.",
    },
    # === Health patterns ===
    {
        "feature": ["health"],
        "reads_any": [85, 88],
        "tags": ["heart_alert"],
        "note": "Heart or stress-load pattern; pace work, manage pressure.",
    },
    {
        "feature": ["health"],
        "triples_any": ["685", "222", "772"],
        "tags": ["mental_health"],
        "note": "Mind-mood strain tendency; protect sleep & routine.",
    },
    {
        "feature": ["health"],
        "reads_any": [42, 24],
        "tags": ["hospital_visit"],
        "note": "Hospital/blood-loss signal; consult early if symptomatic.",
    },
    # === Daily / Monthly: short-term tone ===
    {
        "feature": ["daily", "monthly"],
        "left_digits_any": [1, 2, 3, 4, 5],
        "tags": ["spending_thrift"],
        "note": "If these cluster on the left side, watch impulsive spending.",
    },
    {
        "feature": ["daily", "monthly"],
        "reads_any": [1, 3, 7, 9],
        "tags": ["extrovert_energy"],
        "note": "High social/expressive tone; use it for outreach.",
    },
    {
        "feature": ["daily", "monthly"],
        "reads_any": [2, 4, 6, 8],
        "tags": ["feminine_energy"],
        "note": "Receptive, grounded tone; good for consolidation.",
    },
    # === Dual/split personality rule (A↔D and B↔C pairing) ===
    {
        "feature": ["daily"],
        "abcd_pairing": True,
        "tags": ["dual_personality", "confusion", "daily_instability"],
        "note": (
            "A↔D and B↔C pairing detected (groups: 1–6, 2–7, 3–8, 4–9 or same). "
            "Daily: dual/contradictory personality can rise; avoid impulsive decisions."
        ),
    },
    {
        "feature": ["monthly"],
        "abcd_pairing": True,
        "tags": ["dual_personality", "confusion", "monthly_instability"],
        "note": (
            "A↔D and B↔C pairing detected (groups: 1–6, 2–7, 3–8, 4–9 or same). "
            "Monthly: inner conflict/mood swings can rise—keep routine stable and avoid extremes."
        ),
    },
    {
        "feature": ["yearly"],
        "abcd_pairing": True,
        "tags": ["dual_personality", "confusion", "yearly_indecision"],
        "note": (
            "A↔D and B↔C pairing detected (groups: 1–6, 2–7, 3–8, 4–9 or same). "
            "Yearly: confusion/indecision—delay irreversible commitments; seek clarity."
        ),
    },
    {
        "feature": ["relationship"],
        "abcd_pairing": True,
        "tags": ["dual_personality", "relationship_confusion"],
        "note": (
            "A↔D and B↔C pairing detected (groups: 1–6, 2–7, 3–8, 4–9 or same). "
            "Relationship: mixed signals/inner conflict can affect bonding—communicate clearly."
        ),
    },
    {
        "feature": ["person", "personality"],
        "abcd_pairing": True,
        "tags": ["dual_personality", "split_tendencies", "life_confusion"],
        "note": (
            "A↔D and B↔C pairing detected (groups: 1–6, 2–7, 3–8, 4–9 or same). "
            "Personality: dual/split tendencies; life direction may feel confusing at times."
        ),
    },
    # === Leader rule ===
    {
        "feature": ["yearly"],
        "leader_pattern": True,
        "tags": ["born_leader", "leadership"],
        "note": (
            "Leader pattern detected (C/D, F/G, K/L in 1–2–3). "
            "Yearly: born-leader energy—take charge, but avoid ego clashes."
        ),
    },
    {
        "feature": ["profession"],
        "leader_pattern": True,
        "tags": ["born_leader", "career_leadership"],
        "note": (
            "Leader pattern detected (C/D, F/G, K/L in 1–2–3). "
            "Profession: born-leader profile—best in roles with responsibility and decision power."
        ),
    },
    {
        "feature": ["person", "personality"],
        "leader_pattern": True,
        "tags": ["leadership", "initiative"],
        "note": (
            "Leader pattern detected (C/D, F/G, K/L in 1–2–3). "
            "Personality: strong leadership and initiative—channel it into clear goals."
        ),
    },
    # === Betrayal / back-stepping rule ===
    {
        "feature": ["daily"],
        "betrayal_pattern": True,
        "tags": ["betrayal_risk", "caution"],
        "note_tpl": (
            "Back-stepping/betrayal marker detected ({direction}). "
            "Daily: be careful with trust and confirmations; avoid sharing sensitive plans too quickly."
        ),
    },
    {
        "feature": ["monthly"],
        "betrayal_pattern": True,
        "tags": ["betrayal_risk", "caution"],
        "note_tpl": (
            "Back-stepping/betrayal marker detected ({direction}). "
            "Monthly: check agreements, verify intentions, and keep boundaries strong."
        ),
    },
    {
        "feature": ["yearly"],
        "betrayal_pattern": True,
        "tags": ["betrayal_risk", "caution"],
        "note_tpl": (
            "Back-stepping/betrayal marker detected ({direction}). "
            "Yearly: be selective with partnerships; document important commitments."
        ),
    },
    {
        "feature": ["relationship"],
        "betrayal_pattern": True,
        "tags": ["betrayal_risk", "relationship_trust"],
        "note_tpl": (
            "Back-stepping/betrayal marker detected ({direction}). "
            "Relationship: trust tests can appear—prefer clarity, honesty, and boundaries."
        ),
    },
    {
        "feature": ["person", "personality"],
        "betrayal_pattern": True,
        "tags": ["betrayal_risk", "trust_issues"],
        "note_tpl": (
            "Back-stepping/betrayal marker detected ({direction}). "
            "Personality: you may face trust challenges—choose people carefully and protect your energy."
        ),
    },
]

# ✅ AEG/DFG same-number triple rule-set (111/222/.../999)
SAME_TRIPLES = ["111", "222", "333", "444", "555", "666", "777", "888", "999"]

SPECIAL_RULES += [
    {
        "feature": ["daily"],
        "triples_keys": ["AEG", "DFG"],
        "triples_any": SAME_TRIPLES,
        "tags": ["negative_cycle", "accident_risk", "confusion", "dual_personality"],
        "note": (
            "AEG/DFG same-number triple (111/222/.../999) detected. "
            "Daily: confusion/dual nature can rise; accident/bad incident risk if careless. "
            "Digit mapping: 1→6, 2→7, 3→8, 4→9, and 5 is anytime."
        ),
    },
    {
        "feature": ["monthly"],
        "triples_keys": ["AEG", "DFG"],
        "triples_any": SAME_TRIPLES,
        "tags": ["negative_cycle", "serious_illness_risk", "high_risk_emotional_phase", "confusion", "dual_personality"],
        "note": (
            "AEG/DFG same-number triple (111/222/.../999) detected. "
            "Monthly: serious illness/stress risk; inner conflict can rise—avoid isolation and seek support if overwhelmed. "
            "Digit mapping: 1→6, 2→7, 3→8, 4→9, and 5 is anytime."
        ),
    },
    {
        "feature": ["yearly"],
        "triples_keys": ["AEG", "DFG"],
        "triples_any": SAME_TRIPLES,
        "tags": ["negative_cycle", "decision_confusion", "confusion", "dual_personality"],
        "note": (
            "AEG/DFG same-number triple (111/222/.../999) detected. "
            "Yearly: confusion/indecision—avoid major irreversible decisions without guidance. "
            "Digit mapping: 1→6, 2→7, 3→8, 4→9, and 5 is anytime."
        ),
    },
]

# ✅ AEG/DFG sandwich triple rule-set (1x1 / 2x2 / ... / 9x9)
# Note: this is a DIFFERENT trigger than SAME_TRIPLES, but SAME response intent.
SPECIAL_RULES += [
    {
        "feature": ["daily"],
        "triples_keys": ["AEG", "DFG"],
        "triples_sandwich": True,
        "tags": ["negative_cycle", "accident_risk", "confusion", "dual_personality"],
        "note": (
            "AEG/DFG sandwich triple (1x1/2x2/.../9x9) detected (e.g., 1x1 treated like 111). "
            "Daily: confusion/dual nature can rise; accident/bad incident risk if careless. "
            "Digit mapping: 1→6, 2→7, 3→8, 4→9, and 5 is anytime."
        ),
    },
    {
        "feature": ["monthly"],
        "triples_keys": ["AEG", "DFG"],
        "triples_sandwich": True,
        "tags": ["negative_cycle", "serious_illness_risk", "high_risk_emotional_phase", "confusion", "dual_personality"],
        "note": (
            "AEG/DFG sandwich triple (1x1/2x2/.../9x9) detected (e.g., 2x2 treated like 222). "
            "Monthly: serious illness/stress risk; inner conflict can rise—avoid isolation and seek support if overwhelmed. "
            "Digit mapping: 1→6, 2→7, 3→8, 4→9, and 5 is anytime."
        ),
    },
    {
        "feature": ["yearly"],
        "triples_keys": ["AEG", "DFG"],
        "triples_sandwich": True,
        "tags": ["negative_cycle", "decision_confusion", "confusion", "dual_personality"],
        "note": (
            "AEG/DFG sandwich triple (1x1/2x2/.../9x9) detected (e.g., 9x9 treated like 999). "
            "Yearly: confusion/indecision—avoid major irreversible decisions without guidance. "
            "Digit mapping: 1→6, 2→7, 3→8, 4→9, and 5 is anytime."
        ),
    },
]

# Dedicated “18/81” downfall windows (timeline logic)
def _evaluate_18_windows(read_values: List[int]) -> Optional[Dict[str, Any]]:
    c = sum(1 for v in read_values if v in (18, 81))
    if c == 0:
        return None
    windows = [{"upto_age": 27}, {"upto_age": 36}, {"upto_age": 45}]
    return {
        "occurrences": c,
        "windows": windows,
        "extra_anytime_after_45": bool(c >= 3),
        "estimated_total_downfalls": (3 if c == 1 else 4 if c >= 2 else 0),
        "tags": ["downfall_18"],
        "note": "Downfall windows (legal/financial/relationship) based on 18/81 pattern.",
    }


def scan_special_signals(
    *,
    feature_type: str,
    final_values: Dict[str, Dict[str, int]],
    final_reads: Optional[Dict[str, int]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Inspect the FINAL (active) triangle of a feature and return a compact note
    ONLY when a rule matches for that feature_type.
    """
    flat = _values_flat(final_values)
    triples = _scan_triples(flat)
    reads = final_reads or build_reads(final_values)

    all_read_values = [v for v in (reads or {}).values() if isinstance(v, int)]
    compound_values = [v for v in all_read_values if 10 <= v <= 99]

    left_digits = _digits_on_side(flat, "left")
    right_digits = _digits_on_side(flat, "right")

    hits: List[Dict[str, Any]] = []
    tags: List[str] = []
    notes: List[str] = []

    for rule in SPECIAL_RULES:
        if feature_type not in rule.get("feature", []):
            continue

        ok = False
        extra_tags: List[str] = []
        extra_note: Optional[str] = None

        if "reads_any" in rule and any(rv in rule["reads_any"] for rv in all_read_values):
            ok = True

        # triples_any matcher (with optional key filter)
        if "triples_any" in rule:
            keys = rule.get("triples_keys")
            if keys:
                if any(triples.get(k) in rule["triples_any"] for k in keys):
                    ok = True
            else:
                if any(triples.get(k) in rule["triples_any"] for k in triples):
                    ok = True

        # sandwich triple matcher (1x1,2x2,...,9x9) with optional key filter
        if rule.get("triples_sandwich"):
            keys = rule.get("triples_keys")
            keys_to_check = keys if keys else list(triples.keys())
            if any(_is_sandwich_triple(triples.get(k, "")) for k in keys_to_check):
                ok = True

        if "left_digits_any" in rule and any(d in rule["left_digits_any"] for d in left_digits):
            ok = True
        if "right_digits_any" in rule and any(d in rule["right_digits_any"] for d in right_digits):
            ok = True

        if rule.get("abcd_pairing"):
            A = flat.get("A")
            B = flat.get("B")
            C = flat.get("C")
            D = flat.get("D")
            if _paired_or_equal(A, D) and _paired_or_equal(B, C):
                ok = True

        if rule.get("leader_pattern") and _leader_pattern(flat):
            ok = True

        if rule.get("betrayal_pattern"):
            front, back = _betrayal_flags(flat)
            if front or back:
                ok = True
                if front and back:
                    direction = "front and back"
                elif front:
                    direction = "front/direct"
                else:
                    direction = "back"

                if front:
                    extra_tags.append("betrayal_front")
                if back:
                    extra_tags.append("betrayal_back")

                tpl = rule.get("note_tpl")
                if isinstance(tpl, str) and "{direction}" in tpl:
                    extra_note = tpl.format(direction=direction)
                else:
                    extra_note = tpl or "Back-stepping/betrayal marker detected."

        if ok:
            hits.append(rule)
            tags.extend(rule.get("tags", []))
            tags.extend(extra_tags)

            if extra_note:
                notes.append(extra_note)
            else:
                if rule.get("note"):
                    notes.append(rule["note"])

    r18 = _evaluate_18_windows(compound_values) if feature_type in ("yearly", "monthly") else None
    if r18:
        hits.append({"special": "18_rule"})
        tags.extend(r18["tags"])
        notes.append(r18["note"])

    if not hits:
        return None

    def _dedup(seq: List[str]) -> List[str]:
        seen, out = set(), []
        for x in seq:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    return {
        "present": True,
        "feature": feature_type,
        "tags": _dedup(tags),
        "notes": _dedup(notes),
        "reads_used": sorted(set(compound_values)),
        "triples_seen": {k: v for k, v in triples.items() if v},
        "left_side_digits": sorted(left_digits),
        "right_side_digits": sorted(right_digits),
        "r18": r18,
    }
