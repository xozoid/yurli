"""Compare yurli with Sqids on deterministic integer datasets."""

from __future__ import annotations

import argparse
import cProfile
import logging
import platform
import random
import statistics
import sys
import time
import tracemalloc
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

from sqids import Sqids

from yurli import EXAMPLE_BLOCKLIST, IntegerWidth, Yurli

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

DATASET_SIZE = 100_000
SEED = 20261114
WIDTHS = (16, 32, 64)
LOGGER = logging.getLogger(__name__)
RESULTS_PATH = Path(__file__).with_name("results.md")


class Codec(Protocol):
    """Common interface for the two benchmark implementations."""

    def encode(self, value: int, /) -> str:
        """Encode one integer."""
        ...

    def decode(self, identifier: str, /) -> int:
        """Decode one integer."""
        ...


class YurliAdapter:
    """Adapt Yurli to the benchmark codec interface."""

    def __init__(self, bits: IntegerWidth, *, use_blocklist: bool) -> None:
        """Initialize a Yurli codec at the requested width."""
        blocklist = EXAMPLE_BLOCKLIST if use_blocklist else ()
        self._codec = Yurli(bits=bits, blocklist=blocklist)

    def encode(self, value: int, /) -> str:
        """Encode one integer with Yurli.

        Returns:
            An identifier.
        """
        return self._codec.encode(value)

    def decode(self, identifier: str, /) -> int:
        """Decode one integer with Yurli.

        Returns:
            The input integer.
        """
        return self._codec.decode(identifier)


class SqidsAdapter:
    """Adapt Sqids to the benchmark codec interface."""

    def __init__(self, *, use_blocklist: bool) -> None:
        """Initialize Sqids with or without its default blocklist."""
        self._codec = (
            Sqids(blocklist=list(EXAMPLE_BLOCKLIST))
            if use_blocklist
            else Sqids(blocklist=[])
        )

    def encode(self, value: int, /) -> str:
        """Encode one integer with Sqids.

        Returns:
            An identifier.
        """
        return self._codec.encode([value])

    def decode(self, identifier: str, /) -> int:
        """Decode one integer with Sqids.

        Returns:
            The input integer.
        """
        return self._codec.decode(identifier)[0]


@dataclass(frozen=True)
class Measurement:
    """Measured initialization and operation costs."""

    initialization_ms: float
    encode_per_second: float
    decode_per_second: float
    average_encode_us: float
    average_decode_us: float
    average_length: float
    peak_memory_kib: float


@dataclass(frozen=True)
class BenchmarkResult:
    """One measured width, dataset, and codec combination."""

    bits: int
    dataset: str
    codec: str
    measurement: Measurement


def datasets(bits: int) -> tuple[list[int], list[int]]:
    """Return repeatable sequential and uniformly distributed inputs."""
    # Sqids uses the platform signed integer limit, including for Yurli's 64-bit run.
    maximum = min(1 << bits, sys.maxsize + 1)
    sequential = [value % maximum for value in range(DATASET_SIZE)]
    generator = random.Random(SEED + bits)  # ruff: ignore[suspicious-non-cryptographic-random-usage]
    random_values = [generator.randrange(maximum) for _ in range(DATASET_SIZE)]
    return sequential, random_values


def measure(
    factory: Callable[[], Codec],
    values: Sequence[int],
) -> Measurement:
    """Measure initialization, operations, output length, and peak memory.

    Returns:
        Measurements for one codec and dataset.
    """
    tracemalloc.start()
    start = time.perf_counter()
    codec = factory()
    initialization = time.perf_counter() - start
    baseline, _ = tracemalloc.get_traced_memory()

    start = time.perf_counter()
    identifiers = [codec.encode(value) for value in values]
    encode_elapsed = time.perf_counter() - start

    start = time.perf_counter()
    decoded = [codec.decode(identifier) for identifier in identifiers]
    decode_elapsed = time.perf_counter() - start
    checksum = sum(decoded) + sum(map(len, identifiers))
    LOGGER.debug("Output checksum: %d", checksum)

    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    count = len(values)
    return Measurement(
        initialization_ms=initialization * 1000,
        encode_per_second=count / encode_elapsed,
        decode_per_second=count / decode_elapsed,
        average_encode_us=encode_elapsed * 1_000_000 / count,
        average_decode_us=decode_elapsed * 1_000_000 / count,
        average_length=statistics.fmean(map(len, identifiers)),
        peak_memory_kib=max(0, peak - baseline) / 1024,
    )


def hardware_name() -> str:
    """Return the processor model when Linux exposes it."""
    cpu_info = Path("/proc/cpuinfo")
    if cpu_info.is_file():
        for line in cpu_info.read_text(encoding="utf-8").splitlines():
            if line.startswith("model name"):
                return line.partition(":")[2].strip()
    return platform.processor() or "Not reported by platform"


