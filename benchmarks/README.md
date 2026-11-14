# Benchmarks

Install the optional pinned Sqids comparison dependency, then run the benchmark from the
repository root:

```sh
uv sync --group benchmark
uv run --group benchmark python benchmarks/benchmark.py
```

The script compares yurli with the example blocklist and with filtering disabled, and
Sqids 0.5.2 with the same blocklist and with filtering disabled. A separate section
measures 64-bit integer/string conversion only under separate 16-, 32-, 64-, and
85-character alphabet headings: `AlphabetEncoder` directly, Sqids' internal
`__to_id`/`__to_number` helpers, and the matching standard-library Base16, Base32,
Base64, and Base85 codecs. The 85-character section also measures Ascii85. Base codecs
convert fixed-width big-endian integer bytes. It reports initialization time, encode and
decode throughput, average per-operation latency, average identifier length, and peak
traced memory. Speed measurements run without `tracemalloc`; memory is measured in a
separate pass so tracing overhead can't affect operation timings. Construction is timed
separately from the 100,000 encodes and decodes in each timed operation batch. The
encoded values are decoded, validated, and consumed in a checksum in the timing and
memory passes.

Each width has sequential values from zero and a repeatable uniformly distributed
dataset generated with seed `20261114 + bits`. Sequential datasets retain 100,000 values
at every width. When the width's input domain is smaller than that dataset size, the
sequence wraps around modulo the domain; the 16-bit dataset repeats values after 65,536.
Sqids supports signed platform integers; for the 64-bit comparison, both libraries
receive values limited to that range rather than yurli's full unsigned 64-bit domain.
Sqids comparisons therefore describe the shared input range, not its behavior over every
yurli 64-bit value.

The script prints the Python implementation and version and the operating system and
architecture and writes all results and environment details to
[`results.md`](results.md), replacing the report from the previous run. It uses
`tracemalloc` only during the separate memory pass. Peak memory covers the output
identifiers and decoded values retained for validation. Initialization measurements
include yurli's blocklist pruning when enabled. Run the script on an otherwise idle
machine and repeat it before drawing conclusions from small differences.

To collect cProfile files for yurli's runs:

```sh
uv run --group benchmark python benchmarks/benchmark.py --profile
```

Profiling runs in a separate pass after the normal timing and memory measurements. It
profiles only yurli, so `--profile` doesn't change benchmark throughput or memory
results. The profile pass still performs encode/decode operations, outside those
measurements. The profile files are written to the current directory and aren't needed
to run the library.
