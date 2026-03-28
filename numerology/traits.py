from typing import Any, Dict, List, Tuple, Set



# helper function for traits.py
def meaning(n: int) -> str:
    return NUMBER_MEANINGS.get(n, "—")


def num_traits(n: int) -> dict:
    """
    Return enriched traits for number n with a safe fallback.
    Always includes the short 'meaning' from NUMBER_MEANINGS.
    """
    base = {
        "title": "",
        "positive": [],
        "negative": [],
        "roles": [],
        "story": "",
        "meaning": meaning(n),   # <- keep the short line for quick summaries
    }
    data = NUMBER_TRAITS.get(n)
    if not data:
        return base
    out = dict(base)
    # merge known keys only (ignore typos)
    for k in ("title", "positive", "negative", "roles", "story"):
        if k in data and data[k] is not None:
            out[k] = data[k]
    return out


def get_compound_traits(code: int) -> dict | None:
    return COMPOUND_TRAITS.get(int(code))


# ── Meanings / mini knowledge base ─────────────────────────────────────────────
NUMBER_MEANINGS = {
    1: "Leadership & initiative; authority, independence (watch ego/dominance).",
    2: "Communication & partnership; diplomacy, tact (watch indecision/gossip).",
    3: "Action & expression; creative, fast-moving (watch impatience/scatter).",
    4: "Strategy & structure; disciplined planner (watch rigidity/over-planning).",
    5: "Path-finder & change; resourceful, adaptable (watch inconsistency/restlessness).",
    6: "Family & finance; caring, responsible, wealth-savvy (watch extravagance/over-attachment).",
    7: "Networking & magnetism; insightful, lucky connector (watch manipulation/addiction risks).",
    8: "Work, ambition & execution; disciplined, dutiful (watch stress/judgment).",
    9: "Humanitarian success; generous, big-picture closer (watch greed/rigidity).",
}

# Quick traits table for F (from your sheet)
F_TRAIT = {
    1: "Decisive leader; self-reliant, initiates tasks.",
    2: "Diplomatic communicator; relationship-oriented.",
    3: "Proactive and expressive; acts fast (can be impatient).",
    4: "Methodical planner; disciplined and reliable.",
    5: "Adaptive problem-solver; restless, change-seeking.",
    6: "Family/finance oriented; caring and responsible.",
    7: "Magnetic networker; lucky, socially connected.",
    8: "Duty-driven and ambitious; carries heavy responsibility.",
    9: "Humanitarian achiever; generous, big-picture thinker.",
}



# details 
NUMBER_TRAITS = {
    1: {
        "title": "The Leader",
        "positive": [
            "Independent personality", "Initiative", "Determined",
            "Creative thought", "Wisdom", "Influential power to inspire others"
        ],
        "negative": [
            "Egoistic", "Too clever", "Aggressive", "Jealous",
            "Can attract backstabbers"
        ],
        "roles": ["Leader", "Father", "Husband", "CEO", "King", "Businessman"],
        "story": "Works like a king, takes initiative and responsibility, but must avoid ego and misuse of influence."
    },
    2: {
        "title": "The Communicator",
        "positive": ["Communication", "Diplomatic", "Mediator", "Sharing", "Partnership"],
        "negative": ["Gossip queen", "Fickle mind", "Argumentative", "Indecisive", "Addiction tendencies"],
        "roles": ["Mother", "Wife", "Peace maker", "Deputy in charge"],
        "story": "Emotion and relationship number; mediates between people, but can fall into gossip or over-dependence."
    },
    3: {
        "title": "Proactive Approach",
        "positive": ["Task oriented", "Spiritual inclined", "Expressive", "Creative", "Fast and action-oriented"],
        "negative": ["Quick tempered", "Argumentative", "Scattered energy", "Unfinished tasks"],
        "roles": ["Son/daughter", "Prince/princess", "Artist", "Emotional", "Creative"],
        "story": "Loves to finish tasks quickly and express creativity, but must avoid impatience and rash decisions."
    },
    4: {
        "title": "Strategist / Planner",
        "positive": ["Strategist", "Planner", "Knowledgeable", "Practical and logical", "Fast learner"],
        "negative": ["Rigid", "Over-thinker", "Lonely", "Greedy", "Extreme seriousness"],
        "roles": ["Prime minister", "Planner", "Advisor"],
        "story": "Strong planner, sharp-minded, reliable. Can be too rigid or overthink instead of executing."
    },
    5: {
        "title": "Path Finder / Joker",
        "positive": ["Resourceful", "Energetic", "Good developer", "All rounder", "Investigative"],
        "negative": ["Directionless", "Restless", "Moody", "Stubborn", "Unreliable"],
        "roles": ["Commander", "Fixer", "Business developer"],
        "story": "Explorer, adaptable, jugadu. Must guard against inconsistency and scattered focus."
    },
    6: {
        "title": "Financial Savvy / Family",
        "positive": ["Family oriented", "Protective", "Discipline", "Wisdom", "Creative", "Knowledge seeker"],
        "negative": ["Extravagant", "Wasteful", "Cowardly", "Self-centered"],
        "roles": ["Financier", "Treasurer", "Accountant"],
        "story": "Family-first and wealth-oriented; strong provider but must control overspending."
    },
    7: {
        "title": "Networking / Luck Factor",
        "positive": ["Networking", "Charismatic", "Lucky", "Spiritual path", "Business minded"],
        "negative": ["Fickle mind", "Argumentative", "Jealous", "Manipulative", "Addiction risk"],
        "roles": ["Priest", "Dictator", "Playboy", "Charmer"],
        "story": "Connector and lucky number; attracts people and opportunities but must avoid misuse of charm."
    },
    8: {
        "title": "Workaholic / Responsible",
        "positive": ["Hard work", "Disciplinarian", "Responsible", "Ambitious", "Loyal", "Efficient execution"],
        "negative": ["Stressed", "Judgmental", "Impatient", "Temperamental", "Struggling"],
        "roles": ["Labourer", "Worker", "Maid", "Servant", "Law field professional"],
        "story": "Number of karma and struggle; brings great rewards through discipline, but risks stress and overwork."
    },
    9: {
        "title": "Business Success / Humanitarian",
        "positive": ["Humanitarian", "Inspirational", "Generous", "Creative", "Leadership"],
        "negative": ["Greedy", "Rigid", "Selfish", "Revengeful", "Low tolerance for failure"],
        "roles": ["Philosopher", "Merchant", "Protector"],
        "story": "Success and humanitarian energy; inspires others but must avoid selfishness and greed."
    },
}



