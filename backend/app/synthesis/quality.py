"""Quality checks for synthesized content."""

import re

import structlog

logger = structlog.get_logger()

MAX_CONSECUTIVE_WORDS = 10


def check_originality(synthesis_text: str, source_texts: list[str]) -> dict:
    """Check that synthesis doesn't reproduce too many consecutive words from any source.

    Per spec: NEVER reproduce more than 10 consecutive words from any single source.
    """
    violations = []
    synthesis_words = synthesis_text.split()

    for source_text in source_texts:
        source_words = source_text.split()
        if len(source_words) < MAX_CONSECUTIVE_WORDS:
            continue

        for i in range(len(source_words) - MAX_CONSECUTIVE_WORDS + 1):
            window = " ".join(source_words[i : i + MAX_CONSECUTIVE_WORDS])
            if window.lower() in synthesis_text.lower():
                violations.append({
                    "matched_text": window,
                    "source_text": source_text[:100] + "...",
                })

    return {
        "is_original": len(violations) == 0,
        "violations": violations,
        "consecutive_word_limit": MAX_CONSECUTIVE_WORDS,
    }


def check_attribution(content: dict) -> dict:
    """Verify that interpretive sections have proper attributions."""
    issues = []

    for section in content.get("sections", []):
        if section.get("type") in ("interpretation", "factual_core"):
            attributions = section.get("attributions", [])
            if not attributions:
                issues.append({
                    "section_type": section["type"],
                    "issue": "Missing source attribution",
                })

    return {
        "has_proper_attribution": len(issues) == 0,
        "issues": issues,
    }


def check_missing_voices(content: dict) -> bool:
    """Check if the synthesis includes a 'missing_voices' section."""
    for section in content.get("sections", []):
        if section.get("type") == "missing_voices":
            return True
    return False


def compute_quality_score(content: dict, source_count: int) -> dict:
    """Compute overall quality metrics for a synthesis."""
    quality = content.get("quality_assessment", {})

    # Confirmation density based on source count
    if source_count >= 5:
        confirmation = 0.9
    elif source_count >= 3:
        confirmation = 0.7
    elif source_count >= 2:
        confirmation = 0.5
    else:
        confirmation = 0.3

    # Override with AI assessment if available
    confirmation = quality.get("confirmation_density", confirmation)
    completeness = quality.get("completeness_score", 0.5)
    missing = quality.get("missing_elements", [])

    return {
        "confirmation_density": confirmation,
        "completeness_score": completeness,
        "missing_elements": missing,
        "source_count": source_count,
        "has_missing_voices_section": check_missing_voices(content),
        "has_proper_attribution": check_attribution(content)["has_proper_attribution"],
    }
