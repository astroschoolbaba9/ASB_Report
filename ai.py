# AI/ai.py  (imports section)
from __future__ import annotations
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ValidationError
import logging

from AI.prompts import PERSON_SYSTEM, RELATIONSHIP_SYSTEM, YEARLY_SYSTEM, HEALTH_SYSTEM, HEALTH_DAILY_SYSTEM, HEALTH_MONTHLY_SYSTEM, HEALTH_YEARLY_SYSTEM, MONTHLY_SYSTEM, DAILY_SYSTEM, ANCHORS, PROFESSION_SYSTEM
from AI.settings import settings
from AI.swot import generate_swot_from_interpretation

# replace report imports from core with features:
from numerology.features.single_person_report import mystical_triangle_report
from numerology.features.relationship_report import relationship_triangle_report
from numerology.features.yearly_report import yearly_triangle_report
from numerology.features.monthly_report import monthly_prediction_report
from numerology.features.daily_report import daily_triangle_report
from numerology.features.health_report import (
    health_triangle_report,      # existing (DOB-only)
    health_daily_report,         # NEW
    health_monthly_report,       # NEW
    health_yearly_report,        # NEW
)
from numerology.features.profession_report import profession_report


from numerology.traits import NUMBER_MEANINGS, F_TRAIT,HEALTH_MEANINGS

from datetime import datetime
import random


import re

_FORBID = re.compile(r"\b(?:E|F|G|P|EF|triangle|layer|second layer|third layer|H/I|J/K|N,O,Q,R)\b", re.I)
_HAS_DIGIT = re.compile(r"\d")


def _tokens_present(hint: str, hay: str) -> bool:
    toks = [w for w in re.split(r"\W+", hint) if w]
    if not toks:
        return False
    # consider the hint present if at least 2 tokens match (or 1 if the hint has only 1 token)
    required = 2 if len(toks) >= 2 else 1
    hits = sum(1 for t in toks if t in hay)
    return hits >= required

# --- sanitization helpers (place right after _HAS_DIGIT) ---
_SANITIZE_CODES = re.compile(r"""
    (?:\b[Ee]\s*=\s*\d+\b)|
    (?:\b[Ff]\s*=\s*\d+\b)|
    (?:\b[Gg]\s*=\s*\d+\b)|
    (?:\b[Pp]\s*=\s*\d+\b)|
    (?:\bEF\b)|
    (?:\bE\b|\bF\b|\bG\b|\bP\b)(?:\s*[\+\-–,]\s*\b(?:E|F|G|P)\b)?|
    (?:\bH\s*/\s*I\b)|(?:\bJ\s*/\s*K\b)|(?:\bN\s*,\s*O\s*,\s*Q\s*,\s*R\b)|   # ← add
    (?:\bcore\s+triangle\b)|(?:\blayer(?:s)?\b)|(?:\bsecond layer\b)|(?:\bthird layer\b)
""", re.VERBOSE)

def _anchor_hints(facts: dict) -> tuple[str, str, str]:
    g = p = f = ""

    # normal meanings (person/yearly/etc.)
    if isinstance(facts.get("meanings"), dict):
        g = g or _first_words(facts["meanings"].get("G"))
        p = p or _first_words(facts["meanings"].get("P"))

    # normal core interpretation (person/yearly/etc.)
    core_interp = (facts.get("interpretation") or {}).get("core") or {}
    g = g or _first_words(core_interp.get("g_meaning"))
    p = p or _first_words(core_interp.get("p_meaning"))

    # HEALTH: your health summary stores meanings in facts["core"]
    if not g or not p:
        hc = facts.get("core") or {}
        g = g or _first_words(hc.get("g_meaning"))
        p = p or _first_words(hc.get("p_meaning"))

    # F style (may be absent for health; that’s fine)
    f = _first_words(facts.get("F_trait")) or _first_words((facts.get("core_notes") or {}).get("F_trait"))
    return g, p, f



# Put these near your other compiled regexes (module level)
_WS_MULTI = re.compile(r"\s{2,}")
_SPACE_BEFORE_PUNCT = re.compile(r"\s+([\"'”’]?[,;:.!?])")
_TRAILING_SENTENCE_PUNCT = re.compile(r"[.!?]$")
_DUP_SENTENCES = re.compile(r"(?s)(^|[.!?]\s+)([^.!?]{3,})([.!?])\s+\2\3")

# If you want the “be mindful of impatience” rule compiled too:
_DEDUP_MINDFUL = re.compile(
    r"\b(be mindful of impatience)(,|\.)?\s*(?:\1\b[^\.\!]*[\.!])?",
    flags=re.I
)

def _sanitize_narrative(text: str, facts: dict) -> str:
    if not isinstance(text, str):
        return ""

    # 1) remove codes and layer jargon
    t = _SANITIZE_CODES.sub("", text)

    # 2) strip digits (policy requires no numbers at all)
    t = re.sub(r"\d", "", t)

    # 3) whitespace & punctuation normalization
    t = _WS_MULTI.sub(" ", t).strip()
    t = t.replace("&", " and ")   # ← optional but nice
    t = _SPACE_BEFORE_PUNCT.sub(r"\1", t)

    # 4) targeted de-dup for a common warning phrase
    t = _DEDUP_MINDFUL.sub(r"\1.", t)

    # 5) collapse any immediate duplicate sentences (exact duplicates)
    #    e.g., "... mindful of impatience. mindful of impatience."
    t_prev = None
    # loop once or twice maximum to be safe if multiple dupes exist
    for _ in range(2):
        if t == t_prev: break
        t_prev = t
        t = _DUP_SENTENCES.sub(r"\1\2\3", t).strip()

    # 6) ensure proper sentence end before anchors
    if t and not _TRAILING_SENTENCE_PUNCT.search(t):
        t += "."

    # 7) make sure anchors appear at least once
    g, p, f = _anchor_hints(facts)
    low = t.lower()
    add = []

    # Guard both by presence of the *hint* and the standardized anchor sentence
    anchor_g = f"At the foundation, this points to {g}." if g else ""
    anchor_p = f"Over the long run, the direction leans toward {p}." if p else ""
    anchor_f = f"Day to day, the natural style feels like {f}." if f else ""
    
    if g and (not _tokens_present(g, low)) and (anchor_g.lower() not in low):
        add.append(anchor_g)
    if p and (not _tokens_present(p, low)) and (anchor_p.lower() not in low):
        add.append(anchor_p)
    if f and (not _tokens_present(f, low)) and (anchor_f.lower() not in low):
        add.append(anchor_f)


    if add:
        # ensure exactly one space between the body and the anchors
        t = t.rstrip()  # it already ends with . ! or ?
        t = f"{t} {' '.join(add)}".strip()

    return t



# --- post-processing helpers (place immediately after _sanitize_narrative) ---

_SENT_SPLIT = re.compile(r'(?<=[.!?])\s+')

def _postprocess_narrative(text: str) -> str:
    """
    Final cleanup for model / mock narratives.

    Goals:
      - Keep one bullet per line.
      - Put anchors on their own lines.
      - Fix missing spaces after punctuation (e.g. 'impatience.as').
      - Avoid collapsing newlines.
    """
    if not isinstance(text, str):
        return ""

    # Normalise newlines and fix missing space after punctuation like 'word.as'
    t = text.replace("\r", "")
    t = re.sub(r'([.,!?])([A-Za-z])', r'\1 \2', t)

    # Ensure each bullet starts on its own line with a single space after the dot
    # Handles cases like " ... text. • Next bullet" or "•Bullet"
    t = re.sub(r'\s*•\s*', '\n• ', t)

    # Ensure anchor sentences start on a fresh line
    t = re.sub(r'\s*(At the foundation,)', r'\n\1', t)
    t = re.sub(r'\s*(Over the long run,)', r'\n\1', t)
    t = re.sub(r'\s*(Day to day,)', r'\n\1', t)

    # Collapse spaces and tabs but KEEP newlines
    t = re.sub(r'[ \t]+', ' ', t)

    # Split into lines, strip edges, drop pure-empty lines
    lines = [ln.strip() for ln in t.split("\n")]
    lines = [ln for ln in lines if ln]

    # Remove consecutive duplicate lines (safety)
    cleaned: list[str] = []
    last_lower = ""
    for ln in lines:
        norm = ln.rstrip(" ,;:").lower()
        if norm and norm != last_lower:
            cleaned.append(ln)
            last_lower = norm

    # Ensure bullet lines end with sentence punctuation
    for i, ln in enumerate(cleaned):
        if ln.startswith("•") and not re.search(r"[.!?]$", ln):
            cleaned[i] = ln + "."

    # Re-join with real line breaks so frontend/PDF sees one bullet per line
    t = "\n".join(cleaned).strip()

    # As a final guard, ensure the last line ends with punctuation
    if t and not re.search(r"[.!?]$", cleaned[-1]):
        t += "."

    return t



