"""
Tests for the command line utility deborg accessed via deborg.__main__.py.
"""

from __future__ import annotations

import pytest
from pytest_console_scripts import script_runner


def test_version_argument_works(script_runner):
    result = script_runner.run('deborg', '--version')
    assert result.success
    assert result.stderr == ''


def test_non_existing_orgfile_raises_error(script_runner):
    """Try to open a non-existing file."""
    result = script_runner.run(
        'deborg', '/not/existing/file.org',
        'any_distro', 'any_release')
    assert not result.success
    assert result.returncode == 1
    assert result.stdout.strip().endswith("not found.")


def test_parse_testfile(script_runner):
    """Parse the test file with one setting for distro and repo."""
    expected_packages: list[str] = [
        "basic-commented-package2",
        "basic-package1",
        "package",
        "package2",
        "package5-hyphen",
        "package-distA11",
        "package-distA12",
        "package-distA5",
        "package-distA6",
        "package-with-hyphens",
        "packageX"]
    result = script_runner.run(
        'deborg', 'tests/input/testfile_ex1.org',
        'distroA', 'release0', '--sep=::')
    assert result.success
    output: list[str] = result.stdout.strip().split("::")
    # sort both lists as shell 'sort' seems to sort '-' differently
    assert sorted(output) == sorted(expected_packages)
