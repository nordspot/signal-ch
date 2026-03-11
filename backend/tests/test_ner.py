"""Tests for the NER module."""

from app.nlp.ner import extract_entities


def test_extract_political_parties():
    text = "Die SVP und SP haben sich gegen den Vorschlag ausgesprochen."
    entities = extract_entities(text)
    names = [e.text for e in entities]
    assert "SVP" in names
    assert "SP" in names


def test_extract_institutions():
    text = "Der Bundesrat und die FINMA haben neue Regulierungen beschlossen."
    entities = extract_entities(text)
    names = [e.text for e in entities]
    assert "Bundesrat" in names
    assert "FINMA" in names


def test_extract_companies():
    text = "UBS und Nestlé melden Quartalsergebnisse."
    entities = extract_entities(text)
    names = [e.text for e in entities]
    assert "UBS" in names
    assert "Nestlé" in names


def test_extract_uid():
    text = "Die Firma CHE-123.456.789 wurde im Handelsregister eingetragen."
    entities = extract_entities(text)
    uids = [e for e in entities if e.entity_type == "company" and "CHE-" in e.text]
    assert len(uids) == 1
    assert uids[0].text == "CHE-123.456.789"


def test_extract_chf_amounts():
    text = "Der Kredit beträgt CHF 5 Mio und die Kosten belaufen sich auf Fr. 200'000."
    entities = extract_entities(text)
    financials = [e for e in entities if e.entity_type == "financial_figure"]
    assert len(financials) >= 1


def test_extract_law_references():
    text = "Gemäss SR 210 und SR 220.1 gelten die folgenden Bestimmungen."
    entities = extract_entities(text)
    laws = [e for e in entities if e.entity_type == "law"]
    assert len(laws) >= 1
