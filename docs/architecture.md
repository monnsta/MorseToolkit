# Architecture

MorseToolkit is built as a layered toolkit rather than as a single encoder/decoder implementation. Each layer has a focused responsibility and exposes reusable components that can be used independently or composed through the high-level `Morse` API.

The main design goal is to keep **what Morse means**, **how it is represented**, **how boundaries are handled**, and **how ambiguous Morse is solved** separate from one another.

---

## Design Goals

MorseToolkit is designed around several principles:

- **Separation of concerns** — alphabets, representations, parsing, encoding, and solving are independent components.
- **Composable components** — lower-level classes can be used without going through the high-level API.
- **Extensibility** — custom alphabets, representations, boundary syntax, and scoring strategies can be introduced without modifying the core.
- **Explicit data models** — Morse data is represented with structured types instead of passing raw strings between every layer.
- **Immutable value objects** — core data structures use frozen dataclasses and tuples where appropriate.
- **Simple high-level API** — common operations should require only a few lines of code.
- **Algorithmic separation** — decoding known boundaries and solving unknown boundaries are treated as different problems.

---

## Package Structure

The active package is organized into the following layers:

```text
morse/
├── alphabets/
│   └── international.py
│
├── core/
│   ├── alphabet.py
│   ├── candidate.py
│   ├── sequence.py
│   ├── stream.py
│   ├── symbols.py
│   └── tokens.py
│
├── encoding/
│   ├── decoder.py
│   └── encoder.py
│
├── parsing/
│   ├── base.py
│   ├── boundaries.py
│   ├── spaced.py
│   ├── tokenizer.py
│   └── unspaced.py
│
├── representations/
│   ├── arbitrary.py
│   ├── base.py
│   └── text.py
│
├── solving/
│   ├── dictionary.py
│   ├── index.py
│   ├── scorer.py
│   ├── segmenter.py
│   └── solver.py
│
├── timing/
│   ├── __init__.py
│   ├── decoder.py
│   ├── profile.py
│   └── signal.py

├── utilities/
│   ├── __init__.py
│   ├── formatter.py
│   ├── statistics.py
│   └── validator.py

├── api.py
└── __init__.py
```

---

# Architectural Layers

The project can be viewed roughly as:

```text
        ┌─────────────────┐
        │   Public API    │
        │     Morse       │
        └────────┬────────┘
                 │
     ┌───────────┼──────────────┐
     │           │              │
     ▼           ▼              ▼
Encoding     Parsing        Solving
     │           │              │
     │           ▼              ▼
     │    Representations  Dictionary
     │           │         + Index
     │           │              │
     └─────┬─────┴──────────────┘
           │
           ▼
      Core Types
           │
           ▼
        Alphabets
```

This is a conceptual dependency view rather than a strict inheritance hierarchy.

---

# Core Layer

The `morse.core` package contains the fundamental types used throughout the library.

It does not decide how Morse should be displayed, how text should be encoded, or how an ambiguous message should be solved.

Its job is to provide the vocabulary used by the rest of the system.

---

## `MorseSymbol`

`MorseSymbol` represents the two fundamental Morse signals:

```python
from morse.core import MorseSymbol

MorseSymbol.DOT
MorseSymbol.DASH
```

The values are:

```text
DOT  = "."
DASH = "-"
```

Using an enum instead of raw strings gives the internal system a stable representation of Morse symbols.

For example, an encoded `A` is represented internally as:

```text
DOT DASH
```

rather than directly as the string `".-"`.

This distinction is important because the textual representation of those symbols can be changed independently.

---

## `MorseToken`

`MorseToken` represents a piece of a boundary-aware Morse stream.

There are three token types:

```text
SYMBOL
CHARACTER_BOUNDARY
WORD_BOUNDARY
```

A symbol token contains a `MorseSymbol`.

A boundary token does not contain a symbol.

For example:

```text
.... . .-.. .-.. ---
```

can conceptually become:

```text
SYMBOL SYMBOL SYMBOL SYMBOL
CHARACTER_BOUNDARY
SYMBOL
CHARACTER_BOUNDARY
...
```

This lets encoding and parsing preserve character and word boundaries without representing everything as a raw string.

---

## `MorseStream`

`MorseStream` is an immutable sequence of `MorseToken` objects.

