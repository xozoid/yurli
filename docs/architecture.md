# yurli architecture and mathematical design

## Scope

yurli creates reversible, fixed-length, URL-safe identifiers for unsigned integers. It
provides obfuscation, not encryption, confidentiality, or protection from reverse
engineering. The public `Yurli` class composes an integer permutation and a positional
encoder. The encoder can prune its alphabet to prevent configured substrings.

## Integer permutation

For a configured width $b$ in $\{16, 32, 64\}$, define

$$
X_b = \{0, 1, \ldots, 2^b - 1\}.
$$

`IntegerPermutation` maps $X_b$ to itself. Inputs outside this domain raise
`ValueError`; values are never wrapped or truncated.

The implementation uses a four-round balanced Feistel network. Each supported width is
even, so a value splits into $b / 2$-bit halves $L_0$ and $R_0$. For round key $K_i$ and
the 64-bit SplitMix64 finalizer $F$, each round computes:

$$
L_{i+1} = R_i, \qquad R_{i+1} = L_i \oplus (F(R_i, K_i) \bmod 2^{b / 2}).
$$

The inverse applies rounds in reverse key order:

$$
R_i = L_{i+1}, \qquad L_i = R_{i+1} \oplus (F(L_{i+1}, K_i) \bmod 2^{b / 2}).
$$

Each Feistel round is invertible because it retains the prior right half and combines a
deterministic function of that half with the other half using exclusive OR. Therefore
the four-round permutation is bijective on the configured domain. Four unsigned 64-bit
round keys either come from the caller or are generated with Python's `secrets` module.
The keys select a mapping; they don't make yurli cryptographically secure.

## Fixed-width positional identifiers

The default alphabet is Base62:

```text
0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
```

`AlphabetEncoder` validates the requested width and alphabet, then emits the integer in
least-significant-digit-first order. It returns exactly $L$ characters, so the first
alphabet character pads the most-significant side. Decoding reverses the string and
accumulates its positional value. Values outside the configured domain, identifiers of
the wrong length, and characters outside the alphabet raise `ValueError`.

With the default alphabet, the 16-, 32-, and 64-bit domains need at least 3, 6, and 11
characters. An alphabet must contain unique ASCII characters, with at least two
characters. Uppercase and lowercase characters are distinct digits. The identifier
length is the greater of an explicitly requested length and the minimum length needed
for the complete domain using the final alphabet. Fixed width hides coarse input
magnitude through identifier length, but doesn't provide security.

## Blocklist alphabet pruning

Blocklist behavior is implemented by `AlphabetEncoder`; there is no `BlocklistEncoder`
subclass. Its `blocklist` argument defaults to an empty iterable, so no filtering occurs
unless the caller supplies entries. The optional example list is stored in
[`yurli/blocklist.txt`](../yurli/blocklist.txt), exported as `yurli.EXAMPLE_BLOCKLIST`,
and based on
[Sqids Python's `constants.py`](https://github.com/sqids/sqids-python/blob/main/sqids/constants.py).
[`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md) retains its attribution and MIT
License. Applications choose and maintain their own blocklist policy.

Entries must be non-empty ASCII strings. An empty iterable is valid; an empty entry or
non-ASCII entry raises `ValueError`. Entries are lowercased with `str.lower()` and
deduplicated. Matching is therefore case-insensitive for ASCII characters. A word longer
than the effective identifier length can't occur in output.

To make a relevant blocked word impossible, at least one distinct character in that word
must be absent from the output alphabet. Starting with the candidate alphabet,
`AlphabetEncoder` repeats these steps until no relevant word is spellable:

1. Compute the greater of the explicit length and the minimum length for the current
   alphabet and domain width.
2. Find blocked words no longer than that length whose distinct lowercase characters are
   all available.
3. Count each distinct character once per spellable word.
4. Remove the character with the highest count. Ties remove the lexicographically
   greatest lowercase character.

Removal is case-insensitive, so removing `a` also removes `A` if both occur in the
alphabet. Surviving characters retain their original case and order. Pruning terminates
because each iteration removes a character; if fewer than two remain, construction
raises `ValueError`. The greedy method ensures no configured substring is spellable from
the final alphabet, but doesn't guarantee the globally largest safe alphabet. Pruning
may increase the fixed identifier length.

Encoding and decoding don't scan output or use a fallback namespace, automaton,
rank/unrank step, or retry. They use ordinary fixed-width positional conversion over the
pruned alphabet.

## Public API and persisted configuration

`Yurli` composes the layers in this order:

1. `encode` validates and permutes the integer, then passes it to `AlphabetEncoder`.
2. `decode` validates and converts the identifier to an integer, then inverts the
   permutation.

A new instance generates random round keys unless explicit keys are supplied. The
versioned configuration from `Yurli.config` includes the format version, permutation
algorithm version, width, round keys, final alphabet, and identifier length. `to_bytes`
returns deterministic UTF-8 JSON; `from_bytes` validates and restores those settings.
The original blocklist isn't serialized because the final pruned alphabet is stored.
Restoration rejects malformed UTF-8 or JSON, missing or extra fields, invalid field
types, unsupported versions, and invalid keys or encoder settings. Retain the
configuration to decode identifiers after process restarts or upgrades. A new codec or
changed configuration has a different mapping.

## Tradeoffs

The four-round Feistel network uses more integer operations than a simple affine
permutation. It provides reversible obfuscation, not cryptographic security. Alphabet
pruning keeps runtime conversion simple, but can increase identifier lengths. A dense
blocklist may leave too few characters to represent the domain, in which case
construction fails. See [`../benchmarks/`](../benchmarks/) for benchmark methodology and
results.