# Optional: keep final length inside your target band.
def _clip_words_by_mode(mode: str, text: str) -> str:
    bands = {
        "person": (300, 420),
        "relationship": (300, 420),
        "yearly": (300, 420),
        "monthly": (200, 320),
        "daily": (180, 270),
        "health": (300, 420),
        "health_daily": (180, 270),
        "health_monthly": (200, 320),
        "health_yearly": (300, 420),
        "profession": (130, 210)
    }
    min_w, max_w = bands.get((mode or "person").lower(), (300, 420))
    words = text.split()
    if len(words) <= max_w:
        return text
    clipped = " ".join(words[:max_w])
    last_dot = clipped.rfind('.')
    return (clipped[:last_dot+1] if last_dot != -1 else clipped).strip()


def _first_words(s: str | None, n: int = 6) -> str:
    if not isinstance(s, str) or not s.strip():
        return ""
    return " ".join(s.strip().lower().split()[:n])

def _ensure_anchor_meanings(facts: dict) -> None:
    """Guarantee facts['meanings'] has E/F/G/P phrases so _anchor_hints and _validates work."""
    meanings = facts.get("meanings")
    if not isinstance(meanings, dict):
        meanings = {}
        facts["meanings"] = meanings

    core = facts.get("core_numbers") or {}
    for k in ("E", "F", "G", "P"):
        n = core.get(k)
        if isinstance(n, int) and k not in meanings and n in NUMBER_MEANINGS:
            meanings[k] = NUMBER_MEANINGS[n].split(";")[0].strip()

def _finalize(text: str, facts: dict, mode: str) -> str:
    """Run the full cleanup pipeline on an AI or mock narrative."""
    t = _sanitize_narrative(text, facts)
    t = _postprocess_narrative(t)
    return _clip_words_by_mode(mode, t)


def _validates(text: str, facts: dict, mode: str) -> bool:
    if not text or _FORBID.search(text) or _HAS_DIGIT.search(text):
        return False

    def _norm(s: str) -> str:
        s = (s or "").lower().replace("&", " and ")
        return re.sub(r"\s+", " ", s).strip()

    low = _norm(text)
    g_hint, p_hint, f_hint = _anchor_hints(facts)

    g_present = bool(g_hint and _tokens_present(_norm(g_hint), low))
    p_present = bool(p_hint and _tokens_present(_norm(p_hint), low))
    f_present = bool(f_hint and _tokens_present(_norm(f_hint), low))

    present = sum([g_present, p_present, f_present])

    if not any([g_hint, p_hint, f_hint]):
        return True
    # relax yearly: require only 1 anchor instead of 2
    need = 1 if (mode or "").lower() == "yearly" else 2
    return present >= need






logger = logging.getLogger(__name__)

# Remember last used provider/model so the router can expose it in headers
_LAST_USED: Dict[str, Optional[str]] = {"provider": None, "model": None}


def get_last_used() -> Dict[str, Optional[str]]:
    """Return a copy of the last-used provider/model for debugging."""
    return dict(_LAST_USED)


# ---- Output schema (single key) ----
class AIInterpretation(BaseModel):
    interpretation: str = Field(..., min_length=40)


# ---------------------------- helpers ----------------------------

def _clean_phrase(s: str) -> str:
    # Trim, drop final period if present
    s = (s or "").strip()
    return s[:-1] if s.endswith(".") else s

def _as_readable_list(phrase: str) -> str:
    """
    Turn 'Care, responsibility, harmony.' into
    'care, responsibility, and harmony'.
    """
    parts = [_clean_phrase(p).strip().lower() for p in phrase.split(",") if p.strip()]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    return f"{', '.join(parts[:-1])}, and {parts[-1]}"

def _join_nonempty(chunks: List[str]) -> str:
    return " ".join([c.strip() for c in chunks if c and c.strip()])

def _compose_grounding() -> str:
    parts = ["Meanings:"]
    for k in sorted(NUMBER_MEANINGS.keys()):
        parts.append(f"{k}: {NUMBER_MEANINGS[k]}")
    parts.append("\nF traits:")
    for k in sorted(F_TRAIT.keys()):
        parts.append(f"F={k}: {F_TRAIT[k]}")
    return "\n".join(parts)

def _compose_health_grounding() -> str:
    parts = ["Health Meanings (1–9):"]
    for k in sorted(HEALTH_MEANINGS.keys()):
        parts.append(f"{k}: {HEALTH_MEANINGS[k]}")
    parts.append(
        "\nGuidelines: supportive tone, no diagnosis, suggest gentle habits (sleep, food, movement, pacing)."
    )
    return "\n".join(parts)

def _compose_grounding_for(
    mode: str,
    *,
    used_digits: List[int] | None = None,
    used_f: Optional[int] = None,
    facts: Optional[dict] = None,
) -> str:
    """Return the smallest safe grounding for each mode, using only the meanings actually needed."""

    # 🔹 Profession: Mulank + Bhagyank based career guidance
    if mode == "profession":
        lines: List[str] = ["Profession mapping (Mulank + Bhagyank):"]
        if isinstance(facts, dict):
            m = facts.get("mulank")
            b = facts.get("bhagyank")
            prof = facts.get("profession") or {}
            stars = prof.get("stars")
            rating_text = prof.get("rating_text")
            suggested = prof.get("professions") or []
            remark = prof.get("remark")

            if m is not None and b is not None:
                lines.append(f"Mulank = {m}, Bhagyank = {b}.")
            if stars or rating_text:
                lines.append(f"Star quality: {stars or ''} ({rating_text or ''}).")
            if suggested:
                lines.append("Suggested domains or fields: " + ", ".join(suggested) + ".")
            if remark:
                lines.append(f"Notes: {remark}.")

        lines.append(
            "\nWrite practical, grounded career guidance focused on natural tendencies, "
            "work style, and the kinds of environments that suit this pattern. "
            "Avoid specific job titles, guarantees, or predictions; keep it flexible and empowering."
        )
        return "\n".join(lines)

    # 🔹 Health mode
    if mode == "health":
        nums = sorted(set(used_digits or list(HEALTH_MEANINGS.keys())))
        lines = ["Health Meanings (used only):"]
        for k in nums:
            if k in HEALTH_MEANINGS:
                lines.append(f"{k}: {HEALTH_MEANINGS[k]}")
        lines.append(
            "\nGuidelines: supportive tone, no diagnosis/prescriptions, "
            "avoid letters/positions/codes; ~300–400 words; practical self-care."
        )
    else:
        # person / relationship / yearly / monthly / daily
        nums = sorted(set(used_digits or []))
        lines = ["Meanings (used only):"]
        for k in nums:
            if k in NUMBER_MEANINGS:
                lines.append(f"{k}: {NUMBER_MEANINGS[k]}")
        lines.append("\nF trait (style):")
        if used_f in F_TRAIT:
            lines.append(f"F={used_f}: {F_TRAIT[used_f]}")

    # 🔹 Special notes + polarity from facts / extra_context
    if isinstance(facts, dict):
        extra = facts.get("extra_context") or {}
        # Prefer extra_context.special_notes, fall back to top-level special_notes if user added it there
        sn = extra.get("special_notes") or facts.get("special_notes")
        if isinstance(sn, dict) and sn.get("present"):
            tag_list = ", ".join((sn.get("tags") or [])[:4])
            note = (sn.get("notes") or ["special patterns active"])[0]
            feature = sn.get("feature") or "this feature"
            lines.append(f"\nSpecial signals for {feature}: {tag_list}. Note: {note}")

        pol = extra.get("polarity")
        if isinstance(pol, dict) and pol.get("balance"):
            lines.append(f"\nPolarity tone: {pol.get('balance')}.")

    return "\n".join(lines)




def _system_for_mode(mode: str) -> str:
    """
    Central helper to select the correct SYSTEM prompt for each mode.
    Keeps the mapping in one place to avoid repeating if/else blocks.
    """
    mode = (mode or "person").lower()
    if mode == "relationship":
        return RELATIONSHIP_SYSTEM
    if mode == "health":
        return HEALTH_SYSTEM
    if mode == "health_daily":
        return HEALTH_DAILY_SYSTEM
    if mode == "health_monthly":
        return HEALTH_MONTHLY_SYSTEM
    if mode == "health_yearly":
        return HEALTH_YEARLY_SYSTEM
    if mode == "yearly":
        return YEARLY_SYSTEM
    if mode == "monthly":
        return MONTHLY_SYSTEM
    if mode == "daily":
        return DAILY_SYSTEM
    if mode == "profession":
        return PROFESSION_SYSTEM
    return PERSON_SYSTEM


