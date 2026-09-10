# User Guide

MorseToolkit offers a fully-featured Python API alongside a powerful Command Line Interface (CLI) for parsing, encoding, decoding, and solving Morse code. This guide covers how to utilize both to deeply integrate Morse code manipulation into your workflows.

## Command Line Interface (CLI)

The `morse` command-line utility provides direct access to MorseToolkit's primary capabilities. You can process inputs directly from arguments or pipe content via standard input (`stdin`).

### Core Commands

Command    | Description                                                            | Example Usage                                                     |
:--------- | :--------------------------------------------------------------------- | :---------------------------------------------------------------- |
`encode`   | Converts text to Morse. Use `--unspaced` to omit character boundaries. | `morse encode "hello world"`<br>`morse encode "hello" --unspaced` |
`decode`   | Decodes space-delimited Morse back to plain text.                      | `morse decode ".... . .-.. .-.. ---"`                             |
`solve`    | Infers words from unspaced Morse using a wordlist.                     | `morse solve "......-...-..---" -d dict.txt`                      |
`validate` | Checks if a given sequence is valid Morse. Supports `--unspaced`.      | `morse validate ".... ."`                                         |
`parse`    | Breaks down a Morse string into structured internal tokens.            | `morse parse "... --- ..."`                                       |

### Decoding & Encoding via STDIN

All core commands gracefully handle piped data, making it easy to chain operations in bash:

```bash
# Encode from file
cat message.txt | morse encode

# Validate pipeline output
echo "......-...-..---" | morse validate --unspaced

# Decode piped text
echo ".... . .-.. .-.. ---" | morse decode
```

### Solving Unspaced Morse

Solving requires a dictionary file to establish valid vocabulary. You can limit the number of output matches using the `-n` flag (the default limit depends on interactive context but can be adjusted).

```bash
# Returns the top candidate(s) for the unspaced Morse sequence
morse solve "......-...-..---" -d /path/to/words.txt -n 1
```

### Interactive REPL

Running `morse` without specific subcommand arguments or inputs launches the Interactive REPL. The REPL maintains state and configuration while providing autocompletion and rich console output.

Within the interactive terminal, you can run commands and update internal settings:

```text
morse> encode hello
.... . .-.. .-.. ---
morse> decode .... . .-.. .-.. ---
HELLO

morse> set scorer english
Scorer set to: english
morse> set results 10
Default result count set to: 10
morse> set dictionary /path/to/words.txt
Dictionary set to:
/path/to/words.txt

morse> show
              MorseToolkit
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Setting            ┃ Value              ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ Alphabet           │ InternationalMorse │
│ Representation     │ TextRepresentation │
│ Character boundary │ ' '                │
│ Word boundary      │ '   '              │
│ Dictionary         │ /path/to/words.txt │
│ Scorer             │ english            │
│ Results            │ 10                 │
│ Max word length    │ 32                 │
│ Beam width         │ 8                  │
│ History            │ enabled            │
└────────────────────┴────────────────────┘

morse> solve ......-...-..---
1. hello
2. is as do
3. hits do
4. hide do
5. he as do
6. her i do
7. is as team
8. her in am
9. hits team
10. hell o

morse> quit
Goodbye.
```

---

## Python API

The module-level functions (`morse.encode`, `morse.decode`, `morse.solve`) are sufficient for basic workflows using standard International Morse code and standard `. -` boundaries. For customized behavior, you should use the `Morse` class.

### The `Morse` Instance

The `Morse` class acts as the central coordinator, tying together alphabets, representations, boundary definitions, and solvers.

```python
from morse import Morse
from morse.representations import ArbitraryRepresentation
from morse.core import MorseSymbol

# Customize dot and dash representation
rep = ArbitraryRepresentation({
    MorseSymbol.DOT: "dit",
    MorseSymbol.DASH: "dah"
})

toolkit = Morse(representation=rep)

encoded = toolkit.encode("SOS")
print(encoded) # ditditdit dahdahdah ditditdit
```

### Compiling Dictionaries for Solving

When solving continuous (unspaced) Morse, performance hinges on fast vocabulary lookups. `MorseToolkit` builds a trie-like internal `MorseWordIndex` over dictionaries to prune dead search branches instantly.

For repeated solving tasks, compile the dictionary once using `toolkit.dictionary()` rather than passing raw lists multiple times:

```python
from morse import Morse

toolkit = Morse()
dictionary = toolkit.dictionary(["hello", "world", "sos", "help"])

# The compiled dictionary can be passed safely to the solver
result = toolkit.solve(toolkit.encode_unspaced("help"), dictionary)
print(result.text) # help
```

### Using Advanced Scorers

A continuous Morse sequence often translates to multiple valid segmentations. Solvers rely on *Scorers* to rank these candidates.

- `DictionaryScorer`: Ranks segmentations purely on whether the resolved words exist in the dictionary (returns a uniform score).
- `FrequencyScorer`: Assigns weights based on real-world word frequencies, elevating common words above obscure ones.
- `BigramScorer`: Evaluates transition probabilities between adjacent words for heavily context-dependent solving.

```python
from morse.solving.scorer import FrequencyScorer
from morse.solving.dictionary import MorseDictionary
from morse import Morse

toolkit = Morse()
word_list = ["cat", "the", "bat"]
dictionary = MorseDictionary(word_list)

# Weigh specific words heavier than others
scorer = FrequencyScorer({
    "the": 10.0,
    "cat": 5.0,
    "bat": 1.0,
})

# Under the hood, solvers use the provided Scorer to navigate ambiguous paths
# This API sits lower in the architecture but integrates directly via the `MorseSolver`
```

For a deeper dive into extending the solving behaviors, review [`docs/solving.md`](docs/solving.md) and [`docs/custom-scorers.md`](docs/custom-scorers.md).
