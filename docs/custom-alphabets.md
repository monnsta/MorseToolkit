# Custom Alphabets

MorseToolkit is designed so that the Morse alphabet is replaceable.

The built-in `InternationalMorse` alphabet is only one implementation of the `MorseAlphabet` interface. You can create your own alphabet for different character sets, alternative Morse mappings, or completely custom encoding schemes.

## The Alphabet Interface

Custom alphabets are created by subclassing `MorseAlphabet`.

```python
from collections.abc import Sequence

from morse.core import MorseAlphabet, MorseSymbol


class MyAlphabet(MorseAlphabet):
	def encode(
		self,
		character: str,
	) -> tuple[MorseSymbol, ...]:
		...

	def decode(
		self,
		symbols: Sequence[MorseSymbol],
	) -> str:
		...

	def can_encode(
		self,
		character: str,
	) -> bool:
		...

	def can_decode(
		self,
		symbols: Sequence[MorseSymbol],
	) -> bool:
		...
```

Every alphabet must implement four operations:

Method         | Purpose                                       |
:------------- | :-------------------------------------------- |
`encode()`     | Converts a character into Morse symbols       |
`decode()`     | Converts Morse symbols into a character       |
`can_encode()` | Checks whether a character is supported       |
`can_decode()` | Checks whether a symbol sequence is supported |

The alphabet itself works with `MorseSymbol` objects, not strings such as `"."` and `"-"`.

## A Simple Custom Alphabet

Suppose you only want to support the letters `A`, `B`, and `C`.

```python
from collections.abc import Sequence

from morse.core import MorseAlphabet, MorseSymbol


class SimpleAlphabet(MorseAlphabet):
	_CODES = {
		"A": (MorseSymbol.DOT, MorseSymbol.DASH),
		"B": (
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
		),
		"C": (
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
		),
	}

	def encode(
		self,
		character: str,
	) -> tuple[MorseSymbol, ...]:
		try:
			return self._CODES[character.upper()]
		except KeyError as exc:
			raise ValueError(
				f"Unsupported character: {character!r}"
			) from exc

	def decode(
		self,
		symbols: Sequence[MorseSymbol],
	) -> str:
		symbols = tuple(symbols)

		for character, code in self._CODES.items():
			if code == symbols:
				return character

		raise ValueError(
			f"Unsupported Morse sequence: {symbols!r}"
		)

	def can_encode(
		self,
		character: str,
	) -> bool:
		return character.upper() in self._CODES

	def can_decode(
		self,
		symbols: Sequence[MorseSymbol],
	) -> bool:
		return tuple(symbols) in self._CODES.values()
```

The implementation strategy is completely up to the alphabet. MorseToolkit only requires that the four methods follow the `MorseAlphabet` contract.

## Encoding

`encode()` should return a tuple of `MorseSymbol` values.

For example:

```python
alphabet = SimpleAlphabet()

alphabet.encode("A")
# (MorseSymbol.DOT, MorseSymbol.DASH)
```

The alphabet should raise `ValueError` when the character is not supported.

```python
alphabet.encode("Z")
# ValueError: Unsupported character: 'Z'
```

Whether an alphabet accepts lowercase characters is an implementation decision.

For example, the alphabet above explicitly normalizes characters with `.upper()`, making it case-insensitive.

## Decoding

`decode()` receives a sequence of `MorseSymbol` objects representing one character.

```python
alphabet.decode((
	MorseSymbol.DOT,
	MorseSymbol.DASH,
))
# "A"
```

An unknown sequence should raise `ValueError`.

```python
alphabet.decode((
	MorseSymbol.DOT,
	MorseSymbol.DOT,
	MorseSymbol.DOT,
	MorseSymbol.DOT,
	MorseSymbol.DOT,
))
# ValueError
```

The exact error message is up to the implementation, but unsupported conversions should not silently produce an incorrect character.

## Validation Methods

`can_encode()` and `can_decode()` provide non-raising ways to check whether a conversion is supported.

```python
if alphabet.can_encode("A"):
	print(alphabet.encode("A"))
```

And for decoding:

```python
symbols = (
	MorseSymbol.DOT,
	MorseSymbol.DASH,
)

if alphabet.can_decode(symbols):
	print(alphabet.decode(symbols))
```

These methods are particularly useful when processing input that may contain unsupported characters or invalid Morse sequences.

## Using a Custom Alphabet

Custom alphabets can be passed directly to `Morse`.

```python
from morse import Morse

morse = Morse(
	alphabet=SimpleAlphabet(),
)

print(morse.encode("ABC"))
```

The high-level API will use the custom alphabet for encoding and decoding.

The rest of the MorseToolkit pipeline does not need to know how the alphabet implements its mappings.

This is the main benefit of the `MorseAlphabet` abstraction.

## Alphabet Responsibilities

An alphabet is responsible for **character-to-symbol translation**.

It should answer questions such as:

- Is this character supported?
- Which Morse symbols represent this character?
- Which character does this Morse sequence represent?

It is not responsible for:

- separating characters in a message
- separating words
- parsing textual Morse
- deciding how dots and dashes are displayed
- solving unspaced Morse
- scoring candidate solutions

Those responsibilities belong to other components.

For example, the alphabet works with:

```text
"A"
 ↓
(DOT, DASH)
```

while the representation layer handles:

```text
(DOT, DASH)
 ↓
".-"
```

See [Representations](representations.md) for details about Morse representations.

## Choosing a Mapping

A custom alphabet does not have to use the same mappings as International Morse.

For example, an intentionally small or experimental alphabet could define:

```python
_CODES = {
	"A": (MorseSymbol.DOT,),
	"B": (MorseSymbol.DASH,),
}
```

This is technically valid as an alphabet implementation.

However, if multiple characters map to the same Morse sequence, decoding becomes ambiguous:

```python
_CODES = {
	"A": (MorseSymbol.DOT,),
	"B": (MorseSymbol.DOT,),
}
```

In that situation, `decode()` cannot uniquely determine whether `DOT` means `A` or `B`.

For a normally reversible alphabet, each character should have a unique Morse sequence.

## Performance

The alphabet is used by encoding, decoding, and solving, so its lookup strategy can matter for larger workloads.

A simple implementation can search through mappings:

```python
for character, code in self._CODES.items():
	if code == symbols:
		return character
```

A larger alphabet can instead maintain a reverse mapping:

```python
self._reverse_codes = {
	code: character
	for character, code in self._CODES.items()
}
```

Then decoding becomes a direct lookup.

The built-in `InternationalMorse` implementation uses this reverse-mapping approach.

## Reusing Existing Components

A custom alphabet does not require rewriting the rest of MorseToolkit.

Once it implements `MorseAlphabet`, it can be used with the existing:

- `MorseEncoder`
- `MorseDecoder`
- `Morse`
- parsers
- representations
- solver components

This is intentional: components depend on the alphabet interface rather than a specific alphabet implementation.

## Summary

A custom alphabet needs to provide:

```text
encode(character)
decode(symbols)
can_encode(character)
can_decode(symbols)
```

The important rules are:

- Use `MorseSymbol.DOT` and `MorseSymbol.DASH`.
- Return tuples of `MorseSymbol` from `encode()`.
- Decode one symbol sequence into one character.
- Raise `ValueError` for unsupported conversions.
- Make `can_encode()` and `can_decode()` agree with the actual conversion methods.
- Keep message parsing and string representation outside the alphabet.
- Ensure mappings are unambiguous if decoding must be reversible.

Once implemented, the alphabet can be plugged into `Morse` without changing the rest of the toolkit.
