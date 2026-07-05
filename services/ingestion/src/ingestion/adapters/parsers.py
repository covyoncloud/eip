"""Parsers concrets : CSV, JSON, XML -> CanonicalWork.

Chaque source a son format ; tous produisent le même pivot.
TODO(Sprint 1): implémenter la normalisation (casse, accents, dates, dédup titre).
"""
from __future__ import annotations

import uuid
from typing import BinaryIO

from ingestion.application.ports import SourceParser
from ingestion.domain.models import Artist, CanonicalWork


def _normalize(text: str) -> str:
    """TODO: unidecode + lower + strip + collapse spaces + retirer ponctuation."""
    return text.strip().lower()


class CsvParser(SourceParser):
    def parse(self, stream: BinaryIO) -> list[CanonicalWork]:
        # TODO(Sprint 1): csv.DictReader -> mapping vers CanonicalWork
        raise NotImplementedError


class JsonParser(SourceParser):
    def parse(self, stream: BinaryIO) -> list[CanonicalWork]:
        # TODO(Sprint 1): json.load -> mapping (format MusicBrainz / Discogs)
        raise NotImplementedError


class XmlParser(SourceParser):
    def parse(self, stream: BinaryIO) -> list[CanonicalWork]:
        # TODO(Sprint 1): ElementTree -> mapping (format legacy "sale")
        raise NotImplementedError


def _example_stub() -> CanonicalWork:
    """Exemple de construction d'une oeuvre pivot (à supprimer une fois les parsers faits)."""
    title = "Crazy in Love"
    return CanonicalWork(
        work_id=str(uuid.uuid4()),
        title_raw=title,
        title_normalized=_normalize(title),
        artists=[Artist(name_raw="Beyoncé", name_normalized=_normalize("Beyoncé"))],
    )
