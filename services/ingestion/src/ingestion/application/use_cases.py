"""Use cases : orchestration métier, indépendante de l'infra."""
from __future__ import annotations

from ingestion.application.ports import SourceParser, WorkRepository

class IngestFileUseCase:
    def __init__(self, parser, repository, dedup_index=None):
        self._parser = parser
        self._repository = repository
        self._dedup = dedup_index

    def execute(self, stream) -> int:
        works = self._parser.parse(stream)
        saved = 0
        for work in works:
            key = work.business_key()
            if self._dedup is not None:
                if self._dedup.exists(key):        # DynamoDB : déjà vu ?
                    continue
                self._repository.save(work)         # Aurora : stockage canonique
                self._dedup.register(key, work.work_id)  # DynamoDB : on enregistre
            else:
                # fallback local/tests : dédup via Aurora
                if self._repository.find_by_business_key(key) is None:
                    self._repository.save(work)
            saved += 1
        return saved
