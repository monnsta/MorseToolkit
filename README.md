# MorseToolkit

A flexible Morse code toolkit for Python. This library provides robust abstractions and utilities for encoding, decoding, streaming, parsing, and solving Morse code sequences.

---

## Features

- **Core Primitives**: Immutable sequences, streams, symbols, and token abstractions.
- **Alphabets**: Built-in support for standard International Morse Code, with an extensible base class for custom symbol mappings.
- **Representations**: Define custom string representations for dot and dash symbols (e.g., standard `.` and `-`, or any arbitrary strings).
- **Parsing**: Parse unspaced sequences or fully tokenized, spaced Morse text into structured token streams.
- **Solving**: Powerful segmentation and dictionary-based solving capabilities to decrypt continuous/unspaced Morse sequences.

---

## Installation

```bash
pip install git+https://github.com/monnsta/MorseToolkit.git
```

---

## Basic Usage

```python
from morse.alphabets import InternationalMorse
from morse.encoding import MorseEncoder, MorseDecoder

alphabet = InternationalMorse()
encoder = MorseEncoder(alphabet)
decoder = MorseDecoder(alphabet)

# Encode text to a Morse stream
stream = encoder.encode("HELLO WORLD")

# Decode a stream back to text
text = decoder.decode(stream)
print(text)  # HELLO WORLD
```

---

## License

MIT License