# Compact traits for concatenated reads like AB, CD, EF, IJ, ...
COMPOUND_TRAITS: dict[int, dict] = {
    11: {"positive": "Works alone, independent, mediator; individual thoughts.",
         "negative": "Indecisive, attracts backstabbers; separation tendencies."},
    12: {"positive": "Speaks with authority; specialist; action oriented.",
         "negative": "Straightforward, argumentative."},
    13: {"positive": "Self-motivated, fast, busy individual; action oriented.",
         "negative": "Emotional, hot-tempered, impatient."},
    14: {"positive": "Strong solo planner and developer; systematic.",
         "negative": "Plans but struggles to execute; risk taker; accident prone."},
    15: {"positive": "Travels for work; strongly principled.",
         "negative": "Miserly with money; resists advice; accident prone."},
    16: {"positive": "Financially independent; attracts supporters; modern & stylish.",
         "negative": "Ruthless in business/relations; insensitive."},
    17: {"positive": "Charismatic entrepreneur; builds supporters; travels a lot.",
         "negative": "Supporters may betray; legal/financial/relationship issues."},
    18: {"positive": "Loner & workaholic; always busy to achieve success.",
         "negative": "Stressful; unhealthy practices possible."},
    19: {"positive": "Independent, business-minded; creative ways to succeed.",
         "negative": "Not trusting others; non-cooperative."},
    21: {"positive": "Authoritative communicator; decisive specialist.",
         "negative": "Too blunt; argumentative."},
    22: {"positive": "Vocal, charismatic, refined; neat & clean; deep knowledge.",
         "negative": "Soft-hearted, indecisive; story-teller/gossip."},
    23: {"positive": "Direct, no time wasting; delivers promises.",
         "negative": "Speaks without thinking; offensive; suffers for words."},
    24: {"positive": "Great presenter; talks & plans with wisdom.",
         "negative": "Must deliver or risk legal/relationship issues."},
    25: {"positive": "Principled communicator; attracts supporters.",
         "negative": "Naggy/chaotic talk; indisciplined speech."},
    26: {"positive": "Communicates to make money; family care.",
         "negative": "Money as 'king'; stress & overfocus on wealth."},
    27: {"positive": "Charismatic; attracts opposite sex; networking skills.",
         "negative": "Weak willpower; third-party affairs risk."},
    28: {"positive": "Persuasive speaker; natural salesperson.",
         "negative": "Stressful life; legal/financial issues."},
    29: {"positive": "Strong communicator & planner; business/investments focus.",
         "negative": "Greedy; never satisfied; overly career-minded."},
    31: {"positive": "Passionate & creative planner; energetic.",
         "negative": "Aimless, passive, hot tempered; attracts backstabbers."},
    32: {"positive": "Aggressive communicator; progresses through speech.",
         "negative": "Speaks offensively; problems delivering promises."},
    33: {"positive": "Highly motivated to act; energetic.",
         "negative": "Impulsive; many affairs of the heart; emotional stress."},
    34: {"positive": "Quick sharp mind; fast, planner.",
         "negative": "No time for others; short-term focus only."},
    35: {"positive": "Adapts to change; energetic & aggressive.",
         "negative": "Very emotional, sensitive, moody; health risks."},
    36: {"positive": "Good investor; bold risk-taker.",
         "negative": "Overspending; risky investments; spendthrift."},
    37: {"positive": "Aggressive entrepreneur; gains supporters quickly.",
         "negative": "No loyalty; risk of legal & financial issues."},
    38: {"positive": "Financially independent; success oriented.",
         "negative": "Emotional, naggy, impatient; extreme stress."},
    39: {"positive": "Seeks business opportunities; short-term success.",
         "negative": "Unstable; frequent legal, financial, relationship downfalls."},
    41: {"positive": "Systematic planner; travels for wealth & success.",
         "negative": "Plans derailed by sabotage or lack of focus."},
    42: {"positive": "Great presenter; wise talker.",
         "negative": "Stress from planning/talking; legal issues."},
    43: {"positive": "Quick, sharp-minded; fast planner.",
         "negative": "No time for others; short-term focus."},
    44: {"positive": "Highly intelligent; strong organizer; rule follower.",
         "negative": "Overplanning; rigid; fails to execute."},
    45: {"positive": "Focused planner; good at projects.",
         "negative": "Never satisfied; karmic debt; stubborn."},
    46: {"positive": "Prudent financial planner; attracts supporters.",
         "negative": "Calculative; relationship & marriage issues."},
    47: {"positive": "Good advisor/consultant; learns from elders.",
         "negative": "Exploitative; takes advantage of others."},
    48: {"positive": "Intelligent, hardworking, responsible workaholic.",
         "negative": "Separation, stressful, never satisfied."},
    49: {"positive": "Business strategist; careful planner, visionary.",
         "negative": "Overplanning; greedy; lonely."},
    51: {"positive": "Financially independent; attracts with money talk.",
         "negative": "Self-centered; stubborn."},
    52: {"positive": "Principled communicator; gains support.",
         "negative": "Not compromising; stubborn; self-centered."},
    53: {"positive": "Adaptable, tough, energetic personality.",
         "negative": "Short-tempered; easily provoked; heart disease risk."},
    54: {"positive": "Focused planner; good at developing projects.",
         "negative": "Stubborn; unpredictable; self-destructive."},
    55: {"positive": "Versatile; energetic; family-connected; resilient.",
         "negative": "Relationship/marriage issues; self-sabotage."},
    56: {"positive": "Wise with money; disciplined spender.",
         "negative": "Miserly; relationship & marriage issues."},
    57: {"positive": "Connects with rich/famous; strong influence.",
         "negative": "Supporters betray; legal/financial issues."},
    58: {"positive": "Persistent; energetic; consistent achiever.",
         "negative": "Busy, confused, insecure; creates obstacles."},
    59: {"positive": "Safe, tested methods; cautious success.",
         "negative": "Old-fashioned; stubborn; creates own blocks."},
    61: {"positive": "Financially independent; socially popular.",
         "negative": "Spendthrift; sensitive to comments."},
    62: {"positive": "Communicates for money; family oriented.",
         "negative": "Money as 'king'; inviting stress."},
    63: {"positive": "Good investor; bold, daring risk-taker.",
         "negative": "Spendthrift; overspending."},
    64: {"positive": "Prudent financial planner; attracts support.",
         "negative": "Calculative; relationship issues."},
    65: {"positive": "Well-grounded; wise with money.",
         "negative": "Miserly; relationship issues."},
    66: {"positive": "Money opportunities abound; lucky.",
         "negative": "Overfocus on money; stress."},
    67: {"positive": "Charismatic consultant; hospitable; financial aid.",
         "negative": "Spends money for others; busy-body."},
    68: {"positive": "Creative money-maker; commanding presence.",
         "negative": "High mental stress; insecure."},
    69: {"positive": "Successful investor; 'midas touch'.",
         "negative": "High risk taker; overspending."},
    71: {"positive": "Charismatic entrepreneur; gains supporters; travels.",
         "negative": "Supporters betray; legal/financial issues."},
    72: {"positive": "Charismatic; strong networking skills.",
         "negative": "Weak willpower; risky relationships."},
    73: {"positive": "Aggressive entrepreneur; wins fans quickly.",
         "negative": "No loyalty; legal/relationship risks."},
    74: {"positive": "Many advisers; good at advice.",
         "negative": "Getting wrong advice; misguidance."},
    75: {"positive": "Chance to connect with rich & famous.",
         "negative": "Supporters sabotage; legal/financial trouble."},
    76: {"positive": "Charismatic consultant; creative; hospitable.",
         "negative": "Spends excessively; busy-body."},
    77: {"positive": "Magnetic, lucky, sociable; good networker.",
         "negative": "Manipulative; multiple affairs; exploitative."},
    78: {"positive": "Successful under pressure; stands strong.",
         "negative": "Friends/supporters give stress; sensitive."},
    79: {"positive": "Charismatic & enterprising; lucky in business.",
         "negative": "Overconfident; relationship issues."},
    81: {"positive": "Loner & workaholic; persistent success seeker.",
         "negative": "Stressful; unhealthy practices."},
    82: {"positive": "Persuasive speaker; salesperson.",
         "negative": "Overstressed life; legal/financial issues."},
    83: {"positive": "Financially independent; stable.",
         "negative": "Naggy, impatient, emotional stress."},
    84: {"positive": "Hardworking, responsible workaholic.",
         "negative": "Never satisfied; stressful life."},
    85: {"positive": "Persistent pursuer; highly energetic.",
         "negative": "Busy, confused; insecure."},
    86: {"positive": "Creative communicator; money-making talent.",
         "negative": "High mental stress; relationship issues."},
    87: {"positive": "Enterprising; withstands pressure.",
         "negative": "Exploited by supporters; pressure from peers."},
    88: {"positive": "Successful, lucky, charismatic achiever.",
         "negative": "Overwork; relationship stress; heart issues."},
    89: {"positive": "Persistent; enduring in goals.",
         "negative": "Obstacles before success; relationship issues."},
    91: {"positive": "Independent, talented; succeeds with hard work.",
         "negative": "Not trusting others; non-team player."},
    92: {"positive": "Strong communicator & planner; business talk.",
         "negative": "Loss of humanitarian feeling."},
    93: {"positive": "Aggressive at business; short-term wins.",
         "negative": "Unstable; frequent legal/financial issues."},
    94: {"positive": "Business strategist; visionary planner.",
         "negative": "Greedy; lonely; overplanner."},
    95: {"positive": "Financially independent; emperor’s number.",
         "negative": "Overambitious; selfish; stubborn."},
    96: {"positive": "Midas touch; business brings high returns.",
         "negative": "Egoistic; greedy."},
    97: {"positive": "Charismatic; lucky; successful in business.",
         "negative": "Overconfident; relationship issues."},
    98: {"positive": "Persistent; many opportunities; enduring.",
         "negative": "Obstacles before success; relationship risks."},
    99: {"positive": "Lots of opportunities; creative; wealthy & successful.",
         "negative": "Egoistic; greedy; lonely."},
}


