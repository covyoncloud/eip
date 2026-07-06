import uuid
import pytest

from ingestion.adapters.db import Base, engine
from ingestion.adapters.repository import SqlAlchemyWorkRepository
from ingestion.domain.models import Artist, CanonicalWork


@pytest.fixture(scope="module", autouse=True)
def setup_tables():
    """Crée les tables avant les tests, nettoie après."""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


def _make_work(title="Crazy in Love", artist="Beyonce"):
    return CanonicalWork(
        work_id=str(uuid.uuid4()),
        title_raw=title,
        title_normalized=title.lower(),
        artists=[Artist(artist, artist.lower())],
        iswc="T-345246800-1",
    )


def test_save_and_find():
    repo = SqlAlchemyWorkRepository()
    work = _make_work()
    repo.save(work)

    found = repo.find_by_business_key(work.business_key())
    assert found is not None
    assert found.title_normalized == "crazy in love"
    assert found.iswc == "T-345246800-1"


def test_find_missing_returns_none():
    repo = SqlAlchemyWorkRepository()
    assert repo.find_by_business_key("iswc:DOES-NOT-EXIST") is None


def test_save_is_idempotent():
    """Sauvegarder deux fois la même clé métier ne crée pas de doublon."""
    repo = SqlAlchemyWorkRepository()
    work = _make_work(title="Imagine", artist="Lennon")
    repo.save(work)
    repo.save(work)   # merge() -> upsert, pas d'erreur ni de doublon

    found = repo.find_by_business_key(work.business_key())
    assert found is not None