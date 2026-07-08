import os
import boto3

from ingestion.application.ports import DedupIndex

class DynamoDedupIndex(DedupIndex):
    def __init__(self) -> None:
        self._table = boto3.resource("dynamodb").Table(os.environ["DEDUP_TABLE"])

    def exists(self, business_key: str) -> bool:
        resp = self._table.get_item(Key={"business_key": business_key})
        return "Item" in resp

    def register(self, business_key: str, work_id: str) -> None:
        self._table.put_item(Item={"business_key": business_key, "work_id": work_id})