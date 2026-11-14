"""Illustrative FastAPI route parameter integration."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException

from yurli import Yurli

app = FastAPI()
# Load this persisted configuration from application settings at startup.
codec = Yurli.from_bytes(Path("yurli-config.json").read_bytes())


@app.get("/records/{identifier}")
def get_record(identifier: str) -> dict[str, int]:
    """Return the decoded record key.

    Raises:
        HTTPException: If the identifier is invalid.
    """
    try:
        record_id = codec.decode(identifier)
    except ValueError as error:
        raise HTTPException(status_code=404) from error
    return {"id": record_id}