#----------------------------------------------------
#     Summaries required for the AI Interpretation 
#----------------------------------------------------
def _summarize_person_report(full: dict) -> dict:
    """
    Extracts only the LLM-relevant subset from a single-person mystical_triangle_report.

    Final top-level shape (in insertion order → what the LLM sees):
      - dob
      - mulank_bhagyank
      - core
      - relations
      - upper_cluster
      - polarity  (compact)
      - reads_traits
      - active_codes
      - ...internal helper keys (core_numbers, triangle_traits, etc.) for grounding/anchors
    """

    def _g(d, *path, default=None):
        """Safe getter: _g(obj, 'a','b','c') -> obj['a']['b']['c'] or default."""
        cur = d
        for p in path:
            if not isinstance(cur, dict) or p not in cur:
                return default
            cur = cur[p]
        return cur

    # ---- core numbers from values (E,F,G,P) ----
    vals = full.get("values") or {}
    layer1 = vals.get("layer1") or {}
    third = vals.get("third_layer") or {}

    E = layer1.get("E")
    F = layer1.get("F")
    G = layer1.get("G")
    P = third.get("P")

    core_numbers = {"E": E, "F": F, "G": G, "P": P}

    # ---- mulank / bhagyank block (already computed in single_person_report) ----
    mulank_bhagyank = full.get("mulank_bhagyank")

    # ---- interpretations as you now expose them (EF_core, G, P_outcome, H1..H6, N/O/Q/R) ----
    core_block = (full.get("interpretations") or {}).get("core") or {}
    relations_block = (full.get("interpretations") or {}).get("relations") or {}
    upper_block = (full.get("interpretations") or {}).get("upper_cluster") or {}

    # minimal core interpretation for anchor hints (G/P only)
    core_interpretation = {
        "ef_note": _g(core_block, "EF_core", "note"),
        "g_meaning": _g(core_block, "G", "meaning"),
        "p_meaning": _g(core_block, "P_outcome", "meaning"),
    }

    # ---- polarity: compact form only (no heavy detail list) ----
    pol = full.get("polarity") or {}
    compact_polarity = None
    if pol:
        compact_polarity = {
            "positive": pol.get("positive"),
            "negative": pol.get("negative"),
            "neutral": pol.get("neutral"),
            "balance": pol.get("balance"),
        }

    # ---- reads_traits + active_codes from full report ----
    reads_traits = full.get("reads_traits") or {}
    active_codes = sorted(reads_traits.keys())

    # ---- triangle traits meanings (used for mock + light grounding) ----
    triangle_traits = {
        str(k): v.get("meaning") for k, v in (full.get("traits") or {}).items()
    }

    # ---- small reads summary for mock generator ----
    reads_summary = list((full.get("reads") or {}).items())[:6]

    # ---- build summary in the exact order we want the LLM to see ----
    summary: dict = {
        "dob": full.get("dob"),
        "mulank_bhagyank": mulank_bhagyank,
        "core": core_block,
        "relations": relations_block,
        "upper_cluster": upper_block,
        "polarity": compact_polarity,
        "reads_traits": reads_traits,
        "active_codes": active_codes,
        # internal helpers below (still useful for grounding + mock fallbacks)
        "core_numbers": core_numbers,
        "triangle_traits": triangle_traits,
        "core_notes": full.get("core_notes"),
        "reads_summary": reads_summary,
        # minimal “interpretation” bundle only for anchor hints (G/P)
        "interpretation": {
            "core": core_interpretation,
        },
        # keep elements if you later add them for person report
        "elements": full.get("elements", None),
    }

    # ---- used-only digits (for grounding meanings) ----
    used = [E, F, G, P]
    summary["_used_digits"] = sorted({int(x) for x in used if isinstance(x, int)})
    summary["_used_f"] = F

    # ---- extra_context for _compose_grounding_for (polarity + special notes) ----
    special_notes = full.get("special_notes")
    if compact_polarity or special_notes:
        summary["extra_context"] = {}
        if compact_polarity:
            summary["extra_context"]["polarity"] = compact_polarity
        if special_notes:
            summary["extra_context"]["special_notes"] = special_notes

    # ensure meanings for E/F/G/P exist so _anchor_hints/_validates work
    _ensure_anchor_meanings(summary)
    return summary


def _summarize_relationship_report(full: dict) -> dict:
    """
    Extract only LLM-relevant fields from relationship_triangle_report, including
    a compact 'interpretation' section (text notes only, no bulky refs).
    """
    def _g(d, *path, default=None):
        """Safe getter: _g(obj, 'a','b','c') -> obj['a']['b']['c'] or default."""
        cur = d
        for p in path:
            if not isinstance(cur, dict) or p not in cur:
                return default
            cur = cur[p]
        return cur

    # ---- pull compact interpretations (strings + tiny tuples) ----
    core_interpretation = {
        "ef_union_note": _g(full, "interpretations", "core", "Union EF (emotional–mental blend)", "note"),
        "g_meaning":     _g(full, "interpretations", "core", "Shared G (relationship center)", "meaning"),
        "p_meaning":     _g(full, "interpretations", "core", "Outcome P (direction of bond)", "meaning"),
    }

    relations_interpretation = {
        "hidden_potential": {
            "meaning": _g(full, "interpretations", "relations", "Hidden potential (H/I)", "meaning"),
            "values":  _g(full, "interpretations", "relations", "Hidden potential (H/I)", "values"),
        },
        "family_ties": {
            "meaning": _g(full, "interpretations", "relations", "Family ties (J/K)", "meaning"),
            "values":  _g(full, "interpretations", "relations", "Family ties (J/K)", "values"),
        },
        "outlook_growth": {
            "meaning": _g(full, "interpretations", "relations", "Outlook & growth (L/M)", "meaning"),
            "values":  _g(full, "interpretations", "relations", "Outlook & growth (L/M)", "values"),
        },
    }

    upper_cluster_interpretation = {
        "evolution_meaning": _g(full, "interpretations", "upper_cluster", "N,O,Q,R", "meaning"),
        "values":            _g(full, "interpretations", "upper_cluster", "N,O,Q,R", "values"),
    }

    summary = {
        "relationship": full.get("relationship"),
        "core_numbers": {
            "E": _g(full, "values", "layer1", "E"),
            "F": _g(full, "values", "layer1", "F"),
            "G": _g(full, "values", "layer1", "G"),
            "P": _g(full, "values", "third_layer", "P"),
        },
        "bond_assessment": full.get("bond_assessment"),
        "issue_flags": full.get("issue_flags"),
        "elements": {
            "dominant": _g(full, "elements", "dominant"),
            "counts": _g(full, "elements", "counts"),
        },
        "core_notes": full.get("core_notes"),
        "traits_summary": {
            str(k): v.get("meaning") for k, v in (full.get("traits") or {}).items()
        },
        # ---- newly added compact interpretation bundle ----
        "interpretation": {
            "core": core_interpretation,
            "relations": relations_interpretation,
            "upper_cluster": upper_cluster_interpretation,
        },
    }
        
    # ---- Used-only hints for minimal grounding (E,F,G,P) ----
    core = summary["core_numbers"]
    used = [core.get("E"), core.get("F"), core.get("G"), core.get("P")]
    summary["_used_digits"] = sorted({int(x) for x in used if isinstance(x, int)})
    summary["_used_f"] = core.get("F")
    _ensure_anchor_meanings(summary)

    # NEW: include polarity + special notes if present
    pol = full.get("polarity")
    notes = full.get("special_notes")
    if pol or notes:
        summary["extra_context"] = {}
        if pol:
            summary["extra_context"]["polarity"] = pol
        if notes:
            summary["extra_context"]["special_notes"] = notes

    # --- tiny human-readable blurbs to nudge the model ---
    bond = summary.get("bond_assessment") or {}
    notes = [n for n in (bond.get("notes") or []) if n]
    summary["bond_summary"] = (
        f"Bond: {bond.get('bucket','Unknown')} (score={bond.get('score')}); "
        f"has_27_link={bool(bond.get('has_27_link'))}; lucky_any_9={bool(bond.get('lucky_any_9'))}."
        + (f" Notes: {', '.join(notes)}." if notes else "")
    )

    issues = summary.get("issue_flags") or {}
    issue_keys = list(issues.keys())
    summary["issue_summary"] = ("Issue areas: " + ", ".join(issue_keys)) if issue_keys else "No critical issue flags."

    ele = summary.get("elements") or {}
    counts = ele.get("counts") or {}
    summary["elements_summary"] = f"Dominant element: {ele.get('dominant')}; counts={counts}."

    return summary




