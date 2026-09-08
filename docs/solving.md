# Solving

MorseToolkit can solve **unspaced Morse code** where character and word boundaries are unknown.

For example, this input:

```text
......-...-..---.-- ---.-.
```

does not tell the toolkit where one character or word ends and another begins. The solver uses a dictionary and scoring strategy to determine the most likely text.

The solving system is built from four main components:

- `MorseDictionary` — stores and normalizes valid words.
- `MorseWordIndex` — indexes dictionary words by their Morse sequences.
- `MorseScorer` — assigns scores to possible words.
- `MorseSolver` — finds the highest-scoring segmentation.

The high-level `Morse.solve()` API puts these components together for normal use.

---

## Basic solving

The simplest approach is to provide an unspaced Morse sequence and a collection of valid words.

```python
import morse

result = morse.solve(
	"......-...-..---.-- ---.-.",
	["hello", "world"],
)

if result is not None:
	print(result.text)
	print(result.score)
```

For unspaced input, the solver has to determine both:

1. Where characters begin and end.
2. Where words begin and end.

The dictionary determines which complete words are allowed.

---

## The `MorseDictionary`

`MorseDictionary` is the standard dictionary container used by the solver.

```python
from morse.solving import MorseDictionary

dictionary = MorseDictionary([
	"hello",
	"world",
	"python",
])
```

Words are normalized when stored:

- Leading and trailing whitespace is removed.
- Words are converted to lowercase.
- Empty words are ignored.
- Duplicate normalized words are stored only once.

For example:

```python
dictionary = MorseDictionary([
	"Hello",
	"  WORLD  ",
	"hello",
	"   ",
])

assert dictionary.contains("hello")
assert dictionary.contains("HELLO")
assert dictionary.contains("world")
assert len(dictionary) == 2
```

### Checking words

Use `contains()` or the `in` operator:

```python
dictionary.contains("hello")
# True

"hello" in dictionary
# True

"python" in dictionary
# False
```

Both checks are case-insensitive.

### Checking prefixes

The dictionary also stores prefixes of every word.

```python
dictionary = MorseDictionary([
	"hello",
	"help",
])

dictionary.has_prefix("h")
# True

dictionary.has_prefix("hel")
# True

dictionary.has_prefix("hello")
# True

dictionary.has_prefix("hex")
# False
```

Prefix information is useful to algorithms that need to determine whether a partial word can still become a valid dictionary word.

### Iterating over words

Use `words()` to obtain an iterator over the normalized words:

```python
for word in dictionary.words():
	print(word)
```

The dictionary does not guarantee a particular iteration order.

---

## Morse word indexing

`MorseWordIndex` is the internal index used by `MorseSolver`.

It stores dictionary words in a **trie**, where each edge represents a `MorseSymbol`.

This allows the solver to walk through an unspaced Morse sequence and discover dictionary words without repeatedly encoding and comparing every dictionary entry.

You normally do not need to construct the index yourself.

```python
from morse.solving import MorseWordIndex
```

The index accepts an iterator containing:

```python
(word, encoded_symbols)
```

For example:

```python
index = MorseWordIndex(
	[
		("hello", (...)),
		("world", (...)),
	]
)
```

The actual solver constructs this index automatically from the configured dictionary and alphabet.

### Matching words

The index can find every indexed word beginning at a particular position:

```python
matches = index.matches(
	sequence,
	position=0,
	max_word_length=32,
)

for match in matches:
	print(match.word, match.end)
```

Each result is a `MorseWordMatch` containing:

- `word` — the matched dictionary word.
- `end` — the exclusive Morse sequence position immediately after the match.

The index also respects `max_word_length`.

---

## Scoring

A dictionary tells the solver which words are valid, but it does not necessarily tell it which valid solution is preferable.

That is the purpose of `MorseScorer`.

```python
from morse.solving import MorseScorer
```

A scorer defines two things:

- `context_size` — how many previous words it needs.
- `score()` — how desirable a candidate word is.

