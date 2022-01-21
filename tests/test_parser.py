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


@pytest.fixture
def package_info_str_input() -> Sequence[tuple[str, DebPakInfo]]:
    return [
        ("package",
         DebPakInfo(name="package")),
        (" pack1 {Debian} ",
         DebPakInfo(name="pack1", distro="Debian")),
        (" p-1-package {Debian:10}  ",
         DebPakInfo(name="p-1-package", distro="Debian", release="10")),
        (" thisisa-n20-package {Ubuntu:bionic}",
         DebPakInfo(name="thisisa-n20-package", distro="Ubuntu", release="bionic")),
        ("otherone {Ubuntu:18.04}",
         DebPakInfo(name="otherone", distro="Ubuntu", release="18.04"))
    ]


@pytest.fixture
def deb_package_line_input() -> Sequence[tuple[str, Sequence[DebPakInfo]]]:
    return [
        ("This is not a package line...",
         []),
        ("This neither but it has a + and a - in it.",
         []),
        (" + package1",
         [DebPakInfo(name="package1")]),
        (" - package-x {Debian} ",
         [DebPakInfo(name="package-x", distro="Debian")]),
        ("+ pak-a {Debian}, pak-b {theOtherDistro:42} ",
         [DebPakInfo(name="pak-a", distro="Debian"),
          DebPakInfo(name="pak-b", distro="theOtherDistro", release="42")]),
        ("  - pakx :: this is a great package!",
         [DebPakInfo(name="pakx")]),
        ("+ pak-all, pak-special {forSpecial:321} :: special needs special + love",
         [DebPakInfo(name="pak-all"),
          DebPakInfo(name="pak-special", distro="forSpecial", release="321")])
    ]


class TestParser:
    """Tests for the parser itself."""

    def test_get_package_info(self, package_info_str_input):
        for line, pakinfo in package_info_str_input:
            assert Parser._get_package_info(line) == pakinfo

    def test_line_containing_no_package_info_returns_empty_list(self, non_package_lines):
        for line in non_package_lines:
            output: list[DebPakInfo] = Parser._extract_deb_packages_from_line(line)
            assert output == []

    def test_extract_deb_packages(self, deb_package_line_input):
        for line, expected_list in deb_package_line_input:
            package_list = Parser._extract_deb_packages_from_line(line)
            assert len(package_list) == len(expected_list)
            assert package_list == expected_list
