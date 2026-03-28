# AI/swot.py
from __future__ import annotations
from typing import Dict, List
import json
import logging
import requests

from AI.settings import settings

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# Basic text helpers
# ──────────────────────────────────────────────────────────────
def _split_bullets(text: str) -> List[str]:
    """
    Split interpretation text into logical lines / bullets.
    Handles both '•' bullets and plain sentence-style content.
    """
    if not isinstance(text, str):
        return []

    # First split on newlines
    raw_lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    bullets: List[str] = []
    for ln in raw_lines:
        # Strip leading bullet symbol if present
        if ln.startswith("•"):
            ln = ln.lstrip("•").strip()
        if ln:
            bullets.append(ln)

    # If nothing came out (e.g., a single long paragraph),
    # fall back to splitting by sentences.
    if not bullets:
        # naive sentence split
        parts = []
        for chunk in text.replace("•", "").split("."):
            c = chunk.strip()
            if c:
                parts.append(c + ".")
        bullets = parts

    return bullets


# ──────────────────────────────────────────────────────────────
# Heuristic fallback (your original keyword-based logic)
# ──────────────────────────────────────────────────────────────
def _heuristic_swot(text: str) -> Dict[str, List[str]]:
    strengths: List[str] = []
    weaknesses: List[str] = []
    opportunities: List[str] = []
    threats: List[str] = []

    bullets = _split_bullets(text)

    for line in bullets:
        low = line.lower()

        # ---- Strengths ----
        if any(k in low for k in [
            "strength", "creative", "creativity", "caring", "generous",
            "communication", "communicate", "emotional intelligence",
            "proactive", "adaptable", "dynamic", "vision", "inspire",
            "confident", "balanced", "grounded", "responsible",
        ]):
            strengths.append(line)

        # ---- Weaknesses ----
        if any(k in low for k in [
            "impatience", "impatient", "scatter", "scattered",
            "overindulgence", "extravagance", "over-attachment",
            "overattachment", "mood swing", "mood swings",
            "emotional fluctuation", "restlessness", "rigidity",
            "inconsistent", "inconsistency",
        ]):
            weaknesses.append(line)

        # ---- Opportunities ----
        if any(k in low for k in [
            "growth", "opportunity", "humanitarian", "potential",
            "develop", "development", "learning", "expand",
            "connection", "balance", "planning", "leadership",
            "success", "fulfilment", "fulfillment",
        ]):
            opportunities.append(line)

        # ---- Threats ----
        if any(k in low for k in [
            "stress", "overwhelm", "overwhelmed", "risk",
            "challenge", "instability", "burnout", "fatigue",
            "emotional imbalance", "conflict", "tension","overattachment","inconsistent", "inconsistency",
        ]):
            threats.append(line)

    return {
        "Strengths": strengths,
        "Weaknesses": weaknesses,
        "Opportunities": opportunities,
        "Threats": threats,
    }


# ──────────────────────────────────────────────────────────────
# LLM-based SWOT: OpenAI
# ──────────────────────────────────────────────────────────────
def _openai_swot(text: str) -> Dict[str, List[str]]:
    from openai import OpenAI

    client = OpenAI(
        api_key=(
            settings.openai_api_key.get_secret_value()
            if hasattr(settings.openai_api_key, "get_secret_value")
            else settings.openai_api_key
        )
    )

    system_msg = (
        "You are a precise analyst turning a personality interpretation into a SWOT analysis. "
        "You will receive bullet-point or paragraph-style text describing a person's traits. "
        "Identify distinct ideas and classify them into Strengths, Weaknesses, Opportunities, and Threats. "
        "Strengths: existing positive qualities, resources, or abilities. "
        "Weaknesses: recurring patterns, habits, or tendencies that may limit the person. "
        "Opportunities: ways these qualities can be used for growth, development, or advantage. "
        "Threats: risks, patterns, or external-style factors that could cause stress, conflict, or decline if ignored. "
        "Every relevant idea must appear in at least one bucket; it's okay if one sentence appears in more than one bucket. "
        "Use the *user's own wording* as much as possible (just clean spacing), do not rewrite heavily. "
        "If a bucket has no content, return an empty list for it. "
        "Reply ONLY with JSON of the form: "
        "{\"strengths\": [...], \"weaknesses\": [...], \"opportunities\": [...], \"threats\": [...] }"
    )

    user_msg = (
        "Here is the interpretation text:\n\n"
        f"{text}\n\n"
        "1. Extract distinct ideas (typically one bullet or sentence per idea).\n"
        "2. Classify each idea into one or more of the four SWOT buckets.\n"
        "3. Return clean JSON only, with keys: strengths, weaknesses, opportunities, threats.\n"
        "4. Do not include any explanation or commentary outside the JSON."
    )

    resp = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.1,
        max_tokens=512,
        response_format={"type": "json_object"},
        timeout=settings.timeout_seconds,
    )

    raw = resp.choices[0].message.content
    data = json.loads(raw)

    return {
        "Strengths": data.get("strengths", []) or [],
        "Weaknesses": data.get("weaknesses", []) or [],
        "Opportunities": data.get("opportunities", []) or [],
        "Threats": data.get("threats", []) or [],
    }


