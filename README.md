# MorseToolkit

A flexible Python toolkit for encoding, decoding, parsing, and solving Morse code.

MorseToolkit provides a simple high-level API for everyday use, while exposing lower-level components for applications that need more control.

## Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/monnsta/MorseToolkit.git
```

## Quick Start

The simplest way to use MorseToolkit is through the module-level functions.

### Encode text

```python
import morse

encoded = morse.encode("HELLO WORLD")

print(encoded)
# .... . .-.. .-.. ---   .-- --- .-. .-.. -..
```

MorseToolkit uses standard International Morse Code by default.

### Decode Morse

If the Morse already contains character boundaries, use `decode()`:

```python
import morse

text = morse.decode(".... . .-.. .-.. ---")

print(text)
# HELLO
```

Character boundaries are represented by spaces, while word boundaries use three spaces by default.

For example:

```text
.... . .-.. .-.. ---   .-- --- .-. .-.. -..
```

decodes to:

```text
HELLO WORLD
```

## Continuous Morse

Sometimes Morse is transmitted without character boundaries:

```text
......-...-..---
```

There is no way to directly know where one character ends and another begins.

For this, MorseToolkit provides `encode_unspaced()` and `solve()`.

### Create unspaced Morse

```python
import morse

encoded = morse.encode_unspaced("HELLO")

print(encoded)
# ......-...-..---
```

### Solve unspaced Morse

A dictionary (preferably an english word list) can be supplied to determine how the continuous sequence should be segmented:

```python
import morse

result = morse.solve(
   "......-...-..---.-----.-..-..-..",
   ["hello", "world"],
)

print(result.text)
# hello world
```

For multiple words:

```python
import morse

result = morse.solve(
   morse.encode_unspaced("egg and toast"), # .--.--..--.-..----.-...-
   ["egg", "and", "toast"],
)

print(result.text)
# egg and toast
```

`solve()` returns a `MorseCandidate`, or `None` when the sequence cannot be solved using the supplied dictionary.

## Using the `Morse` Class

For repeated use or customization, create a `Morse` instance instead of using the module-level functions.

```python
from morse import Morse

morse_toolkit = Morse()

encoded = morse_toolkit.encode("HELLO WORLD")
decoded = morse_toolkit.decode(encoded)

print(encoded)
print(decoded)
```

The instance keeps its configuration together, making it useful when working with custom alphabets or representations.

For example, a dictionary can be configured once and reused:

```python
from morse import Morse

morse_toolkit = Morse()

dictionary = morse_toolkit.dictionary([
    "hello",
    "world",
    "egg",
    "and",
    "toast",
])

result = morse_toolkit.solve(
   morse_toolkit.encode_unspaced("egg and toast"),
    dictionary
)

print(result.text)
# egg and toast
```

## Parsing Morse

If you need more control than `decode()` provides, MorseToolkit can expose the parsed Morse structure directly.

```python
from morse import Morse

morse_toolkit = Morse()

stream = morse_toolkit.parse(".... . .-.. .-.. ---")

for token in stream:
   print(token)
```

Continuous Morse can similarly be parsed into a `MorseSequence`:

```python
sequence = morse_toolkit.parse_unspaced("......-...-..---")
```

These lower-level interfaces are useful when building applications on top of MorseToolkit.

## Custom Representations

MorseToolkit does not require dots and dashes to literally be represented by `.` and `-`.

For example, you can use arbitrary symbols:

```python
from morse import Morse
from morse.core import MorseSymbol
from morse.representations import ArbitraryRepresentation

representation = ArbitraryRepresentation({
   MorseSymbol.DOT: "s",
   MorseSymbol.DASH: "d",
})

morse_toolkit = Morse(
   representation=representation,
)

encoded = morse_toolkit.encode("HELLO")

print(encoded)
```

The same representation is used when decoding:

```python
decoded = morse_toolkit.decode(encoded)

print(decoded)
# HELLO
```

More advanced representation options are covered in the documentation.

## Advanced Usage

MorseToolkit is designed to be usable at several levels.

Most users only need:

```python
import morse

morse.encode("HELLO")
morse.decode(".... . .-.. .-.. ---")
morse.solve("......-...-..---.-----.-..-..-..", ["hello", "world"])
```

Applications that need more control can use the `Morse` class and configure:

- Custom Morse representations
- Custom alphabets
- Boundary syntax
- Dictionaries
- Frequency-based scoring
- Contextual bigram scoring
- Low-level parsers
- Morse streams and sequences

See the `docs/` directory for the complete guide.

## Documentation

The documentation is split into two levels:

- **README** — Quick start and common usage.
- **docs/** — Detailed guides and advanced usage.

Start with:

- [`docs/getting-started.md`](docs/getting-started.md)
- [`docs/user-guide.md`](docs/user-guide.md)
- [`docs/representation.md`](docs/representation.md)
- [`docs/alphabets.md`](docs/alphabets.md)
- [`docs/parsing.md`](docs/parsing.md)
- [`docs/solving.md`](docs/solving.md)
- [`docs/custom-alphabets.md`](docs/custom-alphabets.md)
- [`docs/custom-scorers.md`](docs/custom-scorers.md)
- [`docs/architecture.md`](docs/architecture.md)

## License

MorseToolkit is released under the MIT License.