It is used when boundaries matter.

Conceptually:

```text
MorseStream
    │
    ├── symbol
    ├── symbol
    ├── symbol
    ├── symbol
    ├── character boundary
    ├── symbol
    └── ...
```

The encoder produces a `MorseStream`, and the decoder consumes one.

This gives the encoding layer a structured intermediate representation before a textual representation is chosen.

---

## `MorseSequence`

`MorseSequence` is an immutable sequence of `MorseSymbol` values without boundaries.

For example:

```text
......-...-..---
```

becomes a sequence of symbols such as:

```text
DOT DOT DOT DOT DOT DOT
DASH DOT DOT DOT DASH DOT
DOT DASH DASH DASH
```

The sequence intentionally does not contain character or word boundaries.

This makes it suitable for the solving system, where those boundaries have to be inferred.

---

## `MorseSegmentation`

`MorseSegmentation` represents one possible division of a `MorseSequence` into characters.

For example, the same continuous Morse sequence may potentially be divided as:

```text
.... | . | .-.. | .-.. | ---
```

or in another valid way.

The segmenter produces these possible character-level divisions, while the solver determines which segmentation forms a plausible sequence of words.

---

## `MorseCandidate`

`MorseCandidate` represents the result of solving.

It contains:

```python
MorseCandidate(
	text="HELLO",
	score=1.0,
)
```

The candidate keeps the resulting text and its score together.

This allows solving algorithms to return a meaningful result without coupling the caller to the internal dynamic-programming state.

---

# Alphabet Layer

The alphabet layer defines which characters correspond to which Morse symbols.

The main abstraction is:

```python
MorseAlphabet
```

An alphabet provides four operations:

```text
encode(character)
decode(symbols)
can_encode(character)
can_decode(symbols)
```

The alphabet therefore answers:

> "What Morse sequence represents this character?"

It does **not** answer:

> "How should those Morse symbols be displayed?"

That responsibility belongs to the representation layer.

---

## International Morse

The built-in alphabet is:

```python
from morse.alphabets import InternationalMorse

alphabet = InternationalMorse()
```

Its internal mapping associates characters with tuples of `MorseSymbol` values.

For example, conceptually:

```text
A → (DOT, DASH)
B → (DASH, DOT, DOT, DOT)
```

The current implementation supports letters, digits, and the punctuation defined by `InternationalMorse`.

Encoding is case-insensitive, while decoding produces the alphabet's canonical uppercase representation.

---

# Representation Layer

The representation layer controls how `MorseSymbol` values become external strings.

The important distinction is:

```text
Alphabet
    character → Morse symbols

Representation
    Morse symbols → textual symbols
```

For example, the standard representation uses:

```text
DOT  → "."
DASH → "-"
```

But another representation could use:

```text
DOT  → "s"
DASH → "d"
```

The alphabet does not need to change for this.

This separation is one of the central architectural decisions in MorseToolkit.

---

## `TextRepresentation`

`TextRepresentation` provides the standard textual representation:

```text
. = DOT
- = DASH
```

This is what the normal high-level API uses by default.

---

## `ArbitraryRepresentation`

`ArbitraryRepresentation` allows custom strings for the two Morse symbols.

For example:

```text
DOT  → "s"
DASH → "d"
```

The same underlying alphabet can therefore be represented using completely different textual symbols.

See [Representation](representation.md) and [Custom Alphabets](custom-alphabets.md) for extension details.

---

# Encoding Layer

The encoding layer converts text into structured Morse data.

The main components are:

```text
MorseEncoder
MorseDecoder
```

---

## `MorseEncoder`

`MorseEncoder` receives:

```text
text
  ↓
MorseAlphabet
  ↓
Morse symbols
  ↓
MorseStream
```

It is responsible for creating character and word boundary tokens.

For example:

```text
HELLO WORLD
```

becomes a stream conceptually equivalent to:

```text
.... | . | .-.. | .-.. | --- || .-- | --- | .-. | .-.. | -..
```

where `|` represents a character boundary and `||` represents a word boundary conceptually.

The encoder itself does not decide how those boundaries should look as text.

---

## `MorseDecoder`

`MorseDecoder` performs the inverse operation.

It receives a boundary-aware `MorseStream`:

```text
MorseStream
    ↓
MorseDecoder
    ↓
text
```

