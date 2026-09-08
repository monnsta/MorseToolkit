# Alphabets

MorseToolkit separates **Morse alphabets** from **Morse representations**.

An alphabet defines which text characters correspond to which Morse symbols. A representation defines how those symbols are written as strings.

This separation allows the same alphabet to be used with different textual representations.

## Morse Symbols

The fundamental Morse symbols are represented by `MorseSymbol`:

```python
from morse.core import MorseSymbol

print(MorseSymbol.DOT)
print(MorseSymbol.DASH)
```

The two available symbols are:

Symbol             | Value | Meaning              |
:----------------- | :---- | :------------------- |
`MorseSymbol.DOT`  | `"."` | Short signal (`dit`) |
`MorseSymbol.DASH` | `"-"` | Long signal (`dah`)  |

These are the only primitive symbols used by MorseToolkit's alphabet system.

## MorseAlphabet

`MorseAlphabet` is the abstract interface that all Morse alphabets implement.

```python
from morse.core import MorseAlphabet
```

An alphabet provides four operations:

```python
class MorseAlphabet(ABC):
	def encode(self, character: str) -> tuple[MorseSymbol, ...]:
		...

	def decode(self, symbols: Sequence[MorseSymbol]) -> str:
		...

	def can_encode(self, character: str) -> bool:
		...

	def can_decode(self, symbols: Sequence[MorseSymbol]) -> bool:
		...
```

### Encoding

`encode()` converts one text character into Morse symbols.

```python
from morse.alphabets import InternationalMorse

alphabet = InternationalMorse()

symbols = alphabet.encode("A")

print(symbols)
# (
#     MorseSymbol.DOT,
#     MorseSymbol.DASH,
# )
```

The result is a tuple of `MorseSymbol` objects.

An alphabet operates on **individual characters**, not complete strings. Higher-level components such as `Morse` handle complete messages.

### Decoding

`decode()` performs the reverse operation.

```python
from morse.core import MorseSymbol
from morse.alphabets import InternationalMorse

alphabet = InternationalMorse()

character = alphabet.decode((
	MorseSymbol.DOT,
	MorseSymbol.DASH,
))

print(character)
# "A"
```

The supplied symbols must represent exactly one character in the alphabet.

### Checking support

`can_encode()` checks whether a character is supported.

```python
alphabet.can_encode("A")
# True

alphabet.can_encode("5")
# True

alphabet.can_encode("^")
# False
```

`can_decode()` performs the equivalent check for a Morse symbol sequence.

```python
symbols = (
	MorseSymbol.DOT,
	MorseSymbol.DASH,
)

alphabet.can_decode(symbols)
# True
```

These methods are useful when you want to validate input without handling an exception.

## International Morse

`InternationalMorse` is the standard alphabet included with MorseToolkit.

```python
from morse.alphabets import InternationalMorse

alphabet = InternationalMorse()
```

It supports:

- `A`–`Z`
- `0`–`9`
- Standard punctuation

### Letters

All English letters are supported.

```python
alphabet.encode("A")
# (MorseSymbol.DOT, MorseSymbol.DASH)

alphabet.encode("Z")
# (MorseSymbol.DASH, MorseSymbol.DASH,
#  MorseSymbol.DOT, MorseSymbol.DOT)
```

Encoding is case-insensitive.

```python
alphabet.encode("a") == alphabet.encode("A")
# True
```

Decoding letters produces uppercase characters.

```python
alphabet.decode(alphabet.encode("a"))
# "A"
```

### Numbers

The digits `0` through `9` are supported.

```python
alphabet.encode("5")
# (
#     MorseSymbol.DOT,
#     MorseSymbol.DOT,
#     MorseSymbol.DOT,
#     MorseSymbol.DOT,
#     MorseSymbol.DOT,
# )
```

### Punctuation

International Morse currently supports these punctuation characters:

```text
. , ? ' ! / ( ) & : ; = + - _ " $ @
```

For example:

```python
alphabet.encode("?")
# (
#     MorseSymbol.DOT,
#     MorseSymbol.DOT,
#     MorseSymbol.DASH,
#     MorseSymbol.DASH,
#     MorseSymbol.DOT,
#     MorseSymbol.DOT,
# )
```

Punctuation is decoded back to the corresponding punctuation character.

## Errors

Alphabet operations raise `ValueError` when the requested conversion is not supported.

For example:

```python
alphabet.encode("^")
# ValueError: Unsupported character: '^'
```

Likewise, decoding an unknown Morse sequence raises `ValueError`:

```python
alphabet.decode((
	MorseSymbol.DOT,
	MorseSymbol.DOT,
	MorseSymbol.DOT,
	MorseSymbol.DOT,
	MorseSymbol.DOT,
	MorseSymbol.DOT,
	MorseSymbol.DOT,
))
# ValueError: Unsupported Morse sequence: '.......'
```

Use `can_encode()` and `can_decode()` when you want to check support without raising an exception.

## Using an Alphabet with `Morse`

Most users will not need to interact with `MorseAlphabet` directly.

The high-level `Morse` class uses `InternationalMorse` by default:

```python
from morse import Morse

morse = Morse()

morse.encode("HELLO")
# ".... . .-.. .-.. ---"
```

A different alphabet can be supplied when constructing a `Morse` instance:

```python
from morse import Morse
from morse.alphabets import InternationalMorse

alphabet = InternationalMorse()

morse = Morse(alphabet=alphabet)
```

The alphabet is then used by the encoder and decoder behind the high-level API.

This is one of the main extension points of MorseToolkit.

## Alphabet vs Representation

An alphabet and a representation solve different problems.

**Alphabet:**

> Which Morse symbols represent a character?

For example:

```text
A → DOT DASH
```

**Representation:**

> How should those symbols be written as a string?

For example, the default representation writes:

```text
DOT  → .
DASH → -
```

This means you can change the textual representation without changing the alphabet itself.

See [Representations](representations.md) for more information.

## Creating a Custom Alphabet

Custom alphabets can be created by subclassing `MorseAlphabet`.

```python
from collections.abc import Sequence

from morse.core import MorseAlphabet, MorseSymbol


class MyAlphabet(MorseAlphabet):
	def encode(self, character: str) -> tuple[MorseSymbol, ...]:
		...

	def decode(self, symbols: Sequence[MorseSymbol]) -> str:
		...

	def can_encode(self, character: str) -> bool:
		...

	def can_decode(self, symbols: Sequence[MorseSymbol]) -> bool:
		...
```

The four methods form the complete alphabet contract.

A custom alphabet can define its own character set and Morse mappings while remaining compatible with the rest of MorseToolkit.

For a complete implementation guide, see [Custom Alphabets](custom-alphabets.md).

## Summary

MorseToolkit's alphabet system provides:

- `MorseSymbol` for the fundamental dot and dash signals.
- `MorseAlphabet` as the abstract alphabet interface.
- `InternationalMorse` as the built-in International Morse Code implementation.
- Case-insensitive encoding for letters.
- Uppercase decoding for letters.
- Support for letters, digits, and standard punctuation.
- `can_encode()` and `can_decode()` for validation.
- `ValueError` for unsupported conversions.
- Custom alphabet support through subclassing.

The important design distinction is:

```text
Alphabet
	Character ↔ Morse symbols

Representation
	Morse symbols ↔ String

Morse
	High-level API combining both
```
