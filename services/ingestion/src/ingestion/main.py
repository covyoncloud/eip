from fastapi import FastAPI, UploadFile
from ingestion.adapters.db import Base, engine
from ingestion.adapters.repository import SqlAlchemyWorkRepository  
import boto3
import os

app = FastAPI(title="EIP - Ingestion Service", version="0.1.0")
BRONZE_BUCKET = os.environ["BRONZE_BUCKET"]
s3 = boto3.client("s3") if BRONZE_BUCKET else None

_repository = SqlAlchemyWorkRepository()   # <-- au lieu de InMemoryWorkRepository()

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/ingest", status_code=202)
async def ingest(file: UploadFile):
    if not BRONZE_BUCKET:
        return {"error": "BRONZE_BUCKET non configuré (local)"}
    key = f"uploads/{file.filename}"
    s3.upload_fileobj(file.file, BRONZE_BUCKET, key)
    return {"status": "accepted", "key": key}

@app.get("/entities")
def list_entities(limit: int = 50, offset: int = 0) -> list[dict]:
    works = _repository.list_all(limit=limit, offset=offset)
    return [
        {
            "work_id": w.work_id,
            "title": w.title_raw,
            "title_normalized": w.title_normalized,
            "iswc": w.iswc,
            "artists": [a.name_raw for a in w.artists],
            "year": w.first_release_year,
        }
        for w in works
    ]

@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(engine)