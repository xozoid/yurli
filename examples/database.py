"""Keep integer primary keys in storage and encode them at the API boundary."""

from __future__ import annotations

from pathlib import Path

from yurli import Yurli

codec = Yurli.from_bytes(Path("yurli-config.json").read_bytes())

# When reading a row from a database:
database_primary_key = 12345
public_identifier = codec.encode(database_primary_key)

# When a route receives the public identifier, decode it before querying:
decoded_primary_key = codec.decode(public_identifier)
if decoded_primary_key != database_primary_key:
    msg = "round-trip failed"
    raise RuntimeError(msg)
