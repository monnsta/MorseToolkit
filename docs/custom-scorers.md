# Custom Scorers

`MorseScorer` lets you control how the solver ranks possible words and phrases.

The built-in scorers cover simple dictionary membership, word frequency, and previous-word transitions. If your application needs a different definition of "best", you can implement your own scorer.

## The `MorseScorer` Interface

Custom scorers inherit from `MorseScorer`:

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

A scorer has two responsibilities:

- Declare how much previous-word context it needs.
- Assign a numerical score to a candidate word.

Higher scores are preferred by the solver.

## `context_size`

`context_size` tells the solver whether the scorer depends on previous words.

For a scorer that evaluates each word independently:

```python
@property
def context_size(self) -> int:
	return 0
```

For a scorer that needs the immediately preceding word:

```python
@property
def context_size(self) -> int:
	return 1
```

For a scorer that needs the previous three words:

```python
@property
def context_size(self) -> int:
	return 3
```

The solver uses this value to determine which solving strategy to use.

### Context-independent scorers

A `context_size` of `0` allows the solver to keep only the best state at each Morse position.

This is the simplest and most efficient case.

### Context-aware scorers

A positive `context_size` tells the solver that two otherwise identical positions may have different future scores depending on their previous words.

The solver therefore retains a bounded set of competing states using its beam width.

## Basic Custom Scorer

Here is a scorer that prefers shorter words:

```python
from morse.solving import MorseScorer


class ShortWordScorer(MorseScorer):
	@property
	def context_size(self) -> int:
		return 0

	def score(
		self,
		word: str,
		context: tuple[str, ...] = (),
	) -> float:
		_ = context

		if not word:
			return 0.0

		return 1.0 / len(word)
```

The solver will prefer shorter dictionary words when multiple segmentations are possible.

For example, if both `E` and `ET` can explain part of a Morse sequence, the scorer can influence which segmentation wins.

## Frequency-Based Scorers

A scorer can assign weights to words using any data source.

For example:

```python
from morse.solving import MorseScorer


class SimpleFrequencyScorer(MorseScorer):
	def __init__(self, frequencies: dict[str, float]) -> None:
		self.frequencies = {
			word.lower(): score
			for word, score in frequencies.items()
		}

	@property
	def context_size(self) -> int:
		return 0

	def score(
		self,
		word: str,
		context: tuple[str, ...] = (),
	) -> float:
		_ = context

		return self.frequencies.get(
			word.lower(),
			0.0,
		)
```

The frequency values do not have to represent literal word frequencies. They can be any non-negative ranking weights appropriate for your application.

## Context-Aware Scorers

Some scorers need to consider surrounding words.

For example, suppose an application wants to prefer certain word pairs:

```python
from morse.solving import MorseScorer


class PairScorer(MorseScorer):
	def __init__(
		self,
		pairs: dict[tuple[str, str], float],
	) -> None:
		self.pairs = {
			(previous.lower(), word.lower()): score
			for (previous, word), score in pairs.items()
		}

	@property
	def context_size(self) -> int:
		return 1

	def score(
		self,
		word: str,
		context: tuple[str, ...] = (),
	) -> float:
		if not context:
			return 0.0

		previous = context[-1].lower()
		word = word.lower()

		return self.pairs.get(
			(previous, word),
			0.0,
		)
```

This allows the solver to distinguish between otherwise equally valid sequences based on the words that came before them.

For example:

```python
scorer = PairScorer({
	("new", "york"): 10.0,
	("new", "cat"): 1.0,
})
```

Given a sequence that could produce either `new york` or `new cat`, the scorer makes `new york` preferable.

## Context Semantics

The `context` argument contains preceding words.

Its length is limited by `context_size`.

For example, with:

```python
@property
def context_size(self) -> int:
	return 2
```

A scorer may receive:

```python
("new", "york")
```

when evaluating the next word.

The current word is not included in `context`.

The scorer is responsible only for evaluating the current word against the supplied context.

## Combining Multiple Signals

A custom scorer can combine several signals into a single score.

For example:

```python
from morse.solving import MorseScorer


class CombinedScorer(MorseScorer):
	@property
	def context_size(self) -> int:
		return 1

	def score(
		self,
		word: str,
		context: tuple[str, ...] = (),
	) -> float:
		score = 0.0

		if len(word) <= 4:
			score += 1.0

		if word.lower() in {"the", "and", "of", "to"}:
			score += 3.0

		if context and context[-1].lower() == "new":
			if word.lower() == "york":
				score += 10.0

		return score
```

This is often more useful than trying to make one signal responsible for the entire ranking.

You can combine:

- Word frequency
- Word length
- Dictionary membership
- Previous-word relationships
- Application-specific vocabulary
- Domain-specific preferences
- Character or language statistics

## Score Direction

The solver treats larger scores as better.

For example:

```python
return 10.0
```

is preferred over:

```python
return 2.0
```

Scores may be zero.

A scorer should generally use non-negative scores when possible, although `MorseScorer` itself does not require that restriction.

The solver compares total path scores by addition:

```python
total_score = previous_score + current_score
```

Therefore, scores should be designed so that adding them produces a meaningful overall ranking.

## Using a Custom Scorer

A custom scorer can be passed directly to `MorseSolver`:

```python
from morse.alphabets import InternationalMorse
from morse.solving import (
	MorseDictionary,
	MorseSolver,
)

alphabet = InternationalMorse()

dictionary = MorseDictionary([
	"hello",
	"world",
])

scorer = ShortWordScorer()

solver = MorseSolver(
	alphabet,
	dictionary,
	scorer,
)

result = solver.solve(
	morse.parse_unspaced(
		morse.encode_unspaced("HELLO")
	)
)
```

