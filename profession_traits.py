# numerology/profession_traits.py
# Meanings for (Mulank, Bhagyank) pairs. Keys are tuples (m, b).
# Fields: stars (string rating), professions (list[str]), remark (free text).

# helper functions


STAR_MEANINGS = {
    "5star": "Exceptional and highly favourable combination; strongly supports recognition, authority, wealth, stability and long-term success.",
    "4.5star": "Very strong, excellent combination; supports consistent progress, influence, growth and above-average results in career and life.",
    "4star": "Strong and successful combination; generally favourable for career, leadership, money and stable long-term growth with effort.",
    "3.5star": "Very good, above-average combination; good support for opportunities, growth and visibility when actions are focused and disciplined.",
    "3star": "Good, workable combination; with consistent effort it can give steady progress, moderate success and reasonable stability.",
    "2.5star": "Average to slightly favourable combination; requires conscious effort and discipline to convert opportunities into stable success.",
    "2star": "Below-average, somewhat challenging combination; progress is slower and needs extra hard work, planning and guidance to stabilise.",
    "1.5star": "Struggle-oriented combination; frequent obstacles and delays, demanding patience, resilience and corrective measures.",
    "1star": "Difficult and adverse combination; high chances of setbacks, stress and instability unless strong remedies and discipline are applied.",
}


def star_meaning(stars: str) -> str:
    """
    Convert 'stars' field like '3.5star' or '**1/2' or '?' into
    a clean human-readable meaning.
    """
    if not stars:
        return ""

    s = stars.strip().lower()

    # direct match (your clean labels)
    if s in STAR_MEANINGS:
        return STAR_MEANINGS[s]

    # half-star patterns like "*1/2", "**1/2"
    if "1/2" in s:
        # convert patterns like "**1/2"
        star_count = s.count("*")
        numeric = star_count + 0.5
        key = f"{numeric}star"
        return STAR_MEANINGS.get(key, "average")

    # pure patterns like "***"
    if set(s) == {"*"}:
        numeric = len(s)
        key = f"{numeric}star"
        return STAR_MEANINGS.get(key, "good")

    # '?' or complex patterns like '**(****)'
    if "?" in s or "(" in s:
        return "anti / finance issue"

    return "unknown"