def _summarize_yearly_report(full: dict) -> dict:
    """
    Extract the minimal, LLM-relevant info from yearly_triangle_report (DOB ⊕ Year).
    Focuses on combined panel only.
    """
    combo = (full.get("panels") or {}).get("combined") or {}
    vals = combo.get("values") or {}
    layer1 = vals.get("layer1") or {}
    third = vals.get("third_layer") or {}

    E = layer1.get("E")
    F = layer1.get("F")
    G = layer1.get("G")
    P = third.get("P")

    meanings = (full.get("summary") or {}).get("meanings") or {}
    f_trait = (combo.get("core_notes") or {}).get("F_trait")

    summary = {
        "dob": full.get("dob"),
        "year": full.get("year"),
        "core_numbers": {"E": E, "F": F, "G": G, "P": P},
        "meanings": meanings,
        "F_trait": f_trait,
        "traits_summary": {
            str(k): v.get("meaning") for k, v in (full.get("traits") or {}).items()
        },
        "summary": full.get("summary"),
    }

    # Used-only hints for minimal grounding:
    used = [E, F, G, P]
    summary["_used_digits"] = sorted({int(x) for x in used if isinstance(x, int)})
    summary["_used_f"] = F
    # NEW: include polarity + special notes if present
    pol = full.get("polarity")
    notes = full.get("special_notes")
    if pol or notes:
        summary["extra_context"] = {}
        if pol:
            summary["extra_context"]["polarity"] = pol
        if notes:
            summary["extra_context"]["special_notes"] = notes

    _ensure_anchor_meanings(summary)
    return summary



# -------- Monthly summarizer (one target month) --------
def _summarize_monthly_report(full: dict, month: int) -> dict:
    """
    Extract minimal, LLM-relevant info for ONE month from monthly_prediction_report.
    Uses the COMBINED triangle's month slot (E/F/H/I/J/K/N/O/Q/R).
    """
    month_key = str(int(month))
    month_row = (full.get("months") or {}).get(month_key) or {}
    combo = (full.get("panels") or {}).get("combined") or {}
    vals = combo.get("values", {}) or {}
    layer1 = vals.get("layer1") or {}
    third = vals.get("third_layer") or {}

    E = layer1.get("E"); F = layer1.get("F"); G = layer1.get("G"); P = third.get("P")
    meanings = (full.get("summary") or {}).get("meanings") or {}
    # Prefer core_notes for F_trait if present
    f_trait = (combo.get("core_notes") or {}).get("F_trait") or \
              ((combo.get("interpretations") or {}).get("core") or {}).get("F_trait")

    summary = {
        "dob": full.get("dob"),
        "year": full.get("year"),
        "month": int(month),
        "month_slot": month_row.get("position"),
        "month_value": month_row.get("value"),
        "month_meaning": month_row.get("meaning"),
        "month_traits": month_row.get("traits"),
        "core_numbers": {"E": E, "F": F, "G": G, "P": P},
        "meanings": meanings,   # includes E/F/G/P meanings
        "F_trait": f_trait,
    }

    # Used-only hints for minimal grounding (E,F,G,P plus the month value if numeric)
    used = [E, F, G, P, month_row.get("value")]
    summary["_used_digits"] = sorted({int(x) for x in used if isinstance(x, int)})
    summary["_used_f"] = F
    # NEW: include polarity + special notes if present
    pol = full.get("polarity")
    notes = full.get("special_notes")
    if pol or notes:
        summary["extra_context"] = {}
        if pol:
            summary["extra_context"]["polarity"] = pol
        if notes:
            summary["extra_context"]["special_notes"] = notes

    _ensure_anchor_meanings(summary)
    return summary

def _summarize_daily_report(full: dict) -> dict:
    """
    Extract minimal, LLM-relevant info from daily_triangle_report (DOB ⊕ Today).
    Focuses on combined panel only.
    """
    combo = (full.get("panels") or {}).get("combined") or {}
    vals = combo.get("values") or {}
    layer1 = vals.get("layer1") or {}
    third = vals.get("third_layer") or {}

    E = layer1.get("E")
    F = layer1.get("F")
    G = layer1.get("G")
    P = third.get("P")

    # Daily payloads typically don't include a top-level "summary";
    # keep this safe (it may be empty, that's fine).
    meanings = (full.get("summary") or {}).get("meanings") or {}

    # Source F_trait from combined core_notes
    f_trait = (combo.get("core_notes") or {}).get("F_trait")

    payload = {
        "dob": full.get("dob"),
        "today": full.get("today"),
        "core_numbers": {"E": E, "F": F, "G": G, "P": P},
        "meanings": meanings,
        "F_trait": f_trait,
        "traits_summary": {
            str(k): v.get("meaning") for k, v in (full.get("traits") or {}).items()
        },
        "time_slots": combo.get("time_slots"),
    }

    # Used-only hints for minimal grounding (E,F,G,P)
    used = [E, F, G, P]
    payload["_used_digits"] = sorted({int(x) for x in used if isinstance(x, int)})
    payload["_used_f"] = F

    # NEW: include polarity + special notes if present (from combined panel)
    pol = combo.get("polarity")
    notes = combo.get("special_notes")
    if pol or notes:
        payload["extra_context"] = {}
        if pol:
            payload["extra_context"]["polarity"] = pol
        if notes:
            payload["extra_context"]["special_notes"] = notes

    _ensure_anchor_meanings(payload)
    return payload




def _summarize_health_report(full: dict) -> dict:
    def _g(d, *path, default=None):
        cur = d
        for p in path:
            if not isinstance(cur, dict) or p not in cur:
                return default
            cur = cur[p]
        return cur

    # Core numbers
    E = _g(full, "values", "layer1", "E")
    F = _g(full, "values", "layer1", "F")
    G = _g(full, "values", "layer1", "G")
    P = _g(full, "values", "third_layer", "P")

    # Zones ...
    N, O = _g(full, "values", "third_layer", "N"), _g(full, "values", "third_layer", "O")
    H, I, J = _g(full, "values", "second_layer", "H"), _g(full, "values", "second_layer", "I"), _g(full, "values", "second_layer", "J")
    K, L, M = _g(full, "values", "second_layer", "K"), _g(full, "values", "second_layer", "L"), _g(full, "values", "second_layer", "M")
    Q, R = _g(full, "values", "third_layer", "Q"), _g(full, "values", "third_layer", "R")

    def _only_used_health_meanings(nums: list[int]) -> dict:
        out = {}
        for n in nums:
            if isinstance(n, int) and n in HEALTH_MEANINGS and n not in out:
                out[n] = HEALTH_MEANINGS[n]
        return out

    used_for_meanings = [G, P, N, O, H, I, J, K, L, M, Q, R]
    used_health_meanings = _only_used_health_meanings([n for n in used_for_meanings if isinstance(n, int)])

    # 👉 Build a small meanings dict so _anchor_hints/_validates can find G/P phrases
    meanings = {}
    if isinstance(G, int) and G in used_health_meanings:
        meanings["G"] = used_health_meanings[G]
    if isinstance(P, int) and P in used_health_meanings:
        meanings["P"] = used_health_meanings[P]

    # Elements/flags/neoplasm/abdomen/ef_note as you have ...
    elem = full.get("elements")
    elem_summary = None
    if isinstance(elem, dict):
        meta = elem.get("_summary")
        if isinstance(meta, dict):
            elem_summary = {
                "dominant": meta.get("dominant"),
                "deficient": meta.get("deficient"),
                "counts": meta.get("counts"),
            }

    organ_flags_keys = list((full.get("organ_flags") or {}).keys())

    neo = full.get("neoplasm_probability") or {}
    reasons = neo.get("reasons") or []
    if isinstance(reasons, list):
        reasons = reasons[:2]
    neoplasm = {"percent": neo.get("percent"), "reasons": reasons}

    ab = full.get("abdomen") or {}
    abdomen = {"risk": bool(ab.get("risk")), "notes": (ab.get("notes") or [])[:1]}

    ef_note = _g(full, "sections", "core_health", "Balance (E+F)", "note")

    summary = {
        "mode": "health",
        "dob": full.get("dob"),
        "core": {
            "G": G,
            "P": P,
            "EF": int(f"{E}{F}") if isinstance(E, int) and isinstance(F, int) else None,
            "g_meaning": HEALTH_MEANINGS.get(G),
            "p_meaning": HEALTH_MEANINGS.get(P),
            "ef_note": ef_note,
        },
        "zones": {
            "mental": [N, O],
            "physical": [H, I, J],
            "emotional": [K, L, M],
            "recovery": [Q, R],
        },
        "health_meanings": used_health_meanings,
        "elements": elem_summary,
        "flags": {"organ": organ_flags_keys, "abdomen_risk": abdomen["risk"]},
        "neoplasm": neoplasm,
        "notes": {"breast_note": _g(full, "core_notes", "breast_note")},
        "meanings": meanings,                     # 👉 add this
    }

    used_all = [E, F, G, P, N, O, H, I, J, K, L, M, Q, R]
    summary["_used_digits"] = sorted({int(x) for x in used_all if isinstance(x, int)})
    summary["_used_f"] = F
    pol = full.get("polarity")
    notes = full.get("special_notes")
    if pol or notes:
        summary["extra_context"] = {}
        if pol:
            summary["extra_context"]["polarity"] = pol
        if notes:
            summary["extra_context"]["special_notes"] = notes
    _ensure_anchor_meanings(summary)  # safe no-op if already present
    return summary


