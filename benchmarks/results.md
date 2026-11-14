# Benchmark results

Generated: 2026-11-14T18:33:23+00:00

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
| yurli          | sequential |     0.376 |    310,600 |    311,922 |        3.22 |        3.21 |          3.00 |           8,919.3 |
| Sqids          | sequential |     0.646 |    104,819 |    210,294 |        9.54 |        4.76 |          3.92 |           9,011.5 |
| yurli          | random     |     0.288 |    310,627 |    312,777 |        3.22 |        3.20 |          3.00 |           8,934.8 |
| Sqids          | random     |     0.673 |     99,332 |    209,382 |       10.07 |        4.78 |          3.94 |           9,028.7 |

### 32-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |     1.310 |    277,229 |    265,602 |        3.61 |        3.77 |          6.00 |           9,247.0 |
| Sqids          | sequential |     0.652 |    101,901 |    206,214 |        9.81 |        4.85 |          3.96 |           9,047.2 |
| yurli          | random     |     1.370 |    266,270 |    263,662 |        3.76 |        3.79 |          6.00 |           9,279.4 |
| Sqids          | random     |     0.648 |     71,274 |    125,325 |       14.03 |        7.98 |          6.80 |           9,356.2 |

### 64-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |     2.426 |    228,975 |    216,087 |        4.37 |        4.63 |         12.00 |           9,833.4 |
| Sqids          | sequential |     0.673 |    101,170 |    204,003 |        9.88 |        4.90 |          3.96 |           9,047.2 |
| yurli          | random     |     2.535 |    217,714 |    209,563 |        4.59 |        4.77 |         12.00 |          10,208.1 |
| Sqids          | random     |     0.635 |     70,074 |     84,248 |       14.27 |       11.87 |         11.92 |          10,202.5 |

## No blocklist

### 16-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |     0.069 |    320,392 |    309,589 |        3.12 |        3.23 |          3.00 |           8,919.3 |
| Sqids          | sequential |     0.040 |    440,431 |    212,984 |        2.27 |        4.70 |          3.92 |           9,011.5 |
| yurli          | random     |     0.071 |    322,390 |    315,561 |        3.10 |        3.17 |          3.00 |           8,934.7 |
| Sqids          | random     |     0.040 |    432,295 |    206,335 |        2.31 |        4.85 |          3.94 |           9,028.7 |

### 32-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |     0.085 |    277,497 |    272,588 |        3.60 |        3.67 |          6.00 |           9,247.5 |
| Sqids          | sequential |     0.043 |    434,480 |    202,093 |        2.30 |        4.95 |          3.96 |           9,047.2 |
| yurli          | random     |     0.089 |    275,284 |    268,632 |        3.63 |        3.72 |          6.00 |           9,279.6 |
| Sqids          | random     |     0.045 |    375,060 |    135,363 |        2.67 |        7.39 |          6.80 |           9,356.2 |

### 64-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |     0.075 |    221,513 |    213,390 |        4.51 |        4.69 |         11.00 |           9,735.8 |
| Sqids          | sequential |     0.048 |    438,204 |    202,743 |        2.28 |        4.93 |          3.96 |           9,047.2 |
| yurli          | random     |     0.091 |    229,913 |    209,154 |        4.35 |        4.78 |         11.00 |          10,110.4 |
| Sqids          | random     |     0.063 |    289,034 |     77,086 |        3.46 |       12.97 |         11.92 |          10,202.5 |

For the 64-bit comparison, both libraries receive values limited to Sqids' signed
platform integer range. This compares their shared input domain, not yurli's full
unsigned 64-bit domain. Peak memory is the additional traced memory during encoding and
decoding, including the retained outputs.