PAIRS = {
    # ── Mulank 1 ──────────────────────────────────────────────────────────────
    (1, 1): {
        "stars": "4star",
        "professions": [
            "Business & entrepreneurship",
            "Corporate leadership & management",
            "Politics & public administration",
            "Government services & civil administration",
            "Defence services (Army / armed forces)",
            "C-suite and CEO roles",
            "Hotel & hospitality management",
            "Design & creative direction",
        ],
        "remark": "Good, excellent, successful",
    },
    (1, 2): {
        "stars": "3.5star",
        "professions": [
            "Navy & maritime services",
            "Marine & water-based industries",
            "Dairy & milk products business",
            "Business & entrepreneurship",
            "Corporate leadership & management",
            "Politics & public administration",
            "Government services & civil administration",
            "Defence services (Army / armed forces)",
            "C-suite and CEO roles",
            "Hotel & hospitality management",
            "Design & creative direction",
        ],
        "remark": "",
    },
    (1, 3): {
        "stars": "3.5star",
        "professions": [
            "Academic & education sector",
            "Research & knowledge-based roles",
            "Spirituality & occult sciences",
            "Coaching, mentoring & training",
            "Business & entrepreneurship",
            "Corporate leadership & management",
            "Politics & public administration",
            "Government services & civil administration",
            "Defence services (Army / armed forces)",
            "C-suite and CEO roles",
            "Hotel & hospitality management",
            "Design & creative direction",
        ],
        "remark": "king maker chankyaa amit shah",
    },
    (1, 4): {
        "stars": "3star",
        "professions": [
            "Business & entrepreneurship",
            "Strategic management & consulting",
            "Corporate leadership & management",
            "Politics & public administration",
            "Government services & civil administration",
            "Defence services (Army / armed forces)",
            "C-suite and CEO roles",
            "Hotel & hospitality management",
            "Design & creative direction",
        ],
        "remark": "",
    },
    (1, 5): {
        "stars": "4star",
        "professions": [
            "Banking & financial services",
            "Investment & wealth management",
            "Business & entrepreneurship",
            "Corporate leadership & management",
            "Politics & public administration",
            "Government services & civil administration",
            "Defence services (Army / armed forces)",
            "C-suite and CEO roles",
            "Hotel & hospitality management",
            "Design & creative direction",
        ],
        "remark": "",
    },
    (1, 6): {
        "stars": "3.5star",
        "professions": [
            "Media & entertainment industry",
            "Film & television production",
            "Travel & tourism",
            "Hotel & hospitality management",
            "Business & entrepreneurship",
            "Corporate leadership & management",
            "Politics & public administration",
            "Government services & civil administration",
            "Defence services (Army / armed forces)",
            "C-suite and CEO roles",
            "Design & creative direction",
        ],
        "remark": "",
    },
    (1, 7): {
        "stars": "3star",
        "professions": [
            "Education & academic leadership",
            "Research & analysis",
            "Spirituality & occult sciences",
            "Business & entrepreneurship",
            "Corporate leadership & management",
            "Politics & public administration",
            "Government services & civil administration",
            "Defence services (Army / armed forces)",
            "C-suite and CEO roles",
            "Hotel & hospitality management",
            "Design & creative direction",
        ],
        "remark": "",
    },
    (1, 8): {
        "stars": "?",
        "professions": [
            "Hard-work intensive industries",
            "Challenging and high-responsibility roles",
            "Business & entrepreneurship",
            "Corporate leadership & management",
            "Politics & public administration",
            "Government services & civil administration",
            "Defence services (Army / armed forces)",
            "C-suite and CEO roles",
            "Hotel & hospitality management",
            "Design & creative direction",
        ],
        "remark": "Struggle",
    },
    (1, 9): {
        "stars": "5star",
        "professions": [
            "Public-facing roles with fame & recognition",
            "Business & entrepreneurship",
            "Corporate leadership & management",
            "Politics & public administration",
            "Government services & civil administration",
            "Defence services (Army / armed forces)",
            "C-suite and CEO roles",
            "Hotel & hospitality management",
            "Design & creative direction",
        ],
        "remark": "super anything",
    },

    # ── Mulank 2 ──────────────────────────────────────────────────────────────
    (2, 1): {
        "stars": "3star",
        "professions": [
            "Nursing & patient care",
            "Public relations & hospitality",
            "Psychology & counselling",
            "Medical & healthcare professions",
            "Import–export & international trade administration",
            "Physician / clinical practice",
            "Creative & fine arts",
            "Agriculture & agri-business",
            "Music & performing arts",
            "Water-related industries",
            "Dairy & milk products business",
        ],
        "remark": "successful,",
    },
    (2, 2): {
        "stars": "2star",
        "professions": [
            "Water-related industries",
            "Dairy & milk products business",
            "Nursing & patient care",
            "Public relations & hospitality",
            "Psychology & counselling",
            "Medical & healthcare professions",
            "Import–export & international trade administration",
            "Physician / clinical practice",
            "Creative & fine arts",
            "Agriculture & agri-business",
            "Music & performing arts",
        ],
        "remark": "",
    },
    (2, 3): {
        "stars": "2.5star",
        "professions": [
            "Teaching & education",
            "Spirituality & occult sciences",
            "Nursing & patient care",
            "Public relations & hospitality",
            "Psychology & counselling",
            "Medical & healthcare professions",
            "Import–export & international trade administration",
            "Physician / clinical practice",
            "Creative & fine arts",
            "Agriculture & agri-business",
            "Music & performing arts",
            "Water-related industries",
            "Dairy & milk products business",
        ],
        "remark": "",
    },
    (2, 4): {
        "stars": "1star",
        "professions": [
            "Nursing & patient care",
            "Public relations & hospitality",
            "Psychology & counselling",
            "Medical & healthcare professions",
            "Import–export & international trade administration",
            "Physician / clinical practice",
            "Creative & fine arts",
            "Agriculture & agri-business",
            "Music & performing arts",
            "Water-related industries",
            "Dairy & milk products business",
        ],
        "remark": "opposite combination, depression,struggle",
    },
    (2, 5): {
        "stars": "3.5star",
        "professions": [
            "Real-estate & property business",
            "Banking & financial services",
            "Investment & wealth management",
            "Nursing & patient care",
            "Public relations & hospitality",
            "Psychology & counselling",
            "Medical & healthcare professions",
            "Import–export & international trade administration",
            "Physician / clinical practice",
            "Creative & fine arts",
            "Agriculture & agri-business",
            "Music & performing arts",
            "Water-related industries",
            "Dairy & milk products business",
        ],
        "remark": "",
    },
    (2, 6): {
        "stars": "2.5star",
        "professions": [
            "Luxury goods & lifestyle business",
            "Confectionery & sweets business",
            "Nursing & patient care",
            "Public relations & hospitality",
            "Psychology & counselling",
            "Medical & healthcare professions",
            "Import–export & international trade administration",
            "Physician / clinical practice",
            "Creative & fine arts",
            "Agriculture & agri-business",
            "Music & performing arts",
            "Water-related industries",
            "Dairy & milk products business",
        ],
        "remark": "",
    },
    (2, 7): {
        "stars": "**(****)",
        "professions": [
            "Nursing & patient care",
            "Public relations & hospitality",
            "Psychology & counselling",
            "Medical & healthcare professions",
            "Import–export & international trade administration",
            "Physician / clinical practice",
            "Creative & fine arts",
            "Agriculture & agri-business",
            "Music & performing arts",
            "Water-related industries",
            "Dairy & milk products business",
        ],
        "remark": "4star (work on intution,occult,research),2 star(anythingelse)",
    },
    (2, 8): {
        "stars": "?",
        "professions": [
            "Nursing & patient care",
            "Public relations & hospitality",
            "Psychology & counselling",
            "Medical & healthcare professions",
            "Import–export & international trade administration",
            "Physician / clinical practice",
            "Creative & fine arts",
            "Agriculture & agri-business",
            "Music & performing arts",
            "Water-related industries",
            "Dairy & milk products business",
        ],
        "remark": "struggle,health,money",
    },
    (2, 9): {
        "stars": "1star",
        "professions": [
            "Nursing & patient care",
            "Public relations & hospitality",
            "Psychology & counselling",
            "Medical & healthcare professions",
            "Import–export & international trade administration",
            "Physician / clinical practice",
            "Creative & fine arts",
            "Agriculture & agri-business",
            "Music & performing arts",
            "Water-related industries",
            "Dairy & milk products business",
        ],
        "remark": "married life question mark",
    },

    # ── Mulank 3 ──────────────────────────────────────────────────────────────
    (3, 1): {
        "stars": "3star",
        "professions": [
            "Education & teaching",
            "Medical & healing professions",
            "Academic & school leadership",
            "Banking & financial services",
            "Spiritual teaching & guidance",
            "Bureaucratic & administrative services",
            "Priest / spiritual director / film direction",
            "Occult & metaphysical studies",
            "Counselling & advisory services",
            "Architecture & urban planning",
            "Interior design & space planning",
        ],
        "remark": "",
    },
    (3, 2): {
        "stars": "2.5star",
        "professions": [
            "Education linked with water / dairy sector",
            "Education & teaching",
            "Medical & healing professions",
            "Academic & school leadership",
            "Banking & financial services",
            "Spiritual teaching & guidance",
            "Bureaucratic & administrative services",
            "Priest / spiritual director / film direction",
            "Occult & metaphysical studies",
            "Counselling & advisory services",
            "Architecture & urban planning",
            "Interior design & space planning",
        ],
        "remark": "",
    },
    (3, 3): {
        "stars": "3.5star",
        "professions": [
            "Stationery & educational supplies",
            "Education & teaching",
            "Occult science & spiritual studies",
            "Medical & healing professions",
            "Academic & school leadership",
            "Banking & financial services",
            "Spiritual teaching & guidance",
            "Bureaucratic & administrative services",
            "Priest / spiritual director / film direction",
            "Counselling & advisory services",
            "Architecture & urban planning",
            "Interior design & space planning",
        ],
        "remark": "good starter bad finisher",
    },
    (3, 4): {
        "stars": "2.5star",
        "professions": [
            "Sales & marketing",
            "Legal practice & advocacy",
            "Education & teaching",
            "Medical & healing professions",
            "Academic & school leadership",
            "Banking & financial services",
            "Spiritual teaching & guidance",
            "Bureaucratic & administrative services",
            "Priest / spiritual director / film direction",
            "Occult & metaphysical studies",
            "Counselling & advisory services",
            "Architecture & urban planning",
            "Interior design & space planning",
        ],
        "remark": "",
    },
    (3, 5): {
        "stars": "3.5star",
        "professions": [
            "Communication & public speaking",
            "Voice-over & media presentation",
            "Media & broadcasting",
            "Film & content direction",
            "Education & teaching",
            "Medical & healing professions",
            "Academic & school leadership",
            "Banking & financial services",
            "Spiritual teaching & guidance",
            "Bureaucratic & administrative services",
            "Priest / spiritual director / film direction",
            "Occult & metaphysical studies",
            "Counselling & advisory services",
            "Architecture & urban planning",
            "Interior design & space planning",
        ],
        "remark": "",
    },
    (3, 6): {
        "stars": "?",
        "professions": [
            "Education & teaching",
            "Medical & healing professions",
            "Academic & school leadership",
            "Banking & financial services",
            "Spiritual teaching & guidance",
            "Bureaucratic & administrative services",
            "Priest / spiritual director / film direction",
            "Occult & metaphysical studies",
            "Counselling & advisory services",
            "Architecture & urban planning",
            "Interior design & space planning",
        ],
        "remark": "anticombination,difficult but successful, delay in marriage , health issue",
    },
    (3, 7): {
        "stars": "**(****)",
        "professions": [
            "Education & teaching",
            "Medical & healing professions",
            "Academic & school leadership",
            "Banking & financial services",
            "Spiritual teaching & guidance",
            "Bureaucratic & administrative services",
            "Priest / spiritual director / film direction",
            "Occult & metaphysical studies",
            "Counselling & advisory services",
            "Architecture & urban planning",
            "Interior design & space planning",
        ],
        "remark": "4star (work on occult,PHD,doctor),2 star(anything else)",
    },
    (3, 8): {
        "stars": "2.5star",
        "professions": [
            "Judiciary & legal services",
            "Printing & publishing industry",
            "Education & teaching",
            "Medical & healing professions",
            "Academic & school leadership",
            "Banking & financial services",
            "Spiritual teaching & guidance",
            "Bureaucratic & administrative services",
            "Priest / spiritual director / film direction",
            "Occult & metaphysical studies",
            "Counselling & advisory services",
            "Architecture & urban planning",
            "Interior design & space planning",
        ],
        "remark": "",
    },
    (3, 9): {
        "stars": "2star",
        "professions": [
            "Army & defence services",
            "Police & security services",
            "Civil services (IAS, administrative roles)",
            "Education & teaching",
            "Medical & healing professions",
            "Academic & school leadership",
            "Banking & financial services",
            "Spiritual teaching & guidance",
            "Bureaucratic & administrative services",
            "Priest / spiritual director / film direction",
            "Occult & metaphysical studies",
            "Counselling & advisory services",
            "Architecture & urban planning",
            "Interior design & space planning",
        ],
        "remark": "",
    },

    # ── Mulank 4 ──────────────────────────────────────────────────────────────
    (4, 1): {
        "stars": "3star",
        "professions": [
            "Politics & strategic leadership",
            "Business & entrepreneurship",
            "Legal practice & advocacy",
            "Strategy & policy consulting",
            "Electronics & hardware business",
            "Computer & IT services",
            "Recycling & waste-management industry",
            "Technical & IT departments",
            "Long-distance travel & logistics",
            "Management consulting",
            "Pharmaceuticals & medical supplies",
            "Detective & investigative services",
            "Sales & business development",
        ],
        "remark": "",
    },
    (4, 2): {
        "stars": "1star",
        "professions": [
            "Electronics & hardware business",
            "Computer & IT services",
            "Recycling & waste-management industry",
            "Technical & IT departments",
            "Long-distance travel & logistics",
            "Management consulting",
            "Pharmaceuticals & medical supplies",
            "Detective & investigative services",
            "Sales & business development",
        ],
        "remark": "strugling, depression",
    },
    (4, 3): {
        "stars": "2.5star",
        "professions": [
            "Sales & marketing",
            "Education & training",
            "Electronics & hardware business",
            "Computer & IT services",
            "Recycling & waste-management industry",
            "Technical & IT departments",
            "Long-distance travel & logistics",
            "Management consulting",
            "Pharmaceuticals & medical supplies",
            "Detective & investigative services",
            "Sales & business development",
        ],
        "remark": "",
    },
    (4, 4): {
        "stars": "1.5star",
        "professions": [
            "Sales & marketing",
            "Legal practice & advocacy",
            "Business & entrepreneurship",
            "Electronics & hardware business",
            "Computer & IT services",
            "Recycling & waste-management industry",
            "Technical & IT departments",
            "Long-distance travel & logistics",
            "Management consulting",
            "Pharmaceuticals & medical supplies",
            "Detective & investigative services",
            "Sales & business development",
        ],
        "remark": "",
    },
    (4, 5): {
        "stars": "3star",
        "professions": [
            "Media & communications",
            "Legal practice & advocacy",
            "Banking & financial services",
            "Investment & wealth management",
            "Electronics & hardware business",
            "Computer & IT services",
            "Recycling & waste-management industry",
            "Technical & IT departments",
            "Long-distance travel & logistics",
            "Management consulting",
            "Pharmaceuticals & medical supplies",
            "Detective & investigative services",
            "Sales & business development",
        ],
        "remark": "",
    },
    (4, 6): {
        "stars": "3star",
        "professions": [
            "Legal practice & advocacy",
            "Media & entertainment",
            "Alcohol & beverages industry",
            "Hotel & hospitality management",
            "Airlines & aviation services",
            "Electronics & hardware business",
            "Computer & IT services",
            "Recycling & waste-management industry",
            "Technical & IT departments",
            "Long-distance travel & logistics",
            "Management consulting",
            "Pharmaceuticals & medical supplies",
            "Detective & investigative services",
            "Sales & business development",
        ],
        "remark": "",
    },
    (4, 7): {
        "stars": "4star",
        "professions": [
            "Electronics & hardware business",
            "Computer & IT services",
            "Recycling & waste-management industry",
            "Technical & IT departments",
            "Long-distance travel & logistics",
            "Management consulting",
            "Pharmaceuticals & medical supplies",
            "Detective & investigative services",
            "Sales & business development",
        ],
        "remark": "bit delayed but good resullts in eductaion,occult",
    },
    (4, 8): {
        "stars": "1star",
        "professions": [
            "Army & defence services",
            "Judiciary & legal services",
            "Police & security services",
            "Electronics & hardware business",
            "Computer & IT services",
            "Recycling & waste-management industry",
            "Technical & IT departments",
            "Long-distance travel & logistics",
            "Management consulting",
            "Pharmaceuticals & medical supplies",
            "Detective & investigative services",
            "Sales & business development",
        ],
        "remark": "",
    },
    (4, 9): {
        "stars": "1star",
        "professions": [
            "Electronics & hardware business",
            "Computer & IT services",
            "Recycling & waste-management industry",
            "Technical & IT departments",
            "Long-distance travel & logistics",
            "Management consulting",
            "Pharmaceuticals & medical supplies",
            "Detective & investigative services",
            "Sales & business development",
        ],
        "remark": "struggling,setbacks,health issue",
    },

    # ── Mulank 5 ──────────────────────────────────────────────────────────────
    (5, 1): {
        "stars": "4star",
        "professions": [
            "High-impact communication in any field",
            "News reading & anchoring",
            "Spiritual speaking & motivational talks",
            "Real-estate & property business",
            "Journalism & reporting",
            "Corporate training & facilitation",
            "Media & printing industry",
            "Stationery & office supplies business",
            "Voice-over & dubbing artist",
            "Sales & business development",
            "Banking & chartered accountancy",
            "Web design & digital services",
        ],
        "remark": "",
    },
    (5, 2): {
        "stars": "3.5star",
        "professions": [
            "Real-estate & property business",
            "News reading & anchoring",
            "Spiritual speaking & motivational talks",
            "Journalism & reporting",
            "Corporate training & facilitation",
            "Media & printing industry",
            "Stationery & office supplies business",
            "Voice-over & dubbing artist",
            "Sales & business development",
            "Banking & chartered accountancy",
            "Web design & digital services",
        ],
        "remark": "",
    },
    (5, 3): {
        "stars": "3star",
        "professions": [
            "Education & teaching",
            "Media & communications",
            "Interior design & decor",
            "News reading & anchoring",
            "Spiritual speaking & motivational talks",
            "Real-estate & property business",
            "Journalism & reporting",
            "Corporate training & facilitation",
            "Media & printing industry",
            "Stationery & office supplies business",
            "Voice-over & dubbing artist",
            "Sales & business development",
            "Banking & chartered accountancy",
            "Web design & digital services",
        ],
        "remark": "",
    },
    (5, 4): {
        "stars": "3star",
        "professions": [
            "Banking & financial services",
            "Legal practice & advocacy",
            "News reading & anchoring",
            "Spiritual speaking & motivational talks",
            "Real-estate & property business",
            "Journalism & reporting",
            "Corporate training & facilitation",
            "Media & printing industry",
            "Stationery & office supplies business",
            "Voice-over & dubbing artist",
            "Sales & business development",
            "Banking & chartered accountancy",
            "Web design & digital services",
        ],
        "remark": "",
    },
    (5, 5): {
        "stars": "4star",
        "professions": [
            "Banking & financial services",
            "News reading & anchoring",
            "Spiritual speaking & motivational talks",
            "Real-estate & property business",
            "Journalism & reporting",
            "Corporate training & facilitation",
            "Media & printing industry",
            "Stationery & office supplies business",
            "Voice-over & dubbing artist",
            "Sales & business development",
            "Banking & chartered accountancy",
            "Web design & digital services",
        ],
        "remark": "",
    },
    (5, 6): {
        "stars": "4star",
        "professions": [
            "Travel & tourism",
            "Media & entertainment",
            "Luxury products & lifestyle business",
            "News reading & anchoring",
            "Spiritual speaking & motivational talks",
            "Real-estate & property business",
            "Journalism & reporting",
            "Corporate training & facilitation",
            "Media & printing industry",
            "Stationery & office supplies business",
            "Voice-over & dubbing artist",
            "Sales & business development",
            "Banking & chartered accountancy",
            "Web design & digital services",
        ],
        "remark": "",
    },
    (5, 7): {
        "stars": "3star",
        "professions": [
            "Occult sciences & spiritual research",
            "Research & data/IT fields",
            "Education & knowledge-based roles",
            "News reading & anchoring",
            "Spiritual speaking & motivational talks",
            "Real-estate & property business",
            "Journalism & reporting",
            "Corporate training & facilitation",
            "Media & printing industry",
            "Stationery & office supplies business",
            "Voice-over & dubbing artist",
            "Sales & business development",
            "Banking & chartered accountancy",
            "Web design & digital services",
        ],
        "remark": "",
    },
    (5, 8): {
        "stars": "3star",
        "professions": [
            "Real-estate & property development",
            "Administration & operations management",
            "News reading & anchoring",
            "Spiritual speaking & motivational talks",
            "Property & asset management",
            "Journalism & reporting",
            "Corporate training & facilitation",
            "Media & printing industry",
            "Stationery & office supplies business",
            "Voice-over & dubbing artist",
            "Sales & business development",
            "Banking & chartered accountancy",
            "Web design & digital services",
        ],
        "remark": "",
    },
    (5, 9): {
        "stars": "3star",
        "professions": [
            "Army & defence services",
            "Administrative & government services",
            "News reading & anchoring",
            "Spiritual speaking & motivational talks",
            "Real-estate & property business",
            "Journalism & reporting",
            "Corporate training & facilitation",
            "Media & printing industry",
            "Stationery & office supplies business",
            "Voice-over & dubbing artist",
            "Sales & business development",
            "Banking & chartered accountancy",
            "Web design & digital services",
        ],
        "remark": "",
    },

    # ── Mulank 6 ──────────────────────────────────────────────────────────────
    (6, 1): {
        "stars": "3.5star",
        "professions": [
            "Glamour & fashion industry",
            "Travel & tourism",
            "Hotel & hospitality management",
            "Fashion design & styling",
            "Music & performing arts",
            "Interior design & decor",
            "Perfume & fragrance industry",
            "Architecture & space design",
            "Drama & theatre",
            "Garment export–import business",
            "Photography & visual arts",
            "Salons & beauty services",
            "Fine arts & creative professions",
            "Airline cabin crew & hospitality",
            "Jewellery & luxury accessories",
            "Spa & wellness services",
        ],
        "remark": "",
    },
    (6, 2): {
        "stars": "2.5star",
        "professions": [
            "Confectionery & sweets business",
            "Dairy & milk products",
            "Fashion design & styling",
            "Music & performing arts",
            "Interior design & decor",
            "Perfume & fragrance industry",
            "Architecture & space design",
            "Drama & theatre",
            "Travel & tourism",
            "Garment export–import business",
            "Photography & visual arts",
            "Salons & beauty services",
            "Fine arts & creative professions",
            "Airline cabin crew & hospitality",
            "Jewellery & luxury accessories",
            "Spa & wellness services",
        ],
        "remark": "",
    },
    (6, 3): {
        "stars": "?",
        "professions": [
            "Fashion design & styling",
            "Music & performing arts",
            "Interior design & decor",
            "Perfume & fragrance industry",
            "Architecture & space design",
            "Drama & theatre",
            "Travel & tourism",
            "Garment export–import business",
            "Photography & visual arts",
            "Salons & beauty services",
            "Fine arts & creative professions",
            "Airline cabin crew & hospitality",
            "Jewellery & luxury accessories",
            "Spa & wellness services",
        ],
        "remark": "profession successful , family emptiness",
    },
    (6, 4): {
        "stars": "3star",
        "professions": [
            "Media & communications",
            "Legal practice & advocacy",
            "Luxury products & lifestyle business",
            "Fashion design & styling",
            "Music & performing arts",
            "Interior design & decor",
            "Perfume & fragrance industry",
            "Architecture & space design",
            "Drama & theatre",
            "Travel & tourism",
            "Garment export–import business",
            "Photography & visual arts",
            "Salons & beauty services",
            "Fine arts & creative professions",
            "Airline cabin crew & hospitality",
            "Jewellery & luxury accessories",
            "Spa & wellness services",
        ],
        "remark": "",
    },
    (6, 5): {
        "stars": "4star",
        "professions": [
            "Luxury products & premium lifestyle business",
            "Glamour & fashion industry",
            "Travel & tourism",
            "Fashion design & styling",
            "Music & performing arts",
            "Interior design & decor",
            "Perfume & fragrance industry",
            "Architecture & space design",
            "Drama & theatre",
            "Garment export–import business",
            "Photography & visual arts",
            "Salons & beauty services",
            "Fine arts & creative professions",
            "Airline cabin crew & hospitality",
            "Jewellery & luxury accessories",
            "Spa & wellness services",
        ],
        "remark": "",
    },
    (6, 6): {
        "stars": "4star",
        "professions": [
            "Luxury & glamour industry",
            "Modelling & celebrity work",
            "Singing & performance arts",
            "Acting & film/TV roles",
            "Fashion design & styling",
            "Music & performing arts",
            "Interior design & decor",
            "Perfume & fragrance industry",
            "Architecture & space design",
            "Drama & theatre",
            "Travel & tourism",
            "Garment export–import business",
            "Photography & visual arts",
            "Salons & beauty services",
            "Fine arts & creative professions",
            "Airline cabin crew & hospitality",
            "Jewellery & luxury accessories",
            "Spa & wellness services",
        ],
        "remark": "",
    },
    (6, 7): {
        "stars": "3.5star",
        "professions": [
            "Professional sports & athletics",
            "Occult sciences & spiritual work",
            "Luxury products & high-end services",
            "Teaching & training",
            "Fashion design & styling",
            "Music & performing arts",
            "Interior design & decor",
            "Perfume & fragrance industry",
            "Architecture & space design",
            "Drama & theatre",
            "Travel & tourism",
            "Garment export–import business",
            "Photography & visual arts",
            "Salons & beauty services",
            "Fine arts & creative professions",
            "Airline cabin crew & hospitality",
            "Jewellery & luxury accessories",
            "Spa & wellness services",
        ],
        "remark": "",
    },
    (6, 8): {
        "stars": "3star",
        "professions": [
            "Legal practice & advocacy",
            "Media & communications",
            "Fashion design & styling",
            "Music & performing arts",
            "Interior design & decor",
            "Perfume & fragrance industry",
            "Architecture & space design",
            "Drama & theatre",
            "Travel & tourism",
            "Garment export–import business",
            "Photography & visual arts",
            "Salons & beauty services",
            "Fine arts & creative professions",
            "Airline cabin crew & hospitality",
            "Jewellery & luxury accessories",
            "Spa & wellness services",
        ],
        "remark": "",
    },
    (6, 9): {
        "stars": "3star",
        "professions": [
            "Fame-oriented careers (media, arts, public life)",
            "Fashion design & styling",
            "Music & performing arts",
            "Interior design & decor",
            "Perfume & fragrance industry",
            "Architecture & space design",
            "Drama & theatre",
            "Travel & tourism",
            "Garment export–import business",
            "Photography & visual arts",
            "Salons & beauty services",
            "Fine arts & creative professions",
            "Airline cabin crew & hospitality",
            "Jewellery & luxury accessories",
            "Spa & wellness services",
        ],
        "remark": "along with controvery,married life issue",
    },

    # ── Mulank 7 ──────────────────────────────────────────────────────────────
    (7, 1): {
        "stars": "4star",
        "professions": [
            "Occult sciences & spiritual research",
            "Priest & ritual specialist",
            "Biotechnology & scientific research",
            "Drama, theatre & performing arts",
            "Religious & spiritual products business",
            "Foreign languages (interpreter / translator)",
            "Film & entertainment industry (Bollywood etc.)",
            "PhD / advanced academic research",
            "Spiritual teaching & guidance",
            "Glamour & creative industries",
        ],
        "remark": "",
    },
    (7, 2): {
        "stars": "**(****)",
        "professions": [
            "Priest & ritual specialist",
            "Biotechnology & scientific research",
            "Drama, theatre & performing arts",
            "Religious & spiritual products business",
            "Foreign languages (interpreter / translator)",
            "Film & entertainment industry (Bollywood etc.)",
            "PhD / advanced academic research",
            "Spiritual teaching & guidance",
            "Glamour & creative industries",
        ],
        "remark": "4star (work on intution,occult,research),2 star(anythingelse)",
    },
    (7, 3): {
        "stars": "***(****)",
        "professions": [
            "Priest & ritual specialist",
            "Biotechnology & scientific research",
            "Drama, theatre & performing arts",
            "Religious & spiritual products business",
            "Foreign languages (interpreter / translator)",
            "Film & entertainment industry (Bollywood etc.)",
            "PhD / advanced academic research",
            "Spiritual teaching & guidance",
            "Glamour & creative industries",
        ],
        "remark": "4star(education,occult)and 3 star (doctor&IAS)",
    },
    (7, 4): {
        "stars": "4star",
        "professions": [
            "Priest & ritual specialist",
            "Biotechnology & scientific research",
            "Drama, theatre & performing arts",
            "Religious & spiritual products business",
            "Foreign languages (interpreter / translator)",
            "Film & entertainment industry (Bollywood etc.)",
            "PhD / advanced academic research",
            "Spiritual teaching & guidance",
            "Glamour & creative industries",
        ],
        "remark": "bit delayed but good resullts in eductaion,occult",
    },
    (7, 5): {
        "stars": "3star",
        "professions": [
            "Occult sciences & spiritual research",
            "Research, data & computer fields",
            "Education & knowledge-based roles",
            "Priest & ritual specialist",
            "Biotechnology & scientific research",
            "Drama, theatre & performing arts",
            "Religious & spiritual products business",
            "Foreign languages (interpreter / translator)",
            "Film & entertainment industry (Bollywood etc.)",
            "PhD / advanced academic research",
            "Spiritual teaching & guidance",
            "Glamour & creative industries",
        ],
        "remark": "",
    },
    (7, 6): {
        "stars": "4star",
        "professions": [
            "Priest & ritual specialist",
            "Biotechnology & scientific research",
            "Drama, theatre & performing arts",
            "Religious & spiritual products business",
            "Foreign languages (interpreter / translator)",
            "Film & entertainment industry (Bollywood etc.)",
            "PhD / advanced academic research",
            "Spiritual teaching & guidance",
            "Glamour & creative industries",
        ],
        "remark": "good in physical sport,occult ,luxury ,teaching",
    },
    (7, 7): {
        "stars": "1star",
        "professions": [
            "Priest & ritual specialist",
            "Biotechnology & scientific research",
            "Drama, theatre & performing arts",
            "Religious & spiritual products business",
            "Foreign languages (interpreter / translator)",
            "Film & entertainment industry (Bollywood etc.)",
            "PhD / advanced academic research",
            "Spiritual teaching & guidance",
            "Glamour & creative industries",
        ],
        "remark": "disappointment,setbacks, extramateriala affairs , empty life",
    },
    (7, 8): {
        "stars": "1.5star",
        "professions": [
            "Priest & ritual specialist",
            "Biotechnology & scientific research",
            "Drama, theatre & performing arts",
            "Religious & spiritual products business",
            "Foreign languages (interpreter / translator)",
            "Film & entertainment industry (Bollywood etc.)",
            "PhD / advanced academic research",
            "Spiritual teaching & guidance",
            "Glamour & creative industries",
        ],
        "remark": "delayed teaching and research",
    },
    (7, 9): {
        "stars": "2star",
        "professions": [
            "Teaching in occult & spiritual fields",
            "Priest & ritual specialist",
            "Biotechnology & scientific research",
            "Drama, theatre & performing arts",
            "Religious & spiritual products business",
            "Foreign languages (interpreter / translator)",
            "Film & entertainment industry (Bollywood etc.)",
            "PhD / advanced academic research",
            "Spiritual teaching & guidance",
            "Glamour & creative industries",
        ],
        "remark": "",
    },

    # ── Mulank 8 ──────────────────────────────────────────────────────────────
    (8, 1): {
        "stars": "?",
        "professions": [
            "High-responsibility management roles",
            "Construction & infrastructure industry",
            "Judiciary & legal services (judge, senior lawyer)",
            "Iron & metal industry",
            "Leather & footwear products",
            "Spiritual teaching & guidance",
            "Labour-intensive industries & operations",
            "Correctional and execution-related services",
        ],
        "remark": "struggle",
    },
    (8, 2): {
        "stars": "?",
        "professions": [
            "High-responsibility management roles",
            "Construction & infrastructure industry",
            "Judiciary & legal services (judge, senior lawyer)",
            "Iron & metal industry",
            "Leather & footwear products",
            "Spiritual teaching & guidance",
            "Labour-intensive industries & operations",
            "Correctional and execution-related services",
        ],
        "remark": "struggle",
    },
    (8, 3): {
        "stars": "2.5star",
        "professions": [
            "Judiciary & legal services",
            "Printing & publishing industry",
            "High-responsibility management roles",
            "Construction & infrastructure industry",
            "Judiciary & legal services (judge, senior lawyer)",
            "Iron & metal industry",
            "Leather & footwear products",
            "Spiritual teaching & guidance",
            "Labour-intensive industries & operations",
            "Correctional and execution-related services",
        ],
        "remark": "",
    },
    (8, 4): {
        "stars": "1star",
        "professions": [
            "Army & defence services",
            "Judiciary & legal enforcement",
            "Police & security services",
            "High-responsibility management roles",
            "Construction & infrastructure industry",
            "Judiciary & legal services (judge, senior lawyer)",
            "Iron & metal industry",
            "Leather & footwear products",
            "Spiritual teaching & guidance",
            "Labour-intensive industries & operations",
            "Correctional and execution-related services",
        ],
        "remark": "",
    },
    (8, 5): {
        "stars": "3star",
        "professions": [
            "Real-estate & property development",
            "Administration & operations management",
            "Leather & footwear industry",
            "High-responsibility management roles",
            "Construction & infrastructure industry",
            "Judiciary & legal services (judge, senior lawyer)",
            "Iron & metal industry",
            "Spiritual teaching & guidance",
            "Labour-intensive industries & operations",
            "Correctional and execution-related services",
        ],
        "remark": "",
    },
    (8, 6): {
        "stars": "3star",
        "professions": [
            "Legal practice & advocacy",
            "Media & communications",
            "High-responsibility management roles",
            "Construction & infrastructure industry",
            "Judiciary & legal services (judge, senior lawyer)",
            "Iron & metal industry",
            "Leather & footwear products",
            "Spiritual teaching & guidance",
            "Labour-intensive industries & operations",
            "Correctional and execution-related services",
        ],
        "remark": "",
    },
    (8, 7): {
        "stars": "1.5star",
        "professions": [
            "High-responsibility management roles",
            "Construction & infrastructure industry",
            "Judiciary & legal services (judge, senior lawyer)",
            "Iron & metal industry",
            "Leather & footwear products",
            "Spiritual teaching & guidance",
            "Labour-intensive industries & operations",
            "Correctional and execution-related services",
        ],
        "remark": "delayed teaching and research",
    },
    (8, 8): {
        "stars": "1star",
        "professions": [
            "High-responsibility management roles",
            "Construction & infrastructure industry",
            "Judiciary & legal services (judge, senior lawyer)",
            "Iron & metal industry",
            "Leather & footwear products",
            "Spiritual teaching & guidance",
            "Labour-intensive industries & operations",
            "Correctional and execution-related services",
        ],
        "remark": "bad, struggle ,hardwork,shoe and leather",
    },
    (8, 9): {
        "stars": "1.5star",
        "professions": [
            "Delayed success in career",
            "Army & police services",
            "High-responsibility management roles",
            "Construction & infrastructure industry",
            "Judiciary & legal services (judge, senior lawyer)",
            "Iron & metal industry",
            "Leather & footwear products",
            "Spiritual teaching & guidance",
            "Labour-intensive industries & operations",
            "Correctional and execution-related services",
        ],
        "remark": "",
    },

    # ── Mulank 9 ──────────────────────────────────────────────────────────────
    (9, 1): {
        "stars": "4star",
        "professions": [
            "Army & defence services",
            "Police & paramilitary services",
            "Defence & security sector",
            "Fitness & gym training",
            "Surgical & medical specialties",
            "Competitive sports & Olympics",
            "Civil services (IAS, top administration)",
            "Manufacturing & metallurgy (raw to finished goods)",
            "Metallurgy & heavy industry",
            "Commanding & leadership positions",
            "Military & strategic services",
            "Hotel & hospitality industry",
        ],
        "remark": "",
    },
    (9, 2): {
        "stars": "2star",
        "professions": [
            "Defence & security sector",
            "Fitness & gym training",
            "Police & paramilitary services",
            "Surgical & medical specialties",
            "Competitive sports & Olympics",
            "Civil services (IAS, top administration)",
            "Manufacturing & metallurgy (raw to finished goods)",
            "Metallurgy & heavy industry",
            "Commanding & leadership positions",
            "Military & strategic services",
            "Hotel & hospitality industry",
        ],
        "remark": "married life ?",
    },
    (9, 3): {
        "stars": "2.5star",
        "professions": [
            "Medical profession (doctor)",
            "Civil services (IAS)",
            "Administration & operations",
            "Teaching & academic roles",
            "Defence & security sector",
            "Fitness & gym training",
            "Police & paramilitary services",
            "Surgical & medical specialties",
            "Competitive sports & Olympics",
            "Manufacturing & metallurgy (raw to finished goods)",
            "Metallurgy & heavy industry",
            "Commanding & leadership positions",
            "Military & strategic services",
            "Hotel & hospitality industry",
        ],
        "remark": "",
    },
    (9, 4): {
        "stars": "1star",
        "professions": [
            "Defence & security sector",
            "Fitness & gym training",
            "Police & paramilitary services",
            "Surgical & medical specialties",
            "Competitive sports & Olympics",
            "Civil services (IAS, top administration)",
            "Manufacturing & metallurgy (raw to finished goods)",
            "Metallurgy & heavy industry",
            "Commanding & leadership positions",
            "Military & strategic services",
            "Hotel & hospitality industry",
        ],
        "remark": "strugge ,health",
    },
    (9, 5): {
        "stars": "3star",
        "professions": [
            "Army & defence services",
            "Administration & government roles",
            "Defence & security sector",
            "Fitness & gym training",
            "Police & paramilitary services",
            "Surgical & medical specialties",
            "Competitive sports & Olympics",
            "Civil services (IAS, top administration)",
            "Manufacturing & metallurgy (raw to finished goods)",
            "Metallurgy & heavy industry",
            "Commanding & leadership positions",
            "Military & strategic services",
            "Hotel & hospitality industry",
        ],
        "remark": "",
    },
    (9, 6): {
        "stars": "3star",
        "professions": [
            "Fame-oriented public careers",
            "Defence & security sector",
            "Fitness & gym training",
            "Police & paramilitary services",
            "Surgical & medical specialties",
            "Competitive sports & Olympics",
            "Civil services (IAS, top administration)",
            "Manufacturing & metallurgy (raw to finished goods)",
            "Metallurgy & heavy industry",
            "Commanding & leadership positions",
            "Military & strategic services",
            "Hotel & hospitality industry",
        ],
        "remark": "",
    },
    (9, 7): {
        "stars": "2star",
        "professions": [
            "Teaching in occult & spiritual subjects",
            "Defence & security sector",
            "Fitness & gym training",
            "Police & paramilitary services",
            "Surgical & medical specialties",
            "Competitive sports & Olympics",
            "Civil services (IAS, top administration)",
            "Manufacturing & metallurgy (raw to finished goods)",
            "Metallurgy & heavy industry",
            "Commanding & leadership positions",
            "Military & strategic services",
            "Hotel & hospitality industry",
        ],
        "remark": "",
    },
    (9, 8): {
        "stars": "1.5star",
        "professions": [
            "Delayed success in army & police services",
            "Defence & security sector",
            "Fitness & gym training",
            "Police & paramilitary services",
            "Surgical & medical specialties",
            "Competitive sports & Olympics",
            "Civil services (IAS, top administration)",
            "Manufacturing & metallurgy (raw to finished goods)",
            "Metallurgy & heavy industry",
            "Commanding & leadership positions",
            "Military & strategic services",
            "Hotel & hospitality industry",
        ],
        "remark": "",
    },
    (9, 9): {
        "stars": "1star",
        "professions": [
            "Simple, service-oriented lifestyle roles",
            "Defence & security sector",
            "Fitness & gym training",
            "Police & paramilitary services",
            "Surgical & medical specialties",
            "Competitive sports & Olympics",
            "Civil services (IAS, top administration)",
            "Manufacturing & metallurgy (raw to finished goods)",
            "Metallurgy & heavy industry",
            "Commanding & leadership positions",
            "Military & strategic services",
            "Hotel & hospitality industry",
        ],
        "remark": "no name ,no fame ,simple life",
    },
}