Because the stream already contains character and word boundaries, the decoder does not need to guess where characters begin or end.

That distinction is important:

```text
Known boundaries → decode
Unknown boundaries → solve
```

---

# Parsing Layer

Parsing converts external Morse text into the structured representations used internally.

There are two primary parsing paths.

```text
Spaced Morse
    ↓
SpacedParser
    ↓
MorseStream
```

and:

```text
Unspaced Morse
    ↓
UnspacedParser
    ↓
MorseSequence
```

---

## `MorseTokenizer`

The tokenizer is the first stage of spaced parsing.

It scans a string from left to right and identifies:

```text
VALUE
CHARACTER_BOUNDARY
WORD_BOUNDARY
```

Word boundaries are checked before character boundaries.

This matters for the default syntax:

```text
character boundary = " "
word boundary      = "   "
```

Three spaces therefore become one word-boundary token rather than three character-boundary tokens.

---

## `MorseBoundarySyntax`

Boundary syntax defines how boundaries appear in textual Morse.

The defaults are:

```text
character boundary = " "
word boundary      = "   "
```

It is possible to provide different values:

```python
MorseBoundarySyntax(
	character_boundary="/",
	word_boundary="//",
)
```

The parser uses this configuration when interpreting external Morse text.

---

## `SpacedParser`

`SpacedParser` combines:

```text
MorseTokenizer
MorseRepresentation
MorseBoundarySyntax
```

Its responsibility is to transform boundary-aware Morse text into a `MorseStream`.

Conceptually:

```text
".... . .   .... . ."
       │
       ▼
    tokenizer
       │
       ▼
 raw tokens
       │
       ▼
 representation decoding
       │
       ▼
 MorseStream
```

---

## `UnspacedParser`

`UnspacedParser` is deliberately simpler.

It converts the entire textual value into a `MorseSequence`.

It does not attempt to discover characters or words.

For example:

```text
"......-...-..---"
```

becomes:

```text
MorseSequence
```

with no information about how that sequence should be segmented.

That missing information is handled by the solving layer.

---

# Solving Layer

The solving layer handles the fundamentally different problem of interpreting Morse when character and word boundaries are missing.

The main components are:

```text
MorseDictionary
MorseWordIndex
MorseScorer
MorseSegmenter
MorseSolver
```

---

# Dictionary

`MorseDictionary` provides normalized dictionary membership and prefix operations.

Words are normalized to lowercase.

It supports operations such as:

```python
dictionary.contains("hello")
dictionary.has_prefix("hel")
```

The prefix functionality is useful when searching possible word candidates.

---

# Word Index

`MorseWordIndex` is a trie-like index over the Morse encodings of dictionary words.

Instead of repeatedly encoding every dictionary word while solving, the solver can use the index to find words matching a position in a Morse sequence.

Conceptually:

```text
Dictionary words
      ↓
encode each word
      ↓
MorseWordIndex
      ↓
lookup matching Morse spans
```

This makes dictionary matching a separate concern from scoring.

---

# Scorers

A `MorseScorer` determines how desirable a candidate word is.

The base interface provides:

```text
context_size
score(word, context)
```

Several scoring strategies are available.

### `DictionaryScorer`

The default scorer rewards words that exist in the configured dictionary.

### `FrequencyScorer`

Scores words using supplied frequency values.

### `BigramScorer`

Scores a word based on its relationship with the previous word.

The scorer abstraction allows the solving algorithm to remain independent of the source of linguistic preference.

---

# Segmenter

`MorseSegmenter` handles character-level ambiguity.

Given a continuous sequence:

```text
......-...-..---
```

it explores valid ways of splitting the sequence into individual Morse characters.

The alphabet determines which symbol sequences are valid characters.

The segmenter therefore connects:

```text
MorseSequence
      ↓
possible character segmentations
      ↓
MorseSegmentation
```

It does not decide which segmentation forms the best words.

---

# Solver

`MorseSolver` combines the major solving components.

Its conceptual pipeline is:

```text
MorseSequence
      │
      ▼
MorseWordIndex
      │
      ▼
possible dictionary words
      │
      ▼
MorseScorer
      │
      ▼
dynamic programming / beam search
      │
      ▼
MorseCandidate
```

The solver uses different strategies depending on whether the scorer needs context.

