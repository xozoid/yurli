# Benchmark results

Generated: 2026-11-14T19:27:16+00:00

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
| yurli          | sequential |     0.329 |    294,334 |    293,145 |        3.40 |        3.41 |          3.00 |           8,919.3 |
| Sqids          | sequential |     0.646 |    101,939 |    210,952 |        9.81 |        4.74 |          3.92 |           9,011.5 |
| yurli          | random     |     0.289 |    302,140 |    294,204 |        3.31 |        3.40 |          3.00 |           8,934.7 |
| Sqids          | random     |     0.625 |    102,611 |    214,139 |        9.75 |        4.67 |          3.94 |           9,028.7 |

### 32-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |     1.354 |    262,886 |    262,453 |        3.80 |        3.81 |          6.00 |           9,247.2 |
| Sqids          | sequential |     0.663 |     99,946 |    207,004 |       10.01 |        4.83 |          3.96 |           9,047.2 |
| yurli          | random     |     1.385 |    247,876 |    251,535 |        4.03 |        3.98 |          6.00 |           9,279.6 |
| Sqids          | random     |     0.632 |     75,640 |    140,142 |       13.22 |        7.14 |          6.80 |           9,356.2 |

### 64-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |     2.517 |    221,585 |    210,990 |        4.51 |        4.74 |         12.00 |           9,833.4 |
| Sqids          | sequential |     0.657 |    100,923 |    211,548 |        9.91 |        4.73 |          3.96 |           9,047.2 |
| yurli          | random     |     2.582 |    219,668 |    209,240 |        4.55 |        4.78 |         12.00 |          10,208.1 |
| Sqids          | random     |     0.649 |     70,225 |     84,182 |       14.24 |       11.88 |         11.92 |          10,202.5 |

## No blocklist

### 16-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |     0.071 |    278,075 |    297,754 |        3.60 |        3.36 |          3.00 |           8,919.3 |
| Sqids          | sequential |     0.042 |    446,675 |    214,568 |        2.24 |        4.66 |          3.92 |           9,011.5 |
| yurli          | random     |     0.091 |    302,832 |    297,927 |        3.30 |        3.36 |          3.00 |           8,934.7 |
| Sqids          | random     |     0.040 |    439,102 |    212,455 |        2.28 |        4.71 |          3.94 |           9,028.7 |

### 32-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |     0.078 |    265,329 |    262,868 |        3.77 |        3.80 |          6.00 |           9,246.9 |
| Sqids          | sequential |     0.047 |    445,374 |    204,903 |        2.25 |        4.88 |          3.96 |           9,047.2 |
| yurli          | random     |     0.067 |    255,422 |    251,052 |        3.92 |        3.98 |          6.00 |           9,279.5 |
| Sqids          | random     |     0.047 |    372,189 |    143,383 |        2.69 |        6.97 |          6.80 |           9,356.2 |

### 64-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |     0.069 |    227,945 |    210,516 |        4.39 |        4.75 |         11.00 |           9,735.8 |
| Sqids          | sequential |     0.040 |    431,386 |    208,180 |        2.32 |        4.80 |          3.96 |           9,047.2 |
| yurli          | random     |     0.081 |    221,723 |    207,148 |        4.51 |        4.83 |         11.00 |          10,110.4 |
| Sqids          | random     |     0.054 |    289,109 |     84,477 |        3.46 |       11.84 |         11.92 |          10,202.5 |

## Integer/string conversion only

These measurements call `AlphabetEncoder.encode`/`decode`, Sqids' internal integer
conversion helpers, or the standard-library Base encoders directly. They exclude
Yurli/Sqids wrapper logic and blocklist handling.

### 16 character alphabet

| Conversion            | Encode / s | Decode / s | Avg ID length |
| --------------------- | ---------: | ---------: | ------------: |
| AlphabetEncoder       |    631,220 |    572,374 |         16.00 |
| Sqids integer helpers |    517,953 |    201,749 |         15.87 |
| stdlib Base16         |  4,078,107 |  1,555,209 |         16.00 |

### 32 character alphabet

| Conversion            | Encode / s | Decode / s | Avg ID length |
| --------------------- | ---------: | ---------: | ------------: |
| AlphabetEncoder       |    728,691 |    683,422 |         13.00 |
| Sqids integer helpers |    633,182 |    198,914 |         12.87 |
| stdlib Base32         |  3,828,796 |  2,381,121 |         16.00 |

### 64 character alphabet

| Conversion            | Encode / s | Decode / s | Avg ID length |
| --------------------- | ---------: | ---------: | ------------: |
| AlphabetEncoder       |    819,979 |    781,926 |         11.00 |
| Sqids integer helpers |    738,537 |    161,264 |         10.88 |
| stdlib Base64         |  3,179,486 |  2,190,193 |         12.00 |

### 85 character alphabet

| Conversion            | Encode / s | Decode / s | Avg ID length |
| --------------------- | ---------: | ---------: | ------------: |
| AlphabetEncoder       |    875,231 |    814,544 |         10.00 |
| Sqids integer helpers |    799,720 |    146,715 |          9.97 |
| stdlib Base85         |  3,947,802 |  3,305,485 |         10.00 |

For the 64-bit comparison, both libraries receive values limited to Sqids' signed
platform integer range. This compares their shared input domain, not yurli's full
unsigned 64-bit domain. Peak memory is the additional traced memory during encoding and
decoding, including the retained outputs.
