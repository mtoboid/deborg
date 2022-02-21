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
    Basic information container for a .deb package (name, distro, release).
    """
    name: str
    distro: str = None
    release: str = None


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
        """

        if not file.is_file():
            raise FileNotFoundError(f"File {file} not found.")

        lines: list[str]
        packages: list[DebPakInfo] = list()
        with file.open(mode='r') as _file:
            lines = _file.readlines()
        for line in lines:
            package = Parser.extract_deb_package_from_line(line, distro, release)
            if package:
                packages.append(package)
        return [p.name for p in packages]

    @staticmethod
    def extract_deb_package_from_line(line: str, distro: str, release: str) -> DebPakInfo | None:
        """
        Parse a line containing deb package information, and return the deb package matching the specifications.

        Parse a string of the form:
        <list-bullet> <package-name1> {<distro-name1>:<release1>}, <package-name2> {...}, ... :: <comment>
        where:
            <list-bullet> is either '+' or '-'
            <package-name> - a string without whitespaces
            <distro-name> and <release> are strings containing word characters
        Only <list-bullet> and <package-name> are required, the other elements - content in {...} and ':: <comment>' -
        are optional.

        :param line: The string to parse
        :param distro: return package for which distro?
        :param release: return package for which release?
        :return: a DebPakInfo object, or None if none matches the specifications
        """
        if not Parser._is_package_line(line):
            return None
        packages: list[DebPakInfo] = list()

        # remove <list-bullet>
        _line: str = line.strip()[1:].strip()
        # remove :: <comment>
        _line = _line.split("::")[0].strip()
        # parse packages and info
        packages.extend([Parser._get_package_info(pak) for pak in _line.split(",")])

        # filter packages
        # if a package lacks distro or release information (=None) treat it
        # to match any distro or release. If an exact match for distro or
        # distro and release can be found return this.
        kept_packages: list[DebPakInfo] = Parser._matching_packages(packages, distro, release)

        if len(kept_packages) < 1:
            return None

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
            msg = "More than two packages match the distro and release requirements"
            raise ValueError(f"{msg}: {', '.join([p.name for p in kept_packages])}.")
        return kept_packages[0]

    @staticmethod
    def _matching_packages(packages: Sequence[DebPakInfo], distro: str, release: str) -> list[DebPakInfo]:
        """
        Filter packages by distro and release.
        (Retain all packages that are not in conflict with the specified distro or release)
        """
        matching: list[DebPakInfo] = list()
        for package in packages:
            if package.release is not None and package.release != release:
                continue
            if package.distro is not None and package.distro != distro:
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
    def _get_package_info(string: str) -> DebPakInfo:
        """
        Extract debian package information from a string of the form:
        '<package-name> {<distro-name>:<release>}'
        """
        package_info_regex: re.Pattern = re.compile(
            "\\s*(?P<package_name>[-\\w]+)" +
            "(\\s+[{]\\s*" +
            "(?P<distro_name>[\\w]+)" +
            "(\\s*:\\s*(?P<release>[\\w.]+))?" +
            "\\s*[}])?"
        )
        pak = package_info_regex.match(string)
        if not pak:
            raise ValueError("Not a valid package string.")
        return DebPakInfo(
            name=pak.group("package_name"),
            distro=pak.group("distro_name"),
            release=pak.group("release")
        )