### Context-independent scoring

When a scorer has no contextual dependency, the solver can keep the best state at each Morse position.

Conceptually:

```text
position 0 → best state
position 1 → best state
position 2 → best state
...
```

### Context-aware scoring

When a scorer depends on previous words, multiple states may need to survive at each position.

The solver therefore uses a bounded beam controlled by:

```python
beam_width
```

This keeps the search manageable while allowing contextual alternatives to survive.

---

# High-Level API

The `Morse` class in `morse.api` is the orchestration layer.

It wires together:

```text
Alphabet
Representation
Boundary Syntax
Encoder
Decoder
Parsers
Dictionary
Scorer
Solver
```

A default instance is effectively:

```text
Morse
 ├── InternationalMorse
 ├── TextRepresentation
 ├── MorseBoundarySyntax
 ├── MorseEncoder
 ├── MorseDecoder
 ├── SpacedParser
 └── UnspacedParser
```

Solving components are constructed when needed.

This keeps the high-level API convenient while still exposing the underlying architecture.

---

# Module-Level API

The package-level functions:

```python
morse.encode(...)
morse.encode_unspaced(...)
morse.decode(...)
morse.solve(...)
```

are convenience wrappers around a shared default `Morse` instance.

For example:

```python
import morse

encoded = morse.encode("HELLO")
decoded = morse.decode(encoded)
```

For more control, users can create their own instance:

```python
from morse import Morse

morse = Morse(...)
```

This is the preferred entry point when configuration needs to be persistent across multiple operations.

---

# Data Flow

## Normal Encoding

```text
Python string
      │
      ▼
MorseEncoder
      │
      ▼
MorseAlphabet
      │
      ▼
MorseStream
      │
      ▼
Morse.representation
      │
      ▼
Morse.representation + boundaries
      │
      ▼
Morse string
```

For example:

```text
"HELLO"
   ↓
Morse symbols
   ↓
MorseStream
   ↓
".... . .-.. .-.. ---"
```

---

## Normal Decoding

```text
Morse string
      │
      ▼
SpacedParser
      │
      ├── MorseTokenizer
      ├── MorseBoundarySyntax
      └── MorseRepresentation
      │
      ▼
MorseStream
      │
      ▼
MorseDecoder
      │
      ▼
Python string
```

---

## Unspaced Solving

```text
continuous Morse string
          │
          ▼
   UnspacedParser
          │
          ▼
   MorseSequence
          │
          ▼
     MorseSolver
          │
          ├── MorseWordIndex
          ├── MorseDictionary
          ├── MorseScorer
          └── search algorithm
          │
          ▼
    MorseCandidate
          │
          ▼
       text
```

This is intentionally separate from normal decoding because an unspaced sequence is ambiguous by definition.

---

# Extension Points

The architecture is designed so that individual parts can be replaced without rewriting the rest of the system.

## Custom Alphabet

Implement:

```python
class MorseAlphabet(ABC):
	def encode(self, character): ...

	def decode(self, symbols): ...

	def can_encode(self, character): ...

	def can_decode(self, symbols): ...
```

The encoding and solving systems can then use the new alphabet.

---

## Custom Representation

Implement the `MorseRepresentation` interface to change how symbols are represented externally.

This can change:

```text
.
-
```

into another pair of symbols without changing the alphabet.

---

## Custom Boundaries

`MorseBoundarySyntax` can change how character and word boundaries are written.

The tokenizer and spaced parser then interpret Morse according to that syntax.

---

## Custom Scorer

Implement `MorseScorer` to introduce a different definition of "best" solution.

This allows solving to use:

- word frequencies
- linguistic probabilities
- contextual relationships
- application-specific weights
- custom ranking systems

without changing `MorseSolver`.

---

# Separation of Responsibilities

A major part of the architecture is avoiding responsibility overlap.

