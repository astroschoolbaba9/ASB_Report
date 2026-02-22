# numerology/mulank_profile.py
from __future__ import annotations
from typing import Dict, Tuple, Optional

from .core import mulank_bhagyank_from_dob

# ─────────────────────────────────────────────────────────────
# 1) Canonical star labels → human meanings
# ─────────────────────────────────────────────────────────────

STAR_MEANINGS: Dict[str, str] = {
    "5star":  "super successful, outstanding",
    "4.5star": "excellent",
    "4star":  "successful",
    "3.5star": "very good",
    "3star":  "good",
    "2.5star": "average",
    "2star":  "below average",
    "1.5star": "struggle",
    "1star":  "bad / poor",
    "??":     "anti / conflicting, especially around stability & finances",
    "":       "no data / not rated",
}


def _legacy_symbol_to_label(symbol: str) -> str:
    """
    Convert symbols like:
        ****, ***1/2, **(****), ?, *1/2
    into:
        4star, 3.5star, 2star, ??, 1.5star
    """
    if not symbol:
        return ""

    s = symbol.strip()

    if s == "?":
        return "??"

    # treat special patterns same as their base rating (NO extra notes)
    if s.startswith("**("):        # **(****)
        return "2star"
    if s.startswith("***(**"):     # ***(****)
        return "3star"

    mapping = {
        "*****":  "5star",
        "****":   "4star",
        "***1/2": "3.5star",
        "***":    "3star",
        "**1/2":  "2.5star",
        "**":     "2star",
        "*1/2":   "1.5star",
        "*":      "1star",
    }
    return mapping.get(s, "")


# ─────────────────────────────────────────────────────────────
# 2) Pair → legacy symbol map
# ─────────────────────────────────────────────────────────────

PAIR_STARS_LEGACY: Dict[Tuple[int, int], str] = {
    # Mulank 1
    (1, 1): "****",
    (1, 2): "***1/2",
    (1, 3): "***1/2",
    (1, 4): "***",
    (1, 5): "****",
    (1, 6): "***1/2",
    (1, 7): "***",
    (1, 8): "?",
    (1, 9): "*****",

    # Mulank 2
    (2, 1): "***",
    (2, 2): "**",
    (2, 3): "**1/2",
    (2, 4): "*",
    (2, 5): "***1/2",
    (2, 6): "**1/2",
    (2, 7): "**(****)",
    (2, 8): "?",
    (2, 9): "*",

    # Mulank 3
    (3, 1): "***",
    (3, 2): "**1/2",
    (3, 3): "***1/2",
    (3, 4): "**1/2",
    (3, 5): "***1/2",
    (3, 6): "?",
    (3, 7): "**(****)",
    (3, 8): "**1/2",
    (3, 9): "**",

    # Mulank 4
    (4, 1): "***",
    (4, 2): "*",
    (4, 3): "**1/2",
    (4, 4): "*1/2",
    (4, 5): "***",
    (4, 6): "***",
    (4, 7): "****",
    (4, 8): "*",
    (4, 9): "*",

    # Mulank 5
    (5, 1): "****",
    (5, 2): "***1/2",
    (5, 3): "***",
    (5, 4): "***",
    (5, 5): "****",
    (5, 6): "****",
    (5, 7): "***",
    (5, 8): "***",
    (5, 9): "***",

    # Mulank 6
    (6, 1): "***1/2",
    (6, 2): "**1/2",
    (6, 3): "?",
    (6, 4): "***",
    (6, 5): "****",
    (6, 6): "****",
    (6, 7): "***1/2",
    (6, 8): "***",
    (6, 9): "***",

    # Mulank 7
    (7, 1): "****",
    (7, 2): "**(****)",
    (7, 3): "***(****)",
    (7, 4): "****",
    (7, 5): "***",
    (7, 6): "****",
    (7, 7): "*",
    (7, 8): "*1/2",
    (7, 9): "**",

    # Mulank 8
    (8, 1): "?",
    (8, 2): "?",
    (8, 3): "**1/2",
    (8, 4): "*",
    (8, 5): "***",
    (8, 6): "***",
    (8, 7): "*1/2",
    (8, 8): "*",
    (8, 9): "*1/2",

    # Mulank 9
    (9, 1): "****",
    (9, 2): "**",
    (9, 3): "**1/2",
    (9, 4): "*",
    (9, 5): "***",
    (9, 6): "***",
    (9, 7): "**",
    (9, 8): "*1/2",
    (9, 9): "*",
}


def star_info_for_pair(mulank: int, bhagyank: int) -> Dict[str, Optional[str]]:
    """Return clean rating without extra_note."""
    symbol = PAIR_STARS_LEGACY.get((mulank, bhagyank), "")

    label = _legacy_symbol_to_label(symbol)
    meaning = STAR_MEANINGS.get(label, STAR_MEANINGS[""])

    return {

        "rating_label": label or None,
        "rating_meaning": meaning,
    }


# ─────────────────────────────────────────────────────────────
# 3) Public API
# ─────────────────────────────────────────────────────────────

def mulank_bhagyank_profile(dob_str: str) -> Dict[str, object]:
    mulank, bhagyank = mulank_bhagyank_from_dob(dob_str)
    pair_info = star_info_for_pair(mulank, bhagyank)

    return {
        "dob": dob_str,
        "mulank": mulank,
        "bhagyank": bhagyank,
        "pair": pair_info,
    }
