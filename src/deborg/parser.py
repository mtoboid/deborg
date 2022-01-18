from __future__ import annotations
from dataclasses import dataclass


@dataclass
class DebPakInfo:
    """Basic information regarding a .deb package."""
    name: str
    distro: str = None
    release: str = None


class Parser:
    @staticmethod
    def _parse_line(line: str) -> DebPakInfo | None:
        pass
