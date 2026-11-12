# yurli architecture and mathematical design

## Scope

This document describes the implementation currently present in yurli's internal
encoding modules. yurli creates reversible, fixed-length, URL-safe identifiers for
unsigned integers. It provides obfuscation, not encryption, confidentiality, or
protection from reverse engineering.

The implementation has three independent layers:

1. `IntegerPermutation` maps a value in a configured domain to another value in that
   domain.
2. `AlphabetEncoder` maps that value to a fixed-width positional identifier.
3. `BlocklistEncoder` reduces an alphabet before positional encoding, making configured
   blocked substrings impossible to emit.

The permutation knows nothing about strings or blocklists. The base encoder knows
nothing about permutations. The blocklist encoder subclasses the base encoder and has no
fallback namespace or retry path.

## Integer permutation

For a configured width $b$ in $\{16, 32, 64\}$, define

$$
X_b = \{0, 1, \ldots, 2^b - 1\}.
$$

`IntegerPermutation` maps $X_b$ to itself. Inputs below zero or at least $2^b$ are
rejected; values are never wrapped or truncated.

The implementation uses a four-round balanced Feistel network. Each supported width is
even, so split a value into $b / 2$-bit halves $L_0$ and $R_0$. For round key $K_i$ and
the 64-bit SplitMix64 finalizer $F$, compute:

$$
L_{i+1} = R_i, \qquad R_{i+1} = L_i \oplus (F(R_i, K_i) \bmod 2^{b / 2}).
$$

The inverse applies the same rounds in reverse key order:

$$
R_i = L_{i+1}, \qquad L_i = R_{i+1} \oplus (F(L_{i+1}, K_i) \bmod 2^{b / 2}).
$$

The round function need not be invertible. Each Feistel round is invertible because it
retains the prior right half and combines a deterministic function of that half with the
other half using exclusive OR. Thus $P_b^{-1}(P_b(x)) = x$ for every valid $x$.

Four 64-bit round keys either come from the caller or are generated with Python's
`secrets` module. The keys choose a mapping; they don't make yurli cryptographically
secure.

## Fixed-width positional identifiers

The default alphabet is Base62:

```text
0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
```

`AlphabetEncoder` uses the configured alphabet as positional digits and emits them in
least-significant-first order. It always returns exactly $L$ characters, so the
alphabet's first character pads the most-significant side. Decoding reverses the string
and performs ordinary positional accumulation. This creates one canonical representation
for every value in the configured domain.

With the default Base62 alphabet, the 16-, 32-, and 64-bit domains need at least 3, 6,
and 11 characters respectively. A custom alphabet must have at least two unique
characters. A smaller alphabet can require a larger $L$, and an explicitly supplied
length shorter than the minimum is rejected.

Fixed width avoids disclosing a coarse input magnitude through identifier length. It
doesn't provide security.

## Blocklist alphabet reduction

The example blocklist is stored in [`yurli/blocklist.txt`](../yurli/blocklist.txt), with
one entry per line in sorted order. `yurli.constants.EXAMPLE_BLOCKLIST` reads that file
as UTF-8 and exposes the entries as a set. The file order makes additions and review
deterministic, but callers must not rely on the iteration order of the set.

`BlocklistEncoder` requires at least one non-empty entry. An empty iterable or an
iterable containing only empty entries raises `ValueError`. Applications choose and
maintain their own blocklist policy.

Entries are normalized with `str.casefold()` and deduplicated. An entry longer than the
selected identifier length remains in the `blocklist` property for reporting, but can't
occur in output. Empty entries are invalid because every string contains the empty
string.

To make a relevant blocked word impossible, at least one distinct character in that word
must be absent from the output alphabet. Starting with the candidate alphabet,
`BlocklistEncoder` repeatedly:

1. Computes the minimum fixed length from the domain width and current alphabet size.
2. Finds blocked words no longer than that length whose distinct `casefold()` characters
   are all available.
3. Counts character occurrences across those spellable words.
4. Removes the character with the highest count. A tie removes the lexicographically
   greatest `casefold()` character.

Character removal is case-insensitive, so removing `a` also removes `A` when both occur
in the alphabet. Surviving characters retain their original order. The greedy algorithm
ends when no relevant blocked word is spellable. It guarantees output can't contain a
blocked substring, but doesn't claim to produce a globally largest safe alphabet.

The resulting alphabet is passed to `AlphabetEncoder` unchanged. Encoding and decoding
therefore remain ordinary fixed-width positional conversion: there is no identifier
scan, fallback namespace, finite-state automaton, rank/unrank step, or retry. If pruning
would leave fewer than two characters, construction fails. Pruning can increase $L$ for
every identifier in that encoder.

## Public API status

The public `Yurli` interface defines the planned configuration and serialization
surface, but its methods currently raise `NotImplementedError`. The implemented pieces
are `IntegerPermutation`, `AlphabetEncoder`, and `BlocklistEncoder`. Composition of
those layers, public blocklist defaults, and configuration serialization remain future
work.

The planned public API is framework-independent and has no database dependency.

## Tradeoffs

Four Feistel rounds require more integer operations than an affine multiply-and-add
permutation, but obscure more obvious arithmetic structure. This is a non-security
obfuscation tradeoff, not a cryptographic claim.

The current blocklist approach keeps runtime encoding and decoding simple, but alphabet
reduction can make all identifiers longer. Dense or overlapping blocklists may remove
enough characters to make an encoder impossible to construct. Benchmarking belongs after
the public codec is implemented. Don't present yurli as encryption or authorization.
