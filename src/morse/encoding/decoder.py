from morse.core import MorseAlphabet, MorseStream, MorseTokenType


class MorseDecoder:
	"""Decodes tokenized Morse streams into plain text strings using a specified alphabet."""

	def __init__(self, alphabet: MorseAlphabet) -> None:
		"""Initializes the decoder with a specific MorseAlphabet.

		Args:
			alphabet: The MorseAlphabet instance to use for character mapping.
		"""
		self.alphabet = alphabet

	def decode(self, stream: MorseStream) -> str:
		"""Decodes a stream of MorseTokens into a text string.

		Args:
			stream: A MorseStream container holding tokens to process.

		Returns:
			The decoded string representation.

		Raises:
			ValueError: If a symbol token lacks an associated symbol, an empty sequence
				is processed, or an unsupported token type is encountered.
		"""
		characters: list[str] = []
		current_symbols = []

		for token in stream:
			if token.type is MorseTokenType.SYMBOL:
				if token.symbol is None:
					raise ValueError("Symbol token is missing a Morse symbol")

				current_symbols.append(token.symbol)
				continue

			if token.type is MorseTokenType.CHARACTER_BOUNDARY:
				characters.append(self._decode_character(current_symbols))
				current_symbols.clear()
				continue

			if token.type is MorseTokenType.WORD_BOUNDARY:
				characters.append(self._decode_character(current_symbols))
				characters.append(" ")
				current_symbols.clear()
				continue

			raise ValueError(f"Unknown Morse token type: {token.type!r}")

		if current_symbols:
			characters.append(self._decode_character(current_symbols))

		return "".join(characters)

	def _decode_character(self, symbols) -> str:
		"""Internal helper to convert a symbol sequence into a character.

		Args:
			symbols: Sequence of MorseSymbol instances representing a single character.

		Returns:
			The decoded single string character.

		Raises:
			ValueError: If symbol sequence is empty.
		"""
		if not symbols:
			raise ValueError("Cannot decode an empty Morse character")

		return self.alphabet.decode(symbols)