It can also be passed through the high-level `Morse` API:

```python
from morse import Morse

morse = Morse(
	dictionary=["hello", "world"],
	scorer=ShortWordScorer(),
)

result = morse.solve(
	morse.encode_unspaced("HELLO")
)
```

Or supplied for an individual solve operation:

```python
result = morse.solve(
	value,
	dictionary=["hello", "world"],
	scorer=ShortWordScorer(),
)
```

## Custom Scorer with Custom Dictionaries

Scorers do not determine which words are valid.

The dictionary still controls the candidate vocabulary:

```python
dictionary = MorseDictionary([
	"hello",
	"world",
	"python",
	"morse",
])
```

The scorer only determines how those candidates are ranked.

This separation is intentional:

```text
Dictionary
	↓
Which words are possible?

Scorer
	↓
Which possible words are preferable?

Solver
	↓
Which complete segmentation has the highest total score?
```

This allows the same dictionary to be reused with completely different ranking strategies.

## Custom Context Models

A scorer can implement more sophisticated context models.

For example, a trigram-style scorer could consider the previous two words:

```python
class TrigramScorer(MorseScorer):
	@property
	def context_size(self) -> int:
		return 2

	def score(
		self,
		word: str,
		context: tuple[str, ...] = (),
	) -> float:
		if len(context) < 2:
			return 0.0

		previous_two = (
			context[-2],
			context[-1],
		)

		# Evaluate (previous_two[0], previous_two[1], word)
		return 0.0
```

The solver will retain contextual states according to its configured `beam_width`.

For example:

```python
solver = MorseSolver(
	alphabet,
	dictionary,
	scorer,
	beam_width=16,
)
```

A larger beam allows more competing contextual interpretations to survive.

This can improve results for complex scorers, at the cost of additional computation.

## Stateful Scorers

A scorer may maintain its own read-only model or lookup data.

For example:

```python
class DomainScorer(MorseScorer):
	def __init__(
		self,
		weights: dict[str, float],
	) -> None:
		self.weights = weights

	@property
	def context_size(self) -> int:
		return 0

	def score(
		self,
		word: str,
		context: tuple[str, ...] = (),
	) -> float:
		_ = context
		return self.weights.get(word.lower(), 0.0)
```

The scorer should behave predictably for repeated calls.

Avoid making `score()` mutate state in a way that changes the meaning of later scores unless that behavior is explicitly part of your model.

## Keep Scoring Separate from Decoding

A scorer should not perform Morse decoding itself.

The solver has already converted dictionary words into Morse symbol sequences and found candidate matches.

The scorer receives the resulting text word:

```text
Morse sequence
	↓
Trie matching
	↓
"hello"
	↓
scorer.score("hello", context)
	↓
numeric score
```

This keeps the components independent.

A scorer should generally not need to know about:

- `MorseSymbol`
- Morse representations
- Morse boundaries
- Parsers
- Alphabet encoding rules

Its job is to rank text candidates.

## Testing a Custom Scorer

Custom scorers should be tested independently from the solver.

For a context-independent scorer:

```python
def test_short_word_scorer() -> None:
	scorer = ShortWordScorer()

	assert scorer.context_size == 0
	assert scorer.score("a") > scorer.score("hello")
```

For a contextual scorer:

```python
def test_pair_scorer() -> None:
	scorer = PairScorer({
		("new", "york"): 10.0,
		("new", "cat"): 1.0,
	})

	assert scorer.context_size == 1
	assert scorer.score(
		"york",
		("new",),
	) > scorer.score(
		"cat",
		("new",),
	)
```

The solver should then have separate integration tests verifying that the scorer actually changes the selected solution.

## Choosing `context_size`

Use the smallest context that completely describes the information your scorer needs.

Scorer                   | `context_size` |
:----------------------- | :------------- |
Word frequency           | `0`            |
Word length              | `0`            |
Dictionary membership    | `0`            |
Previous-word transition | `1`            |
Trigram model            | `2`            |
Four-word context        | `3`            |

A larger context increases the number of distinct states the solver may need to consider.

Only request as much context as your scoring model actually requires.

## Common Mistakes

### Returning larger scores for worse candidates

Remember that higher scores win.

```python
# Better candidate should have the larger score.
return 10.0
```

### Forgetting `context_size`

A context-aware scorer must report its required context:

```python
@property
def context_size(self) -> int:
	return 1
```

Otherwise the solver will treat it as context-independent.

### Including the current word in `context`

The solver passes only preceding words.

This:

```python
score(word, context)
```

means `word` is the current candidate and `context` contains previous words.

### Mixing dictionary validation into scoring

The dictionary and scorer have separate responsibilities.

If a word must not be considered at all, put it in the dictionary logic rather than relying on the scorer to reject it.

## Summary

Custom scorers give `MorseSolver` an application-specific definition of the best solution.

Implement:

```python
class MyScorer(MorseScorer):
	@property
	def context_size(self) -> int:
		...

	def score(
		self,
		word: str,
		context: tuple[str, ...] = (),
	) -> float:
		...
```

Then:

1. Set `context_size` to the amount of previous-word context required.
2. Return a higher score for more desirable candidates.
3. Keep scoring logic independent from Morse parsing and decoding.
4. Test the scorer independently.
5. Use `beam_width` when contextual scoring requires multiple competing interpretations.

This makes the solver extensible without coupling it to any particular language model, vocabulary, or ranking strategy.