def _summarize_profession_report(dob: str) -> dict:
    """
    Build a compact, LLM-ready view of Mulank/Bhagyank-based profession mapping.
    """
    base = profession_report(dob)  # deterministic JSON from numerology.features.profession_report

    m = base.get("mulank")
    b = base.get("bhagyank")
    prof = base.get("profession") or {}

    summary = {
        "dob": base.get("dob", dob),
        "mulank": m,
        "bhagyank": b,
        "profession": {
            "pair_key": prof.get("pair_key"),
            "stars": prof.get("stars"),
            "rating_text": prof.get("rating_text"),
            "professions": list(prof.get("professions") or []),
            "remark": prof.get("remark"),
        },
    }

    used = [m, b]
    summary["_used_digits"] = sorted({int(x) for x in used if isinstance(x, int)})
    summary["_used_f"] = None  # no F-style anchor for profession
    return summary


# ---------------------------- generators ----------------------------
def _mock_generate(grounding: dict, facts: dict) -> dict:
    dob = facts.get("dob", "Unknown")
    core = facts.get("core_numbers", {})
    E, F, G, P = core.get("E"), core.get("F"), core.get("G"), core.get("P")
    traits = facts.get("triangle_traits", {})

    def meaning_of(n):
        m = traits.get(str(n))
        return m.split(";")[0] if m else ""

    meaning_E = meaning_of(E)
    meaning_F = meaning_of(F)
    meaning_G = meaning_of(G)
    meaning_P = meaning_of(P)

    paragraph = (
        f"For DOB {dob}, the core triangle reveals E={E}, F={F}, G={G}, and P={P}. "
        f"E reflects {meaning_E.lower()}; F shows {meaning_F.lower()}. "
        f"G defines the foundation — {meaning_G.lower()}, while P describes the long-term path as {meaning_P.lower()}. "
        "Overall, this chart emphasizes how inner drive (F) and emotional tone (E) combine to shape your outward style (G) and life trajectory (P). "
        "Stay mindful of balance and consistency to make the most of these signatures."
    ).strip()

    return {
        "interpretation": paragraph,   # ← key matches AIInterpretation
        "created_at": datetime.utcnow().isoformat(),
        "meta": {"provider": "mock","mode": "yearly" ,"used_core": core},
    }

    
def _mock_generate_relationship(grounding: dict, facts: dict) -> dict:
    rel = facts.get("relationship", "Unknown + Unknown")
    core = facts.get("core_numbers", {})
    bond = facts.get("bond_assessment", {})
    issues = facts.get("issue_flags", {})
    elements = facts.get("elements", {})
    traits = facts.get("traits_summary", {})

    E, F, G, P = core.get("E"), core.get("F"), core.get("G"), core.get("P")
    bucket = bond.get("bucket", "Fair")
    dominant = elements.get("dominant", "—")

    lucky = bond.get("lucky_any_9")
    has_27 = bond.get("has_27_link")
    qr_linked = bond.get("qr_linked")

    def meaning_of(n):
        m = traits.get(str(n))
        return m.split(";")[0] if m else ""

    meaning_E = meaning_of(E)
    meaning_F = meaning_of(F)
    meaning_G = meaning_of(G)
    meaning_P = meaning_of(P)

    tone_phrases = {
        "Highest Possibility": "an exceptionally compatible match with profound understanding",
        "Stronger": "a strong and promising connection",
        "Strong": "a balanced and mutually supportive bond",
        "Fair": "a fair connection that may require conscious effort",
    }
    tone = tone_phrases.get(bucket, "a meaningful relationship")

    issue_bits = []
    if "never_separate" in issues:       issue_bits.append("a very stable, enduring bond")
    if "relationship_issue" in issues:   issue_bits.append("some relationship challenges to watch")
    if "marriage_issue" in issues:       issue_bits.append("possible marriage-compatibility concerns")
    if "downfall" in issues:             issue_bits.append("risk of misunderstandings or setbacks")
    issue_phrase = ", ".join(issue_bits) if issue_bits else "overall harmony"

    extras = []
    if lucky:   extras.append("Lucky 9 vibrations support growth.")
    if has_27:  extras.append("A 27/72 link strengthens karmic bonding.")
    if qr_linked: extras.append("Q–R mirroring suggests occasional complications.")
    extras_text = (" " + " ".join(extras)) if extras else ""

    paragraph = (
        f"Relationship: {rel}. The combined core numbers (E={E}, F={F}, G={G}, P={P}) indicate {tone}. "
        f"E reflects {meaning_E.lower()}, F shows {meaning_F.lower()}, while G forms the shared foundation — {meaning_G.lower()}. "
        f"Long-term direction (P) aligns with {meaning_P.lower()}. "
        f"Bond assessment places this pair as *{bucket}*, with {issue_phrase}. "
        f"The shared energy leans toward the {dominant.capitalize()} element, shaping the emotional tone and approach to life.{extras_text} "
        "Overall, the connection benefits from empathy, clear communication, and mutual respect."
    ).strip()

    return {
        "interpretation": paragraph,  # ← key matches AIInterpretation
        "created_at": datetime.utcnow().isoformat(),
        "meta": {
            "provider": "mock",
            "bucket": bucket,
            "dominant_element": dominant,
            "issues_detected": list(issues.keys()),
        },
    }


def _mock_generate_yearly(grounding: dict, facts: dict) -> dict:
    """
    Deterministic, human-friendly fallback for yearly (DOB ⊕ Year) interpretation.
    Varies slightly with G, P, and F_trait so it's repeatable but personal.
    """
    dob = facts.get("dob", "Unknown")
    year = facts.get("year", "Unknown")
    core = facts.get("core_numbers", {})
    E, F, G, P = core.get("E"), core.get("F"), core.get("G"), core.get("P")
    meanings = facts.get("meanings", {}) or {}
    f_trait = facts.get("F_trait", "")

    g_mean = (meanings.get("G") or "").split(";")[0].lower()
    p_mean = (meanings.get("P") or "").split(";")[0].lower()
    e_mean = (meanings.get("E") or "").split(";")[0].lower()
    f_mean = (meanings.get("F") or "").split(";")[0].lower()

    # use parts of dob/year to seed slight variation
    seed = int(str(G or 0) + str(P or 0) + str(E or 0) + str(F or 0)) % 100
    random.seed(seed)
    tone = random.choice(
        [
            "a year of meaningful progress",
            "a cycle of renewal and clarity",
            "a phase for steady growth",
            "a period of deeper self-mastery",
            "a balanced year of integration",
        ]
    )

    paragraph = (
        f"For {year}, your combined pattern (DOB ⊕ Year) highlights {tone}. "
        f"G={G} reflects {g_mean}, while P={P} points toward {p_mean}. "
        f"E={E} adds a sense of {e_mean}, and F={F} emphasizes {f_mean}. "
        f"Together these energies awaken your {f_trait.lower()} side, helping you align "
        f"personal goals with inner stability. Stay grounded, plan patiently, "
        f"and let progress unfold naturally throughout the year."
    ).strip()

    return {
        "interpretation": paragraph,
        "created_at": datetime.utcnow().isoformat(),
        "meta": {
            "provider": "mock",
            "used_core": {"E": E, "F": F, "G": G, "P": P},
            "dob": dob,
            "year": year,
        },
    }

