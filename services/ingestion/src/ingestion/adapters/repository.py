"""Repository SQLAlchemy : persistance des oeuvres canoniques dans PostgreSQL/Aurora.

TODO(Sprint 1): définir le modèle SQLAlchemy + Alembic migration.
"""
from __future__ import annotations

from ingestion.application.ports import WorkRepository
from ingestion.domain.models import Artist, CanonicalWork
from ingestion.adapters.db import SessionLocal, WorkORM

class SqlAlchemyWorkRepository(WorkRepository):
    def save(self, work: CanonicalWork) -> None:
        with SessionLocal() as s:
            existing = s.query(WorkORM).filter_by(business_key=work.business_key()).first()
            if existing is not None:
                return   # déjà présent -> on ne réinsère pas (idempotence)
            s.add(WorkORM(
                work_id=work.work_id,
                business_key=work.business_key(),
                title_normalized=work.title_normalized,
                title_raw=work.title_raw,
                iswc=work.iswc,
                artists=[{"raw": a.name_raw, "norm": a.name_normalized} for a in work.artists],
                first_release_year=work.first_release_year,
                confidence_score=work.confidence_score,
            ))
            s.commit()

    def find_by_business_key(self, key: str) -> CanonicalWork | None:
        with SessionLocal() as s:
            row = s.query(WorkORM).filter_by(business_key=key).first()
            if row is None:
                return None
            return CanonicalWork(
                work_id=row.work_id, title_raw=row.title_raw,
                title_normalized=row.title_normalized, iswc=row.iswc,
                artists=[Artist(a["raw"], a["norm"]) for a in row.artists],
                first_release_year=row.first_release_year,
            )
    
    def list_all(self, limit: int = 50, offset: int = 0) -> list[CanonicalWork]:
        with SessionLocal() as s:
            rows = (
                s.query(WorkORM)
                .order_by(WorkORM.title_normalized)
                .limit(limit)
                .offset(offset)
                .all()
            )
            return [
                CanonicalWork(
                    work_id=row.work_id,
                    title_raw=row.title_raw,
                    title_normalized=row.title_normalized,
                    iswc=row.iswc,
                    artists=[Artist(a["raw"], a["norm"]) for a in row.artists],
                    first_release_year=row.first_release_year,
                )
                for row in rows
            ]

class InMemoryWorkRepository(WorkRepository):
    """Implémentation mémoire pour les tests (pattern à connaître)."""

    def __init__(self) -> None:
        self._store: dict[str, CanonicalWork] = {}

    def save(self, work: CanonicalWork) -> None:
        self._store[work.business_key()] = work

    def find_by_business_key(self, key: str) -> CanonicalWork | None:
        return self._store.get(key)
    
    def list_all(self, limit: int = 50, offset: int = 0) -> list[CanonicalWork]:
        return list(self._store.values())[offset : offset + limit]
