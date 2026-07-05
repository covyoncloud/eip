"""Use cases : orchestration métier, indépendante de l'infra."""
from __future__ import annotations

from ingestion.application.ports import SourceParser, WorkRepository


class IngestFileUseCase:
    """Ingest un fichier, normalise, déduplique, persiste.

    TODO(Sprint 1): implémenter la dédup basique via business_key.
    TODO(Sprint 3): brancher la réconciliation Bedrock quand la dédup déterministe échoue.
    """

    def __init__(self, parser: SourceParser, repository: WorkRepository) -> None:
        self._parser = parser
        self._repository = repository

    def execute(self, stream) -> int:
        works = self._parser.parse(stream)
        for work in works:
            existing = self._repository.find_by_business_key(work.business_key())
            if existing is None:
                self._repository.save(work)
            # TODO: sinon, stratégie de merge / réconciliation
        return len(works)