# ──────────────────────────────────────────────────────────────
# LLM-based SWOT: Ollama
# ──────────────────────────────────────────────────────────────
def _ollama_swot(text: str) -> Dict[str, List[str]]:
    """
    Ask an Ollama model (e.g. llama3) to classify SWOT and return JSON.
    """
    base = settings.ollama_base_url.rstrip("/")
    model = settings.ollama_model

    prompt = (
        "You are a precise analyst turning a personality interpretation into a SWOT analysis.\n\n"
        "You will receive bullet-point or paragraph-style text describing a person's traits.\n"
        "Identify distinct ideas and classify them into Strengths, Weaknesses, Opportunities, and Threats.\n\n"
        "Definitions:\n"
        "- Strengths: existing positive qualities, abilities, resources.\n"
        "- Weaknesses: limiting patterns, habits, or tendencies.\n"
        "- Opportunities: ways these qualities can support growth, development, or advantage.\n"
        "- Threats: risks, stress patterns, or factors that may cause problems if ignored.\n\n"
        "Use the user's wording as much as possible, only cleaning spacing.\n"
        "If a bucket has no content, use an empty list for it.\n\n"
        "Return ONLY valid JSON of this shape:\n"
        "{\n"
        "  \"strengths\": [\"...\"],\n"
        "  \"weaknesses\": [\"...\"],\n"
        "  \"opportunities\": [\"...\"],\n"
        "  \"threats\": [\"...\"]\n"
        "}\n\n"
        f"Interpretation text:\n{text}\n\n"
        "Now output the JSON only."
    )

    r = requests.post(
        f"{base}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "format": "json",   # ask Ollama to emit JSON
            "stream": False,
            "options": {
                "num_predict": 512,
                "temperature": 0.1,
            },
        },
        timeout=(settings.timeout_connect_seconds, settings.timeout_seconds),
    )
    r.raise_for_status()

    # For format='json', Ollama returns a JSON string, not a stream.
    txt = r.text.strip()
    data = json.loads(txt)

    return {
        "Strengths": data.get("strengths", []) or [],
        "Weaknesses": data.get("weaknesses", []) or [],
        "Opportunities": data.get("opportunities", []) or [],
        "Threats": data.get("threats", []) or [],
    }


# ──────────────────────────────────────────────────────────────
# Public entry point
# ──────────────────────────────────────────────────────────────
def generate_swot_from_interpretation(text: str) -> Dict[str, List[str]]:
    """
    Main entry point for SWOT creation.

    1. Try LLM-based classification using OpenAI or Ollama (as per settings.llm_provider).
    2. If provider is 'mock', no API key is set, or the call fails, fall back to heuristic.
    3. Always returns a dict with keys:
       'Strengths', 'Weaknesses', 'Opportunities', 'Threats'
       where each value is a list of strings.
    """
    provider = (settings.llm_provider or "").lower()
    logger.info("SWOT: llm_provider=%s", provider or "mock")

    # Fallback early if no text
    if not isinstance(text, str) or not text.strip():
        return {"Strengths": [], "Weaknesses": [], "Opportunities": [], "Threats": []}

    try:
        if provider == "openai" and getattr(settings, "openai_api_key", None):
            return _openai_swot(text)
        elif provider == "ollama":
            return _ollama_swot(text)
        else:
            logger.info("SWOT: using heuristic fallback (provider=%s).", provider or "mock")
            return _heuristic_swot(text)
    except Exception:
        logger.exception("SWOT: LLM-based generation failed; using heuristic fallback.")
        return _heuristic_swot(text)
