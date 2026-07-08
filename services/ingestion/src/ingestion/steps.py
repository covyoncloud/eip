"""Handlers des étapes de la state machine Step Functions.

Chaque étape reçoit un dict, en renvoie un autre. Les données transitent par S3,
seules les références (bucket/key) voyagent entre états (limite 256 Ko).
"""
import json
import os

import boto3

from ingestion.adapters.dedup_index import DynamoDedupIndex
from ingestion.adapters.parsers import CsvParser, JsonParser, XmlParser
from ingestion.adapters.repository import SqlAlchemyWorkRepository

s3 = boto3.client("s3")
SILVER_BUCKET = os.environ["SILVER_BUCKET"]
_parsers = {"csv": CsvParser(), "json": JsonParser(), "xml": XmlParser()}


def _work_to_dict(w) -> dict:
    return {
        "work_id": w.work_id,
        "business_key": w.business_key(),
        "title_raw": w.title_raw,
        "title_normalized": w.title_normalized,
        "iswc": w.iswc,
        "artists": [{"raw": a.name_raw, "norm": a.name_normalized} for a in w.artists],
        "first_release_year": w.first_release_year,
    }


# ---------- Étape 1 : parse & normalize (bronze -> silver) ----------
def parse_normalize(event, context):
    bucket, key = event["bucket"], event["key"]
    fmt = key.split(".")[-1].lower()
    parser = _parsers[fmt]

    obj = s3.get_object(Bucket=bucket, Key=key)
    works = parser.parse(obj["Body"])

    payload = [_work_to_dict(w) for w in works]
    silver_key = f"silver/{key.split('/')[-1]}.json"
    s3.put_object(Bucket=SILVER_BUCKET, Key=silver_key, Body=json.dumps(payload).encode())

    print(f"normalisé {len(payload)} œuvres -> s3://{SILVER_BUCKET}/{silver_key}")
    return {"bucket": SILVER_BUCKET, "key": silver_key, "count": len(payload)}


# ---------- Étape 2 : quality gate ----------
def quality_gate(event, context):
    obj = s3.get_object(Bucket=event["bucket"], Key=event["key"])
    works = json.loads(obj["Body"].read())

    invalid = [w for w in works if not w.get("title_normalized")]
    valid_ratio = 1 - (len(invalid) / len(works)) if works else 0

    print(f"qualité: {len(works)} œuvres, {len(invalid)} invalides, ratio={valid_ratio:.2f}")
    return {**event, "valid": valid_ratio >= 0.95, "valid_ratio": valid_ratio}


# ---------- Étape 3 : load (dédup + Aurora) ----------
def load(event, context):
    from ingestion.domain.models import Artist, CanonicalWork

    obj = s3.get_object(Bucket=event["bucket"], Key=event["key"])
    works_data = json.loads(obj["Body"].read())

    repo = SqlAlchemyWorkRepository()
    dedup = DynamoDedupIndex()
    loaded = 0

    for d in works_data:
        if dedup.exists(d["business_key"]):
            continue
        work = CanonicalWork(
            work_id=d["work_id"],
            title_raw=d["title_raw"],
            title_normalized=d["title_normalized"],
            iswc=d["iswc"],
            artists=[Artist(a["raw"], a["norm"]) for a in d["artists"]],
            first_release_year=d["first_release_year"],
        )
        repo.save(work)
        dedup.register(d["business_key"], d["work_id"])
        loaded += 1

    print(f"chargé {loaded} nouvelles œuvres")
    return {**event, "loaded": loaded}