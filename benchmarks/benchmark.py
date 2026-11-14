"""Compare yurli with Sqids on deterministic integer datasets."""

from __future__ import annotations

import argparse
import base64
import cProfile
import logging
import platform
import random
import statistics
import string
import sys
import time
import tracemalloc
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, cast

from yurli import EXAMPLE_BLOCKLIST, IntegerWidth, Yurli
from yurli._impl.encoding import AlphabetEncoder  # ruff: ignore[import-private-name]

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
        from sqids import Sqids  # ruff: ignore[import-outside-top-level]

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


class StdlibBaseAdapter:
    """Adapt a standard-library bytes-to-text codec to integer inputs."""

    def __init__(self, bits: int, name: str) -> None:
        """Initialize a base codec for fixed-width big-endian integers."""
        self._byte_length = bits // 8
        self._encode = getattr(base64, f"{name}encode")
        self._decode = getattr(base64, f"{name}decode")

    def encode(self, value: int, /) -> str:
        """Encode an integer as fixed-width big-endian bytes, then text.

        Returns:
            The encoded identifier.
        """
        return self._encode(value.to_bytes(self._byte_length, "big")).decode("ascii")

    def decode(self, identifier: str, /) -> int:
        """Decode text to fixed-width bytes, then to an integer.

        Returns:
            The decoded integer.
        """
        return int.from_bytes(self._decode(identifier.encode("ascii")), "big")


def conversion_measure(
    encode: Callable[[int], str],
    decode: Callable[[str], int],
    values: Sequence[int],
) -> tuple[float, float, float]:
    """Measure conversion throughput and mean encoded length.

    Returns:
        Encode operations per second, decode operations per second, and mean ID length.

    Raises:
        ValueError: If the conversion functions don't round trip the input values.
    """
    start = time.perf_counter()
    identifiers = [encode(value) for value in values]
    encode_elapsed = time.perf_counter() - start
    start = time.perf_counter()
    decoded = [decode(identifier) for identifier in identifiers]
    decode_elapsed = time.perf_counter() - start
    if decoded != list(values):
        msg = "integer/string conversion did not round trip"
        raise ValueError(msg)
    count = len(values)
    return (
        count / encode_elapsed,
        count / decode_elapsed,
        statistics.fmean(map(len, identifiers)),
    )


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
    """Return repeatable sequential and uniformly distributed inputs.

    Sequential inputs wrap around when the input domain is smaller than
    ``DATASET_SIZE``.
    """
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
    """Measure initialization and operation speed without memory tracing.

    Returns:
        Measurements for one codec and dataset.
    """
    start = time.perf_counter()
    codec = factory()
    initialization = time.perf_counter() - start

    start = time.perf_counter()
    identifiers = [codec.encode(value) for value in values]
    encode_elapsed = time.perf_counter() - start

    start = time.perf_counter()
    decoded = [codec.decode(identifier) for identifier in identifiers]
    decode_elapsed = time.perf_counter() - start
    _validate_round_trip(values, decoded)
    checksum = sum(decoded) + sum(map(len, identifiers))
    LOGGER.debug("Output checksum: %d", checksum)

    count = len(values)
    return Measurement(
        initialization_ms=initialization * 1000,
        encode_per_second=count / encode_elapsed,
        decode_per_second=count / decode_elapsed,
        average_encode_us=encode_elapsed * 1_000_000 / count,
        average_decode_us=decode_elapsed * 1_000_000 / count,
        average_length=statistics.fmean(map(len, identifiers)),
        peak_memory_kib=0,
    )


def measure_peak_memory(factory: Callable[[], Codec], values: Sequence[int]) -> float:
    """Measure retained output memory separately from operation timings.

    Returns:
        Additional peak traced memory in KiB, excluding codec initialization.
    """
    codec = factory()
    tracemalloc.start()
    try:
        baseline, _ = tracemalloc.get_traced_memory()
        identifiers = [codec.encode(value) for value in values]
        decoded = [codec.decode(identifier) for identifier in identifiers]
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    _validate_round_trip(values, decoded)
    checksum = sum(decoded) + sum(map(len, identifiers))
    LOGGER.debug("Memory pass checksum: %d", checksum)
    return max(0, peak - baseline) / 1024


def _validate_round_trip(values: Sequence[int], decoded: Sequence[int]) -> None:
    """Raise when decoded results differ from their original inputs.

    Raises:
        ValueError: If decoded results don't match their inputs.
    """
    if any(
        actual != expected for expected, actual in zip(values, decoded, strict=True)
    ):
        msg = "integer/string conversion did not round trip"
        raise ValueError(msg)


def profile_measure(
    factory: Callable[[], Codec],
    values: Sequence[int],
    output_path: Path,
) -> None:
    """Profile one untimed encode/decode pass and write its cProfile data."""
    profiler = cProfile.Profile()
    try:
        profiler.enable()
        codec = factory()
        identifiers = [codec.encode(value) for value in values]
        decoded = [codec.decode(identifier) for identifier in identifiers]
    finally:
        profiler.disable()
    _validate_round_trip(values, decoded)
    checksum = sum(decoded) + sum(map(len, identifiers))
    LOGGER.debug("Profile pass checksum: %d", checksum)
    profiler.dump_stats(str(output_path))


