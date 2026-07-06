from fastapi import FastAPI, UploadFile
from ingestion.adapters.db import Base, engine
from ingestion.adapters.parsers import CsvParser, JsonParser, XmlParser
from ingestion.adapters.repository import SqlAlchemyWorkRepository   # <-- changé
from ingestion.application.use_cases import IngestFileUseCase

app = FastAPI(title="EIP - Ingestion Service", version="0.1.0")

_repository = SqlAlchemyWorkRepository()   # <-- au lieu de InMemoryWorkRepository()
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
    count = use_case.execute(file.file)
    return {"ingested": count}

@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(engine)