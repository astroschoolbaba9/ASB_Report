# numerology/features/profile_bulletins.py
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple, Union


def _today_ddmmyyyy() -> str:
    return date.today().strftime("%d-%m-%Y")


def _safe_int(x: Any, default: int) -> int:
    try:
        return int(x)
    except Exception:
        return default


def _unique_keep_order(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for s in items:
        s = (s or "").strip()
        if not s:
            continue
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def _find_first(obj: Any, keys: Tuple[str, ...]) -> Optional[Any]:
    """Depth-first search for first matching key in nested dicts/lists."""
    if isinstance(obj, dict):
        for k in keys:
            if k in obj:
                return obj[k]
        for v in obj.values():
            got = _find_first(v, keys)
            if got is not None:
                return got
    elif isinstance(obj, list):
        for it in obj:
            got = _find_first(it, keys)
            if got is not None:
                return got
    return None


def _collect_strings(obj: Any, keys: Tuple[str, ...]) -> List[str]:
    """
    Collect strings from fields like tags/notes/bullets anywhere in nested structure.
    """
    out: List[str] = []

    def walk(x: Any):
        if isinstance(x, dict):
            for k, v in x.items():
                if k in keys:
                    if isinstance(v, str):
                        out.append(v)
                    elif isinstance(v, list):
                        for it in v:
                            if isinstance(it, str):
                                out.append(it)
                walk(v)
        elif isinstance(x, list):
            for it in x:
                walk(it)

    walk(obj)
    return _unique_keep_order(out)


def _mk_card(
    *,
    headline: str,
    bullets: List[str],
    tags: List[str],
    max_bullets: int = 4,
    max_tags: int = 6,
) -> Dict[str, Any]:
    bullets2 = _unique_keep_order(bullets)[:max_bullets]
    tags2 = _unique_keep_order(tags)[:max_tags]
    return {"headline": headline.strip() or "-", "bullets": bullets2, "tags": tags2}


def _summarize_personality(report: Dict[str, Any]) -> Dict[str, Any]:
    # Pull a few meaningful things if present
    mulank = report.get("mulank")
    bhagyank = report.get("bhagyank")

    polarity = _find_first(report, ("balance", "balance_label", "polarity_label", "overall_balance"))
    headline_parts = []
    if mulank is not None and bhagyank is not None:
        headline_parts.append(f"Mulank {mulank} • Bhagyank {bhagyank}")
    if isinstance(polarity, str) and polarity.strip():
        headline_parts.append(polarity.strip())
    headline = " — ".join(headline_parts) if headline_parts else "Core personality snapshot"

    bullets: List[str] = []
    # Often you have “core notes” somewhere
    core_note = _find_first(report, ("core_note", "core_notes", "priority", "remark", "note"))
    if isinstance(core_note, str) and core_note.strip():
        bullets.append(core_note.strip())

    bullets.extend(_collect_strings(report, ("notes", "highlights", "summary_points", "insights")))
    tags = _collect_strings(report, ("tags", "traits", "labels"))

    # Fallback: if nothing exists
    if not bullets:
        bullets = ["Personality traits are available in the Personality Traits section."]

    return _mk_card(headline=headline, bullets=bullets, tags=tags)


def _summarize_profession(report: Dict[str, Any]) -> Dict[str, Any]:
    prof = report.get("profession") or {}
    rating = None
    if isinstance(prof, dict):
        rating = prof.get("rating_short") or prof.get("rating_text")

    headline = f"Career fit: {rating}" if rating else "Career snapshot"

    bullets: List[str] = []
    if isinstance(prof, dict):
        if prof.get("remark"):
            bullets.append(str(prof["remark"]))
        professions = prof.get("professions") or []
        if isinstance(professions, list) and professions:
            bullets.append("Top domains: " + ", ".join(str(x) for x in professions[:5]))

    tags = _collect_strings(report, ("tags", "labels"))

    if not bullets:
        bullets = ["Profession guidance is available in the Profession section."]

    return _mk_card(headline=headline, bullets=bullets, tags=tags)


def _summarize_health(generic: Dict[str, Any], daily: Dict[str, Any], monthly: Dict[str, Any], yearly: Dict[str, Any]) -> Dict[str, Any]:
    tags = _unique_keep_order(
        _collect_strings(generic, ("tags",))
        + _collect_strings(daily, ("tags",))
        + _collect_strings(monthly, ("tags",))
        + _collect_strings(yearly, ("tags",))
    )
    bullets = _unique_keep_order(
        _collect_strings(generic, ("notes", "bullets", "highlights"))
        + _collect_strings(daily, ("notes", "bullets", "highlights"))
        + _collect_strings(monthly, ("notes", "bullets", "highlights"))
        + _collect_strings(yearly, ("notes", "bullets", "highlights"))
    )

    headline = "Health & wellbeing snapshot"

    if not bullets:
        bullets = ["Health patterns are available in the Health section."]

    # Keep wording safe + supportive (no explicit self-harm language)
    # If your tags include high-risk mood tags, add a gentle safety note:
    if any(t in tags for t in ("high_risk_emotional_phase", "mental_health", "confusion", "dual_personality")):
        bullets = _unique_keep_order(
            bullets + ["If you feel overwhelmed, prioritize rest, support, and professional guidance."]
        )

    return _mk_card(headline=headline, bullets=bullets, tags=tags)


def _summarize_cycles(daily: Dict[str, Any], monthly: Dict[str, Any], yearly: Dict[str, Any]) -> Dict[str, Any]:
    tags = _unique_keep_order(
        _collect_strings(daily, ("tags",))
        + _collect_strings(monthly, ("tags",))
        + _collect_strings(yearly, ("tags",))
    )
    bullets = _unique_keep_order(
        _collect_strings(daily, ("notes", "bullets", "highlights"))
        + _collect_strings(monthly, ("notes", "bullets", "highlights"))
        + _collect_strings(yearly, ("notes", "bullets", "highlights"))
    )

    headline = "Time cycles: daily • monthly • yearly"

    if not bullets:
        bullets = ["Time-cycle predictions are available in the Time Cycles section."]

    return _mk_card(headline=headline, bullets=bullets, tags=tags)


def _extract_time_slots(daily_report: Dict[str, Any], limit: int = 3) -> List[Dict[str, str]]:
    """
    Tries to find time-slot style panels inside daily report.
    This is intentionally defensive (won't break if structure differs).
    """
    slots: List[Dict[str, str]] = []

    # Common patterns you might have:
    # daily_report["time_slots"] or daily_report["panels"] etc.
    candidates = [
        _find_first(daily_report, ("time_slots", "timeSlots", "slots")),
        _find_first(daily_report, ("panels", "time_panels", "timePanels")),
    ]

    for c in candidates:
        if isinstance(c, list):
            for it in c:
                if isinstance(it, dict):
                    label = str(it.get("label") or it.get("time") or it.get("window") or "").strip()
                    note = str(it.get("note") or it.get("text") or it.get("meaning") or "").strip()
                    if label or note:
                        slots.append({"label": label or "-", "note": note or "-"})
                elif isinstance(it, str):
                    slots.append({"label": it, "note": ""})

    # Dedup by label+note
    seen = set()
    out = []
    for s in slots:
        key = (s.get("label", ""), s.get("note", ""))
        if key not in seen:
            seen.add(key)
            out.append(s)
    return out[:limit]


def build_profile_bulletins(
    *,
    dob: str,
    gender: Optional[str] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Builds compact bulletin summaries by calling existing report functions.
    Does NOT alter existing logic; only aggregates.
    """
    # Lazy imports to avoid circular imports
    from numerology.features.single_person_report import mystical_triangle_report
    from numerology.features.profession_report import profession_report
    from numerology.features.yearly_report import yearly_triangle_report
    from numerology.features.monthly_report import monthly_prediction_report
    from numerology.features.daily_report import daily_triangle_report
    from numerology.features.health_report import (
        health_triangle_report,
        health_daily_report,
        health_monthly_report,
        health_yearly_report,
    )

    y = _safe_int(year, date.today().year)
    m = _safe_int(month, date.today().month)
    d = (day or "today").strip() or "today"

    # Core reports (existing)
    personality_r = mystical_triangle_report(dob)
    profession_r = profession_report(dob)

    # Time cycles (existing)
    yearly_r = yearly_triangle_report(dob, y)
    monthly_r = monthly_prediction_report(dob, y)  # your monthly is year-driver

    # daily_triangle_report in your project is DOB-only; it likely uses today internally
    daily_r = daily_triangle_report(dob)

    # Health (existing)
    health_generic = health_triangle_report(dob, gender=gender)
    health_d = health_daily_report(dob, day=d, gender=gender)
    health_m = health_monthly_report(dob, y, gender=gender)
    health_y = health_yearly_report(dob, y, gender=gender)

    # Summaries
    personality = _summarize_personality(personality_r if isinstance(personality_r, dict) else {})
    profession = _summarize_profession(profession_r if isinstance(profession_r, dict) else {})
    health = _summarize_health(
        health_generic if isinstance(health_generic, dict) else {},
        health_d if isinstance(health_d, dict) else {},
        health_m if isinstance(health_m, dict) else {},
        health_y if isinstance(health_y, dict) else {},
    )
    cycles = _summarize_cycles(
        daily_r if isinstance(daily_r, dict) else {},
        monthly_r if isinstance(monthly_r, dict) else {},
        yearly_r if isinstance(yearly_r, dict) else {},
    )

    time_slots = _extract_time_slots(daily_r if isinstance(daily_r, dict) else {}, limit=3)

    return {
        "dob": dob,
        "gender": gender,
        "year": y,
        "month": m,
        "day": d if d != "today" else _today_ddmmyyyy(),
        "personality": personality,
        "profession": profession,
        "health": health,
        "cycles": {**cycles, "timeSlots": time_slots},
    }