# ────────────────────────────────────────────────────────────────
# ⚡ Excel-style relationship extensions 
# ────────────────────────────────────────────────────────────────

# Each key is a read code (EFCORE, DF, AE, etc.)
# Each value is a dict of flags (True means this issue type applies).
# Expand this mapping as you transcribe more from your Excel sheet.
COMPOUND_ALERTS: dict[str, dict[str, bool]] = {
    # Example in your screenshots: DF marked "Downfall"
    "DF": {"downfall": True},

    # Add others as you find them:
    "AE": {"relationship_issue": True},
    "EFCORE": {"relationship_issue": True},
    "FG": {"marriage_issue": True},
    "IU": {"travel": True},
    "KL": {"never_separate": True},
}

# Define the preferred order when exporting issue_flags
ALERT_TAG_ORDER = [
    "never_separate",
    "relationship_issue",
    "marriage_issue",
    "downfall",
    "travel",
]

# ── Five Elements mapping (matches your Excel lower chart) ─────────────────────

ELEMENT_PRESETS = {
    "excel_style": {  # 2,7=water | 4,9=wood | 3,8=fire | 5=earth | 1,6=metal
        1: "metal", 2: "water", 3: "fire", 4: "wood", 5: "earth",
        6: "metal", 7: "water", 8: "fire", 9: "wood",
    },
    "classical": {  # optional traditional scheme
        1: "water", 2: "earth", 3: "wood", 4: "wood", 5: "earth",
        6: "metal", 7: "metal", 8: "earth", 9: "fire",
    },
}

