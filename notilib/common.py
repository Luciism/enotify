import os
from typing import Literal, Any


PROJECT_PATH = os.path.abspath(f'{__file__}/../..')

WebmailServiceLiteral = Literal['gmail']


class _MissingSentinel:  # borrowed from discord.py
    __slots__ = ()

    def __eq__(self, other) -> bool:
        return False

    def __bool__(self) -> bool:
        return False

    def __hash__(self) -> int:
        return 0

    def __repr__(self):
        return '...'

MISSING: Any = _MissingSentinel()
