"""Use and restore a yurli mapping in plain Python."""

from __future__ import annotations

from pathlib import Path

from yurli import Yurli

configuration_path = Path("yurli-config.json")
if configuration_path.exists():
    codec = Yurli.from_bytes(configuration_path.read_bytes())
else:
    codec = Yurli(bits=32, blocklist=["example", "badword"])
    configuration_path.write_bytes(codec.to_bytes())

value = 12345
identifier = codec.encode(value)
decoded_value = codec.decode(identifier)
if decoded_value != value:
    msg = "round-trip failed"
    raise RuntimeError(msg)

for value in range(20):
    identifier = codec.encode(value)
    decoded_value = codec.decode(identifier)
    print(f"{value:2} -> {identifier} -> {decoded_value:2}")
