# numerology/features/profession_report.py
from __future__ import annotations

from typing import Any, Dict

from numerology.core import mulank_bhagyank_from_dob
from numerology.profession_traits import (
    PAIRS as PROFESSION_PAIRS,
    star_meaning,
    star_meaning_parts,
)



def _build_pair_profession_block(mulank: int, bhagyank: int) -> Dict[str, Any]:
    """
    Build deterministic profession block from the (Mulank, Bhagyank) pair.

    Reads PAIRS + star_meaning from numerology.profession_traits.
    """
    key = (int(mulank), int(bhagyank))
    info = PROFESSION_PAIRS.get(key)

    if not info:
        return {
            "mulank": int(mulank),
            "bhagyank": int(bhagyank),
            "pair_key": f"{int(mulank)}-{int(bhagyank)}",
            "stars": None,
            "rating_text": "",
            "rating_short": "",
            "rating_detail": "",
            "professions": [],
            "remark": "",
        }

    stars = info.get("stars") or ""
    rating_text = star_meaning(stars)              # combined: "Average; Average combination ..."
    rating_short, rating_detail = star_meaning_parts(stars)

    return {
        "mulank": int(mulank),
        "bhagyank": int(bhagyank),
        "pair_key": f"{int(mulank)}-{int(bhagyank)}",
        "stars": stars,
        "rating_text": rating_text,                # keep for backward compatibility
        "rating_short": rating_short,              # e.g. "Average"
        "rating_detail": rating_detail,            # e.g. "Average combination that requires ..."
        "professions": info.get("professions", []),
        "remark": info.get("remark", ""),
    }



def profession_report(dob_str: str) -> Dict[str, Any]:
    """
    Deterministic profession report driven ONLY by:
      • Mulank (A)
      • Bhagyank (G)
      • Mulank+Bhagyank PAIRS mapping

    No AI and no personality traits here.
    """
    mulank, bhagyank = mulank_bhagyank_from_dob(dob_str)
    pair_profession = _build_pair_profession_block(mulank, bhagyank)

    return {
        "dob": dob_str,
        "mulank": int(mulank),
        "bhagyank": int(bhagyank),
        "profession": pair_profession,
    }
