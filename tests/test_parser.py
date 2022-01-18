from __future__ import annotations

import pytest
from collections.abc import Sequence


from src.deborg.parser import DebPakInfo, Parser


class TestDebPakInfo:
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


@pytest.fixture
def non_package_lines() -> Sequence[str]:
    return [
        "",
        "This is just a line",
        "A line with some + and - symbols in it.",
        "One with a colon: will that pass?",
        "* A Heading - yep",
        "** Subheading",
        "The next word is =verbatim=",
        "Here we have a ~code~ tag.",
        "No idea when one would do {that}, but whatever."
    ]


class TestParser:
    """Test for the parser itself."""

    def test_line_containing_no_package_info_returns_none(self, non_package_lines):
        for file_line in non_package_lines:
            output: DebPakInfo | None = Parser._parse_line(file_line)
            assert output is None