def _mock_generate_monthly(grounding: dict, facts: dict) -> dict:
    """
    Deterministic fallback for a single month interpretation.
    Mentions the month, its slot/value/meaning, and ties back to core themes.
    """
    from calendar import month_name

    year = facts.get("year", "Unknown")
    m = int(facts.get("month") or 1)
    mname = month_name[m]
    slot = facts.get("month_slot", "—")
    val = facts.get("month_value")
    m_mean = (facts.get("month_meaning") or "").split(";")[0].lower() if facts.get("month_meaning") else ""

    core = facts.get("core_numbers", {})
    E, F, G, P = core.get("E"), core.get("F"), core.get("G"), core.get("P")
    meanings = facts.get("meanings", {}) or {}
    g_mean = (meanings.get("G") or "").split(";")[0].lower()
    p_mean = (meanings.get("P") or "").split(";")[0].lower()
    f_trait = (facts.get("F_trait") or "").lower()

    paragraph = (
        f"In {mname} {year}, your month energy keys into the {slot} position with a value of {val}, "
        f"which leans toward {m_mean}. Against the backdrop of the year’s pattern, G={G} points to {g_mean} "
        f"while P={P} guides the direction toward {p_mean}. This month benefits from the steady balance of E={E} and F={F}, "
        f"and expressing your natural {f_trait} helps you stay grounded. Keep plans realistic, protect your attention, "
        f"and let small, consistent actions carry you—momentum matters more than speed."
    ).strip()

    return {
        "interpretation": paragraph,
        "created_at": datetime.utcnow().isoformat(),
        "meta": {
            "provider": "mock",
            "mode": "monthly",
            "month": m,
            "slot": slot,
            "value": val,
        },
    }


def _mock_generate_daily(grounding: dict, facts: dict) -> dict:
    """
    Deterministic fallback for daily interpretation (DOB ⊕ Today).
    Mirrors yearly/monthly tone but shorter and day-focused.
    """
    dob = facts.get("dob", "Unknown")
    today = facts.get("today", "")
    core = facts.get("core_numbers", {})
    E, F, G, P = core.get("E"), core.get("F"), core.get("G"), core.get("P")

    meanings = facts.get("meanings", {}) or {}
    e_mean = (meanings.get("E") or "").split(";")[0].lower()
    f_mean = (meanings.get("F") or "").split(";")[0].lower()
    g_mean = (meanings.get("G") or "").split(";")[0].lower()
    p_mean = (meanings.get("P") or "").split(";")[0].lower()
    f_trait = (facts.get("F_trait") or "").lower()

    paragraph = (
        f"For {today}, your combined daily triangle (DOB ⊕ Today) highlights a mix of E={E}, F={F}, G={G}, and P={P}. "
        f"E brings {e_mean}, while F adds {f_mean}, creating a tone of {f_trait}. "
        f"G defines the focus for the day — {g_mean}, and P signals outcomes around {p_mean}. "
        "This pattern encourages balance between planning and flow: act steadily in the morning, "
        "keep flexibility through midday, and end with reflection or closure. "
        "Stay kind, attentive, and grounded—the day favors awareness over speed."
    ).strip()

    return {
        "interpretation": paragraph,
        "created_at": datetime.utcnow().isoformat(),
        "meta": {
            "provider": "mock",
            "mode": "daily",
            "used_core": {"E": E, "F": F, "G": G, "P": P},
        },
    }


def _mock_generate_health(grounding: dict, facts: dict) -> dict:
    dob = facts.get("dob", "Unknown")
    core = facts.get("core_numbers", {})
    E, F, G, P = core.get("E"), core.get("F"), core.get("G"), core.get("P")
    hm = facts.get("health_meanings", {})

    g_mean = (hm.get(G) or "").lower()
    p_mean = (hm.get(P) or "").lower()

    zones = facts.get("zones") or facts.get("interpretation", {}).get("zones", {})
    hints = []
    for key in ("mental", "physical", "emotional"):
        vals = zones.get(key, [])
        # Accept list or dict-with-values
        if isinstance(vals, dict):
            vals = vals.get("values") or vals.get("digits") or []
        for v in (vals if isinstance(vals, (list, tuple)) else []):
            if isinstance(v, int) and hm.get(v):
                hints.append(hm[v].split(";")[0].lower())
    hint_txt = ""
    if hints:
        uniq = []
        for h in hints:
            if h and h not in uniq:
                uniq.append(h)
        if uniq:
            hint_txt = " You may be a bit sensitive around " + ", ".join(uniq[:2]) + "."

    paragraph = (
        f"For DOB {dob}, your health triangle shows a steady base with G={G} pointing to {g_mean}. "
        f"The balance of E+F ({E}{F}) reflects how mind and body coordinate, while P={P} leans your healing path toward {p_mean}. "
        f"Keep routines simple: regular sleep, gentle movement, and digestion-friendly meals.{hint_txt} "
        f"Pace busy periods, notice early signals, and give yourself short recovery windows so energy can rebound."
    ).strip()

    return {"interpretation": paragraph}


def _mock_generate_profession(grounding: dict | str, facts: dict) -> dict:
    """
    Deterministic, human-friendly fallback for profession / career guidance.
    Uses Mulank + Bhagyank profession mapping only.
    """
    dob = facts.get("dob", "Unknown")
    m = facts.get("mulank")
    b = facts.get("bhagyank")
    prof = facts.get("profession") or {}
    stars = prof.get("stars")
    rating_text = prof.get("rating_text") or ""
    suggested = prof.get("professions") or []
    remark = prof.get("remark") or ""

    fields_txt = ", ".join(suggested) if suggested else "general roles that allow learning and growth"

    # simple, deterministic tone seed
    seed = int(f"{m or 0}{b or 0}") % 100
    random.seed(seed)
    tone = random.choice(
        [
            "steady, patient progress",
            "creative, people-focused work",
            "structured, responsibility-driven roles",
            "flexible, exploratory paths",
        ]
    )

    paragraph = (
        f"For DOB {dob}, your Mulank–Bhagyank blend suggests a natural pull toward {fields_txt}. "
        f"The overall quality of this combination leans toward {rating_text or 'balanced potential'}, "
        f"so you tend to grow when you stay consistent and choose environments that respect your pace and values. "
        f"This pattern is well suited to {tone}, where you can bring both reliability and personal insight to what you do. "
        f"{remark or 'Over time, you are likely to thrive when you treat your career as a space for learning, contribution, and steady self-improvement.'}"
    ).strip()

    return {
        "interpretation": paragraph,
        "created_at": datetime.utcnow().isoformat(),
        "meta": {
            "provider": "mock",
            "mode": "profession",
            "mulank": m,
            "bhagyank": b,
        },
    }




def _openai_generate(grounding: str, facts: Dict[str, Any], mode: str = "person") -> Dict[str, Any]:
    """
    Ask OpenAI for a *single* plain-language paragraph under the 'interpretation' key.
    """
    from openai import OpenAI
    import json

    client = OpenAI(api_key=(settings.openai_api_key.get_secret_value()
                             if hasattr(settings.openai_api_key, "get_secret_value")
                             else settings.openai_api_key))

    system = _system_for_mode(mode)

    lengths = {
        "person": "300–400 words",
        "relationship": "300–400 words",
        "yearly": "300–400 words",
        "monthly": "200–300 words",
        "daily": "180–250 words",
        "health": "300–400 words",
        "health_daily": "180–250 words",
        "health_monthly": "200–300 words",
        "health_yearly": "300–400 words",
        "profession": "130–190 words",
    }
    target = lengths.get(mode, "300–400 words")

    user_msg = (
        "Grounding (meanings, traits):\n"
        f"{grounding}\n\n"
        "Facts (DOB and computed values):\n"
        f"{facts}\n\n"
        "Write ONE friendly paragraph in everyday human language (no theory or jargon). "
        "Do not mention letters, codes, triangle layers, or numbers. "
        f"Keep it ~{target}. "
        "Return JSON with a single key 'interpretation'."
    )

    resp = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.3,
        max_tokens=settings.max_tokens,
        response_format={"type": "json_object"},
        timeout=settings.timeout_seconds,
    )
    text = resp.choices[0].message.content
    return json.loads(text)


def _ollama_generate(grounding: str, facts: Dict[str, Any], mode: str = "person") -> Dict[str, Any]:
    import json, requests

    base = settings.ollama_base_url.rstrip("/")
    model = settings.ollama_model

    # Select the correct system prompt
    system = _system_for_mode(mode)

    # Pick target length band per mode
    lengths = {
        "person": "300–400 words",
        "relationship": "300–400 words",
        "yearly": "300–400 words",
        "monthly": "200–300 words",
        "daily": "180–250 words",
        "health": "300–400 words",
        "health_daily": "180–250 words",
        "health_monthly": "200–300 words",
        "health_yearly": "300–400 words",
        "profession": "130–190 words",
    }
    target = lengths.get(mode, "300–400 words")

    # Compose the unified message for the model
    user_msg = (
        f"{system}\n\n"
        "Grounding (meanings, traits):\n"
        f"{grounding}\n\n"
        "Facts (DOB and computed values):\n"
        f"{facts}\n\n"
        "Write ONE friendly paragraph in everyday human language (no theory or jargon). "
        "Do not mention letters, codes, triangle layers, or numbers. "
        f"Keep it ~{target}. "
        "Return JSON with a single key 'interpretation'."
    )

    # Send to Ollama API — non-streaming model response + conservative options
    r = requests.post(
        f"{base}/api/generate",
        json={
            "model": model,
            "prompt": user_msg,
            "format": "json",
            "stream": False,            # ← important: disable model-side streaming
            "options": {
                "num_predict": 256,     # safe decode size for 1 JSON paragraph
                "num_ctx": 2048,        # conservative context on Windows
                "temperature": 0.3
            }
        },
        timeout=(settings.timeout_connect_seconds, settings.timeout_seconds),
        stream=True,  # keep HTTP streaming; we'll read the single JSON object below
    )
    r.raise_for_status()

    # Collect output (works for one-line JSON too)
    data = ""
    for line in r.iter_lines():
        if not line:
            continue
        obj = json.loads(line)
        if "response" in obj:
            data += obj["response"]
        if obj.get("done"):
            break

    return json.loads(data)





