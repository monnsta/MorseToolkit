# Morse Representations

MorseToolkit separates the **Morse symbols themselves** from how those symbols are represented as text.

This allows the same Morse data to be serialized using standard dots and dashes, or using a completely custom representation.

## The Two Morse Symbols

MorseToolkit represents Morse using two symbols:

- `MorseSymbol.DOT`
- `MorseSymbol.DASH`

The standard text representation maps these to:

Morse symbol       | Text |
:----------------- | :--- |
`MorseSymbol.DOT`  | `.`  |
`MorseSymbol.DASH` | `-`  |

The representation layer controls this mapping.

This means that an alphabet does not need to know whether a dot is written as `.`, `s`, `0`, `dit`, or anything else.

## `MorseRepresentation`

Custom representations implement the `MorseRepresentation` interface.

```python
from morse.representations import MorseRepresentation
```

A representation is responsible for converting between `MorseSymbol` objects and their string form.

It provides four operations:

Method                   | Purpose                                                    |
:----------------------- | :--------------------------------------------------------- |
`encode(symbol)`         | Converts one `MorseSymbol` to its string representation    |
`decode(value)`          | Converts one representation back to a `MorseSymbol`        |
`decode_sequence(value)` | Converts a continuous representation into multiple symbols |
`can_decode(value)`      | Checks whether a value represents a valid symbol           |

### Implementing a Representation

A custom representation must implement all four methods:

```python
from morse.core import MorseSymbol
from morse.representations import MorseRepresentation


class MyRepresentation(MorseRepresentation):
	def encode(self, symbol: MorseSymbol) -> str:
		...

	def decode(self, value: str) -> MorseSymbol:
		...

	def decode_sequence(
		self,
		value: str,
	) -> tuple[MorseSymbol, ...]:
		...

	def can_decode(self, value: str) -> bool:
		...
```

The representation is concerned only with symbol serialization. It does not determine which characters exist in an alphabet or how Morse boundaries work.

## `TextRepresentation`

`TextRepresentation` is the default representation.

```python
from morse.representations import TextRepresentation

representation = TextRepresentation()
```

It maps:

```text
MorseSymbol.DOT  -> "."
MorseSymbol.DASH -> "-"
```

For example:

```python
from morse.core import MorseSymbol
from morse.representations import TextRepresentation

representation = TextRepresentation()

print(representation.encode(MorseSymbol.DOT))
print(representation.encode(MorseSymbol.DASH))
```

Output:

```text
.
-
```

It can also convert the strings back into Morse symbols:

```python
print(representation.decode("."))
print(representation.decode("-"))
```

### Decoding a Sequence

`decode_sequence()` accepts a continuous sequence of standard Morse characters:

```python
symbols = representation.decode_sequence("...-")

print(symbols)
```

The result is a tuple of `MorseSymbol` objects:

```text
(
	MorseSymbol.DOT,
	MorseSymbol.DOT,
	MorseSymbol.DOT,
	MorseSymbol.DASH,
)
```

Invalid characters raise `ValueError`:

```python
representation.decode_sequence("..x.")
```

### Checking Values

`can_decode()` can be used when you want to validate an individual symbol representation without catching an exception:

```python
representation.can_decode(".")   # True
representation.can_decode("-")   # True
representation.can_decode("x")   # False
```

## `ArbitraryRepresentation`

`ArbitraryRepresentation` allows dots and dashes to be represented using arbitrary strings.

```python
from morse.core import MorseSymbol
from morse.representations import ArbitraryRepresentation

representation = ArbitraryRepresentation({
	MorseSymbol.DOT: "s",
	MorseSymbol.DASH: "d",
})
```

Now:

```text
DOT  -> "s"
DASH -> "d"
```

The representation can be used normally:

```python
print(representation.encode(MorseSymbol.DOT))
print(representation.encode(MorseSymbol.DASH))

print(representation.decode("s"))
print(representation.decode("d"))
```

Output:

```text
s
d
MorseSymbol.DOT
MorseSymbol.DASH
```

### Using a Custom Representation with `Morse`

Pass the representation to `Morse`:

