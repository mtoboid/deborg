# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright (C) 2022 Tobias Marczewski
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Parse an emacs orgmode file to extract Debian package information.

Classes:

    DebPakInfo
    Parser

Misc variables:

    __author__
    __version__
"""

from __future__ import annotations

__author__ = "Tobias Marczewski"
__version__ = "1.0.0"


import re

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DebPakInfo:
    """
    Basic information container for a .deb package (name, distro, release, tags).
    """
    name: str
    distro: str = None
    release: str = None
    tags: list[str] = None


class ParserError(BaseException):
    pass


class DuplicatePackageError(ParserError):
    pass


class Parser:
    """Class that contains static methods to parse an emacs .org file """

    # symbols that can indicate a line in a list, which can contain a .deb package
    LIST_BULLETS: str = "-+"

    @staticmethod
    def extract_deb_packages(file: Path, distro: str, release: str) -> list[str]:
        """
        Extract .deb packages from a file that match distro and release.
        (for line format see :func:`~parser.Parser.extract_deb_package_from_line`)

        :param file: path to the orgmode file
        :param distro: string
        :param release: string
        :return: list of packages

        :raises: ParserError
        :raises: FileNotFoundError
        """

        if not file.is_file():
            raise FileNotFoundError(f"File {file} not found.")

        lines: list[str]
        packages: list[DebPakInfo] = list()
        with file.open(mode='r') as _file:
            lines = _file.readlines()
        for nr, line in enumerate(lines):
            try:
                package = Parser.extract_deb_package_from_line(line, distro, release)
                if package:
                    packages.append(package)
            except DuplicatePackageError as e:
                msg: str = f"Error in line {nr}: {e}"
                raise ParserError(msg)

        return [p.name for p in packages]

    @staticmethod
    def extract_deb_package_from_line(line: str, distro: str, release: str, tags: Sequence[str] = None)\
            -> DebPakInfo | None:
        """
        Parse a line containing deb package information, and return the deb package matching the specifications.

        Parse a string of the form:
            <list-bullet> <package-name1> {<distro-name1>:<release1>}, <package-name2> {...}, ... :: <comment>
          OR the {<term>} can also contain tags (a comma separated list of tags):
            <package> {<distro>:<release>:<tag1>,<tag2>,...}
          OR minimal (tags only):
            <package1> {::<tag1>,<tag2>,...}, <package2>...
        where:
            <list-bullet> is either '+' or '-'
            <package-name> - a string without whitespaces
            <distro-name> and <release> are strings containing word characters
            <tag> a string of word characters
        Only <list-bullet> and <package-name> are required, the other elements - content in {...} and ':: <comment>' -
        are optional.

        :param line: The string to parse
        :param distro: return package for which distro?
        :param release: return package for which release?
        :param tags: package matching which tags?

        :return: a DebPakInfo object, or None if none matches the specifications.

        :raises: DuplicatePackageError, when more than one package matches in a given line.
        """
        if not Parser._is_package_line(line):
            return None
        _tags: list[str] = []
        if tags:
            _tags = list(tags)
        packages: list[DebPakInfo] = list()

        for package_string in Parser._split_package_line(line):
            packages.append(Parser._get_package_info(package_string))

        # filter packages
        # if a package lacks distro or release information (=None) treat it
        # to match any distro or release. If an exact match for distro or
        # distro and release can be found return this.
        kept_packages: list[DebPakInfo] = Parser._matching_packages(packages, distro, release, _tags)

        if len(kept_packages) < 1:
            return None

        # narrow by tags
        if len(kept_packages) > 1 and len(_tags) > 0:
            if any([p.tags is not None for p in kept_packages]):
                kept_packages = [p for p in kept_packages if p.tags is not None]
        # narrow by release
        if len(kept_packages) > 1:
            if any([p.release is not None for p in kept_packages]):
                kept_packages = [p for p in kept_packages if p.release is not None]
        # narrow by distro
        if len(kept_packages) > 1:
            if any([p.distro is not None for p in kept_packages]):
                kept_packages = [p for p in kept_packages if p.distro is not None]

        # still more than 1 package -> error
        if len(kept_packages) > 1:
            msg = "More than two packages match the specifications."
            raise DuplicatePackageError(f"{msg}: {', '.join([p.name for p in kept_packages])}.")
        return kept_packages[0]

    @staticmethod
    def _matching_packages(packages: Sequence[DebPakInfo], distro: str, release: str, tags: list[str]) ->\
            list[DebPakInfo]:
        """
        Filter packages by distro, release and tags.
        (Retain all packages that are not in conflict with the specified distro or release)
        """
        matching: list[DebPakInfo] = list()
        for package in packages:
            if package.release is not None and package.release != release:
                continue
            if package.distro is not None and package.distro != distro:
                continue
            if package.tags is not None:
                if not any([tag in package.tags for tag in tags]):
                    continue
            if package not in matching:
                matching.append(package)
        return matching

    @staticmethod
    def _is_package_line(line: str) -> bool:
        """Is the passed line a list entry that can contain package information?"""
        check = re.match("^\\s*[" + Parser.LIST_BULLETS + "]\\s+\\w", line)
        return True if check else False

    @staticmethod
    def _split_package_line(line: str) -> list[str]:
        """
        Split a package line into separate strings for each package info;
        also discard the leading item bullet and any comment at the end of the line.

        :param line: a line containing package information
        :return: a list of strings containing the info for each separate package.
        """
        if not Parser._is_package_line(line):
            raise ValueError("Non package line passed!")
        package_strings: list[str] = []
        # remove <list-bullet>
        _line: str = line.strip()[1:].strip()
        last_pos: int = 0
        pos: int = 0

        # parse package by package (pak1 {..}, pak2, .. :: comment)
        while pos < len(_line):
            # ignore leading space
            while _line[pos] == ' ':
                pos += 1
            # ignore a trailing comment
            if _line[pos] == ':' and _line[pos+1] == ':':
                break
            # package name
            while pos < len(_line) and _line[pos] not in [' ', ',']:
                pos += 1
            # when not comma
            if pos < len(_line) and _line[pos] != ',':
                # if space go to next non-space char
                while pos < len(_line) and _line[pos] == ' ':
                    pos += 1
                # check if bracket term
                if pos < len(_line) and _line[pos] == '{':
                    while _line[pos] != '}':
                        pos += 1
                    pos += 1
            # save part package string
            pack_string: str = _line[last_pos:pos].strip()
            package_strings.append(pack_string)
            if pos < len(_line) and _line[pos] == ',':
                pos += 1
            last_pos = pos

        return package_strings

    @staticmethod
    def _get_package_info(string: str) -> DebPakInfo:
        """
        Extract debian package information from a string of the form:
        '<package-name> {<distro-name>:<release>:<tag1>,<tag2>,...}'
        """
        package_info_regex: re.Pattern = re.compile(
            "\\s*(?P<package_name>[-\\w]+)" +
            "(\\s+[{]\\s*" +
            "(?P<distro_name>[\\w]+)?" +
            "((\\s*:\\s*(?P<release>[\\w.]*)?)" +
            "(\\s*:\\s*(?P<tags>[-,\\w]*))?)?" +
            "\\s*[}])?"
        )
        pak = package_info_regex.match(string)
        if not pak:
            raise ValueError("Not a valid package string.")

        name: str = pak.group("package_name")
        distro: str | None = pak.group("distro_name")
        release: str | None = pak.group("release")

        if distro == '':
            distro = None
        if release == '':
            release = None

        tags: list[str] | None = None
        if pak.group("tags"):
            tags = pak.group("tags").split(",")

        return DebPakInfo(
                    name=name,
                    distro=distro,
                    release=release,
                    tags=tags
               )
