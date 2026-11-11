# yurli architecture and mathematical design

## Scope

This document establishes the proposed design for yurli before implementation of its
permutation, string encoding, and blocklist behavior. yurli creates reversible,
fixed-length, URL-safe identifiers for unsigned integers. It's an obfuscation library,
not a security library. It doesn't provide encryption, confidentiality, or protection
from reverse engineering.

The implementation is split into three layers:

1. An integer permutation maps a value in the configured domain to another value in the
   same domain.
2. A fixed-width Base62 encoder maps that value to a normal identifier.
3. A blocklist layer emits the normal identifier when allowed, or encodes the same value
   in a disjoint, blocklist-safe fallback namespace.

The integer permutation doesn't know about alphabets, strings, or blocklists. The string
encoder doesn't choose or modify the permutation. The blocklist layer decides which
string representation to use.

## Integer permutation

For a configured width $b$ in $\{16, 32, 64\}$, define

$$
X_b = \{0, 1, \ldots, 2^b - 1\}.
$$

The permutation $P_b$ maps $X_b$ to itself. Inputs below zero or at least $2^b$ are
rejected; the implementation never wraps or truncates them.

The proposed implementation is a four-round balanced Feistel network. Each supported
width is even, so split a value into $b/2$-bit halves $L_0$ and $R_0$. For round key
$K_i$ and a fixed, documented 64-bit mixing function $F$, compute:

$$
L_{i+1} = R_i, \qquad R_{i+1} = L_i \oplus (F(R_i, K_i) \bmod 2^{b/2}).
$$

The inverse round is:

$$
R_i = L_{i+1}, \qquad L_i = R_{i+1} \oplus (F(L_{i+1}, K_i) \bmod 2^{b/2}).
$$

Decode applies the rounds in reverse key order. The round function doesn't need to be
invertible. Each Feistel round is invertible because its output contains the prior right
half and applies exclusive OR with a deterministic function of that half to the other
half. Thus, for every valid input $x$:

$$
P_b^{-1}(P_b(x)) = x.
$$

Generate four independent round keys with Python's `secrets` module. This randomness
chooses an instance's mapping; it doesn't make yurli secure. The 16-, 32-, and 64-bit
domain widths are fixed supported choices rather than arbitrary bit lengths. Custom
alphabets are deferred from the initial design.

## Fixed-length Base62 identifiers

The normal alphabet is:

```text
0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
```

Encode the permuted integer as Base62 and left-pad with `0` to the configured codec
identifier length $L$. This gives each value one canonical normal representation. Unlike
variable-width encoding, the length doesn't disclose the input's magnitude within a
codec. Fixed width doesn't provide security.

With no blocklist exclusions and no fallback prefix, Base62 needs at least 3, 6, and 11
characters for the 16-, 32-, and 64-bit domains. The fallback namespace consumes one
non-Base62 prefix character, so the initial total lengths must be at least 4, 7, and 12
characters respectively. A blocklist may require a longer $L$.

## Blocklist and fallback namespace