def _normalize_profession_label(p: str) -> str:
    """
    Map similar / raw profession labels to a clean, canonical form
    so that near-duplicates also get merged.

    Examples:
    - "army", "Army", "army and police" -> "Army & defence services" / "Army & police services"
    - "hotel", "Hotel industry" -> "Hotel & hospitality management"
    - "media", "Media, printing media" -> "Media & printing industry" / "Media & communications"
    """
    if not p:
        return ""

    txt = p.strip()
    lower = txt.lower()

    # --- Defence / police / security ---
    if "army" in lower or "military" in lower or "defence" in lower or "defense" in lower:
        if "police" in lower:
            return "Army & police services"
        return "Army & defence services"
    if "police" in lower or "security" in lower:
        return "Police & security services"

    # --- Hotel / hospitality / tourism ---
    if "hotel" in lower or "hospitality" in lower:
        return "Hotel & hospitality management"
    if "tour and travel" in lower or "tourism" in lower or "travel" in lower:
        return "Travel & tourism"

    # --- Media / journalism / printing ---
    if "news reader" in lower or "newsreading" in lower or "anchor" in lower:
        return "News reading & anchoring"
    if "journalism" in lower or "journalist" in lower:
        return "Journalism & reporting"
    if "media" in lower and "printing" in lower:
        return "Media & printing industry"
    if "media" in lower:
        return "Media & communications"

    # --- Banking / finance / ca ---
    if "bank" in lower or "banking" in lower or "ca" in lower or "finance" in lower or "financial" in lower:
        return "Banking & financial services"

    # --- Law / judiciary ---
    if "lawyer" in lower or "law " in lower or "legal" in lower:
        return "Legal practice & advocacy"
    if "judge" in lower or "judic" in lower:
        return "Judiciary & legal services"

    # --- Real estate / property ---
    if "real state" in lower or "real estate" in lower or "real-estate" in lower or "property" in lower:
        return "Real-estate & property business"

    # --- Teaching / education / counselling ---
    if "teaching" in lower or "teacher" in lower or "education" in lower or "school" in lower:
        return "Education & teaching"
    if "counselling" in lower or "counseling" in lower or "psychologist" in lower:
        return "Psychology & counselling"

    # --- Healthcare / doctor / medicine ---
    if "doctor" in lower or "physician" in lower or "surgeon" in lower:
        return "Medical & healthcare professions"
    if "medicine" in lower or "healthcare" in lower or "nursing" in lower:
        return "Medical & healthcare professions"

    # --- Spiritual / occult ---
    if "occult" in lower:
        return "Occult sciences & spiritual research"
    if "spiritual" in lower or "pandit" in lower or "puja" in lower:
        return "Spiritual teaching & guidance"

    # --- IT / computer / electronics ---
    if "computer" in lower or "it " in lower or "technical dept" in lower:
        return "Computer & IT services"
    if "electronics" in lower:
        return "Electronics & hardware business"

    # --- Fashion / glamour / arts ---
    if "fashion" in lower:
        return "Fashion design & styling"
    if "glamour" in lower or "model" in lower or "acting" in lower or "drama" in lower:
        return "Glamour & performing arts"
    if "music" in lower or "singer" in lower:
        return "Music & performing arts"
    if "interior" in lower:
        return "Interior design & decor"

    # --- Sales / marketing / consulting ---
    if "sales" in lower or "marketing" in lower:
        return "Sales & marketing"
    if "consult" in lower or "advisory" in lower:
        return "Management consulting & advisory"

    # --- Construction / iron / leather ---
    if "construction" in lower:
        return "Construction & infrastructure industry"
    if "iron" in lower or "metallurgy" in lower or "metal" in lower:
        return "Metallurgy & heavy industry"
    if "leather" in lower or "shoe" in lower or "footwear" in lower:
        return "Leather & footwear industry"

    # --- Real generic tweaks ---
    if txt.lower() == "business":
        return "Business & entrepreneurship"

    # default: cleaned original
    return txt


def _dedupe_professions_in_pairs():
    """
    Remove duplicate and similar professions inside each PAIRS[(mulank, bhagyank)] list.

    - Normalizes labels first (case, wording, synonyms)
    - Keeps the first occurrence, preserves order
    - Ignores empty labels
    """
    for key, data in PAIRS.items():
        seen = set()
        unique = []
        cleaned = []

        # 1) normalize each label
        for p in data.get("professions", []):
            canon = _normalize_profession_label(p)
            if canon:  # skip empty after normalization
                cleaned.append(canon)

        # 2) dedupe while preserving order
        for p in cleaned:
            if p not in seen:
                seen.add(p)
                unique.append(p)

        data["professions"] = unique



# run once on import so everyone using PAIRS gets the cleaned data
_dedupe_professions_in_pairs()
