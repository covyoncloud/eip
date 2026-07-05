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
