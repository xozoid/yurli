# Benchmark results

Generated: 2026-11-14T17:40:25+00:00

- Python: 3.15.2 (CPython)
- Operating system: Linux-7.0.0-43-generic-x86_64-with-glibc2.39
- Processor: AMD Ryzen 7 2700X Eight-Core Processor
- Dataset size: 100,000 values per dataset
- Random seed: 20261114 + integer width

Throughput and latency include `tracemalloc` overhead. Values below are from this single
run and shouldn't be treated as general performance claims.

## Example blocklist

### 16-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |     1.919 |     37,138 |     36,568 |       26.93 |       27.35 |          3.00 |           8,922.6 |
| Sqids          | sequential |     4.654 |     45,927 |     55,070 |       21.77 |       18.16 |          3.92 |           9,014.8 |
| yurli          | random     |     1.050 |     38,123 |     36,750 |       26.23 |       27.21 |          3.00 |           8,934.8 |
| Sqids          | random     |     5.014 |     45,419 |     55,075 |       22.02 |       18.16 |          3.94 |           9,028.8 |

### 32-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |     6.832 |     31,711 |     32,000 |       31.53 |       31.25 |          6.00 |           9,247.4 |
| Sqids          | sequential |     4.534 |     45,478 |     55,126 |       21.99 |       18.14 |          3.96 |           9,047.3 |
| yurli          | random     |     6.840 |     30,306 |     30,771 |       33.00 |       32.50 |          6.00 |           9,279.5 |
| Sqids          | random     |     4.685 |     35,837 |     42,622 |       27.90 |       23.46 |          6.80 |           9,356.3 |

### 64-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |    12.993 |     23,755 |     24,029 |       42.10 |       41.62 |         12.00 |           9,833.4 |
| Sqids          | sequential |     4.962 |     42,299 |     51,282 |       23.64 |       19.50 |          3.96 |           9,047.3 |
| yurli          | random     |    13.355 |     21,851 |     21,307 |       45.76 |       46.93 |         12.00 |          10,208.1 |
| Sqids          | random     |     4.887 |     29,695 |     25,641 |       33.68 |       39.00 |         11.92 |          10,202.5 |

## No blocklist

### 16-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |     0.182 |     36,943 |     36,657 |       27.07 |       27.28 |          3.00 |           8,919.3 |
| Sqids          | sequential |     0.084 |     71,613 |     54,929 |       13.96 |       18.21 |          3.92 |           9,011.6 |
| yurli          | random     |     0.181 |     37,360 |     36,079 |       26.77 |       27.72 |          3.00 |           8,934.8 |
| Sqids          | random     |     0.076 |     71,562 |     55,041 |       13.97 |       18.17 |          3.94 |           9,028.8 |

### 32-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |     0.165 |     32,000 |     31,979 |       31.25 |       31.27 |          6.00 |           9,247.4 |
| Sqids          | sequential |     0.076 |     71,132 |     53,610 |       14.06 |       18.65 |          3.96 |           9,047.3 |
| yurli          | random     |     0.188 |     30,799 |     30,868 |       32.47 |       32.40 |          6.00 |           9,279.6 |
| Sqids          | random     |     0.104 |     58,716 |     42,215 |       17.03 |       23.69 |          6.80 |           9,356.3 |

### 64-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |     0.183 |     24,566 |     23,567 |       40.71 |       42.43 |         11.00 |           9,735.8 |
| Sqids          | sequential |     0.104 |     66,976 |     52,134 |       14.93 |       19.18 |          3.96 |           9,047.3 |
| yurli          | random     |     0.179 |     22,617 |     22,805 |       44.21 |       43.85 |         11.00 |          10,110.4 |
| Sqids          | random     |     0.076 |     50,472 |     27,690 |       19.81 |       36.11 |         11.92 |          10,202.5 |

For the 64-bit comparison, both libraries receive values limited to Sqids' signed
platform integer range. This compares their shared input domain, not yurli's full
unsigned 64-bit domain. Peak memory is the additional traced memory during encoding and
decoding, including the retained outputs.
