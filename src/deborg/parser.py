# Copyright 2022 Tobias Marczewski (mtoboid)
# SPDX-License-Identifier: MIT

from __future__ import annotations

import re

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass
class DebPakInfo:
    """Basic information regarding a .deb package."""
    name: str
    distro: str = None
    release: str = None


class Parser:
    """Class that contains methods to parse an emacs .org file """
    # symbols that can indicate a line in a list, which can contain a .deb package
    LIST_BULLETS: str = "-+"

    @staticmethod
    def extract_deb_packages(file: str, distro: str, release: str) -> list[str]:
        lines: list[str]
        packages: list[DebPakInfo] = list()
        with open(file, "r") as _file:
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

        # filter packages (by adding a score)
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
        """Filter packages by distro and release."""
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
        """Is the passed line a list entry that contains package information?"""
        check = re.match("^\\s*[" + Parser.LIST_BULLETS + "]\\s+\\w", line)
        return True if check else False

    @staticmethod
    def _get_package_info(string: str) -> DebPakInfo:
        """
        Extract debian package information from a line of the form:
        <package-name> {<distro-name>:<release>}
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