Component             | Responsibility                                |
:-------------------- | :-------------------------------------------- |
`MorseSymbol`         | Represents dot/dash signals                   |
`MorseAlphabet`       | Maps characters to Morse symbols              |
`MorseRepresentation` | Maps symbols to external representations      |
`MorseToken`          | Represents symbols and boundaries             |
`MorseStream`         | Stores boundary-aware Morse                   |
`MorseSequence`       | Stores boundary-free Morse                    |
`MorseEncoder`        | Converts text into a Morse stream             |
`MorseDecoder`        | Converts a known-boundary stream into text    |
`MorseTokenizer`      | Finds textual Morse boundaries                |
`SpacedParser`        | Parses boundary-aware Morse                   |
`UnspacedParser`      | Parses continuous Morse                       |
`MorseDictionary`     | Stores normalized words                       |
`MorseWordIndex`      | Efficiently finds Morse word matches          |
`MorseScorer`         | Scores candidate words                        |
`MorseSegmenter`      | Finds possible character splits               |
`MorseSolver`         | Searches for the best complete interpretation |
`Morse`               | Coordinates the components                    |
`morse.*` functions   | Convenience API                               |

The goal is that no individual class needs to know how the entire toolkit works.

---

# Immutability

Several core structures are immutable:

```python
@dataclass(frozen=True, slots=True)
class MorseCandidate: ...
```

and:

```python
@dataclass(frozen=True, slots=True)
class MorseSequence: ...
```

The underlying collections are also stored as tuples.

This provides predictable value objects that can safely be passed between layers without callers accidentally modifying shared state.

Mutable algorithmic state remains internal to components such as the solver and indexes where mutation is useful for construction or search.

---

# Why Raw Strings Are Not Used Everywhere

It would be possible to implement the entire library using strings:

```text
".-.. --- ..."
```

but that would force every component to understand the same textual representation.

Instead, MorseToolkit introduces intermediate types:

```text
MorseSymbol
MorseToken
MorseStream
MorseSequence
MorseSegmentation
MorseCandidate
```

This means a representation can change without changing the alphabet, and a solver can work with symbol sequences without knowing anything about textual delimiters.

For example:

```text
TextRepresentation
        ↓
      "." "-"
```

can be replaced with:

```text
ArbitraryRepresentation
        ↓
      "s" "d"
```

while the internal alphabet remains unchanged.

---

# Testing Architecture

Tests are organized around the same major package boundaries as the implementation:

```text
tests/
├── alphabets/
├── core/
├── encoding/
├── parsing/
├── representations/
├── solving/
├── timing/
├── utilities/
└── test_api.py
```

This makes individual layers independently testable.

For example:

```text
tests/encoding/
```

tests encoding behavior without requiring the high-level API to be involved, while:

```text
tests/solving/
```

covers dictionary, indexing, scoring, segmentation, and solving independently.

`test_api.py` covers the public high-level interface.

---

# Packaging and Public Exports

The package uses a `src/` layout:

```text
src/
└── morse/
```

The public package exposes the convenient API through `morse.__init__`.

The individual subpackages also provide their own exports:

```text
morse.core
morse.alphabets
morse.encoding
morse.parsing
morse.representations
morse.solving
```

This allows users to start simple:

```python
import morse
```

and progressively access lower-level functionality when needed.

---

# Current Scope

The currently active architecture covers:

- Morse symbols
- Morse alphabets
- textual representations
- arbitrary representations
- encoding
- decoding
- spaced parsing
- unspaced parsing
- dictionaries
- Morse word indexing
- scoring
- character segmentation
- unspaced Morse solving
- the high-level `Morse` API

The following directories exist as architectural placeholders but are not currently active feature layers:

```text
morse/timing/
morse/utilities/
```

They should not be treated as part of the current public feature set until their implementations are completed.

---

# Summary

MorseToolkit separates Morse processing into a pipeline of focused components:

```text
Character meaning
      │
      ▼
   Alphabet
      │
      ▼
 Morse symbols
      │
      ├───────────────┐
      │               │
      ▼               ▼
Representation     Solver
      │               │
      ▼               │
Textual Morse         │
      │               │
      ▼               ▼
   Parsing       Dictionary/
      │            Scoring
      ▼               │
MorseStream or        ▼
MorseSequence   MorseCandidate
```

The most important architectural distinction is between **known-boundary Morse** and **unknown-boundary Morse**:

```text
Known boundaries
    → parse
    → decode

Unknown boundaries
    → parse into a sequence
    → search
    → score
    → solve
```

This separation allows the simple encode/decode path to remain straightforward while giving the solving system enough structure to support substantially more advanced algorithms.

The result is a toolkit where the common path is simple, while the underlying components remain independently replaceable and extensible.
