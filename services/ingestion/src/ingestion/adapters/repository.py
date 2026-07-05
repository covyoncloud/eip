"""Repository SQLAlchemy : persistance des oeuvres canoniques dans PostgreSQL/Aurora.

TODO(Sprint 1): définir le modèle SQLAlchemy + Alembic migration.
"""
from __future__ import annotations

from ingestion.application.ports import WorkRepository
from ingestion.domain.models import CanonicalWork


class SqlAlchemyWorkRepository(WorkRepository):
    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def save(self, work: CanonicalWork) -> None:
        raise NotImplementedError  # TODO(Sprint 1)

    def find_by_business_key(self, key: str) -> CanonicalWork | None:
        raise NotImplementedError  # TODO(Sprint 1)


class InMemoryWorkRepository(WorkRepository):
    """Implémentation mémoire pour les tests (pattern à connaître)."""

    def __init__(self) -> None:
        self._store: dict[str, CanonicalWork] = {}

    def save(self, work: CanonicalWork) -> None:
        self._store[work.business_key()] = work

    def find_by_business_key(self, key: str) -> CanonicalWork | None:
        return self._store.get(key)
