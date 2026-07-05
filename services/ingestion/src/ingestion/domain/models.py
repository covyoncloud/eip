"""Modèle de domaine : l'entité pivot canonique CanonicalWork.

C'est le coeur de EIP. Toutes les sources hétérogènes convergent vers ce format.
Aucune dépendance à FastAPI, SQLAlchemy ou boto3 ici (architecture hexagonale).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ArtistRole(str, Enum):
    COMPOSER = "composer"
    AUTHOR = "author"
    PERFORMER = "performer"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Artist:
    name_raw: str            # tel qu'ingéré
    name_normalized: str     # nettoyé (casse, accents, ponctuation)
    role: ArtistRole = ArtistRole.UNKNOWN


@dataclass
class CanonicalWork:
    """Une oeuvre musicale, format pivot unique."""
    work_id: str                              # UUID interne canonique
    title_normalized: str
    title_raw: str
    artists: list[Artist] = field(default_factory=list)
    iswc: str | None = None                   # International Standard Musical Work Code
    identifiers: dict[str, str] = field(default_factory=dict)  # source -> id externe
    isrcs: list[str] = field(default_factory=list)             # enregistrements liés
    language: str | None = None
    first_release_year: int | None = None
    genres: list[str] = field(default_factory=list)
    source_records: list[str] = field(default_factory=list)    # provenance
    confidence_score: float = 1.0             # confiance de la réconciliation
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def business_key(self) -> str:
        """Clé de dédup déterministe.

        Priorité à l'ISWC s'il existe, sinon hash(titre normalisé + artiste principal).
        C'est cette clé qui alimente l'index DynamoDB (Sprint 2).
        """
        if self.iswc:
            return f"iswc:{self.iswc}"
        primary = self.artists[0].name_normalized if self.artists else ""
        return f"tn:{self.title_normalized}|ar:{primary}"