DEFAULT_ELEMENT_PRESET = "excel_style"


def element_of(n: int, preset: str | None = None) -> str:
    """
    Map a single digit (1–9) to its element category according to the chosen preset.
    Unknown numbers → '—'.
    """
    if n not in range(1, 10):
        return "—"
    p = preset or DEFAULT_ELEMENT_PRESET
    return ELEMENT_PRESETS.get(p, ELEMENT_PRESETS["excel_style"]).get(n, "—")


###----------------------------------------------------------------------###
### HEALTH TRAITS ###
###----------------------------------------------------------------------###

# Health meanings per number (organ-centric, distilled from the user's sheet)
HEALTH_MEANINGS: Dict[int, str] = {
    1: "Head/brain/eyes; headaches; overdrive of will.",
    2: "Throat/thyroid/hormonal balance; cervical region.",
    3: "Heart/circulation/chest; blood pressure swings.",
    4: "Bones/joints/teeth/spine alignment.",
    5: "Liver/digestion/stomach; intestines & absorption.",
    6: "Kidneys/urinary; reproductive; sugar/diabetes tendency.",
    7: "Nervous system; sleep; anxiety/overthinking.",
    8: "Skin/legs; stress-driven fatigue; muscle tension.",
    9: "Blood quality/inflammation; immunity; recovery curve.",
}