```python
from morse import Morse
from morse.core import MorseSymbol
from morse.representations import ArbitraryRepresentation

representation = ArbitraryRepresentation({
	MorseSymbol.DOT: "s",
	MorseSymbol.DASH: "d",
})

morse = Morse(
	representation=representation,
)

encoded = morse.encode("HELLO")

print(encoded)
```

The resulting Morse uses `s` and `d` instead of `.` and `-`.

Because the same representation is used by the parser, the encoded result can be decoded again:

```python
decoded = morse.decode(encoded)

print(decoded)
# HELLO
```

This keeps encoding and decoding consistent.

## Multi-Character Representations

A symbol representation does not have to be a single character.

For example:

```python
representation = ArbitraryRepresentation({
	MorseSymbol.DOT: "dit",
	MorseSymbol.DASH: "dah",
})
```

A Morse sequence such as:

```text
ditdahdit
```

can then represent:

```text
.-.
```

Use `decode_sequence()` to decode the continuous representation:

```python
symbols = representation.decode_sequence("ditdahdit")
```

The representation parser determines where each configured symbol representation begins and ends.

## Representation Validation

`ArbitraryRepresentation` validates its mapping when it is created.

Both Morse symbols must be defined.

This is invalid:

```python
ArbitraryRepresentation({
	MorseSymbol.DOT: "s",
})
```

It raises:

```text
ValueError: Representation must define DASH
```

Representations also cannot be empty:

```python
ArbitraryRepresentation({
	MorseSymbol.DOT: "",
	MorseSymbol.DASH: "d",
})
```

The two representations must be different:

```python
ArbitraryRepresentation({
	MorseSymbol.DOT: "s",
	MorseSymbol.DASH: "s",
})
```

And neither representation may be a prefix of the other.

For example, this is invalid:

```python
ArbitraryRepresentation({
	MorseSymbol.DOT: "s",
	MorseSymbol.DASH: "sd",
})
```

Because `"s"` is a prefix of `"sd"`.

This restriction is necessary so a continuous string can be decoded unambiguously.

A valid mapping might instead be:

```python
ArbitraryRepresentation({
	MorseSymbol.DOT: "s",
	MorseSymbol.DASH: "d",
})
```

Or:

```python
ArbitraryRepresentation({
	MorseSymbol.DOT: "dit",
	MorseSymbol.DASH: "dah",
})
```

## Representations vs. Alphabets

Representations and alphabets solve different problems.

An **alphabet** determines which text characters correspond to which Morse symbol sequences.

A **representation** determines how those Morse symbols are written as strings.

For example, the letter `A` is:

```text
.-
```

The International Morse alphabet defines that mapping.

A representation can then decide how `. -` is serialized.

With the standard representation:

```text
.-
```

With a custom representation:

```text
sd
```

The underlying Morse symbols are still the same:

```text
DOT, DASH
```

Only their textual representation has changed.

This separation allows the same alphabet to work with many different representations.

## When to Use a Custom Representation

Custom representations are useful when working with:

- Alternative Morse notation
- Encoded or obfuscated Morse
- Morse puzzles using arbitrary symbols
- Applications that use words instead of punctuation
- Custom transmission formats
- Protocols where `.` and `-` are inconvenient or unavailable

For example, a protocol could represent Morse using `0` and `1`:

```python
binary_morse = ArbitraryRepresentation({
	MorseSymbol.DOT: "0",
	MorseSymbol.DASH: "1",
})
```

Or using arbitrary textual markers:

```python
word_morse = ArbitraryRepresentation({
	MorseSymbol.DOT: "short",
	MorseSymbol.DASH: "long",
})
```

The rest of MorseToolkit can work with these representations without changing the alphabet itself.

## Summary

MorseToolkit's representation layer provides a clean separation between Morse symbols and their textual encoding.

- `MorseRepresentation` defines the interface.
- `TextRepresentation` provides standard `.` and `-` notation.
- `ArbitraryRepresentation` allows custom symbol representations.
- Representations can use strings longer than one character.
- Custom representations must be unambiguous.
- Alphabets define character-to-Morse mappings; representations define Morse-to-string mappings.
- A `Morse` instance can use a custom representation for both encoding and decoding.