def hardware_name() -> str:
    """Return the processor model when Linux exposes it."""
    cpu_info = Path("/proc/cpuinfo")
    if cpu_info.is_file():
        for line in cpu_info.read_text(encoding="utf-8").splitlines():
            if line.startswith("model name"):
                return line.partition(":")[2].strip()
    return platform.processor() or "Not reported by platform"


def render_results(results: Sequence[BenchmarkResult]) -> str:  # ruff: ignore[too-many-locals]
    """Render measurements and run metadata as a Markdown report.

    Returns:
        A complete Markdown report for the current benchmark run.
    """
    from sqids import Sqids  # ruff: ignore[import-outside-top-level]

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
            "Speed measurements run without `tracemalloc`; peak memory is measured "
            "in a separate pass. Values below are from this"
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
                implementation = result.codec
                if result.codec.startswith("yurli"):
                    implementation = "yurli"
                elif result.codec.startswith("sqids"):
                    implementation = "Sqids"
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
    lines.extend(("## Integer/string conversion only", ""))
    conversion_description = (
        "These measurements call `AlphabetEncoder.encode`/`decode`, Sqids' internal "
        "integer conversion helpers, or the standard-library Base encoders directly. "
        "They exclude Yurli/Sqids wrapper logic and blocklist handling."
    )
    lines.extend((conversion_description, ""))
    values = datasets(64)[1]
    alphabet = string.ascii_letters + string.digits + string.punctuation
    for base, label, stdlib_name in (
        (16, "16 character alphabet", "b16"),
        (32, "32 character alphabet", "b32"),
        (64, "64 character alphabet", "b64"),
        (85, "85 character alphabet", "b85"),
    ):
        lines.extend(
            (
                f"### {label}",
                "",
                "| Conversion | Encode / s | Decode / s | Avg ID length |",
                "| --- | ---: | ---: | ---: |",
            ),
        )
        alphabet_encoder = AlphabetEncoder(64, alphabet[:base])
        sqids = Sqids(alphabet=alphabet[: base + 1], blocklist=[])
        sqids_to_id = cast(
            "Callable[[int, str], str]",
            getattr(sqids, "_Sqids__to_id"),  # ruff: ignore[get-attr-with-constant]
        )
        sqids_to_number = cast(
            "Callable[[str, str], int]",
            getattr(sqids, "_Sqids__to_number"),  # ruff: ignore[get-attr-with-constant]
        )
        # Helpers take the shuffled digit alphabet without its prefix character.
        sqids_alphabet = cast(
            "str",
            getattr(sqids, "_Sqids__alphabet"),  # ruff: ignore[get-attr-with-constant]
        )
        sqids_digits = sqids_alphabet[1:]
        stdlib_adapter = StdlibBaseAdapter(64, stdlib_name)
        conversions: list[tuple[str, Callable[[int], str], Callable[[str], int]]] = [
            ("AlphabetEncoder", alphabet_encoder.encode, alphabet_encoder.decode),
            (
                "Sqids integer helpers",
                partial(cast("Any", sqids_to_id), alphabet=sqids_digits),
                partial(cast("Any", sqids_to_number), alphabet=sqids_digits),
            ),
            (
                f"stdlib Base{base}",
                stdlib_adapter.encode,
                stdlib_adapter.decode,
            ),
        ]
        if stdlib_name == "b85":
            ascii85_adapter = StdlibBaseAdapter(64, "a85")
            conversions.append(
                ("stdlib Ascii85", ascii85_adapter.encode, ascii85_adapter.decode),
            )
        for name, encode, decode in conversions:
            encode_rate, decode_rate, average_length = conversion_measure(
                encode,
                decode,
                values,
            )
            lines.append(
                f"| {name} | {encode_rate:,.0f} | {decode_rate:,.0f} | "
                f"{average_length:.2f} |",
            )
        lines.append("")
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
                result = measure(factory, values)
                result = Measurement(
                    initialization_ms=result.initialization_ms,
                    encode_per_second=result.encode_per_second,
                    decode_per_second=result.decode_per_second,
                    average_encode_us=result.average_encode_us,
                    average_decode_us=result.average_decode_us,
                    average_length=result.average_length,
                    peak_memory_kib=measure_peak_memory(factory, values),
                )
                results.append(BenchmarkResult(bits, dataset_name, label, result))
                LOGGER.info("%2s bit %-10s %-20s %s", bits, dataset_name, label, result)
    if profile:
        for bits in WIDTHS:
            for dataset_name, values in zip(
                ("sequential", "random"),
                datasets(bits),
                strict=True,
            ):
                for use_blocklist, label in (
                    (True, "yurli-default"),
                    (False, "yurli-no-blocklist"),
                ):
                    factory = partial(YurliAdapter, bits, use_blocklist=use_blocklist)
                    profile_measure(
                        factory,
                        values,
                        Path(f"profile-{bits}-{dataset_name}-{label}.prof"),
                    )
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