# ---------------------------- entry point ----------------------------

def generate_interpretation(dob: str) -> AIInterpretation:
    report = mystical_triangle_report(dob)
    facts = _summarize_person_report(report)  # ← facts first
    grounding = _compose_grounding_for(       # ← grounding after facts
        "person",
        used_digits=facts.get("_used_digits"),
        used_f=facts.get("_used_f"),
        facts=facts,
    )

    provider = (settings.llm_provider or "").lower()
    logger.info("AI provider configured: %s", provider or "mock")

    try:
        if provider == "openai" and settings.openai_api_key:
            raw = _openai_generate(grounding, facts, mode="person")
            _LAST_USED.update({"provider": "openai", "model": settings.openai_model})
            logger.info("AI provider used: openai, model=%s", settings.openai_model)
        elif provider == "ollama":
            raw = _ollama_generate(grounding, facts, mode="person")
            _LAST_USED.update({"provider": "ollama", "model": "llama3"})
            logger.info("AI provider used: ollama, model=llama3")
        else:
            raw = _mock_generate(grounding, facts)
            _LAST_USED.update({"provider": "mock", "model": None})
            logger.info("AI provider used: mock")
            return AIInterpretation(**raw)
        cand = AIInterpretation(**raw)
        clean = _finalize(cand.interpretation, facts, "person")
        if not _validates(clean, facts, "person"):
            raise ValueError("AI narrative failed validation; falling back to mock.")
        return AIInterpretation(interpretation=clean)

    except (ValidationError, Exception):
        logger.exception("Provider '%s' failed; falling back to mock.", provider or "mock")
        raw = _mock_generate(grounding, facts)
        _LAST_USED.update({"provider": "mock", "model": None})
        return AIInterpretation(**raw)



def generate_relationship_interpretation(dob_left: str, dob_right: str) -> AIInterpretation:
    """
    Build the deterministic combined triangle (relationship report),
    then ask the chosen LLM for a plain-language paragraph.
    """
    report = relationship_triangle_report(dob_left, dob_right)
    facts = _summarize_relationship_report(report)
    grounding = _compose_grounding_for(
        "relationship",
        used_digits=facts.get("_used_digits"),
        used_f=facts.get("_used_f"),
        facts=facts,
    )

    provider = (settings.llm_provider or "").lower()
    logger.info("AI provider configured: %s", provider or "mock")

    try:
        if provider == "openai" and settings.openai_api_key:
            raw = _openai_generate(grounding, facts, mode="relationship")
            _LAST_USED.update({"provider": "openai", "model": settings.openai_model})
        elif provider == "ollama":
            raw = _ollama_generate(grounding, facts, mode="relationship")
            _LAST_USED.update({"provider": "ollama", "model": settings.ollama_model})
        else:
            raw = _mock_generate_relationship(grounding, facts)
            _LAST_USED.update({"provider": "mock", "model": None})
            return AIInterpretation(**raw)
        cand = AIInterpretation(**raw)
        clean = _finalize(cand.interpretation, facts, "relationship")
        if not _validates(clean, facts, "relationship"):
            raise ValueError("AI narrative failed validation; falling back to mock.")
        return AIInterpretation(interpretation=clean)


    except Exception:
        logger.exception("Validation failed; using mock fallback.")
        raw = _mock_generate_relationship(grounding, facts)
        _LAST_USED.update({"provider": "mock", "model": None})
        return AIInterpretation(**raw)

    
def generate_yearly_interpretation(dob: str, year: int) -> AIInterpretation:
    """
    Build the deterministic combined yearly triangle (DOB ⊕ Year),
    summarize key facts, and ask the AI for a one-paragraph interpretation.
    """
    report = yearly_triangle_report(dob, year)
    facts = _summarize_yearly_report(report)
    grounding = _compose_grounding_for(
        "person",  # same base as personal
        used_digits=facts.get("_used_digits"),
        used_f=facts.get("_used_f"),
        facts=facts,
    )

    provider = (settings.llm_provider or "").lower()
    logger.info("AI provider configured: %s", provider or "mock")

    try:
        if provider == "openai" and settings.openai_api_key:
            raw = _openai_generate(grounding, facts, mode="yearly")
            _LAST_USED.update({"provider": "openai", "model": settings.openai_model})
        elif provider == "ollama":
            raw = _ollama_generate(grounding, facts, mode="yearly")
            _LAST_USED.update({"provider": "ollama", "model": settings.ollama_model})
        else:
            raw = _mock_generate_yearly(grounding, facts)
            _LAST_USED.update({"provider": "mock", "model": None})
            return AIInterpretation(**raw)
        
        cand = AIInterpretation(**raw)
        clean = _finalize(cand.interpretation, facts, "yearly")
        if not _validates(clean, facts, "yearly"):
            raise ValueError("AI narrative failed validation; falling back to mock.")
        return AIInterpretation(interpretation=clean)

    except Exception:
        logger.exception("Yearly AI generation failed; using mock fallback.")
        raw = _mock_generate_yearly(grounding, facts)
        _LAST_USED.update({"provider": "mock", "model": None})
        return AIInterpretation(**raw)


def generate_monthly_interpretation(dob: str, year: int, month: int) -> AIInterpretation:
    """
    Build the deterministic monthly report (DOB ⊕ Month-Year driver),
    summarize ONE target month, and ask the AI for a short interpretation.
    """
    monthly = monthly_prediction_report(dob, year)
    facts = _summarize_monthly_report(monthly, month)
    grounding = _compose_grounding_for(
        "person",
        used_digits=facts.get("_used_digits"),
        used_f=facts.get("_used_f"),
        facts=facts,
    )

    provider = (settings.llm_provider or "").lower()
    logger.info("AI provider configured: %s", provider or "mock")

    try:
        if provider == "openai" and settings.openai_api_key:
            raw = _openai_generate(grounding, facts, mode="monthly")
            _LAST_USED.update({"provider": "openai", "model": settings.openai_model})
        elif provider == "ollama":
            raw = _ollama_generate(grounding, facts, mode="monthly")
            _LAST_USED.update({"provider": "ollama", "model": settings.ollama_model})
        else:
            raw = _mock_generate_monthly(grounding, facts)
            _LAST_USED.update({"provider": "mock", "model": None})
            return AIInterpretation(**raw)
        
        cand = AIInterpretation(**raw)
        clean = _finalize(cand.interpretation, facts, "monthly")
        if not _validates(clean, facts, "monthly"):
            raise ValueError("AI narrative failed validation; falling back to mock.")
        return AIInterpretation(interpretation=clean)

    except Exception:
        logger.exception("Monthly AI generation failed; using mock fallback.")
        raw = _mock_generate_monthly(grounding, facts)
        _LAST_USED.update({"provider": "mock", "model": None})
        return AIInterpretation(**raw)

    
    
def generate_daily_interpretation(dob: str, day: Optional[str] = None) -> AIInterpretation:
    """
    Build the deterministic daily report (DOB ⊕ [Today or a specific date]),
    summarize combined facts, and ask the AI for a one-paragraph interpretation.
    """
    report = daily_triangle_report(dob, right_day=day)
    facts = _summarize_daily_report(report)
    grounding = _compose_grounding_for(
        "person",
        used_digits=facts.get("_used_digits"),
        used_f=facts.get("_used_f"),
        facts=facts,
    )

    provider = (settings.llm_provider or "").lower()
    logger.info("AI provider configured: %s", provider or "mock")

    try:
        if provider == "openai" and settings.openai_api_key:
            raw = _openai_generate(grounding, facts, mode="daily")
            _LAST_USED.update({"provider": "openai", "model": settings.openai_model})
        elif provider == "ollama":
            raw = _ollama_generate(grounding, facts, mode="daily")
            _LAST_USED.update({"provider": "ollama", "model": settings.ollama_model})
        else:
            raw = _mock_generate_daily(grounding, facts)
            _LAST_USED.update({"provider": "mock", "model": None})
            return AIInterpretation(**raw)
        
        cand = AIInterpretation(**raw)
        clean = _finalize(cand.interpretation, facts, "daily")
        if not _validates(clean, facts, "daily"):
            raise ValueError("AI narrative failed validation; falling back to mock.")
        return AIInterpretation(interpretation=clean)

    except Exception:
        logger.exception("Daily AI generation failed; using mock fallback.")
        raw = _mock_generate_daily(grounding, facts)
        _LAST_USED.update({"provider": "mock", "model": None})
        return AIInterpretation(**raw)


    
    
