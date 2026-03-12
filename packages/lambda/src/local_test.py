#!/usr/bin/env python3
"""Basic local smoke test for lambda handlers.

Usage:
  python local_test.py            # JSON parsing path (default)
  python local_test.py json
  python local_test.py csv
"""

import json
import sys
import uuid
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

import graph_processor_handler  # type: ignore


def _sample_json_graph():
    return json.dumps(
        {
            "nodes": [
                {"id": "d1", "label": "Disease", "properties": {"name": "Diabetes"}},
                {"id": "m1", "label": "Medication", "properties": {"name": "Metformin"}},
            ],
            "edges": [
                {
                    "id": str(uuid.uuid4()),
                    "source": "d1",
                    "target": "m1",
                    "label": "treated_by",
                    "properties": {},
                }
            ],
        }
    )


def _sample_csv_graph():
    return "\n".join(
        [
            "id,label,name",
            "d1,Disease,Diabetes",
            "m1,Medication,Metformin",
            "",
            "source,target,label",
            "d1,m1,treated_by",
        ]
    )


class _MockBody:
    def __init__(self, text):
        self._text = text

    def read(self):
        return self._text.encode("utf-8")


class _MockS3Client:
    def __init__(self, payload):
        self.payload = payload

    def get_object(self, Bucket, Key):
        return {"Body": _MockBody(self.payload)}


class _MockContext:
    aws_request_id = "local-test-request"


def run(mode: str):
    mode = (mode or "json").lower()
    payload = _sample_csv_graph() if mode == "csv" else _sample_json_graph()
    key = "sample.csv" if mode == "csv" else "sample.json"

    # Monkeypatch external side effects for local smoke test.
    original_s3_client = graph_processor_handler.s3_client
    original_insert = graph_processor_handler.insert_into_neptune

    graph_processor_handler.s3_client = _MockS3Client(payload)

    def _mock_insert(nodes, edges):
        print(f"[mock] insert_into_neptune called with {len(nodes)} nodes, {len(edges)} edges")
        return True

    graph_processor_handler.insert_into_neptune = _mock_insert

    event = {
        "Records": [
            {
                "eventSource": "aws:s3",
                "s3": {"bucket": {"name": "mock-bucket"}, "object": {"key": key}},
            }
        ]
    }

    try:
        response = graph_processor_handler.handler(event, _MockContext())
        print("statusCode:", response.get("statusCode"))
        print("body:", response.get("body"))
        return 0 if response.get("statusCode") == 200 else 1
    finally:
        graph_processor_handler.s3_client = original_s3_client
        graph_processor_handler.insert_into_neptune = original_insert


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "json"
    raise SystemExit(run(arg))