# Five-element style table as seen in the screenshot (numbers → organ groups)
ELEMENT_TABLE: Dict[str, Dict[str, Any]] = {
    "Metal": {"numbers": [1, 6], "organs": "Lungs, Large Intestine"},
    "Water": {"numbers": [2, 7], "organs": "Kidney, Bladder"},
    "Fire":  {"numbers": [3, 8], "organs": "Heart, Small Intestine"},
    "Wood":  {"numbers": [4, 8], "organs": "Bones, Eyes, Liver, Gallbladder"},
    "Earth": {"numbers": [5],    "organs": "Pancreas, Stomach, Spleen"},
}

# Helper: all single-value fields in canonical order for triple scanning
TRIPLE_ROWS: List[Tuple[str, Tuple[str, ...]]] = [
    ("ABC", ("A", "B", "C")),
    ("BCD", ("B", "C", "D")),
    ("EGN", ("E", "G", "N")),
    ("FGO", ("F", "G", "O")),
    ("HIJ", ("H", "I", "J")),
    ("KLM", ("K", "L", "M")),
    ("NOP", ("N", "O", "P")),
]

CANCER_TRIPLES: Set[str] = {"333", "555", "222", "666", "888", "999"}
HEART_ATTACK_COMPOUNDS: Set[int] = {33, 35, 53, 38, 83, 88, 58}
NERVOUS_ISSUE_READS: Set[int] = {15, 51}
MENTAL_DISORDER_TRIPLE: str = "685"

# Critical neoplasm helpers (from the sheet: EF=33 => 50%,
# and pairs with 9 add probability). We model these as additive flags.
CRITICAL_NINE_PAIRS: Set[int] = {
    19, 91, 29, 92, 39, 93, 49, 94, 59, 95, 69, 96, 79, 97, 89, 98, 99
}



# ────────────────────────────────────────────────────────────────
# Polarity summary (positions → positive / negative / neutral)
# A,B,E are negative; C,D,F,G are positive; the rest are neutral.
# Input: full triangle dict with sections (inputs/layer1/second_layer/third_layer)
# Output: counts + qualitative balance + detail list
# ────────────────────────────────────────────────────────────────
_POLARITY_POSITIVE = {"C", "D", "F", "G"}
_POLARITY_NEGATIVE = {"A", "B", "E"}

def summarize_polarity(values: dict) -> dict:
    # flatten safely
    flat: Dict[str, int] = {}
    for sec in ("inputs", "layer1", "second_layer", "third_layer"):
        block = values.get(sec) or {}
        if isinstance(block, dict):
            flat.update(block)

    pos = neg = neu = 0
    detail = {"positive": [], "negative": [], "neutral": []}

    for label, digit in flat.items():
        # consider only single-letter cells with int digits
        if not isinstance(label, str) or len(label) != 1 or not isinstance(digit, int):
            continue
        if label in _POLARITY_POSITIVE:
            pos += 1; detail["positive"].append((label, digit))
        elif label in _POLARITY_NEGATIVE:
            neg += 1; detail["negative"].append((label, digit))
        else:
            neu += 1; detail["neutral"].append((label, digit))

    if pos > neg:
        balance = "Mostly positive"
    elif neg > pos:
        balance = "Mostly negative"
    else:
        balance = "Neutral"

    return {
        "positive": pos,
        "negative": neg,
        "neutral": neu,
        "balance": balance,
        "detail": detail,
    }
