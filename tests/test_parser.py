from __future__ import annotations

from unittest import TestCase


from src.deborg.parser import DebPakInfo, Parser


class TestDebPakInfo(TestCase):
    """Tests for the dataclass used to store the parsed packages."""
    def test_instantiation_name_only(self):
        d: DebPakInfo = DebPakInfo("package_name")
        assert d.name == "package_name"

    def test_instantiation_name_and_distro(self):
        d: DebPakInfo = DebPakInfo("package_name", distro="distro_name")
        assert (d.name == "package_name" and d.distro == "distro_name")

    def test_instantiation_name_distro_release(self):
        d: DebPakInfo = DebPakInfo(
            "package_name", distro="distro_name", release="release_name"
        )
        assert (
                d.name == "package_name"
                and d.distro == "distro_name"
                and d.release == "release_name"
        )


class TestParser(TestCase):
    """Test for the parser itself."""

    def test_empty_string_returns_None(self):
        file_line: str = ""
        output: DebPakInfo | None = Parser._parse_line(file_line)
        assert output is None


# from dataclasses import dataclass
# @dataclass