

# Core essence for each single number (Mulank / Bhagyank)
# These are distilled from your detailed MEANINGS[1..9].
PAIR_CORE = {
    1: {
        "label": "Leadership, authority, independence, management",
        "strength_tags": [
            "strong leadership",
            "independent decision-making",
            "strategic management",
        ],
        "weakness_tags": [
            "aggression",
            "trust issues",
        ],
    },
    2: {
        "label": "Communication, emotional sensitivity, loyalty, creativity",
        "strength_tags": [
            "communication skills",
            "emotional intelligence",
            "loyal, supportive nature",
        ],
        "weakness_tags": [
            "fickle-mindedness",
            "mood swings",
        ],
    },
    3: {
        "label": "Pro-activeness, discipline, growth, spiritual guidance",
        "strength_tags": [
            "proactive initiative",
            "discipline and structure",
            "guiding and advising others",
        ],
        "weakness_tags": [
            "aggression",
            "impatience",
        ],
    },
    4: {
        "label": "Strategy, planning, practicality, system-oriented thinking",
        "strength_tags": [
            "strategic planning",
            "practical and logical approach",
            "system-driven work style",
        ],
        "weakness_tags": [
            "stubbornness",
            "unpredictable temper",
        ],
    },
    5: {
        "label": "Adaptability, communication, movement, analytical mind",
        "strength_tags": [
            "adaptability and flexibility",
            "sharp communication",
            "analytical and calculative thinking",
        ],
        "weakness_tags": [
            "restlessness",
            "unreliable tendencies",
        ],
    },
    6: {
        "label": "Love, care, relationships, family focus, luxury",
        "strength_tags": [
            "loving and caring nature",
            "family-oriented mindset",
            "diplomatic and harmonious approach",
        ],
        "weakness_tags": [
            "over-spending",
            "weak support system or boundaries",
        ],
    },
    7: {
        "label": "Intuition, research, analysis, networking, spiritual depth",
        "strength_tags": [
            "intuitive insight",
            "research and investigation",
            "magnetic networking ability",
        ],
        "weakness_tags": [
            "manipulative behaviour",
            "emotional detachment",
        ],
    },
    8: {
        "label": "Discipline, hard work, ambition, responsibility, judgment",
        "strength_tags": [
            "strong discipline",
            "hard-working attitude",
            "ambition with responsibility",
        ],
        "weakness_tags": [
            "stress and pressure",
            "tension-prone nature",
        ],
    },
    9: {
        "label": "Courage, name and fame, humanitarian expression, passion",
        "strength_tags": [
            "courage and bravery",
            "drive for name and fame",
            "humanitarian and expressive nature",
        ],
        "weakness_tags": [
            "ego",
            "strong emotional reactions",
        ],
    },
}


def _combine_strengths(base: dict, support: dict) -> list[str]:
    """
    Build 3 combined strength sentences from base + support strength_tags.
    """
    bs = base["strength_tags"]
    ss = support["strength_tags"]

    return [
        f"{bs[0].capitalize()} supported by {ss[0]}",
        f"{bs[1].capitalize()} backed by {ss[1]}",
        f"{bs[2].capitalize()} balanced with {ss[2]}",
    ]


def _combine_weaknesses(base: dict, support: dict) -> list[str]:
    """
    Build 2 combined weakness sentences from base + support weakness_tags.
    """
    bw = base["weakness_tags"]
    sw = support["weakness_tags"]

    return [
        f"{bw[0].capitalize()} amplified by {sw[0]}",
        f"{bw[1].capitalize()} combined with {sw[1]}",
    ]


def _combined_summary(m: int, b: int, base: dict, support: dict, strengths: list[str]) -> str:
    """
    Short combined paragraph for each (mulank, bhagyank) pair.
    """
    return (
        f"Mulank {m} gives {base['label'].lower()}, while Bhagyank {b} adds "
        f"{support['label'].lower()}. Together, this combination often shows "
        f"{strengths[0].lower()} and {strengths[1].lower()}, creating a pattern where "
        f"the core nature of {m} is shaped and supported by the qualities of {b}."
    )


def build_pair_meanings() -> dict[tuple[int, int], dict]:
    """
    Build PAIR_MEANINGS for all (mulank, bhagyank) from 1–9.

    Structure:
    PAIR_MEANINGS[(m, b)] = {
        "ruled_by": "<essence of mulank>",
        "supported_by": "<essence of bhagyank>",
        "combined": {
            "strengths": [str, str, str],
            "weakness": [str, str],
            "summary": str,
        },
    }
    """
    pairs: dict[tuple[int, int], dict] = {}

    for m in range(1, 10):
        base = PAIR_CORE[m]
        for b in range(1, 10):
            support = PAIR_CORE[b]

            strengths = _combine_strengths(base, support)
            weakness = _combine_weaknesses(base, support)
            summary = _combined_summary(m, b, base, support, strengths)

            pairs[(m, b)] = {
                "ruled_by": base["label"],
                "supported_by": support["label"],
                "combined": {
                    "strengths": strengths,
                    "weakness": weakness,
                    "summary": summary,
                },
            }

    return pairs


# Final ready-to-use dataset:
PAIR_MEANINGS = build_pair_meanings()
