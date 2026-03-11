"""Named Entity Recognition for Swiss content.

Uses regex patterns + keyword lists for Phase 0.
Will be replaced by fine-tuned spaCy model in Phase 1.
"""

import re

import structlog

logger = structlog.get_logger()


class EntityMention:
    def __init__(self, text: str, entity_type: str, start: int = 0, end: int = 0):
        self.text = text
        self.entity_type = entity_type
        self.start = start
        self.end = end

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "entity_type": self.entity_type,
            "start": self.start,
            "end": self.end,
        }


# Swiss-specific entity patterns
SWISS_PARTIES = {
    "SVP": "political_party", "SP": "political_party", "FDP": "political_party",
    "Die Mitte": "political_party", "Grüne": "political_party", "GLP": "political_party",
    "EDU": "political_party", "EVP": "political_party",
    "UDC": "political_party", "PS": "political_party", "PLR": "political_party",
    "Le Centre": "political_party", "Les Verts": "political_party", "PVL": "political_party",
}

SWISS_INSTITUTIONS = {
    "Bundesrat": "government_body", "Nationalrat": "government_body",
    "Ständerat": "government_body", "Bundesgericht": "government_body",
    "Bundesverwaltungsgericht": "government_body", "FINMA": "government_body",
    "SNB": "government_body", "Schweizerische Nationalbank": "government_body",
    "ETH": "academic_institution", "ETH Zürich": "academic_institution",
    "EPFL": "academic_institution", "Universität Zürich": "academic_institution",
    "Universität Bern": "academic_institution", "Universität Basel": "academic_institution",
    "SBB": "company", "Swisscom": "company", "Post": "company",
    "UBS": "company", "Credit Suisse": "company", "Nestlé": "company",
    "Novartis": "company", "Roche": "company", "ABB": "company",
    "Zurich Insurance": "company", "Swiss Re": "company", "Swatch": "company",
    "Conseil fédéral": "government_body", "Conseil national": "government_body",
    "Conseil des États": "government_body", "Tribunal fédéral": "government_body",
    "Consiglio federale": "government_body",
}

# Swiss company UID pattern: CHE-xxx.xxx.xxx
UID_PATTERN = re.compile(r"CHE-\d{3}\.\d{3}\.\d{3}")

# SR number pattern (law reference)
SR_PATTERN = re.compile(r"SR\s*\d{3}(?:\.\d+)*")

# Money amounts in CHF
CHF_PATTERN = re.compile(r"(?:CHF|Fr\.)\s*[\d',]+(?:\.\d{2})?(?:\s*(?:Mio|Mrd|Milliarden|Millionen))?")

# Dates in Swiss format
DATE_PATTERN = re.compile(r"\d{1,2}\.\s*(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s*\d{4}")


def extract_entities(text: str) -> list[EntityMention]:
    """Extract named entities from text using pattern matching."""
    entities: list[EntityMention] = []

    if not text:
        return entities

    # Political parties
    for name, etype in SWISS_PARTIES.items():
        for match in re.finditer(rf"\b{re.escape(name)}\b", text):
            entities.append(EntityMention(name, etype, match.start(), match.end()))

    # Known institutions/companies
    for name, etype in SWISS_INSTITUTIONS.items():
        for match in re.finditer(rf"\b{re.escape(name)}\b", text):
            entities.append(EntityMention(name, etype, match.start(), match.end()))

    # Company UIDs
    for match in UID_PATTERN.finditer(text):
        entities.append(EntityMention(match.group(), "company", match.start(), match.end()))

    # Law references
    for match in SR_PATTERN.finditer(text):
        entities.append(EntityMention(match.group(), "law", match.start(), match.end()))

    # Financial figures
    for match in CHF_PATTERN.finditer(text):
        entities.append(EntityMention(match.group(), "financial_figure", match.start(), match.end()))

    # Capitalized multi-word names (heuristic for person/org names)
    name_pattern = re.compile(r"\b([A-ZÄÖÜ][a-zäöüéèêàâîôûç]+(?:\s+[A-ZÄÖÜ][a-zäöüéèêàâîôûç]+)+)\b")
    for match in name_pattern.finditer(text):
        name = match.group()
        # Skip if already matched
        if any(e.text == name for e in entities):
            continue
        # Skip very common phrases
        if name.lower() in {"die schweiz", "la suisse", "la svizzera"}:
            continue
        # Classify as person or organization (heuristic)
        entity_type = "person"  # default guess
        org_markers = ["AG", "GmbH", "SA", "Sàrl", "Verein", "Stiftung", "Institut", "Amt"]
        if any(marker in name for marker in org_markers):
            entity_type = "organization"
        entities.append(EntityMention(name, entity_type, match.start(), match.end()))

    # Deduplicate
    seen = set()
    unique_entities = []
    for e in entities:
        key = (e.text, e.entity_type)
        if key not in seen:
            seen.add(key)
            unique_entities.append(e)

    return unique_entities
