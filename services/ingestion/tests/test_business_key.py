from ingestion.domain.models import Artist, CanonicalWork


def test_business_key_prefers_iswc():
    w = CanonicalWork(work_id="1", title_raw="X", title_normalized="x", iswc="T-123")
    assert w.business_key() == "iswc:T-123"


def test_business_key_falls_back_to_title_artist():
    w = CanonicalWork(
        work_id="1", title_raw="Crazy in Love", title_normalized="crazy in love",
        artists=[Artist(name_raw="Beyonce", name_normalized="beyonce")],
    )
    assert w.business_key() == "tn:crazy in love|ar:beyonce"
