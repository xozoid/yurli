"""Illustrative Flask route parameter integration."""

from __future__ import annotations

from pathlib import Path

from flask import Flask, abort

from yurli import Yurli

app = Flask(__name__)
# Load this persisted configuration from application settings at startup.
codec = Yurli.from_bytes(Path("yurli-config.json").read_bytes())


@app.get("/records/<identifier>")
def get_record(identifier: str) -> dict[str, int]:
    """Return the decoded record key."""
    try:
        record_id = codec.decode(identifier)
    except ValueError:
        abort(404)
    return {"id": record_id}
