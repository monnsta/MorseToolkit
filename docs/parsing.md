# Parsing

MorseToolkit provides parsers for converting string representations of Morse code into structured Morse data.

There are two primary parsing modes:

- **Spaced parsing** — boundaries between characters and words are already present.
- **Unspaced parsing** — the entire Morse sequence is continuous and contains no boundaries.

Parsing is separate from encoding and decoding. A parser turns strings into Morse structures; the decoder can then interpret those structures as text.

## The Parser Interface

All parsers implement `MorseParser`.

```python
from morse.parsing import MorseParser
```

`MorseParser` is a generic abstract interface:

```python
class MorseParser(ABC, Generic[T]):
	def parse(self, value: str) -> T: ...
```

Different parser implementations return different structures.

Parser           | Result          |
:--------------- | :-------------- |
`SpacedParser`   | `MorseStream`   |
`UnspacedParser` | `MorseSequence` |

## Boundary Syntax

`MorseBoundarySyntax` defines how character and word boundaries appear in a Morse string.

```python
from morse.parsing import MorseBoundarySyntax

boundaries = MorseBoundarySyntax()
```

The default syntax is:

Boundary  | Representation |
:-------- | :------------- |
Character | one space      |
Word      | three spaces   |

For example:

```text
.... . .-.. .-.. ---   .-- --- .-. .-.. -..
```

Here, single spaces separate characters while three spaces separate words.

### Custom Boundaries

The boundary syntax can be changed:

```python
boundaries = MorseBoundarySyntax(
	character_boundary="|",
	word_boundary="||",
)
```

The resulting syntax can be used with a parser:

```python
from morse.parsing import SpacedParser
from morse.representations import TextRepresentation

parser = SpacedParser(
	TextRepresentation(),
	boundaries=boundaries,
)

stream = parser.parse("....|.|.-..|.-..|---||.--|---|.-.|.-..|-..")
```

Character and word boundaries must both be non-empty and must be different.

```python
MorseBoundarySyntax(
	character_boundary="",
)
# ValueError

MorseBoundarySyntax(
	character_boundary="|",
	word_boundary="|",
)
# ValueError
```

## Tokenization

`MorseTokenizer` is the first stage of spaced parsing.

It scans a string and breaks it into raw tokens without interpreting the Morse symbols themselves.

```python
from morse.parsing import MorseTokenizer

tokenizer = MorseTokenizer()

tokens = tokenizer.tokenize("... --- ...")
```

The tokenizer produces `RawToken` objects.

Each token has:

- `type`
- `value`

There are three token types:

Type                           | Meaning                                                     |
:----------------------------- | :---------------------------------------------------------- |
`TokenType.VALUE`              | A Morse value containing one or more representation symbols |
`TokenType.CHARACTER_BOUNDARY` | A character separator                                       |
`TokenType.WORD_BOUNDARY`      | A word separator                                            |

For example:

```python
tokens = tokenizer.tokenize("... --- ...")

[(token.type, token.value) for token in tokens]
# [
#     (TokenType.VALUE, "..."),
#     (TokenType.CHARACTER_BOUNDARY, " "),
#     (TokenType.VALUE, "---"),
#     (TokenType.CHARACTER_BOUNDARY, " "),
#     (TokenType.VALUE, "..."),
# ]
```

The tokenizer does not convert `"..."` into `MorseSymbol` values. It only identifies the structure of the input.

That conversion happens later in `SpacedParser`.

### Boundary Precedence

When the word boundary contains the character boundary, the tokenizer checks for the word boundary first.

With the default syntax:

```text
character boundary = " "
word boundary      = "   "
```

the input:

```text
... ---   ...
```

correctly produces a `WORD_BOUNDARY` token for the three spaces rather than three separate character boundaries.

The same behavior applies to custom boundaries:

```python
boundaries = MorseBoundarySyntax(
	character_boundary="|",
	word_boundary="||",
)

tokenizer = MorseTokenizer(boundaries)

tokens = tokenizer.tokenize("...||---")

tokens[1].type is TokenType.WORD_BOUNDARY
# True
```

### Custom Boundaries Need Not Be Whitespace

Boundaries can use arbitrary non-empty strings.

```python
boundaries = MorseBoundarySyntax(
	character_boundary=" ",
	word_boundary="/",
)

tokenizer = MorseTokenizer(boundaries)

tokens = tokenizer.tokenize("... ---/...")

# The "/" is recognized as a word boundary.
```

The boundary itself does not have to look like conventional Morse notation.

### Empty Input

Tokenizing an empty string produces no tokens.

```python
MorseTokenizer().tokenize("")
# ()
```

## SpacedParser

`SpacedParser` converts boundary-delimited strings into `MorseStream`.

```python
from morse.parsing import SpacedParser
from morse.representations import TextRepresentation

parser = SpacedParser(
	TextRepresentation(),
)

stream = parser.parse("... --- ...")
```

The parser performs two stages:

1. Tokenize the input using `MorseTokenizer`.
2. Decode each value token using the configured `MorseRepresentation`.

Boundary tokens become corresponding `MorseToken` values.

For example:

```text
"... --- ..."
      │
      ▼
MorseTokenizer
      │
      ▼
VALUE → CHARACTER_BOUNDARY → VALUE → CHARACTER_BOUNDARY → VALUE
      │
      ▼
SpacedParser
      │
      ▼
MorseStream
```

### Parsed Symbols

A value token is decoded into one or more `MorseSymbol` values.

```python
parser = SpacedParser(TextRepresentation())

stream = parser.parse("...")

[token.symbol for token in stream]
# [
#     MorseSymbol.DOT,
#     MorseSymbol.DOT,
#     MorseSymbol.DOT,
# ]
```

