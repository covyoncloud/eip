from pathlib import Path
from ingestion.adapters.parsers import CsvParser, JsonParser, XmlParser
FIXTURES = Path(__file__).parent / "fixtures"

def test_csv_parser_reads_all_rows():
    with open(FIXTURES / "sample.csv", "rb") as f:   # "rb" : le parser attend du binaire
        works = CsvParser().parse(f)
    assert len(works) == 3

def test_csv_parser_normalizes_title():
    with open(FIXTURES / "sample.csv", "rb") as f:
        works = CsvParser().parse(f)
    # "BOHEMIAN RHAPSODY" doit être normalisé
    rhapsody = next(w for w in works if "rhapsody" in w.title_normalized)
    assert rhapsody.title_normalized == "bohemian rhapsody"
    assert rhapsody.title_raw == "BOHEMIAN RHAPSODY"   # le brut est préservé

def test_csv_parser_maps_iswc():
    with open(FIXTURES / "sample.csv", "rb") as f:
        works = CsvParser().parse(f)
    crazy = next(w for w in works if w.title_normalized == "crazy in love")
    assert crazy.iswc == "T-345246800-1"

def test_csv_parser_handles_missing_iswc():
    with open(FIXTURES / "sample.csv", "rb") as f:
        works = CsvParser().parse(f)
    imagine = next(w for w in works if w.title_normalized == "imagine")
    assert imagine.iswc is None   # colonne vide -> None

def test_json_parser():
    with open(FIXTURES / "sample.json", "rb") as f:
        works = JsonParser().parse(f)
    assert len(works) == 2
    crazy = next(w for w in works if w.title_normalized == "crazy in love")
    assert crazy.iswc == "T-345246800-1"
    assert len(crazy.artists) == 2                    # liste d'artistes gérée
    assert crazy.identifiers["musicbrainz"] == "mbid-abc"

def test_xml_parser():
    with open(FIXTURES / "sample.xml", "rb") as f:
        works = XmlParser().parse(f)
    assert len(works) == 2
    assert works[0].title_normalized == "crazy in love"