def render_results(results: Sequence[BenchmarkResult]) -> str:
    """Render measurements and run metadata as a Markdown report.

    Returns:
        A complete Markdown report for the current benchmark run.
    """
    generated_at = datetime.now(UTC).isoformat(timespec="seconds")
    lines = [
        "# Benchmark results",
        "",
        f"Generated: {generated_at}",
        "",
        f"- Python: {sys.version.split()[0]} ({platform.python_implementation()})",
        f"- Operating system: {platform.platform()}",
        f"- Processor: {hardware_name()}",
        f"- Dataset size: {DATASET_SIZE:,} values per dataset",
        f"- Random seed: {SEED} + integer width",
        "",
        (
            "Throughput and latency include `tracemalloc` overhead. Values below are "
            "from this"
        ),
        "single run and shouldn't be treated as general performance claims.",
        "",
    ]
    for blocklist, label in ((True, "Example blocklist"), (False, "No blocklist")):
        lines.extend((f"## {label}", ""))
        for bits in WIDTHS:
            lines.extend(
                (
                    f"### {bits}-bit",
                    "",
                    (
                        "| Implementation | Dataset | Init (ms) | Encode / s | "
                        "Decode / s | Encode (us) | Decode (us) | Avg ID length | "
                        "Peak memory (KiB) |"
                    ),
                    "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
                ),
            )
            for result in results:
                if (
                    result.bits != bits
                    or result.codec.endswith("-default") != blocklist
                ):
                    continue
                item = result.measurement
                implementation = (
                    "yurli" if result.codec.startswith("yurli") else "Sqids"
                )
                lines.append(
                    f"| {implementation} | {result.dataset} | "
                    f"{item.initialization_ms:.3f} | "
                    f"{item.encode_per_second:,.0f} | "
                    f"{item.decode_per_second:,.0f} | "
                    f"{item.average_encode_us:.2f} | "
                    f"{item.average_decode_us:.2f} | "
                    f"{item.average_length:.2f} | "
                    f"{item.peak_memory_kib:,.1f} |",
                )
            lines.append("")
    lines.extend(
        (
            "",
            (
                "For the 64-bit comparison, both libraries receive values limited to "
                "Sqids'"
            ),
            (
                "signed platform integer range. This compares their shared input "
                "domain, not"
            ),
            "yurli's full unsigned 64-bit domain. Peak memory is the additional traced",
            "memory during encoding and decoding, including the retained outputs.",
            "",
        ),
    )
    return "\n".join(line.rstrip() for line in lines)


def run(*, profile: bool) -> None:
    """Run all width, input, and implementation combinations."""
    results: list[BenchmarkResult] = []
    LOGGER.info(
        "Python: %s (%s)",
        sys.version.split()[0],
        platform.python_implementation(),
    )
    LOGGER.info("Platform: %s", platform.platform())
    LOGGER.info("Dataset: %s values per input, random seed %s", DATASET_SIZE, SEED)
    for bits in WIDTHS:
        for dataset_name, values in zip(
            ("sequential", "random"),
            datasets(bits),
            strict=True,
        ):
            cases: tuple[tuple[str, Callable[[], Codec]], ...] = (
                (
                    "yurli-default",
                    lambda width=bits: YurliAdapter(width, use_blocklist=True),
                ),
                (
                    "yurli-no-blocklist",
                    lambda width=bits: YurliAdapter(width, use_blocklist=False),
                ),
                ("sqids-default", lambda: SqidsAdapter(use_blocklist=True)),
                ("sqids-no-blocklist", lambda: SqidsAdapter(use_blocklist=False)),
            )
            for label, factory in cases:
                profiler = (
                    cProfile.Profile()
                    if profile and label.startswith("yurli")
                    else None
                )
                if profiler is not None:
                    profiler.enable()
                result = measure(factory, values)
                if profiler is not None:
                    profiler.disable()
                    profiler.dump_stats(f"profile-{bits}-{dataset_name}-{label}.prof")
                results.append(BenchmarkResult(bits, dataset_name, label, result))
                LOGGER.info("%2s bit %-10s %-20s %s", bits, dataset_name, label, result)
    RESULTS_PATH.write_text(render_results(results), encoding="utf-8")
    LOGGER.info("Wrote results to %s", RESULTS_PATH)


def main() -> None:
    """Parse options and run benchmarks."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile",
        action="store_true",
        help="write cProfile data for yurli runs",
    )
    arguments = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    run(profile=arguments.profile)


if __name__ == "__main__":
    main()
