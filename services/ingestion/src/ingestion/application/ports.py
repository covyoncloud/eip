"""Ports (interfaces) que les adapters doivent implémenter.

Le domaine et les use cases dépendent de CES abstractions, jamais des implémentations.
C'est le Dependency Inversion Principle en pratique.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import BinaryIO

from ingestion.domain.models import CanonicalWork


class SourceParser(ABC):
    """Port inbound : transforme un fichier source en oeuvres canoniques."""

    @abstractmethod
    def parse(self, stream: BinaryIO) -> list[CanonicalWork]:
        ...

class WorkRepository(ABC):
    """Port outbound : persistance des oeuvres canoniques."""

    @abstractmethod
    def save(self, work: CanonicalWork) -> None:
        ...

    @abstractmethod
    def find_by_business_key(self, key: str) -> CanonicalWork | None:
        ...

    @abstractmethod
    def list_all(self, limit: int = 50, offset: int = 0) -> list[CanonicalWork]:
        ...

class DedupIndex(ABC):
    """Port : index rapide pour savoir si une œuvre a déjà été vue."""

    @abstractmethod
    def exists(self, business_key: str) -> bool:
        ...

    @abstractmethod
    def register(self, business_key: str, work_id: str) -> None:
        ...