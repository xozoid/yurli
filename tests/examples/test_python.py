from __future__ import annotations

import runpy
from pathlib import Path
from typing import TYPE_CHECKING

from yurli import Yurli

if TYPE_CHECKING:
    import pytest

_EXAMPLE_PATH = Path(__file__).resolve().parents[2] / "examples" / "python.py"


def test_example_creates_persisted_configuration(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    runpy.run_path(str(_EXAMPLE_PATH))

    assert (tmp_path / "yurli-config.json").is_file()


def test_example_reuses_persisted_configuration(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    config_path = tmp_path / "yurli-config.json"
    config_path.write_bytes(Yurli(bits=32, round_keys=(0, 1, 2, 3)).to_bytes())
    saved_configuration = config_path.read_bytes()

    runpy.run_path(str(_EXAMPLE_PATH))

    assert config_path.read_bytes() == saved_configuration


def test_example_prints_round_trips_for_first_20_values(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)

    runpy.run_path(str(_EXAMPLE_PATH))
    lines = capsys.readouterr().out.splitlines()

    assert len(lines) == 20
    for expected_value, line in enumerate(lines):
        original, identifier, decoded = line.split(" -> ")
        assert int(original) == expected_value
        assert identifier
        assert int(decoded) == expected_value
