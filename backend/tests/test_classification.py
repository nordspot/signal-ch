"""Tests for the text classification module."""

from app.nlp.classification import classify_category, detect_cantons, detect_language, detect_scope


def test_classify_politics():
    text = "Der Bundesrat hat heute eine neue Verordnung beschlossen"
    assert classify_category(text) == "politics"


def test_classify_economy():
    text = "Die SNB senkt den Leitzins um 0.25 Prozentpunkte"
    assert classify_category(text) == "economy"


def test_classify_health():
    text = "Das BAG meldet neue Empfehlungen zur Impfung"
    assert classify_category(text) == "health"


def test_detect_language_de():
    text = "Der Bundesrat hat die neue Verordnung beschlossen und für gut befunden"
    assert detect_language(text) == "de"


def test_detect_language_fr():
    text = "Le Conseil fédéral a décidé de la nouvelle ordonnance pour les citoyens"
    assert detect_language(text) == "fr"


def test_detect_cantons():
    text = "Im Kanton Zürich und Bern wurden neue Regelungen eingeführt"
    cantons = detect_cantons(text)
    assert "ZH" in cantons
    assert "BE" in cantons


def test_detect_scope_national():
    assert detect_scope([], "Der Bundesrat beschliesst") == "national"


def test_detect_scope_cantonal():
    assert detect_scope(["ZH"], "Im Kanton Zürich") == "cantonal"


def test_detect_scope_international():
    assert detect_scope([], "Die EU hat neue Regelungen") == "international"
