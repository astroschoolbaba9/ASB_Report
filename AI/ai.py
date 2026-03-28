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

    # Check if we are in mock mode (if meta indicates provider: mock)
    # We relax the stripping for mocks to allow more detail
    is_mock = facts.get("meta", {}).get("provider") == "mock"

    # 1) remove codes and layer jargon
    if not is_mock:
        t = _SANITIZE_CODES.sub("", text)
    else:
        t = text

    # 2) strip digits (RELAXED: we now keep digits as they are useful for dates and cycles)
    if is_mock:
        # For mocks, specifically keep the E=x, F=x patterns but maybe clean punctuation around them
        t = t.replace(" =", "=").replace("= ", "=")

    # 3) whitespace & punctuation normalization
    t = _WS_MULTI.sub(" ", t).strip()
    # Replace non-breaking spaces and other known artifacts
    t = t.replace("\u00a0", " ").replace("\u2022", "- ").replace("\ufffd", "")
    
    # Final safety: strip all non-printable/non-ASCII leading junk from each line
    lines = t.split("\n")
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        # Strip any character at the start that isn't a word, number, or common markdown
        while line and line[0] not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789*#+- ":
            line = line[1:]
        cleaned_lines.append(line)
    t = "\n".join(cleaned_lines).strip()
    
    t = t.replace("&", " and ")
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
        "person": (500, 700),
        "relationship": (500, 700),
        "yearly": (500, 700),
        "monthly": (350, 500),
        "daily": (300, 450),
        "health": (500, 700),
        "health_daily": (300, 450),
        "health_monthly": (350, 500),
        "health_yearly": (500, 700),
        "profession": (250, 400)
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
    is_mock = facts.get("meta", {}).get("provider") == "mock"
    
    # If it's a mock, we TRUST it (since we wrote the generator) and allow digits/codes
    if is_mock:
        return True

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
def _ensure_str_interpretation(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Make sure raw['interpretation'] is a single string.

    - If it's a list (bullet points), join with newlines.
    - If it's anything else, cast to string.
    """
    if not isinstance(raw, dict):
        return {"interpretation": str(raw)}

    data = dict(raw)  # shallow copy
    val = data.get("interpretation")

    if isinstance(val, list):
        parts: list[str] = []
        for item in val:
            if item is None:
                continue
            s = str(item).strip()
            if not s:
                continue
            # Ensure bullet prefix
            if not s.lstrip().startswith("•"):
                s = "• " + s.lstrip("• ").strip()
            parts.append(s)
        data["interpretation"] = "\n".join(parts)

    elif not isinstance(val, str):
        data["interpretation"] = "" if val is None else str(val).strip()

    return data


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
    strip_digits: bool = True,
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
            "Using the 'Suggested domains or fields' provided above, YOU MUST EXPLICITLY LIST 6 TO 10 "
            "SPECIFIC CAREER OPTIONS OR JOB TITLES that best fit this numeric combination."
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


def _summarize_health_report(full: dict) -> dict:
    """Extract minimal LLM-relevant info for health reports."""
    vals = full.get("values") or {}
    layer1 = vals.get("layer1") or {}
    third = vals.get("third_layer") or {}

    E = layer1.get("E")
    F = layer1.get("F")
    G = layer1.get("G")
    P = third.get("P")

    # The payload from health_triangle_report has 'sections'
    sections = full.get("sections") or {}
    core_health = sections.get("core_health") or {}
    
    g_meaning = (core_health.get("Vital Energy (G)") or {}).get("meaning")
    p_meaning = (core_health.get("Healing Direction (P)") or {}).get("meaning")
    ef_note = (core_health.get("Balance (E+F)") or {}).get("note")

    summary = {
        "dob": full.get("dob"),
        "core": {
            "G": G,
            "P": P,
            "E": E,
            "F": F,
            "g_meaning": g_meaning,
            "p_meaning": p_meaning,
            "ef_note": ef_note,
        },
        "zones": {
            "mental": (sections.get("zones") or {}).get("Mental Health Zone (N,O)", {}).get("values", []),
            "physical": (sections.get("zones") or {}).get("Physical Health Zone (H,I,J)", {}).get("values", []),
            "emotional": (sections.get("zones") or {}).get("Emotional Health Zone (K,L,M)", {}).get("values", []),
            "recovery": (sections.get("zones") or {}).get("Recovery Potential (Q,R)", {}).get("values", []),
        },
        "elements": full.get("elements"),
        "flags": full.get("organ_flags"),
        "neoplasm": full.get("neoplasm_probability"),
        "notes": full.get("abdomen"),
        "meanings": {},
    }

    used = [E, F, G, P]
    summary["_used_digits"] = sorted({int(x) for x in used if isinstance(x, int)})
    summary["_used_f"] = F
    
    if G is not None: summary["meanings"]["G"] = g_meaning
    if P is not None: summary["meanings"]["P"] = p_meaning
    
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

    # Core numbers - try multiple potential paths
    E = _g(full, "values", "layer1", "E") or _g(full, "layer1", "E")
    F = _g(full, "values", "layer1", "F") or _g(full, "layer1", "F")
    G = _g(full, "values", "layer1", "G") or _g(full, "layer1", "G") or _g(full, "core", "G")
    P = _g(full, "values", "third_layer", "P") or _g(full, "third_layer", "P") or _g(full, "core", "P_outcome")

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
    polarity = facts.get("polarity") or {}
    active_codes = facts.get("active_codes") or []
    reads_summary = facts.get("reads_summary") or []
    mb = facts.get("mulank_bhagyank") or {}
    mulank = mb.get("mulank")
    bhagyank = mb.get("bhagyank")

    def meaning_of(n):
        m = traits.get(str(n))
        return m.split(";")[0] if m else ""

    meaning_E = meaning_of(E)
    meaning_F = meaning_of(F)
    meaning_G = meaning_of(G)
    meaning_P = meaning_of(P)

    # Seeded randomization so each DOB always gets the same but unique text
    seed_val = int(str(G or 0) + str(P or 0) + str(E or 0) + str(F or 0)) % 100
    random.seed(seed_val)

    # Build polarity section
    balance = polarity.get("balance", "balanced")
    pos_count = polarity.get("positive", 0)
    neg_count = polarity.get("negative", 0)

    polarity_texts = {
        "positive-heavy": "Your chart leans strongly toward positive energy, giving you natural optimism and an uplifting influence on those around you",
        "negative-heavy": "Your chart carries a deeper, more introspective energy — this gives you remarkable analytical depth and the ability to see truths others miss",
        "balanced": "Your chart displays a beautifully balanced polarity, blending depth of thought with expressive warmth",
    }
    polarity_note = polarity_texts.get(balance, polarity_texts["balanced"])

    # Build active codes section (unique per person)
    code_section = ""
    if active_codes and len(active_codes) >= 2:
        sample_codes = random.sample(active_codes, min(3, len(active_codes)))
        code_labels = ", ".join(str(c) for c in sample_codes)
        code_section = (
            f"\n#### 🔑 Active Patterns\n"
            f"- Your chart activates the following unique codes: **{code_labels}**. "
            f"These create a distinctive behavioral fingerprint that sets you apart.\n"
        )

    # Build reads summary section (unique insights per person)
    reads_section = ""
    if reads_summary and len(reads_summary) >= 2:
        picks = random.sample(reads_summary, min(2, len(reads_summary)))
        reads_lines = []
        for code, detail in picks:
            if isinstance(detail, dict):
                note = detail.get("note") or detail.get("meaning") or ""
                if note:
                    reads_lines.append(f"- **{code}**: {note}")
        if reads_lines:
            reads_section = (
                f"\n#### 📖 Personalized Reads\n"
                + "\n".join(reads_lines) + "\n"
            )

    # Mulank/Bhagyank section
    mb_section = ""
    if mulank is not None and bhagyank is not None:
        mb_section = f"- **Mulank {mulank} × Bhagyank {bhagyank}**: This core pairing defines your life's primary rhythm and career orientation.\n"

    # Personalize greeting
    name = facts.get("name")
    persona = f"**{name}**" if name else "You"
    subject = f"**{name}'s**" if name else "Your"
    name_possessive = f"{name}'s" if name else "your"
    name_comma = f"{name}, your" if name else "Your"
    
    paragraph = (
        f"Based on ASB Numerology, your cosmic blueprint for DOB {dob} reveals a deeply layered numerical signature. "
        f"Your core foundation is built on {meaning_G.lower()}, which provides a stable bedrock for your character. "
        f"Your inner drive and psychic baseline are focused on {meaning_F.lower()}, while your ultimate life path points toward {meaning_P.lower()}. "
        f"Overall, your chart highlights how your emotional tone and inner drive combine to shape your outward style and life trajectory. "
        f"By harmonizing with these frequencies, you unlock your highest potential and achieve lasting fulfillment."
    ).strip()

    return {
        "interpretation": paragraph,
        "created_at": datetime.utcnow().isoformat(),
        "meta": {"provider": "mock", "mode": "person", "used_core": core},
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
        "Highest Possibility": "reflects an exceptionally compatible match with profound mutual understanding",
        "Stronger": "indicates a strong and promising connection with high resonance",
        "Strong": "suggests a balanced and mutually supportive bond",
        "Fair": "points to a fair connection that may require conscious effort and patience",
    }
    tone = tone_phrases.get(bucket, "suggests a meaningful relationship dynamic")

    issue_bits = []
    if "never_separate" in issues:       issue_bits.append("a very stable, enduring bond")
    if "relationship_issue" in issues:   issue_bits.append("some relationship challenges to navigate")
    if "marriage_issue" in issues:       issue_bits.append("potential marriage-compatibility areas to address")
    if "downfall" in issues:             issue_bits.append("a risk of significant misunderstandings if not communicated")
    issue_phrase = ", ".join(issue_bits) if issue_bits else "overall structural harmony"

    extras = []
    if lucky:   extras.append("The presence of Lucky 9 vibrations provides strong energetic support for long-term growth.")
    if has_27:  extras.append("A rare 27/72 karmic link strengthens the spiritual bonding between both individuals.")
    if qr_linked: extras.append("The Q–R mirroring suggests that while there is a deep reflection, occasional complications may arise.")
    extras_text = (" " + " ".join(extras)) if extras else ""

    # Extracting dob_left and dob_right from 'rel' if possible, otherwise default to 'Unknown'
    dob_left, dob_right = "Unknown", "Unknown"
    if " + " in rel:
        parts = rel.split(" + ")
        if len(parts) == 2:
            dob_left, dob_right = parts[0], parts[1]

    # Personalize greeting
    name = facts.get("name")
    persona = f"**{name}**" if name else "This"
    
    paragraph = (
        f"The relationship between {rel} presents a {bucket} alignment. "
        f"With a dominant {dominant} element and core traits focused on {meaning_F.lower()}, this bond thrives on mutual understanding and shared values. "
        f"Your numerical synergy creates a distinctive rhythm that supports both individual growth and collective stability. "
        f"Focus on open communication and nurturing your shared path to unlock the highest potential of this partnership."
    ).strip()

    return {
        "interpretation": paragraph,
        "created_at": datetime.utcnow().isoformat(),
        "meta": {
            "provider": "mock",
            "mode": "relationship",
            "bucket": bucket,
            "dominant_element": dominant,
            "issues_detected": list(issues.keys()),
        },
    }


def _mock_generate_yearly(grounding: dict, facts: dict) -> dict:
    dob = facts.get("dob", "Unknown")
    year = facts.get("year", "Unknown")
    core = facts.get("core_numbers", {})
    E, F, G, P = core.get("E"), core.get("F"), core.get("G"), core.get("P")
    meanings = facts.get("meanings", {}) or {}

    g_mean = (meanings.get("G") or "").split(";")[0].lower()
    p_mean = (meanings.get("P") or "").split(";")[0].lower()
    e_mean = (meanings.get("E") or "").split(";")[0].lower()
    f_mean = (meanings.get("F") or "").split(";")[0].lower()

    seed = int(str(G or 0) + str(P or 0) + str(E or 0) + str(F or 0)) % 100
    random.seed(seed)
    
    tones = [
        f"a pivotal year of meaningful progress and internal adjustment, centered on **{g_mean}**",
        f"a broad cycle of renewal, clarity, and intentional shifts toward **{p_mean}**",
        f"a significant phase for steady growth, leaning into your foundation of **{g_mean}**",
        f"a period of deeper self-mastery where your drive for **{f_mean}** takes center stage",
        f"a balanced year focusing on integration and long-term vision, guided by **{e_mean}**"
    ]
    tone = random.choice(tones)

    paragraph = (
        f"### 📅 {year} Forecast: The Path of Progress\n\n"
        f"Your ASB Numerology forecast for the year **{year}** is governed by the shifting annual frequencies and your core DOB {dob}. This cycle is {tone}.\n\n"
        f"#### 🌟 Annual Pillars\n"
        f"- **Foundation (G={G})**: This year serves as an anchor of **{g_mean}**, providing the steady platform you need for major decisions and sustaining your momentum.\n"
        f"- **Destination (P={P})**: Your ultimate peak for {year} points toward **{p_mean}**, marking a period of transition and significant personal achievement.\n\n"
        f"#### 🚦 Strategic Navigation\n"
        f"- **Baseline Alignment (E={E})**: Your external style (**{e_mean}**) is highly synchronized with the year's demands, allowing you to navigate challenges with poise.\n"
        f"- **Inner Drive (F={F})**: Your motivation (**{f_mean}**) fuels the disciplined action required to manifest your desires and overcome obstacles.\n\n"
        f"*Stay mindful of the subtle shifts in your P={P} markers to stay on track for your highest success this year. Cosmic alignment is on your side.*"
    ).strip()

    return {
        "interpretation": paragraph,
        "created_at": datetime.utcnow().isoformat(),
        "meta": {
            "provider": "mock",
            "mode": "yearly",
            "used_core": {"E": E, "F": F, "G": G, "P": P},
            "dob": dob,
            "year": year,
        },
    }

def _mock_generate_monthly(grounding: dict, facts: dict) -> dict:
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

    paragraph = (
        f"### 🌙 {mname} {year} Insight\n\n"
        f"For **{mname} {year}**, your ASB Numerology chart indicates a significant energetic focus in the **{slot}** position with a value of **{val}**.\n\n"
        f"#### 📍 Monthly Indicators\n"
        f"- **Primary Influence**: This month leans strongly toward **{m_mean}**. Expect these qualities to be prominent in your daily experiences and professional interactions.\n"
        f"- **Anchor Frequency (G={G})**: Provides a stable **{g_mean}** backdrop, ensuring you stay grounded during seasonal transitions and project shifts.\n\n"
        f"#### ⚡ Action Strategy\n"
        f"- **Purpose (P={P})**: Guides your energy toward **{p_mean}**, marking the ultimate goal and achievement point of this monthly cycle.\n"
        f"- **Daily Balance**: Utilize your Psychic Baseline (E={E}) and Inner Drive (F={F}) to enhance your intuitive responses and maintain social momentum.\n\n"
        f"*Momentum matters more than speed this month. Focus on deliberate progress and the conscious manifestation of your core intentions.*"
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
    dob = facts.get("dob", "Unknown")
    today = facts.get("today", "")
    core = facts.get("core_numbers", {})
    E, F, G, P = core.get("E"), core.get("F"), core.get("G"), core.get("P")

    meanings = facts.get("meanings", {}) or {}
    e_mean = (meanings.get("E") or "").split(";")[0].lower()
    f_mean = (meanings.get("F") or "").split(";")[0].lower()
    g_mean = (meanings.get("G") or "").split(";")[0].lower()
    p_mean = (meanings.get("P") or "").split(";")[0].lower()

    paragraph = (
        f"For today, {today}, your ASB Numerology profile highlights a focused numerical signature. "
        f"Your primary foundation is centered on {g_mean.lower()}, while your daily tone and drive create a reactive and intuitive atmosphere for your tasks. "
        f"As the day unfolds, your life path points toward {p_mean.lower()}, guiding your growth and personal performance. "
        f"Stay mindful of these frequencies to stay perfectly aligned with your higher path."
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
    core = facts.get("core", {})
    G, P = core.get("G"), core.get("P")
    g_mean = (core.get("g_meaning") or "").lower()
    p_mean = (core.get("p_meaning") or "").lower()
    ef_note = (core.get("ef_note") or "").lower()

    if G is None: G = "?"
    if P is None: P = "?"

    # Richer data points
    zones = facts.get("zones") or {}
    elements = facts.get("elements") or {}
    flags = facts.get("flags") or {}
    neoplasm = facts.get("neoplasm") or {}
    health_meanings = facts.get("health_meanings") or {}
    notes = facts.get("notes") or {}

    # Build zone analysis
    mental = zones.get("mental", [])
    physical = zones.get("physical", [])
    emotional = zones.get("emotional", [])
    recovery = zones.get("recovery", [])

    zone_section = ""
    if any([mental, physical, emotional, recovery]):
        zone_lines = []
        if mental and any(x is not None for x in mental):
            nums = [str(x) for x in mental if x is not None]
            zone_lines.append(f"- **Mental Zone** ({', '.join(nums)}): Governs cognitive patterns, decision-making speed, and mental resilience.")
        if physical and any(x is not None for x in physical):
            nums = [str(x) for x in physical if x is not None]
            zone_lines.append(f"- **Physical Zone** ({', '.join(nums)}): Influences stamina, metabolic rhythm, and structural health.")
        if emotional and any(x is not None for x in emotional):
            nums = [str(x) for x in emotional if x is not None]
            zone_lines.append(f"- **Emotional Zone** ({', '.join(nums)}): Shapes stress responses, emotional regulation, and interpersonal well-being.")
        if recovery and any(x is not None for x in recovery):
            nums = [str(x) for x in recovery if x is not None]
            zone_lines.append(f"- **Recovery Zone** ({', '.join(nums)}): Determines healing speed and restorative capacity.")
        if zone_lines:
            zone_section = "\n#### 🧬 Health Zone Map\n" + "\n".join(zone_lines) + "\n"

    # Build element section
    elem_section = ""
    if elements:
        dominant = elements.get("dominant")
        deficient = elements.get("deficient")
        if dominant or deficient:
            elem_lines = []
            if dominant: elem_lines.append(f"- **Dominant Element**: {dominant} — this element drives your energy and metabolism.")
            if deficient: elem_lines.append(f"- **Deficient Element**: {deficient} — consider lifestyle adjustments to balance this area.")
            elem_section = "\n#### 🌊 Elemental Balance\n" + "\n".join(elem_lines) + "\n"

    # Build organ flag warnings
    organ_section = ""
    organ_keys = flags.get("organ", [])
    abdomen_risk = flags.get("abdomen_risk", False)
    if organ_keys or abdomen_risk:
        organ_lines = []
        if organ_keys:
            organ_lines.append(f"- **Flagged areas**: {', '.join(organ_keys[:4])}. Preventive care in these areas is recommended.")
        if abdomen_risk:
            organ_lines.append("- **Abdominal sensitivity**: Your chart indicates attention to digestive and core health may be beneficial.")
        organ_section = "\n#### ⚠️ Preventive Indicators\n" + "\n".join(organ_lines) + "\n"

    paragraph = (
        f"Your wellness archetype for DOB {dob} reflects a profile focused on long-term vitality. "
        f"Your numerical signature, driven by frequencies of {g_mean.lower()}, suggests a need for rhythmic routines and grounding practices to maintain internal harmony. "
        f"By focusing on consistent lifestyle choices that align with your growth direction of {p_mean.lower()}, you can achieve peak physical and mental performance. "
        f"Stay attentive to your body's subtle signals to ensure lasting well-being."
    ).strip()

    return {"interpretation": paragraph}


def _mock_generate_health_yearly(grounding: dict, facts: dict) -> dict:
    year = facts.get("year", "this year")
    core = facts.get("core", {})
    G, P = core.get("G"), core.get("P")
    g_mean = (core.get("g_meaning") or "stability").lower()
    p_mean = (core.get("p_meaning") or "growth").lower()

    if G is None: G = "?"
    if P is None: P = "?"

    paragraph = (
        f"Your annual health frequency for **{year}** encourages building resilience and solidifying your wellness foundation. "
        f"This cycle is centered on long-term vitality, with your root frequency ({g_mean}) acting as a major buffer against external disruptions. "
        f"The destination frequency ({p_mean}) suggests this is an ideal window for preventive care and a total habit reset. "
        f"Blend consistent physical activity with spiritual grounding to maintain internal harmony and achieve your most efficient state of recovery and performance."
    ).strip()

    return {"interpretation": paragraph}

def _mock_generate_health_monthly(grounding: dict, facts: dict) -> dict:
    from calendar import month_name
    year = facts.get("year", "")
    m = int(facts.get("month") or 1)
    mname = month_name[m]
    core = facts.get("core", {})
    G, P = core.get("G"), core.get("P")
    g_mean = (core.get("g_meaning") or "stability").lower()
    p_mean = (core.get("p_meaning") or "purpose").lower()

    if G is None: G = "?"
    if P is None: P = "?"

    paragraph = (
        f"In the month of {mname} {year}, your health cycle highlights a need for tactical adjustments. "
        f"Focus on moderate activity and optimizing your biological clock to match your internal rhythm. "
        f"Nutrition and mindfulness are key this month; notice how your emotional climate impacts your physical drive. "
        f"By making these small adjustments, you will stay in peak resonance with your environment, supported by your core {g_mean} and {p_mean} energies."
    ).strip()

    return {"interpretation": paragraph}

def _mock_generate_health_daily(grounding: dict, facts: dict) -> dict:
    day = facts.get("today", "today")
    core = facts.get("core", {})
    G, P = core.get("G"), core.get("P")

    if G is None: G = "?"
    if P is None: P = "?"

    paragraph = (
        f"For {day}, your physical and mental landscape is influenced by a calm yet focused vibration. "
        f"Pay attention to your body's need for hydration and rest, and avoid over-exertion during high-pressure moments. "
        f"Your natural resilience is strong today, provided you maintain a steady pace and stay mindful of your energy boundaries."
    ).strip()

    return {"interpretation": paragraph}


def _mock_generate_profession(grounding: dict | str, facts: dict) -> dict:
    dob = facts.get("dob", "Unknown")
    m = facts.get("mulank")
    b = facts.get("bhagyank")
    prof = facts.get("profession") or {}
    suggested = prof.get("professions") or []
    
    core = facts.get("core_numbers", {})
    E, F, G, P = core.get("E"), core.get("F"), core.get("G"), core.get("P")
    meanings = facts.get("meanings", {}) or {}
    g_trait = (meanings.get("G") or "").split(";")[0].lower()
    p_trait = (meanings.get("P") or "").split(";")[0].lower()

    fields_txt = ", ".join(suggested) if suggested else "fields that allow for strategic growth and creative expression"

    seed = int(f"{m or 0}{b or 0}") % 100
    random.seed(seed)
    tone = random.choice([
        "steady, patient progress in structured environments",
        "creative and people-focused work that allows for high expression",
        "structured, responsibility-driven roles with significant leadership potential",
        "flexible, exploratory paths that utilize your diverse analytical skills",
        "high-precision roles that benefit from your intense focus and detail orientation"
    ])

    # Personalize
    name = facts.get("name")
    persona = f"**{name}**" if name else "You"
    subject = f"**{name}'s**" if name else "Your"
    name_possessive = f"{name}'s" if name else "your"

    paragraph = (
        f"Based on ASB Numerology, your professional path is uniquely shaped by the combination of Mulank {m} and Bhagyank {b}. "
        f"This signature suggests a natural pull toward {tone}. "
        f"You are naturally equipped for professions that value {g_trait} and disciplined, rhythmic execution. "
        f"Your long-term direction points toward {p_trait}, which represents the peak of your professional influence. "
        f"With your psychic baseline and inner drive, you can navigate complex workplace dynamics with ease. "
        f"In your chart, you excel in fields like {fields_txt}. Focus on roles that allow your natural destination to manifest consistently over time. "
        f"Trust the synergy of your numbers to lead you to a prosperous and fulfilling professional future."
    ).strip()

    return {
        "interpretation": paragraph,
        "created_at": datetime.utcnow().isoformat(),
        "meta": {
            "provider": "mock",
            "mode": "profession",
            "mulank": m,
            "bhagyank": b,
            "top_profs": suggested[:5]
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

def generate_interpretation(dob: str, name: str | None = None) -> AIInterpretation:
    report = mystical_triangle_report(dob)
    facts = _summarize_person_report(report)  # ← facts first
    if name:
        facts["name"] = name
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
            raw = _mock_generate(grounding, facts)
            _LAST_USED.update({"provider": "mock", "model": None})
            logger.info("AI provider used: mock")
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



def generate_relationship_interpretation(dob_left: str, dob_right: str, name: str | None = None) -> AIInterpretation:
    """
    Build the deterministic combined triangle (relationship report),
    then ask the chosen LLM for a plain-language paragraph.
    """
    report = relationship_triangle_report(dob_left, dob_right)
    facts = _summarize_relationship_report(report)
    if name:
        facts["name"] = name
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
            raw = _mock_generate_relationship(grounding, facts)
            _LAST_USED.update({"provider": "mock", "model": None})
        cand = AIInterpretation(**raw)
        clean = _finalize(cand.interpretation, facts, "relationship")
        if not _validates(clean, facts, "relationship"):
            raise ValueError("AI narrative failed validation; falling back to mock.")
        return AIInterpretation(interpretation=clean)


    except Exception:
        logger.exception("Validation failed; using mock fallback.")
        raw = _mock_generate_relationship(grounding, facts)
        _LAST_USED.update({"provider": "mock", "model": None})
        clean = _finalize(raw["interpretation"], facts, "relationship")
        return AIInterpretation(interpretation=clean)

    
def generate_yearly_interpretation(dob: str, year: int, name: str | None = None) -> AIInterpretation:
    """
    Build the deterministic combined yearly triangle (DOB ⊕ Year),
    summarize key facts, and ask the AI for a one-paragraph interpretation.
    """
    report = yearly_triangle_report(dob, year)
    facts = _summarize_yearly_report(report)
    if name:
        facts["name"] = name
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
        
        cand = AIInterpretation(**raw)
        clean = _finalize(cand.interpretation, facts, "yearly")
        if not _validates(clean, facts, "yearly"):
            raise ValueError("AI narrative failed validation; falling back to mock.")
        return AIInterpretation(interpretation=clean)

    except Exception:
        logger.exception("Yearly AI generation failed; using mock fallback.")
        raw = _mock_generate_yearly(grounding, facts)
        _LAST_USED.update({"provider": "mock", "model": None})
        clean = _finalize(raw["interpretation"], facts, "yearly")
        return AIInterpretation(interpretation=clean)


def generate_monthly_interpretation(dob: str, year: int, month: int, name: str | None = None) -> AIInterpretation:
    """
    Build the deterministic monthly report (DOB ⊕ Month-Year driver),
    summarize ONE target month, and ask the AI for a short interpretation.
    """
    monthly = monthly_prediction_report(dob, year)
    facts = _summarize_monthly_report(monthly, month)
    if name:
        facts["name"] = name
    grounding = _compose_grounding_for(
        "person",
        used_digits=facts.get("_used_digits"),
        used_f=facts.get("_used_f"),
        facts=facts,
        strip_digits=False, # Relax digit stripping
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
            raw = _ensure_str_interpretation(raw)
            return AIInterpretation(**raw)

        # 🔹 Normalize OpenAI/Ollama output (list → multi-line string)
        raw = _ensure_str_interpretation(raw)

        cand = AIInterpretation(**raw)
        clean = _finalize(cand.interpretation, facts, "monthly")
        if not _validates(clean, facts, "monthly"):
            raise ValueError("AI narrative failed validation; falling back to mock.")
        return AIInterpretation(interpretation=clean)

    except Exception:
        logger.exception("Monthly AI generation failed; using mock fallback.")
        raw = _mock_generate_monthly(grounding, facts)
        _LAST_USED.update({"provider": "mock", "model": None})
        clean = _finalize(raw["interpretation"], facts, "monthly")
        return AIInterpretation(interpretation=clean)


    
    
def generate_daily_interpretation(dob: str, day: Optional[str] = None, name: str | None = None) -> AIInterpretation:
    """
    Build the deterministic daily report (DOB ⊕ [Today or a specific date]),
    summarize combined facts, and ask the AI for a one-paragraph interpretation.
    """
    report = daily_triangle_report(dob, right_day=day)
    facts = _summarize_daily_report(report)
    if name:
        facts["name"] = name
    grounding = _compose_grounding_for(
        "person",
        used_digits=facts.get("_used_digits"),
        used_f=facts.get("_used_f"),
        facts=facts,
        strip_digits=False, # Relax digit stripping
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
        clean = _finalize(raw["interpretation"], facts, "daily")
        return AIInterpretation(interpretation=clean)


    
    
def generate_health_interpretation(dob: str, gender: Optional[str] = None, name: str | None = None) -> AIInterpretation:
    """
    Build the deterministic health triangle (numerology.features.health),
    then ask the chosen LLM for a plain paragraph (or deterministic mock).
    """
    report = health_triangle_report(dob, gender=gender)
    facts = _summarize_health_report(report)
    if name:
        facts["name"] = name
    grounding = _compose_grounding_for("health", used_digits=facts.get("_used_digits"),facts=facts, strip_digits=False,) # Relax digit stripping

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



def generate_health_daily_interpretation(dob: str, day: Optional[str] = None, gender: Optional[str] = None, name: str | None = None) -> AIInterpretation:
    """
    Health interpretation for the combined DAILY triangle (DOB ⊕ Day).
    """
    report = health_daily_report(dob, day=day, gender=gender)
    facts = _summarize_health_report(report)
    if name:
        facts["name"] = name
    grounding = _compose_grounding_for("health", used_digits=facts.get("_used_digits"),facts=facts, strip_digits=False,) # Relax digit stripping

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
            raw = _mock_generate_health_daily(grounding, facts)
            _LAST_USED.update({"provider": "mock", "model": None})
            return AIInterpretation(**raw)

        cand = AIInterpretation(**raw)
        clean = _finalize(cand.interpretation, facts, "health_daily")
        if not _validates(clean, facts, "health_daily"):
            raise ValueError("AI narrative failed validation; falling back to mock.")
        return AIInterpretation(interpretation=clean)

    except Exception:
        logger.exception("Daily Health AI generation failed; using mock fallback.")
        raw = _mock_generate_health_daily(grounding, facts)
        _LAST_USED.update({"provider": "mock", "model": None})
        return AIInterpretation(**raw)



def generate_health_monthly_interpretation(dob: str, year: int, gender: Optional[str] = None, name: str | None = None) -> AIInterpretation:
    """
    Health interpretation for the combined MONTHLY driver (DOB ⊕ Month-Year driver).
    (This yields a year-scoped health report with month slots inside; we still summarize the whole.)
    """
    report = health_monthly_report(dob, year, gender=gender)
    facts = _summarize_health_report(report)
    if name:
        facts["name"] = name
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
            raw = _mock_generate_health_monthly(grounding, facts)
            _LAST_USED.update({"provider": "mock", "model": None})
            return AIInterpretation(**raw)

        cand = AIInterpretation(**raw)
        clean = _finalize(cand.interpretation, facts, "health_monthly")
        if not _validates(clean, facts, "health_monthly"):
            raise ValueError("AI narrative failed validation; falling back to mock.")
        return AIInterpretation(interpretation=clean)

    except Exception:
        logger.exception("Monthly Health AI generation failed; using mock fallback.")
        raw = _mock_generate_health_monthly(grounding, facts)
        _LAST_USED.update({"provider": "mock", "model": None})
        return AIInterpretation(**raw)



def generate_health_yearly_interpretation(dob: str, year: int, gender: Optional[str] = None, name: str | None = None) -> AIInterpretation:
    """
    Health interpretation for the combined YEARLY triangle (DOB ⊕ Year-only).
    """
    report = health_yearly_report(dob, year, gender=gender)
    facts = _summarize_health_report(report)
    if name:
        facts["name"] = name
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
            raw = _mock_generate_health_yearly(grounding, facts)
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


def generate_profession_interpretation(dob: str, name: str | None = None) -> AIInterpretation:
    """
    Build the deterministic profession report (Mulank + Bhagyank → PAIRS),
    summarize it, and ask the AI for a career-style interpretation.
    """
    facts = _summarize_profession_report(dob)
    if name:
        facts["name"] = name
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
            raw = _mock_generate_profession(grounding, facts)
            _LAST_USED.update({"provider": "mock", "model": None})

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
        clean = _finalize(raw["interpretation"], facts, "profession")
        return AIInterpretation(interpretation=clean)