Higher scores are preferred.

---

## `DictionaryScorer`

`DictionaryScorer` gives every dictionary word a score of `1.0`.

```python
from morse.solving import (
	MorseDictionary,
	DictionaryScorer,
)

dictionary = MorseDictionary([
	"hello",
	"world",
])

scorer = DictionaryScorer(dictionary)

scorer.score("hello")
# 1.0

scorer.score("python")
# 0.0
```

It has no contextual requirements:

```python
scorer.context_size
# 0
```

This is the default scoring strategy when solving through `Morse.solve()` without providing another scorer.

It is useful when every dictionary word should be treated equally.

---

## `FrequencyScorer`

`FrequencyScorer` assigns explicit numerical scores to words.

```python
from morse.solving import FrequencyScorer

scorer = FrequencyScorer({
	"hello": 10.0,
	"world": 5.0,
})
```

Higher values are preferred:

```python
scorer.score("hello")
# 10.0

scorer.score("world")
# 5.0
```

Words missing from the mapping receive `default_score`.

```python
scorer = FrequencyScorer(
	{
		"hello": 10.0,
	},
	default_score=0.5,
)

scorer.score("hello")
# 10.0

scorer.score("python")
# 0.5
```

Frequency values and the default score cannot be negative.

Word normalization is case-insensitive and strips surrounding whitespace.

```python
scorer = FrequencyScorer({
	"hello": 10.0,
})

scorer.score("HELLO")
# 10.0
```

`FrequencyScorer` does not use context:

```python
scorer.context_size
# 0
```

---

## `BigramScorer`

`BigramScorer` scores a word based on the word immediately before it.

This allows the solver to express preferences between adjacent words without requiring a complete language model.

```python
from morse.solving import BigramScorer

scorer = BigramScorer({
	("new", "york"): 10.0,
	("new", "cat"): 1.0,
})
```

The first word has no preceding word, so the scorer uses `default_score` for it.

Once context exists, transitions can be scored:

```python
scorer.score("york", ("new",))
# 10.0

scorer.score("cat", ("new",))
# 1.0
```

Unknown transitions receive the configured default score.

```python
scorer = BigramScorer(
	{
		("new", "york"): 10.0,
	},
	default_score=0.5,
)

scorer.score("cat", ("new",))
# 0.5
```

`BigramScorer` requires one previous word:

```python
scorer.context_size
# 1
```

Like the other built-in scorers, transition words are normalized to lowercase and surrounding whitespace is ignored.

---

## Choosing a scorer

Different scorers are useful for different situations.

Scorer               | Context       | Purpose                                    |
:------------------- | :------------ | :----------------------------------------- |
`DictionaryScorer`   | None          | Treat every dictionary word equally        |
`FrequencyScorer`    | None          | Prefer words with higher frequency scores  |
`BigramScorer`       | Previous word | Prefer particular word-to-word transitions |
Custom `MorseScorer` | Configurable  | Implement your own scoring strategy        |

The scorer should represent **how you want solutions ranked**, not how Morse itself works.

For example, MorseToolkit does not assume that a particular English-language frequency model is universally correct.

---

## The `MorseSolver`

`MorseSolver` is the lower-level solving engine.

```python
from morse.alphabets import InternationalMorse
from morse.solving import (
	MorseDictionary,
	DictionaryScorer,
	MorseSolver,
)

dictionary = MorseDictionary([
	"hello",
	"world",
])

scorer = DictionaryScorer(dictionary)

solver = MorseSolver(
	InternationalMorse(),
	dictionary,
	scorer,
)
```

Then provide a `MorseSequence`:

```python
from morse.parsing import UnspacedParser
from morse.representations import TextRepresentation

parser = UnspacedParser(TextRepresentation())
sequence = parser.parse("......-...-..---.-----.-..-..-..")

result = solver.solve(sequence)
```

The solver returns either a `MorseCandidate` or `None`.

```python
if result is not None:
	print(result.text)
	print(result.score)
```

