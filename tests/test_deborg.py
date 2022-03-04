"""
Tests for the command line utility deborg accessed via deborg.__main__.py.
"""

from __future__ import annotations

from pytest_console_scripts import RunResult

from deborg.cli import Examples


def test_two_package_match_in_same_line_raises_error(tmpdir, script_runner):
    file_content: str = "" +\
        "# file created by pytest test_deborg.py\n" +\
        "# this item entry contains two packages matching any distro and release:\n" +\
        "+ package-1-a, package-1-b\n"
    error_msg_start: str = "Error while parsing"
    error_msg_end: str = "Error in line 2: More than two packages match " +\
                         "the specifications: package-1-a, package-1-b."
    orgfile = tmpdir.join("testfile.org")
    orgfile.write(file_content)
    result = script_runner.run('deborg', str(orgfile), 'distro', 'release')
    assert result.returncode == 1
    assert result.stderr.strip().startswith(error_msg_start)
    assert result.stderr.strip().endswith(error_msg_end)


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


def test_example_file_examples(tmpdir, script_runner):
    tests: Examples = Examples()
    orgfile = tmpdir.join("testfile.org")
    command_out = script_runner.run('deborg', '--example-file')
    orgfile.write(command_out.stdout)
    for i in range(tests.n):
        # the parsed input 'distro1' becomes "'distro1'" which is not "distro1"
        # -> remove all ' from the strings
        args = [a.replace("'", "") for a in tests.input[i].split(' ')]
        command = ['deborg', str(orgfile), *args]
        result: RunResult = script_runner.run(*command)
        assert result.returncode == 0
        assert result.stdout.strip() == tests.output[i].strip()
