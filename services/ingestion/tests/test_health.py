from fastapi.testclient import TestClient
import os
os.environ.setdefault("BRONZE_BUCKET", "test-bucket")
from ingestion.main import app


def test_health():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