`EXAMPLE_BLOCKLIST` is an empty public set. An empty blocklist is the default.
Applications choose, persist, and maintain their own policy. The
[Sqids blocklist repository](https://github.com/sqids/sqids-blocklist) is the source for
any populated example list. Its MIT license names `Copyright (c) 2023 Sqids`; preserve
that notice and the license text with any copied data. The example list is sample data,
not maintained by the yurli project.

Matching is case-insensitive substring matching for every configured entry. This is
yurli's policy even when it uses Sqids-derived vocabulary; it doesn't copy Sqids'
entry-length-specific matching rules. Normalize and deduplicate entries as part of
configuration construction. Empty entries are invalid because every string contains the
empty string.

The fallback uses a prefix outside Base62, selected from URL-safe candidates such as
`-`, `_`, and `~`. Store it in the codec configuration. The decoder routes a
Base62-leading string to normal decoding and a non-Base62-leading string to fallback
decoding. The fallback matcher checks the entire prefix and suffix together, including
substrings that span their boundary.

For a fixed prefix $p$ and length $L$, let $A_L$ be the lexicographically ordered set of
strings $p + s$, where $s$ is a Base62 string of length $L - 1$ and the complete string
contains no configured blocked substring. A finite-state substring automaton plus
dynamic programming counts $A_L$ and supports ranking and unranking its strings. Choose
the shortest length and first configured prefix for which $|A_L| \ge 2^b$. Reject a
configuration if no supported prefix and length has sufficient capacity.

When the normal Base62 identifier is blocklisted, use the permuted integer as a rank in
$A_L$ and emit that fallback string. Both namespaces have exactly length $L$ and are
disjoint: normal identifiers contain only Base62 characters, while fallback strings
begin with a character outside Base62. Within each namespace, fixed-width Base62 or
rank/unrank gives a unique representation. Decoding therefore recovers the permuted
integer and applies $P_b^{-1}$. The fallback is deterministic, collision-free, and
terminates because configuration construction proves that the finite fallback set has at
least $2^b$ entries.

The automaton stores substring state, not an identifier-to-ID lookup table. Precompute
completion counts by remaining length and automaton state. Encoding and decoding cost
depend on the number of automaton states, alphabet size, and $L$; fallback rank and
unrank are slower than ordinary base conversion. Normal identifiers only need a
blocklist scan before emission.

If a custom blocklist leaves too few allowed strings for the chosen width, codec
construction fails clearly. No algorithm can produce $2^b$ distinct allowed IDs when the
configured output language has fewer than $2^b$ allowed strings.

## Blocklist strategy comparison

| Strategy                    | Correctness and length                                                                                                                                                                       | Complexity and decoding                                                                                                    | Decision                                                                                             |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| Reduced alphabet            | Makes blocked substrings impossible only if every forbidden entry is made unrepresentable. Removing characters can shrink capacity and increase all identifier lengths.                      | Simple matching and decoding; custom lists can remove too much of the alphabet.                                            | Reject as the primary strategy because it wastes capacity and doesn't handle every custom list well. |
| Normal Base62 plus fallback | Normal IDs stay compact. Fallback IDs use a separate prefix namespace with enough allowed strings at the same configured total length. The namespaces are disjoint by their first character. | Normal path is ordinary Base62 plus a match check. Fallback needs automaton counts and rank/unrank.                        | Recommend. It keeps the common path simple while proving uniqueness, safety, and termination.        |
| Rank/unrank every ID        | Maps every integer directly into the allowed-string set. A fixed length with at least $2^b$ allowed strings gives a direct injectivity proof.                                                | Automaton counting and rank/unrank are used for every encode and decode; all IDs pay the larger constrained-language cost. | Keep as a correctness comparison, not a selectable runtime profile.                                  |

The recommended fallback strategy improves on an unmarked retry or prefix convention:
the prefix is outside the normal alphabet, and its complete output is checked by the
automaton. This proves namespace separation and blocks unsafe strings across the prefix
boundary. This method uses no probabilistic retries.

## Configuration and compatibility

`Yurli()` generates a fresh random permutation configuration with an empty blocklist.
Applications must save that configuration and reuse it to preserve identifiers across
process restarts. The public API accepts Python keyword arguments, exposes `to_kwargs()`
for reconstruction, and provides versioned `to_bytes()` and `from_bytes()` methods for
storage. A caller can base64-encode the bytes when a text column is needed.

The persisted configuration includes everything that affects identifiers:

- `ConfigurationFormatVersion` and `PermutationAlgorithmVersion` enum values.
- Integer width and all four Feistel round keys.
- The exact normalized blocklist entries and matching policy.
- The selected fallback prefix and identifier length.
- The fixed alphabet and matching rules through the algorithm version.

Changing round keys changes every mapping. Changing the blocklist or fallback settings
can change which IDs use which namespace or rank. Keep the old configuration to decode
IDs created with it. Format versions must not silently reinterpret old configuration
bytes after an upgrade.

## Proposed public API

This design PR defines the public names and signatures. The methods raise
`NotImplementedError` until later implementation PRs. `Yurli()` uses 64 bits by default;
callers can pass `bits=16` or `bits=32`. An empty blocklist is the default.

```python
from yurli import EXAMPLE_BLOCKLIST, Yurli

codec = Yurli(bits=32, blocklist=EXAMPLE_BLOCKLIST)
identifier = codec.encode(12345)
original = codec.decode(identifier)

assert original == 12345

saved_kwargs = codec.to_kwargs()
restored_from_kwargs = Yurli(**saved_kwargs)

saved_bytes = codec.to_bytes()
restored_from_bytes = Yurli.from_bytes(saved_bytes)
```

The runtime surface is framework-independent and has no database dependency. The library
exposes the empty example set; applications own their list and decide how to persist it.

## Performance and tradeoffs

Four Feistel rounds use more integer operations than an affine multiply-and-add
permutation. An affine permutation is faster but preserves obvious arithmetic structure.
Four rounds are the proposed balance for non-security obfuscation. Measure the complete
codec before making speed claims.

The normal encoding is fixed-width. This costs a few characters compared with
variable-width Base62 but avoids disclosing a coarse input magnitude through the normal
length. Fallback capacity may increase the configured length. More aggressive blocklists
can increase it further or make a width impossible.

Benchmarking and optimization belong in a later PR. Compare deterministic 16-, 32-, and
64-bit workloads against Sqids only after the implementation and blocklist behavior are
stable. Don't present yurli as encryption or as an authorization mechanism.
