# Getting Started

MorseToolkit is a Python toolkit for working with Morse code.

It provides a simple module-level API for common operations, while also allowing you to create configured `Morse` instances when you need more control.

## Requirements

MorseToolkit requires:

- Python 3.11 or newer
- No external Python dependencies

## Installation

MorseToolkit can be installed directly from GitHub:

```bash
pip install git+https://github.com/monnsta/MorseToolkit.git
```

Once installed, import the package as `morse`:

```python
import morse
```

## Your First Encode

The simplest operation is encoding text into standard Morse code.

```python
import morse

encoded = morse.encode("HELLO")

print(encoded)
```

Output:

```text
.... . .-.. .-.. ---
```

By default, MorseToolkit uses standard International Morse Code and the familiar `.` and `-` representation.

### Encoding Words

Spaces in the input text are represented using a word boundary in the resulting Morse:

```python
import morse

print(morse.encode("HELLO WORLD"))
```

Output:

```text
.... . .-.. .-.. ---   .-- --- .-. .-.. -..
```

A single space separates Morse characters, while three spaces separate words by default.

## Decoding Morse

When character boundaries are already known, use `decode()`:

```python
import morse

decoded = morse.decode(".... . .-.. .-.. ---")

print(decoded)
```

Output:

```text
HELLO
```

You can also decode a complete sentence:

```python
import morse

decoded = morse.decode(
	".... . .-.. .-.. ---   .-- --- .-. .-.. -.."
)

print(decoded)
```

Output:

```text
HELLO WORLD
```

`decode()` expects the Morse character and word boundaries to already be present. It does not attempt to guess where characters begin or end.

## Encoding Without Boundaries

Morse code can also be represented without character boundaries.

For example, `HELLO` can be transmitted as:

```text
......-...-..---
```

MorseToolkit provides `encode_unspaced()` for creating this form:

```python
import morse

encoded = morse.encode_unspaced("HELLO")

print(encoded)
```

Output:

```text
......-...-..---
```

Unlike `encode()`, this representation does not contain spaces between characters.

This is useful when working with Morse signals or puzzles where the original character boundaries have been lost.

## Solving Unspaced Morse

Once character boundaries have been removed, decoding becomes an inference problem.

For example:

```text
......-...-..---
```

could potentially be split into different combinations of Morse characters.

`solve()` can search for a valid interpretation using a dictionary:

```python
import morse

result = morse.solve(
	"......-...-..---",
	["hello"],
)

print(result.text)
```

Output:

```text
hello
```

The dictionary tells the solver which words are valid candidates.

### Solving Multiple Words

The solver can also find multiple words when the continuous Morse sequence represents them:

```python
import morse

value = morse.encode_unspaced("egg and toast")

result = morse.solve(
	value,
	["egg", "and", "toast"],
)

print(result.text)
```

Output:

```text
egg and toast
```

If no valid interpretation can be found using the supplied dictionary, `solve()` returns `None`.

## Using `Morse`

The module-level functions are convenient when using the default configuration.

For more control, create a `Morse` instance:

```python
from morse import Morse

morse = Morse()

encoded = morse.encode("HELLO WORLD")
decoded = morse.decode(encoded)

print(encoded)
print(decoded)
```

A `Morse` instance keeps configuration together, allowing you to customize how MorseToolkit behaves.

For example, a dictionary can be attached to an instance:

```python
from morse import Morse

morse = Morse(
	dictionary=[
		"hello",
		"world",
		"egg",
		"and",
		"toast",
	],
)

result = morse.solve(
	morse.encode_unspaced("egg and toast")
)

print(result.text)
```

Once configured, the dictionary does not need to be supplied to every call.

## Parsing Morse

Encoding and decoding are the most common operations, but MorseToolkit can also expose the underlying parsed representation.

Use `parse()` when the Morse contains boundaries:

```python
from morse import Morse

morse = Morse()

stream = morse.parse(".... . .-.. .-.. ---")

for token in stream:
	print(token)
```

For continuous Morse, use `parse_unspaced()`:

```python
sequence = morse.parse_unspaced("......-...-..---")
```

The two parsers serve different purposes:

Method             | Input                    | Result          |
:----------------- | :----------------------- | :-------------- |
`parse()`          | Boundary-delimited Morse | `MorseStream`   |
`parse_unspaced()` | Continuous Morse         | `MorseSequence` |

These lower-level interfaces are useful when an application needs to inspect or manipulate Morse before decoding or solving it.

## Choosing the Right Operation

A useful rule of thumb is:

Goal                     | Use                 |
:----------------------- | :------------------ |
Text → spaced Morse      | `encode()`          |
Text → continuous Morse  | `encode_unspaced()` |
Spaced Morse → text      | `decode()`          |
Continuous Morse → text  | `solve()`           |
Inspect spaced Morse     | `parse()`           |
Inspect continuous Morse | `parse_unspaced()`  |

For most applications, the module-level API is enough:

```python
import morse

morse.encode("HELLO")
morse.decode(".... . .-.. .-.. ---")
morse.encode_unspaced("HELLO")
morse.solve("......-...-..---", ["hello"])
```

When you need customization, use `Morse`.

## Where to Go Next

Once the basics are familiar, the rest of MorseToolkit can be explored through the specialized guides:

- [`representations.md`](representations.md) — Customize how dots and dashes are represented.
- [`alphabets.md`](alphabets.md) — Use or implement different Morse alphabets.
- [`parsing.md`](parsing.md) — Work directly with Morse parsing and boundaries.
- [`solving.md`](solving.md) — Learn how unspaced Morse solving and scoring work.
- [`custom-alphabets.md`](custom-alphabets.md) — Build your own alphabet implementations.
- [`custom-scorers.md`](custom-scorers.md) — Create custom scoring strategies.
- [`architecture.md`](architecture.md) — Understand how MorseToolkit is structured internally.