def generate_health_interpretation(dob: str, gender: Optional[str] = None) -> AIInterpretation:
    """
    Build the deterministic health triangle (numerology.features.health),
    then ask the chosen LLM for a plain paragraph (or deterministic mock).
    """
    report = health_triangle_report(dob, gender=gender)
    facts = _summarize_health_report(report)
    grounding = _compose_grounding_for("health", used_digits=facts.get("_used_digits"),facts=facts,)

    provider = (settings.llm_provider or "").lower()
    logger.info("AI provider configured: %s", provider or "mock")

    try:
        if provider == "openai" and settings.openai_api_key:
            raw = _openai_generate(grounding, facts, mode="health")
            _LAST_USED.update({"provider": "openai", "model": settings.openai_model})
        elif provider == "ollama":
            raw = _ollama_generate(grounding, facts, mode="health")
            _LAST_USED.update({"provider": "ollama", "model": settings.ollama_model})
        else:
            raw = _mock_generate_health(grounding, facts)
            _LAST_USED.update({"provider": "mock", "model": None})
            return AIInterpretation(**raw)

        cand = AIInterpretation(**raw)
        clean = _finalize(cand.interpretation, facts, "health")
        if not _validates(clean, facts, "health"):
            raise ValueError("AI narrative failed validation; falling back to mock.")
        return AIInterpretation(interpretation=clean)

    except Exception:
        logger.exception("Provider '%s' failed; falling back to mock.", provider or "mock")
        raw = _mock_generate_health(grounding, facts)
        _LAST_USED.update({"provider": "mock", "model": None})
        return AIInterpretation(**raw)



def generate_health_daily_interpretation(dob: str, day: Optional[str] = None, gender: Optional[str] = None) -> AIInterpretation:
    """
    Health interpretation for the combined DAILY triangle (DOB ⊕ Day).
    """
    report = health_daily_report(dob, day=day, gender=gender)
    facts = _summarize_health_report(report)
    grounding = _compose_grounding_for("health", used_digits=facts.get("_used_digits"),facts=facts,)

    provider = (settings.llm_provider or "").lower()
    logger.info("AI provider configured: %s", provider or "mock")

    try:
        if provider == "openai" and settings.openai_api_key:
            raw = _openai_generate(grounding, facts, mode="health_daily")
            _LAST_USED.update({"provider": "openai", "model": settings.openai_model})
        elif provider == "ollama":
            raw = _ollama_generate(grounding, facts, mode="health_daily")
            _LAST_USED.update({"provider": "ollama", "model": settings.ollama_model})
        else:
            raw = _mock_generate_health(grounding, facts)
            _LAST_USED.update({"provider": "mock", "model": None})
            return AIInterpretation(**raw)

        cand = AIInterpretation(**raw)
        clean = _finalize(cand.interpretation, facts, "health_daily")
        if not _validates(clean, facts, "health_daily"):
            raise ValueError("AI narrative failed validation; falling back to mock.")
        return AIInterpretation(interpretation=clean)

    except Exception:
        logger.exception("Daily Health AI generation failed; using mock fallback.")
        raw = _mock_generate_health(grounding, facts)
        _LAST_USED.update({"provider": "mock", "model": None})
        return AIInterpretation(**raw)



def generate_health_monthly_interpretation(dob: str, year: int, gender: Optional[str] = None) -> AIInterpretation:
    """
    Health interpretation for the combined MONTHLY driver (DOB ⊕ Month-Year driver).
    (This yields a year-scoped health report with month slots inside; we still summarize the whole.)
    """
    report = health_monthly_report(dob, year, gender=gender)
    facts = _summarize_health_report(report)
    grounding = _compose_grounding_for("health", used_digits=facts.get("_used_digits"),facts=facts,)

    provider = (settings.llm_provider or "").lower()
    logger.info("AI provider configured: %s", provider or "mock")

    try:
        if provider == "openai" and settings.openai_api_key:
            raw = _openai_generate(grounding, facts, mode="health_monthly")
            _LAST_USED.update({"provider": "openai", "model": settings.openai_model})
        elif provider == "ollama":
            raw = _ollama_generate(grounding, facts, mode="health_monthly")
            _LAST_USED.update({"provider": "ollama", "model": settings.ollama_model})
        else:
            raw = _mock_generate_health(grounding, facts)
            _LAST_USED.update({"provider": "mock", "model": None})
            return AIInterpretation(**raw)

        cand = AIInterpretation(**raw)
        clean = _finalize(cand.interpretation, facts, "health_monthly")
        if not _validates(clean, facts, "health_monthly"):
            raise ValueError("AI narrative failed validation; falling back to mock.")
        return AIInterpretation(interpretation=clean)

    except Exception:
        logger.exception("Monthly Health AI generation failed; using mock fallback.")
        raw = _mock_generate_health(grounding, facts)
        _LAST_USED.update({"provider": "mock", "model": None})
        return AIInterpretation(**raw)



def generate_health_yearly_interpretation(dob: str, year: int, gender: Optional[str] = None) -> AIInterpretation:
    """
    Health interpretation for the combined YEARLY triangle (DOB ⊕ Year-only).
    """
    report = health_yearly_report(dob, year, gender=gender)
    facts = _summarize_health_report(report)
    grounding = _compose_grounding_for("health", used_digits=facts.get("_used_digits"),facts=facts,)

    provider = (settings.llm_provider or "").lower()
    logger.info("AI provider configured: %s", provider or "mock")

    try:
        if provider == "openai" and settings.openai_api_key:
            raw = _openai_generate(grounding, facts, mode="health_yearly")
            _LAST_USED.update({"provider": "openai", "model": settings.openai_model})
        elif provider == "ollama":
            raw = _ollama_generate(grounding, facts, mode="health_yearly")
            _LAST_USED.update({"provider": "ollama", "model": settings.ollama_model})
        else:
            raw = _mock_generate_health(grounding, facts)
            _LAST_USED.update({"provider": "mock", "model": None})
            return AIInterpretation(**raw)

        cand = AIInterpretation(**raw)
        clean = _finalize(cand.interpretation, facts, "health_yearly")
        if not _validates(clean, facts, "health_yearly"):
            raise ValueError("AI narrative failed validation; falling back to mock.")
        return AIInterpretation(interpretation=clean)

    except Exception:
        logger.exception("Yearly Health AI generation failed; using mock fallback.")
        raw = _mock_generate_health(grounding, facts)
        _LAST_USED.update({"provider": "mock", "model": None})
        return AIInterpretation(**raw)


def generate_profession_interpretation(dob: str) -> AIInterpretation:
    """
    Build the deterministic profession report (Mulank + Bhagyank → PAIRS),
    summarize it, and ask the AI for a career-style interpretation.
    """
    facts = _summarize_profession_report(dob)
    grounding = _compose_grounding_for(
        "profession",
        used_digits=facts.get("_used_digits"),
        used_f=facts.get("_used_f"),
        facts=facts,
    )

    provider = (settings.llm_provider or "").lower()
    logger.info("AI provider configured: %s", provider or "mock")

    try:
        if provider == "openai" and settings.openai_api_key:
            raw = _openai_generate(grounding, facts, mode="profession")
            _LAST_USED.update({"provider": "openai", "model": settings.openai_model})
        elif provider == "ollama":
            raw = _ollama_generate(grounding, facts, mode="profession")
            _LAST_USED.update({"provider": "ollama", "model": settings.ollama_model})
        else:
            raw = _mock_generate_profession(grounding, facts)
            _LAST_USED.update({"provider": "mock", "model": None})
            return AIInterpretation(**raw)

        cand = AIInterpretation(**raw)
        # Treat profession similar to person for clipping/validation
        clean = _finalize(cand.interpretation, facts, "profession")
        if not _validates(clean, facts, "profession"):
            raise ValueError("AI narrative failed validation; falling back to mock.")
        return AIInterpretation(interpretation=clean)

    except Exception:
        logger.exception("Profession AI generation failed; using mock fallback.")
        raw = _mock_generate_profession(grounding, facts)
        _LAST_USED.update({"provider": "mock", "model": None})
        return AIInterpretation(**raw)
