from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from benchmarks import benchmark

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from pathlib import Path

    from benchmarks.benchmark import Codec


class CodecStub:
    """Small codec for focused benchmark measurement tests."""

    def __init__(self, *, wrong_decode: bool = False) -> None:
        self.wrong_decode = wrong_decode

    @staticmethod
    def encode(value: int, /) -> str:
        return str(value)

    def decode(self, identifier: str, /) -> int:
        decoded = int(identifier)
        return decoded + int(self.wrong_decode)


@pytest.mark.parametrize(
    "measure_function",
    [benchmark.measure, benchmark.measure_peak_memory],
)
def test_measure_functions_reject_incorrect_round_trips(
    measure_function: Callable[[Callable[[], Codec], Sequence[int]], object],
) -> None:
    values = [1, 2, 3]

    with pytest.raises(ValueError, match="did not round trip"):
        measure_function(lambda: CodecStub(wrong_decode=True), values)


def test_datasets_are_deterministic_bounded_and_wraparound(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(benchmark, "DATASET_SIZE", 8)

    sequential, random_values = benchmark.datasets(2)
    repeat_sequential, repeat_random = benchmark.datasets(2)

    assert sequential == [0, 1, 2, 3, 0, 1, 2, 3]
    assert sequential == repeat_sequential
    assert random_values == repeat_random
    assert all(0 <= value < 4 for value in sequential)
    assert all(0 <= value < 4 for value in random_values)


@pytest.mark.parametrize("profile", [False, True])
def test_profile_pass_runs_after_timing_and_memory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    profile: bool,
) -> None:
    events: list[tuple[str, str | None]] = []
    measured = benchmark.Measurement(1, 2, 3, 4, 5, 6, 0)

    def fake_measure(
        factory: Callable[[], Codec],
        values: Sequence[int],
    ) -> benchmark.Measurement:
        del factory, values
        events.append(("timing", None))
        return measured

    def fake_memory(factory: Callable[[], Codec], values: Sequence[int]) -> float:
        del factory, values
        events.append(("memory", None))
        return 7

    def fake_render_results(results: Sequence[benchmark.BenchmarkResult]) -> str:
        del results
        return ""

    def fake_profile(
        factory: Callable[[], Codec],
        values: Sequence[int],
        output_path: Path,
    ) -> None:
        del factory, values
        events.append(("profile", output_path.name))

    monkeypatch.setattr(benchmark, "WIDTHS", (16,))
    monkeypatch.setattr(benchmark, "DATASET_SIZE", 1)
    monkeypatch.setattr(benchmark, "RESULTS_PATH", tmp_path / "results.md")
    monkeypatch.setattr(benchmark, "render_results", fake_render_results)
    monkeypatch.setattr(benchmark, "measure", fake_measure)
    monkeypatch.setattr(benchmark, "measure_peak_memory", fake_memory)
    monkeypatch.setattr(benchmark, "profile_measure", fake_profile)

    benchmark.run(profile=profile)

    assert len([event for event in events if event[0] == "timing"]) == 8
    assert len([event for event in events if event[0] == "memory"]) == 8
    profile_events = [event for event in events if event[0] == "profile"]
    assert [event[1] for event in profile_events] == (
        [
            "profile-16-sequential-yurli-default.prof",
            "profile-16-sequential-yurli-no-blocklist.prof",
            "profile-16-random-yurli-default.prof",
            "profile-16-random-yurli-no-blocklist.prof",
        ]
        if profile
        else []
    )
    assert all(event[0] in {"timing", "memory"} for event in events[:16])
    assert all(event[0] == "profile" for event in events[16:])
