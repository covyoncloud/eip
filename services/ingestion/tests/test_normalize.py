from ingestion.adapters.parsers import _normalize


def test_lowercase():
    assert _normalize("BEYONCE") == "beyonce"


def test_removes_accents():
    assert _normalize("Beyoncé") == "beyonce"


def test_removes_punctuation():
    assert _normalize("Crazy in Love!!!") == "crazy in love"


def test_collapses_spaces():
    assert _normalize("crazy   in    love") == "crazy in love"


def test_strips_edges():
    assert _normalize("  Hello  ") == "hello"


def test_empty_string():
    assert _normalize("") == ""


def test_full_case():
    # le cas réel : deux graphies doivent converger
    assert _normalize("Beyoncé — Crazy In Love") == _normalize("BEYONCE Crazy in Love")