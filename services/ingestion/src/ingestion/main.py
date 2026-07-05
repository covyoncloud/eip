"""Point d'entrée FastAPI du service d'ingestion."""
from __future__ import annotations

from fastapi import FastAPI, UploadFile

from ingestion.adapters.parsers import CsvParser, JsonParser, XmlParser
from ingestion.adapters.repository import InMemoryWorkRepository
from ingestion.application.use_cases import IngestFileUseCase

app = FastAPI(title="EIP - Ingestion Service", version="0.1.0")

# TODO(Sprint 1): injecter le vrai repository (SQLAlchemy) via un container/dépendance
_repository = InMemoryWorkRepository()
_parsers = {"csv": CsvParser(), "json": JsonParser(), "xml": XmlParser()}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ingest")
async def ingest(file: UploadFile) -> dict[str, int | str]:
    fmt = (file.filename or "").split(".")[-1].lower()
    parser = _parsers.get(fmt)
    if parser is None:
        return {"error": f"format non supporté: {fmt}"}
    use_case = IngestFileUseCase(parser, _repository)
    count = use_case.execute(file.file)  # TODO: brancher quand les parsers sont faits
    return {"ingested": count}
