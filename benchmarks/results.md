# Benchmark results

Generated: 2026-11-14T20:17:30+00:00

- Python: 3.15.2 (CPython)
- Operating system: Linux-7.0.0-43-generic-x86_64-with-glibc2.39
- Processor: AMD Ryzen 7 2700X Eight-Core Processor
- Dataset size: 100,000 values per dataset
- Random seed: 20261114 + integer width

Speed measurements run without `tracemalloc`; peak memory is measured in a separate
pass. Values below are from this single run and shouldn't be treated as general
performance claims.

## Example blocklist

### 16-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |     0.379 |    311,241 |    309,101 |        3.21 |        3.24 |          3.00 |           8,919.3 |
| Sqids          | sequential |     1.283 |    103,356 |    207,656 |        9.68 |        4.82 |          3.92 |           9,011.5 |
| yurli          | random     |     0.313 |    312,213 |    297,312 |        3.20 |        3.36 |          3.00 |           8,934.7 |
| Sqids          | random     |     0.682 |    101,531 |    206,890 |        9.85 |        4.83 |          3.94 |           9,028.7 |

### 32-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |     1.467 |    272,000 |    275,253 |        3.68 |        3.63 |          6.00 |           9,247.4 |
| Sqids          | sequential |     0.656 |     97,595 |    208,441 |       10.25 |        4.80 |          3.96 |           9,047.2 |
| yurli          | random     |     1.369 |    264,121 |    265,997 |        3.79 |        3.76 |          6.00 |           9,279.5 |
| Sqids          | random     |     0.693 |     73,529 |    139,147 |       13.60 |        7.19 |          6.80 |           9,356.2 |

### 64-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |     2.473 |    239,410 |    222,188 |        4.18 |        4.50 |         12.00 |           9,833.4 |
| Sqids          | sequential |     0.644 |    102,071 |    208,112 |        9.80 |        4.81 |          3.96 |           9,047.2 |
| yurli          | random     |     2.495 |    229,019 |    216,077 |        4.37 |        4.63 |         12.00 |          10,208.1 |
| Sqids          | random     |     0.667 |     69,399 |     84,056 |       14.41 |       11.90 |         11.92 |          10,202.5 |

## No blocklist

### 16-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |     0.068 |    306,603 |    315,508 |        3.26 |        3.17 |          3.00 |           8,919.3 |
| Sqids          | sequential |     0.047 |    449,870 |    203,360 |        2.22 |        4.92 |          3.92 |           9,011.5 |
| yurli          | random     |     0.076 |    307,899 |    312,161 |        3.25 |        3.20 |          3.00 |           8,934.7 |
| Sqids          | random     |     0.059 |    443,575 |    205,758 |        2.25 |        4.86 |          3.94 |           9,028.7 |

### 32-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |     0.068 |    261,610 |    261,280 |        3.82 |        3.83 |          6.00 |           9,247.3 |
| Sqids          | sequential |     0.054 |    453,697 |    210,628 |        2.20 |        4.75 |          3.96 |           9,047.2 |
| yurli          | random     |     0.072 |    261,948 |    264,402 |        3.82 |        3.78 |          6.00 |           9,279.5 |
| Sqids          | random     |     0.058 |    360,708 |    142,121 |        2.77 |        7.04 |          6.80 |           9,356.2 |

### 64-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |     0.071 |    235,315 |    215,348 |        4.25 |        4.64 |         11.00 |           9,735.8 |
| Sqids          | sequential |     0.048 |    433,898 |    207,653 |        2.30 |        4.82 |          3.96 |           9,047.2 |
| yurli          | random     |     0.073 |    220,704 |    212,069 |        4.53 |        4.72 |         11.00 |          10,110.4 |
| Sqids          | random     |     0.053 |    287,092 |     82,477 |        3.48 |       12.12 |         11.92 |          10,202.5 |

## Integer/string conversion only

These measurements call `AlphabetEncoder.encode`/`decode`, Sqids' internal integer
conversion helpers, or the standard-library Base encoders directly. They exclude
Yurli/Sqids wrapper logic and blocklist handling.

### 16 character alphabet

| Conversion            | Encode / s | Decode / s | Avg ID length |
| --------------------- | ---------: | ---------: | ------------: |
| AlphabetEncoder       |    639,943 |    578,560 |         16.00 |
| Sqids integer helpers |    527,193 |    209,181 |         15.87 |
| stdlib Base16         |  3,982,065 |  1,520,396 |         16.00 |

### 32 character alphabet

| Conversion            | Encode / s | Decode / s | Avg ID length |
| --------------------- | ---------: | ---------: | ------------: |
| AlphabetEncoder       |    742,120 |    664,282 |         13.00 |
| Sqids integer helpers |    643,184 |    197,065 |         12.87 |
| stdlib Base32         |  3,741,103 |  2,344,319 |         16.00 |

### 64 character alphabet

| Conversion            | Encode / s | Decode / s | Avg ID length |
| --------------------- | ---------: | ---------: | ------------: |
| AlphabetEncoder       |    843,005 |    775,560 |         11.00 |
| Sqids integer helpers |    747,108 |    151,901 |         10.88 |
| stdlib Base64         |  3,562,318 |  2,083,195 |         12.00 |

### 85 character alphabet

| Conversion            | Encode / s | Decode / s | Avg ID length |
| --------------------- | ---------: | ---------: | ------------: |
| AlphabetEncoder       |    856,210 |    816,397 |         10.00 |
| Sqids integer helpers |    782,283 |    143,829 |          9.97 |
| stdlib Base85         |  3,834,893 |  3,216,092 |         10.00 |
| stdlib Ascii85        |  3,460,651 |  2,837,858 |         10.00 |

For the 64-bit comparison, both libraries receive values limited to Sqids' signed
platform integer range. This compares their shared input domain, not yurli's full
unsigned 64-bit domain. Peak memory is the additional traced memory during encoding and
decoding, including the retained outputs.
