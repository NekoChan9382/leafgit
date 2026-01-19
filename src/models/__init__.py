"""Models package - データモデルの定義"""

from .command_result import CommandResult
from .glossary import Glossary, GlossaryTerm

__all__ = [
    "CommandResult",
    "Glossary",
    "GlossaryTerm",
]
