#!/usr/bin/python3
#
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
"""Provides a command line entry point for the program deborg."""

from __future__ import annotations

__author__ = "Tobias Marczewski (mtoboid)"
__version__ = "1.0.0"

import sys

from argparse import ArgumentParser
from pathlib import Path

from deborg.cli import cli_parser
from deborg.orgparser import OrgParser, OrgParserError


def main():
    parser: ArgumentParser = cli_parser()
    args = parser.parse_args()
    file: Path = Path(args.orgfile)

    if not file.exists():
        print(f"Error: specified file '{file.resolve().as_posix()}' not found.")
        sys.exit(1)

    _tags: list[str] | None = None
    if args.tags:
        _tags: list[str] = args.tags.split(",")

    try:
        packages: list[str] = OrgParser.extract_deb_packages(file, args.distro, args.release, _tags)
        sys.stdout.write(args.sep.join(packages))
        sys.exit(0)
    except OrgParserError as pe:
        sys.stderr.write(f"Error while parsing {file.as_posix()}:\n{pe}")
        sys.exit(1)


if __name__ == '__main__':
    main()