Character and word boundaries are preserved as structural tokens.

```python
stream = parser.parse("... ---   ...")

[token.type for token in stream]
# [
#     SYMBOL,
#     SYMBOL,
#     SYMBOL,
#     CHARACTER_BOUNDARY,
#     SYMBOL,
#     SYMBOL,
#     SYMBOL,
#     WORD_BOUNDARY,
#     SYMBOL,
#     SYMBOL,
#     SYMBOL,
# ]
```

This means parsing does not lose the original message structure.

### Input Without Boundaries

`SpacedParser` can also parse a single value without any boundary characters.

```python
parser.parse("...")
```

The result simply contains the decoded symbols.

It does **not** infer character boundaries.

For example:

```python
parser.parse("...---...")
```

produces one continuous sequence of symbols rather than attempting to determine whether the input represents `SOS`, `...`, or some other segmentation.

Use `UnspacedParser` when the input is intentionally continuous.

## UnspacedParser

`UnspacedParser` handles Morse strings with no character or word boundaries.

```python
from morse.parsing import UnspacedParser
from morse.representations import TextRepresentation

parser = UnspacedParser(
	TextRepresentation(),
)

sequence = parser.parse("...---...")
```

It directly passes the entire string through the configured representation's `decode_sequence()` method and stores the resulting symbols in a `MorseSequence`.

```python
sequence.symbols
# (
#     MorseSymbol.DOT,
#     MorseSymbol.DOT,
#     MorseSymbol.DOT,
#     MorseSymbol.DASH,
#     MorseSymbol.DASH,
#     MorseSymbol.DASH,
#     MorseSymbol.DOT,
#     MorseSymbol.DOT,
#     MorseSymbol.DOT,
# )
```

No character or word boundaries are created.

### Why Unspaced Morse Needs a Separate Parser

A sequence such as:

```text
...---...
```

contains only signal information.

There is no indication of where one character ends and another begins.

The parser therefore cannot directly decode it into text.

Instead, it produces a `MorseSequence`, which can then be passed to the solving system to infer possible character boundaries.

```text
"...---..."
     │
     ▼
UnspacedParser
     │
     ▼
MorseSequence
     │
     ▼
Solver
     │
     ▼
Possible text
```

See [Solving](solving.md) for more information.

## Representations and Parsing

Parsers do not assume that Morse is written specifically with `"."` and `"-"`.

They operate through `MorseRepresentation`.

This allows custom symbol representations to work with the same parsers.

For example:

```python
from morse.core import MorseSymbol
from morse.parsing import SpacedParser
from morse.representations import ArbitraryRepresentation

representation = ArbitraryRepresentation(
	{
		MorseSymbol.DOT: "dot",
		MorseSymbol.DASH: "dash",
	}
)

parser = SpacedParser(representation)

stream = parser.parse("dotdotdash")
```

The parser produces the equivalent symbol sequence:

```python
[token.symbol for token in stream]
# [
#     MorseSymbol.DOT,
#     MorseSymbol.DOT,
#     MorseSymbol.DASH,
# ]
```

The same applies to unspaced parsing:

```python
from morse.parsing import UnspacedParser

representation = ArbitraryRepresentation(
	{
		MorseSymbol.DOT: "e",
		MorseSymbol.DASH: "r",
	}
)

parser = UnspacedParser(representation)

sequence = parser.parse("eeerrr")
```

The parser does not need to know what `"e"` or `"r"` mean. That responsibility belongs to the representation.

See [Representations](representations.md) for details.

## Parser Composition

The parsing system is intentionally split into small components.

For spaced input:

```text
Input string
    │
    ▼
MorseTokenizer
    │
    ▼
RawToken objects
    │
    ▼
MorseRepresentation
    │
    ▼
MorseToken objects
    │
    ▼
MorseStream
```

For unspaced input:

```text
Input string
    │
    ▼
MorseRepresentation
    │
    ▼
MorseSequence
```

This separation keeps boundary handling, string representation, and Morse structure independent from each other.

## Choosing a Parser

Use `SpacedParser` when the input already contains character or word boundaries.

```python
parser = SpacedParser(TextRepresentation())

stream = parser.parse(".... . .-.. .-.. ---   .-- --- .-. .-.. -..")
```

Use `UnspacedParser` when the input is continuous.

```python
parser = UnspacedParser(TextRepresentation())

sequence = parser.parse("......-...-..---")
```

The difference is important:

Input                  | Parser           | Result          |
:--------------------- | :--------------- | :-------------- |
`.... . .-.. .-.. ---` | `SpacedParser`   | `MorseStream`   |
`......-...-..---`     | `UnspacedParser` | `MorseSequence` |

## High-Level API

Most users do not need to instantiate parsers directly.

The `Morse` class exposes both parsing operations:

```python
from morse import Morse

morse = Morse()

stream = morse.parse("... --- ...")

sequence = morse.parse_unspaced("...---...")
```

Use the high-level methods when you want the standard toolkit configuration.

Direct parser construction is useful when you need lower-level control over representations, boundaries, or parser components.

## Summary

MorseToolkit's parsing system provides:

- `MorseParser` as the common parser interface.
- `MorseBoundarySyntax` for configurable character and word boundaries.
- `MorseTokenizer` for splitting spaced input into raw tokens.
- `SpacedParser` for producing structured `MorseStream` objects.
- `UnspacedParser` for producing continuous `MorseSequence` objects.
- Integration with any `MorseRepresentation`.
- Support for custom boundary syntax.
- Preservation of character and word boundaries during spaced parsing.

The central distinction is:

```text
Spaced Morse
	Boundaries are known
		→ MorseStream

Unspaced Morse
	Boundaries are unknown
		→ MorseSequence
		→ Solver can infer possible text
```