A candidate contains:

- `text` — the reconstructed words separated by spaces.
- `score` — the total score of the selected solution.

---

## How solving works

The solver does not first guess individual characters and then try to assemble them into words.

Instead, the dictionary is encoded into Morse and stored in a trie.

Given an unspaced sequence, the solver:

1. Starts at the beginning of the Morse sequence.
2. Finds every dictionary word whose Morse representation matches from that position.
3. Advances to the end of each possible word.
4. Scores each candidate.
5. Continues solving from each resulting position.
6. Keeps the highest-scoring valid path.
7. Reconstructs the selected words into a `MorseCandidate`.

Conceptually:

```text
Morse sequence
       │
       ▼
Dictionary word matches
       │
       ├── "hello" ──────┐
       ├── "hell" ───────┤
       ├── "he" ─────────┤
       └── ...           │
                         ▼
                  Candidate paths
                         │
                         ▼
                      Scoring
                         │
                         ▼
                 Best valid solution
```

This is why the solver can handle ambiguity caused by removing Morse character boundaries.

---

## Dynamic programming

For scorers that do not require context, the solver uses dynamic programming.

It keeps the best-scoring state for each Morse position.

For example, if multiple paths reach the same position:

```text
position
   │
   ├── path A → score 4
   ├── path B → score 7
   └── path C → score 3

keep path B
```

A lower-scoring path to the same position cannot produce a better result later when scoring is context-independent.

This keeps the context-free solver considerably smaller than explicitly retaining every possible segmentation.

---

## Context-aware solving

Some scoring strategies depend on previous words.

`BigramScorer` is the built-in example.

In that case, two paths reaching the same Morse position can still have different future potential because they have different preceding words.

For example:

```text
... same Morse position ...

"path A" → previous word: new
"path B" → previous word: cat
```

A future word such as `york` may score highly after `new` but poorly after `cat`.

The solver therefore retains multiple contextual states using a bounded **beam**.

The beam width controls how many competing contextual states survive at each position.

---

## Beam width

The default beam width is `8`.

```python
solver = MorseSolver(
	alphabet,
	dictionary,
	scorer,
	beam_width=8,
)
```

A larger beam can preserve more competing interpretations:

```python
solver = MorseSolver(
	alphabet,
	dictionary,
	scorer,
	beam_width=32,
)
```

A smaller beam reduces the number of retained alternatives:

```python
solver = MorseSolver(
	alphabet,
	dictionary,
	scorer,
	beam_width=4,
)
```

`beam_width` must be at least `1`.

Beam search is only relevant to scorers with context. Context-free scorers use the single-best-state dynamic programming approach.

---

## Maximum word length

The solver defaults to a maximum dictionary word length of `32`.

```python
solver = MorseSolver(
	alphabet,
	dictionary,
	scorer,
	max_word_length=20,
)
```

This limits how long a dictionary word may be considered during trie matching.

The value must be at least `1`.

The limit is based on the **text word's character count**, not its Morse symbol count.

For example, with:

```python
max_word_length=3
```

`"hello"` will not be considered because it contains five characters.

---

## Empty input

An empty Morse sequence is considered a valid empty solution.

```python
result = solver.solve(MorseSequence(()))

assert result.text == ""
assert result.score == 0.0
```

---

## Unsolvable input

If no complete sequence of dictionary words can consume the input, the solver returns `None`.

```python
result = solver.solve(sequence)

if result is None:
	print("No solution found")
```

This is different from an empty input, which produces an empty `MorseCandidate`.

---

## Repeated words

The solver does not prevent words from being used more than once.

For example, a dictionary containing:

```python
[
	"the",
	"cat",
]
```

can solve a sequence corresponding to:

```text
the the cat
```

Dictionary membership determines whether a word is valid; the solver does not consume dictionary entries after using them.

---

## Custom scorers

You can create your own scoring strategy by subclassing `MorseScorer`.

