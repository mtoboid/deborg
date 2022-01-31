from __future__ import annotations

import pytest
from collections.abc import Sequence
from pathlib import Path

from src.deborg.parser import DebPakInfo, Parser


class TestDebPakInfo:
    """Tests for the dataclass used to hold deb package information."""
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
    """Text that could occur in the file, but is not a line specifying a deb package."""
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
def deb_package_line_input() -> Sequence[tuple[str, str, str, DebPakInfo]]:
    """1) Input line | 2) distro (arg) | 3) release (arg) | 4) expected out"""
    return [
        ("This is not a package line...",
         "any_distro", "any_release",
         None),

        ("This neither but it has a + and a - in it.",
         "any_distro", "any_release",
         None),

        (" + package1",
         "any_distro", "any_release",
         DebPakInfo(name="package1")),

        (" - package-x {Distro} ",
         "not_distro", "any_release",
         None),

        (" - package-x {Distro} ",
         "Distro", "any_release",
         DebPakInfo(name="package-x", distro="Distro")),

        ("+ pak-a {Debian}, pak-b {theOtherDistro:42}, pak-c ",
         "any_distro", "any_release",
         DebPakInfo(name="pak-c")),

        ("+ pak-a {Debian}, pak-b {theOtherDistro:42}, pak-c ",
         "Debian", "any_release",
         DebPakInfo(name="pak-a", distro="Debian")),

        ("+ pak-a {Debian}, pak-b {theOtherDistro:42}, pak-c ",
         "theOtherDistro", "any_release",
         DebPakInfo(name="pak-c")),

        ("+ pak-a {Debian}, pak-b {theOtherDistro:42}, pak-c ",
         "theOtherDistro", "42",
         DebPakInfo(name="pak-b", distro="theOtherDistro", release="42")),

        ("  - pakx :: this is a great package!",
         "any_distro", "any_release",
         DebPakInfo(name="pakx")),

        ("+ pak-all, pak-special {forSpecial:321} :: special needs special + love",
         "any_distro", "any_release",
         DebPakInfo(name="pak-all")),

        ("+ pak-all, pak-special {forSpecial:321} :: special needs special + love",
         "forSpecial", "other_release",
         DebPakInfo(name="pak-all")),

        ("+ pak-all, pak-special {forSpecial:321} :: special needs special + love",
         "forSpecial", "321",
         DebPakInfo(name="pak-special", distro="forSpecial", release="321"))
    ]


# packages obtained from parsing a file
ExpectedPackagesOutput = Sequence[str]
# distro, release, expected_output
InputOutputSpec = tuple[str, str, ExpectedPackagesOutput]


@pytest.fixture
def org_file1_tests() -> tuple[Path, Sequence[InputOutputSpec]]:
    """Parsing tests for file ./tests/input/testfile_ex1.org."""
    testfile: str = "input/testfile_ex1.org"
    test_dir: Path = Path(__file__).resolve().parent
    test_input_org_file: Path = test_dir.joinpath(testfile)
    if not test_input_org_file.exists():
        raise FileNotFoundError(f"Testfile: {testfile} not found.")

    test_params: list[InputOutputSpec] = [
        ("distro", "any",
         [
            "package",
            "package2",
            "package-with-hyphens",
            "package5-hyphen",
            "packageX",
            "basic-package1",
            "basic-commented-package2",
            "package-dist3",
            "package-dist4",
            "package-distA11"
         ]),

        ("distroA", "any",
         [
            "package",
            "package2",
            "package-with-hyphens",
            "package5-hyphen",
            "packageX",
            "basic-package1",
            "basic-commented-package2",
            "package-distA5",
            "package-distA6",
            "package-distA11",
            "package-distA12"
         ]),

        ("distroA", "release1",
         [
            "package",
            "package2",
            "package-with-hyphens",
            "package5-hyphen",
            "packageX",
            "basic-package1",
            "basic-commented-package2",
            "package-distA5",
            "package-distA6",
            "package-distA7",
            "package-distA8",
            "package-distA9",
            "package-distA10",
            "package-distA11",
            "package-distA12"
         ]),

        ("distroA", "release2",
         [
            "package",
            "package2",
            "package-with-hyphens",
            "package5-hyphen",
            "packageX",
            "basic-package1",
            "basic-commented-package2",
            "package-distA5",
            "package-distA6",
            "package-distB9",
            "package-distA11",
            "package-distB12"
         ]),

        ("distroB", "any",
         [
            "package",
            "package2",
            "package-with-hyphens",
            "package5-hyphen",
            "packageX",
            "basic-package1",
            "basic-commented-package2",
            "package-distB5",
            "package-distB6",
            "package-distA11"
         ]),

        ("distroB", "release1",
         [
            "package",
            "package2",
            "package-with-hyphens",
            "package5-hyphen",
            "packageX",
            "basic-package1",
            "basic-commented-package2",
            "package-distB5",
            "package-distB6",
            "package-distB11"
         ]),

        ("distroB", "release2",
         [
            "package",
            "package2",
            "package-with-hyphens",
            "package5-hyphen",
            "packageX",
            "basic-package1",
            "basic-commented-package2",
            "package-distB5",
            "package-distB6",
            "package-distB10",
            "package-distA11"
         ])
    ]
    return test_input_org_file, test_params


class TestParser:
    """Tests for the parser itself."""

    def test_get_package_info(self, package_info_str_input):
        for line, pak_info in package_info_str_input:
            assert Parser._get_package_info(line) == pak_info

    def test_line_containing_no_package_info_returns_empty_list(self, non_package_lines):
        for line in non_package_lines:
            output: DebPakInfo | None = Parser.extract_deb_package_from_line(line, "any", "any")
            assert output is None

    def test_extract_deb_package_from_line(self, deb_package_line_input):
        for line, *param, expected_DebPakInfo in deb_package_line_input:
            package_info = Parser.extract_deb_package_from_line(line, *param)
            assert package_info == expected_DebPakInfo

    def test_extract_deb_packages(self, org_file1_tests):
        file: Path
        io_args: InputOutputSpec
        file, io_args = org_file1_tests
        for args in io_args:
            distro, release, expected_out = args
            packages: list[str] = Parser.extract_deb_packages(
                file.as_posix(), distro, release)
            assert sorted(packages) == sorted(expected_out)
