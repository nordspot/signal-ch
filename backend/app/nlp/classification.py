"""Text classification — category, language, scope detection."""

import re

import structlog

logger = structlog.get_logger()

# Keyword-based classifier (replaced by Llama in production)
CATEGORY_KEYWORDS = {
    "politics": [
        "bundesrat", "parlament", "nationalrat", "ständerat", "abstimmung",
        "initiative", "referendum", "partei", "wahl", "conseil fédéral",
        "parlement", "votation", "consiglio federale",
    ],
    "economy": [
        "wirtschaft", "unternehmen", "börse", "aktie", "inflation", "snb",
        "konjunktur", "arbeitsmarkt", "économie", "entreprise", "economia",
        "finma", "bank", "kredit",
    ],
    "health": [
        "gesundheit", "bag", "spital", "krankenhaus", "impf", "pandemie",
        "santé", "hôpital", "salute", "swissmedic",
    ],
    "environment": [
        "umwelt", "klima", "energie", "co2", "nachhaltigkeit", "bafu",
        "environnement", "climat", "ambiente", "clima",
    ],
    "education": [
        "bildung", "universität", "schule", "forschung", "eth",
        "éducation", "université", "educazione",
    ],
    "technology": [
        "technologie", "digital", "cyber", "ki", "künstliche intelligenz",
        "software", "startup", "technologie", "numérique", "tecnologia",
    ],
    "legal": [
        "gericht", "urteil", "gesetz", "recht", "bundesgericht",
        "tribunal", "jugement", "loi", "tribunale",
    ],
    "sport": [
        "sport", "fussball", "hockey", "ski", "olympi", "liga",
        "football", "calcio",
    ],
    "infrastructure": [
        "verkehr", "strasse", "bahn", "sbb", "autobahn", "tunnel",
        "transport", "route", "trasporto",
    ],
    "society": [
        "gesellschaft", "migration", "asyl", "integration", "demografie",
        "société", "migration", "società",
    ],
    "culture": [
        "kultur", "museum", "kunst", "film", "musik", "theater",
        "culture", "musée", "cultura", "museo",
    ],
    "science": [
        "wissenschaft", "studie", "forschung", "entdeckung",
        "science", "étude", "scienza", "ricerca",
    ],
    "international": [
        "eu", "europa", "usa", "china", "nato", "uno", "diplomatisch",
        "international", "mondial", "internazionale",
    ],
}

CANTON_CODES = [
    "AG", "AI", "AR", "BE", "BL", "BS", "FR", "GE", "GL", "GR",
    "JU", "LU", "NE", "NW", "OW", "SG", "SH", "SO", "SZ", "TG",
    "TI", "UR", "VD", "VS", "ZG", "ZH",
]

CANTON_NAMES = {
    "aargau": "AG", "appenzell innerrhoden": "AI", "appenzell ausserrhoden": "AR",
    "bern": "BE", "basel-landschaft": "BL", "basel-stadt": "BS", "freiburg": "FR",
    "fribourg": "FR", "genf": "GE", "genève": "GE", "glarus": "GL",
    "graubünden": "GR", "grisons": "GR", "jura": "JU", "luzern": "LU",
    "lucerne": "LU", "neuenburg": "NE", "neuchâtel": "NE", "nidwalden": "NW",
    "obwalden": "OW", "st. gallen": "SG", "schaffhausen": "SH", "solothurn": "SO",
    "schwyz": "SZ", "thurgau": "TG", "tessin": "TI", "ticino": "TI",
    "uri": "UR", "waadt": "VD", "vaud": "VD", "wallis": "VS", "valais": "VS",
    "zug": "ZG", "zürich": "ZH", "zurich": "ZH",
}


def classify_category(text: str) -> str:
    """Classify text into a category based on keyword matching."""
    text_lower = text.lower()
    scores: dict[str, int] = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[category] = score

    if scores:
        return max(scores, key=scores.get)
    return "society"  # default


def detect_language(text: str) -> str:
    """Simple language detection based on common words."""
    text_lower = text.lower()

    fr_words = ["le", "la", "les", "des", "une", "est", "dans", "pour", "avec", "sur"]
    it_words = ["il", "la", "le", "dei", "una", "nel", "per", "con", "sul", "che"]
    de_words = ["der", "die", "das", "und", "ist", "für", "mit", "von", "auf", "ein"]
    en_words = ["the", "and", "for", "with", "that", "this", "from", "have", "has"]

    words = text_lower.split()
    fr_count = sum(1 for w in words if w in fr_words)
    it_count = sum(1 for w in words if w in it_words)
    de_count = sum(1 for w in words if w in de_words)
    en_count = sum(1 for w in words if w in en_words)

    counts = {"de": de_count, "fr": fr_count, "it": it_count, "en": en_count}
    return max(counts, key=counts.get)


def detect_cantons(text: str) -> list[str]:
    """Detect canton references in text."""
    cantons = set()
    text_lower = text.lower()

    # Check canton codes (2-letter)
    for code in CANTON_CODES:
        if re.search(rf"\b{code}\b", text):
            cantons.add(code)

    # Check canton names
    for name, code in CANTON_NAMES.items():
        if name in text_lower:
            cantons.add(code)

    return sorted(cantons)


def detect_scope(cantons: list[str], text: str) -> str:
    """Determine geographic scope."""
    text_lower = text.lower()

    international_markers = ["eu", "europa", "usa", "international", "global", "weltweit"]
    if any(m in text_lower for m in international_markers):
        return "international"

    if not cantons:
        return "national"

    if len(cantons) == 1:
        # Check for commune-level
        if any(word in text_lower for word in ["gemeinde", "commune", "comune", "stadt"]):
            return "communal"
        return "cantonal"

    if len(cantons) <= 3:
        return "regional"

    return "national"
