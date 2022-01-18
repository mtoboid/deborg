from __future__ import annotations
from dataclasses import dataclass
import re


@dataclass
class DebPakInfo:
    """Basic information regarding a .deb package."""
    name: str
    distro: str = None
    release: str = None


class Parser:
    """Class that contains methods to parse an emacs .org file """
    @staticmethod
    def _parse_line(line: str) -> DebPakInfo | None:
        out: DebPakInfo | None = None
        return None

