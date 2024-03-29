from logging import warning
from typing import Iterable

from domain.message_handlers import Alias


class SplitParser:

    def _validate(self, words: Iterable[str]) -> Iterable[Alias]:
        warning(msg='Commands\' validation is not implemented')
        return words

    def parse(self, text: str) -> Iterable[Alias]:
        if not isinstance(text, str):
            raise TypeError(f'Wrong input type: {type(text)}. Should be str')
        # split with space. trimmed. no empty strings. {'a  a  c   b   ' -> {'a', 'b', 'c'}
        aliases = set(text.strip('/').split())
        return aliases


class ListenParser:
    def __init__(self, command: str = '/listen'):
        self._command = command

    def _validate(self, words: Iterable[str]) -> Iterable[Alias]:
        warning(msg='Commands\' validation is not implemented')
        return words

    def parse(self, text: str) -> Iterable[Alias]:
        """
        Parses input cutting len(self._command) chars nad splitting remaining with spaces
        """
        if not isinstance(text, str) and not text.startswith('/listen'):
            raise TypeError(f'Wrong input type: {type(text)}. Should be str')
        if not text.startswith(self._command):
            raise ValueError(f'Text must starts with "{self._command}"')

        # split with space. trimmed. no empty strings. '/listen a  a  c   b   ' -> {'a', 'b', 'c'}
        aliases = set(text[len(self._command):].split())
        return aliases
