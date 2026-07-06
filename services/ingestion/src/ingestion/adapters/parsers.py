"""Parsers concrets : CSV, JSON, XML -> CanonicalWork.

Chaque source a son format ; tous produisent le même pivot.
TODO(Sprint 1): implémenter la normalisation (casse, accents, dates, dédup titre).
"""
from __future__ import annotations

import uuid
import re
import unicodedata
import csv
import json
import io
import xml.etree.ElementTree as ET

from ingestion.domain.models import Artist, CanonicalWork
from typing import BinaryIO
from ingestion.application.ports import SourceParser
from ingestion.domain.models import Artist, CanonicalWork

def _normalize(text: str) -> str:
    if not text:
        return ""
    # décompose les accents (é -> e + accent) puis retire les accents
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)     # ponctuation -> espace
    text = re.sub(r"\s+", " ", text).strip()  # espaces multiples -> un seul
    return text

class CsvParser(SourceParser):
    def parse(self, stream: BinaryIO) -> list[CanonicalWork]:
        text = io.TextIOWrapper(stream, encoding="utf-8")
        reader = csv.DictReader(text)
        works = []
        for row in reader:
            title = (row.get("title") or "").strip()
            artist = (row.get("artist") or "").strip()
            year = row.get("year")
            works.append(CanonicalWork(
                work_id=str(uuid.uuid4()),
                title_raw=title,
                title_normalized=_normalize(title),
                artists=[Artist(artist, _normalize(artist))] if artist else [],
                iswc=(row.get("iswc") or None),
                first_release_year=int(year) if year and year.isdigit() else None,
                source_records=["csv"],
            ))
        return works

class JsonParser(SourceParser):
    def parse(self, stream: BinaryIO) -> list[CanonicalWork]:
        data = json.load(stream)                     # json.load accepte un flux binaire
        items = data.get("works", data) if isinstance(data, dict) else data
        works = []
        for item in items:
            title = (item.get("title") or "").strip()

            # les artistes peuvent être une liste OU une chaîne unique
            raw_artists = item.get("artists") or item.get("artist") or []
            if isinstance(raw_artists, str):
                raw_artists = [raw_artists]

            year = item.get("first-release-year") or item.get("year")

            # identifiant externe de la source (ex: MBID MusicBrainz)
            identifiers = {}
            if item.get("id"):
                identifiers["musicbrainz"] = str(item["id"])

            works.append(CanonicalWork(
                work_id=str(uuid.uuid4()),
                title_raw=title,
                title_normalized=_normalize(title),
                artists=[Artist(a, _normalize(a)) for a in raw_artists if a],
                iswc=item.get("iswc") or None,
                isrcs=item.get("isrcs") or [],
                identifiers=identifiers,
                first_release_year=int(year) if year else None,
                source_records=["json"],
            ))
        return works
    
class XmlParser(SourceParser):
    def parse(self, stream: BinaryIO) -> list[CanonicalWork]:
        tree = ET.parse(stream)                      # ET.parse accepte un flux binaire
        root = tree.getroot()
        works = []
        for node in root.findall("work"):
            title = (node.findtext("title") or "").strip()
            artist = (node.findtext("artist") or "").strip()
            year = node.findtext("year")

            works.append(CanonicalWork(
                work_id=str(uuid.uuid4()),
                title_raw=title,
                title_normalized=_normalize(title),
                artists=[Artist(artist, _normalize(artist))] if artist else [],
                iswc=node.findtext("iswc") or None,
                first_release_year=int(year) if year and year.isdigit() else None,
                source_records=["xml"],
            ))
        return works

def _example_stub() -> CanonicalWork:
    """Exemple de construction d'une oeuvre pivot (à supprimer une fois les parsers faits)."""
    title = "Crazy in Love"
    return CanonicalWork(
        work_id=str(uuid.uuid4()),
        title_raw=title,
        title_normalized=_normalize(title),
        artists=[Artist(name_raw="Beyoncé", name_normalized=_normalize("Beyoncé"))],
    )
