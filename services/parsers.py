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
        aliases = set(text[1:].split())  # split with space. trimmed. no empty strings. 'a  a  c   b   ' -> {'a', 'b', 'c'}
        return aliases