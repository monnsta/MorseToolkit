from morse.core import (
	MorseAlphabet,
	MorseStream,
	MorseToken,
	MorseTokenType,
)


class MorseEncoder:
	"""Encodes plain text into structured streams of MorseTokens using a specified alphabet."""

	def __init__(self, alphabet: MorseAlphabet) -> None:
		"""Initializes the encoder with a specific MorseAlphabet.

		Args:
			alphabet: The MorseAlphabet instance to use for character mapping.
		"""
		self.alphabet = alphabet

	def encode(self, value: str) -> MorseStream:
		"""Encodes a string into a stream of structured Morse tokens.

		Inserts appropriate character boundary and word boundary tokens during process.

		Args:
			value: The plain text string to encode.

		Returns:
			A MorseStream containing the generated token sequence.

		Raises:
			ValueError: If a character in the string is unsupported by the alphabet.
		"""
		tokens: list[MorseToken] = []

		for index, character in enumerate(value):
			if character == " ":
				if (
					tokens
					and tokens[-1].type is MorseTokenType.CHARACTER_BOUNDARY
				):
					tokens.pop()

				tokens.append(MorseToken.word_boundary())
				continue

			symbols = self.alphabet.encode(character)

			if index > 0 and tokens:
				previous = value[index - 1]

				if previous != " ":
					tokens.append(MorseToken.character_boundary())

			tokens.extend(MorseToken.symbol_token(symbol) for symbol in symbols)

		return MorseStream.from_tokens(iter(tokens))
