# Benchmark results

Generated: 2026-11-14T19:50:59+00:00

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
| yurli          | sequential |     0.337 |    295,751 |    308,490 |        3.38 |        3.24 |          3.00 |           8,919.3 |
| Sqids          | sequential |     0.653 |    104,248 |    215,014 |        9.59 |        4.65 |          3.92 |           9,011.5 |
| yurli          | random     |     0.285 |    308,783 |    314,886 |        3.24 |        3.18 |          3.00 |           8,934.8 |
| Sqids          | random     |     0.636 |    102,824 |    211,123 |        9.73 |        4.74 |          3.94 |           9,028.7 |

### 32-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |     1.324 |    270,941 |    274,430 |        3.69 |        3.64 |          6.00 |           9,247.4 |
| Sqids          | sequential |     0.612 |    101,331 |    208,726 |        9.87 |        4.79 |          3.96 |           9,047.2 |
| yurli          | random     |     1.340 |    267,816 |    269,276 |        3.73 |        3.71 |          6.00 |           9,279.6 |
| Sqids          | random     |     0.637 |     73,869 |    140,258 |       13.54 |        7.13 |          6.80 |           9,356.2 |

### 64-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |     2.448 |    224,764 |    214,919 |        4.45 |        4.65 |         12.00 |           9,833.4 |
| Sqids          | sequential |     0.640 |    100,896 |    204,380 |        9.91 |        4.89 |          3.96 |           9,047.2 |
| yurli          | random     |     2.449 |    219,860 |    210,102 |        4.55 |        4.76 |         12.00 |          10,208.1 |
| Sqids          | random     |     0.623 |     70,984 |     84,631 |       14.09 |       11.82 |         11.92 |          10,202.5 |

## No blocklist

### 16-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |     0.084 |    274,767 |    275,321 |        3.64 |        3.63 |          3.00 |           8,919.3 |
| Sqids          | sequential |     0.041 |    449,786 |    215,170 |        2.22 |        4.65 |          3.92 |           9,011.5 |
| yurli          | random     |     0.066 |    307,277 |    315,165 |        3.25 |        3.17 |          3.00 |           8,934.8 |
| Sqids          | random     |     0.043 |    472,272 |    208,919 |        2.12 |        4.79 |          3.94 |           9,028.7 |

### 32-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |     0.069 |    272,190 |    279,012 |        3.67 |        3.58 |          6.00 |           9,247.3 |
| Sqids          | sequential |     0.037 |    463,780 |    211,772 |        2.16 |        4.72 |          3.96 |           9,047.2 |
| yurli          | random     |     0.067 |    261,361 |    268,114 |        3.83 |        3.73 |          6.00 |           9,279.4 |
| Sqids          | random     |     0.043 |    367,377 |    141,013 |        2.72 |        7.09 |          6.80 |           9,356.2 |

### 64-bit

| Implementation | Dataset    | Init (ms) | Encode / s | Decode / s | Encode (us) | Decode (us) | Avg ID length | Peak memory (KiB) |
| -------------- | ---------- | --------: | ---------: | ---------: | ----------: | ----------: | ------------: | ----------------: |
| yurli          | sequential |     0.068 |    229,571 |    217,774 |        4.36 |        4.59 |         11.00 |           9,735.8 |
| Sqids          | sequential |     0.039 |    445,547 |    209,527 |        2.24 |        4.77 |          3.96 |           9,047.2 |
| yurli          | random     |     0.081 |    228,900 |    217,583 |        4.37 |        4.60 |         11.00 |          10,110.4 |
| Sqids          | random     |     0.046 |    290,961 |     84,537 |        3.44 |       11.83 |         11.92 |          10,202.5 |

## Integer/string conversion only

These measurements call `AlphabetEncoder.encode`/`decode`, Sqids' internal integer
conversion helpers, or the standard-library Base encoders directly. They exclude
Yurli/Sqids wrapper logic and blocklist handling.

### 16 character alphabet

| Conversion            | Encode / s | Decode / s | Avg ID length |
| --------------------- | ---------: | ---------: | ------------: |
| AlphabetEncoder       |    606,879 |    574,541 |         16.00 |
| Sqids integer helpers |    521,128 |    206,718 |         15.87 |
| stdlib Base16         |  3,853,324 |  1,498,094 |         16.00 |

### 32 character alphabet

| Conversion            | Encode / s | Decode / s | Avg ID length |
| --------------------- | ---------: | ---------: | ------------: |
| AlphabetEncoder       |    724,842 |    683,261 |         13.00 |
| Sqids integer helpers |    650,113 |    196,694 |         12.87 |
| stdlib Base32         |  3,823,483 |  2,277,312 |         16.00 |

### 64 character alphabet

| Conversion            | Encode / s | Decode / s | Avg ID length |
| --------------------- | ---------: | ---------: | ------------: |
| AlphabetEncoder       |    838,330 |    794,220 |         11.00 |
| Sqids integer helpers |    751,630 |    163,002 |         10.88 |
| stdlib Base64         |  3,609,319 |  2,205,016 |         12.00 |

### 85 character alphabet

| Conversion            | Encode / s | Decode / s | Avg ID length |
| --------------------- | ---------: | ---------: | ------------: |
| AlphabetEncoder       |    898,965 |    829,739 |         10.00 |
| Sqids integer helpers |    806,866 |    147,016 |          9.97 |
| stdlib Base85         |  3,875,257 |  3,195,568 |         10.00 |
| stdlib Ascii85        |  3,358,564 |  2,775,143 |         10.00 |

For the 64-bit comparison, both libraries receive values limited to Sqids' signed
platform integer range. This compares their shared input domain, not yurli's full
unsigned 64-bit domain. Peak memory is the additional traced memory during encoding and
decoding, including the retained outputs.