```python
from morse.solving import MorseScorer


class MyScorer(MorseScorer):

	@property
	def context_size(self) -> int:
		return 0

	def score(
		self,
		word: str,
		context: tuple[str, ...] = (),
	) -> float:
		return 1.0
```

`context_size` tells the solver how much previous context the scorer requires.

A value of `0` means the scorer is context-independent.

A value greater than `0` tells the solver to use contextual solving.

See [Custom Scorers](custom-scorers.md) for a complete guide.

---

## Using the high-level API

Most applications should use `Morse.solve()` instead of constructing the lower-level solver manually.

```python
from morse.api import Morse

morse = Morse(
	dictionary=["hello", "world"],
)

result = morse.solve(
	"......-...-..---.-- ---.-.",
)

if result is not None:
	print(result.text)
```

You can also provide a scorer:

```python
from morse.api import Morse

morse = Morse(
	dictionary=["new", "york", "cat"],
	scorer=BigramScorer({
		("new", "york"): 10.0,
		("new", "cat"): 1.0,
	}),
)

result = morse.solve(
	"...",
)
```

The high-level API also allows solver defaults such as `max_word_length` and `beam_width` to be configured when creating the `Morse` instance and overridden for individual calls.

---

## Dictionary versus scorer

The dictionary and scorer have separate responsibilities.

The **dictionary** answers:

> Is this word allowed?

The **scorer** answers:

> How desirable is this word in this solution?

This distinction allows the same dictionary to be paired with different scoring strategies.

For example:

```python
dictionary = MorseDictionary([
	"hello",
	"world",
])

dictionary_scorer = DictionaryScorer(dictionary)

frequency_scorer = FrequencyScorer({
	"hello": 10.0,
	"world": 2.0,
})
```

The first treats both words equally.

The second prefers `"hello"`.

---

## Alphabet interaction

The solver uses the configured `MorseAlphabet` to encode dictionary words into Morse.

This means custom alphabets can also be used by the solving system.

```python
solver = MorseSolver(
	custom_alphabet,
	dictionary,
	scorer,
)
```

Dictionary words that cannot be encoded by the configured alphabet are skipped when the internal word index is built.

The solver therefore only considers words that the active alphabet can represent.

---

## Solving versus parsing

`parse_unspaced()` and `solve()` solve different problems.

### Parsing

Parsing only converts the Morse representation into symbols:

```python
sequence = morse.parse_unspaced("......-...-..---")
```

It does not know where characters or words are.

### Solving

Solving attempts to determine those boundaries using a dictionary and scoring strategy:

```python
result = morse.solve(
	"......-...-..---",
	["hello"],
)
```

Use parsing when you need the raw Morse sequence.

Use solving when you need to reconstruct text from an unspaced sequence.

---

## Choosing the right tool

Situation                                         | Use                |
:------------------------------------------------ | :----------------- |
Morse already has character boundaries            | `decode()`         |
Morse has no boundaries and you only need symbols | `parse_unspaced()` |
Morse has no boundaries and you want text         | `solve()`          |
Every dictionary word should be equally valid     | `DictionaryScorer` |
Prefer specific word frequencies                  | `FrequencyScorer`  |
Prefer particular word pairs                      | `BigramScorer`     |
Need custom ranking behavior                      | `MorseScorer`      |
Need direct low-level control                     | `MorseSolver`      |

---

## Summary

The solving system is designed around a few separate responsibilities:

- `MorseDictionary` manages normalized vocabulary.
- `MorseWordIndex` provides efficient Morse-to-word matching.
- `MorseScorer` determines how candidates are ranked.
- `MorseSegmenter` can enumerate valid character-level segmentations.
- `MorseSolver` combines dictionary matching and scoring to reconstruct unspaced Morse.
- `Morse.solve()` provides the convenient high-level interface.

The default solver is deliberately conservative: it does not assume a language model or silently impose natural-language rules. If contextual behavior is wanted, it can be explicitly introduced through a scorer such as `BigramScorer` or a custom `MorseScorer`.
