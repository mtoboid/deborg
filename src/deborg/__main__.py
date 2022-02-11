#!/usr/bin/env python3
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

"""
Provide the cli program 'deborg'.
"""

__author__ = "Tobias Marczewski"
__version__ = "1.0.0"

import argparse
import sys
from pathlib import Path
from deborg.parser import Parser

# TODO add an option to display version information
def main():
    parser = argparse.ArgumentParser(
        prog="deborg",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Extract package information from an emacs .org file.",
        #       *                                                                               *
        epilog="To obtain distro and release information use a tool like 'lsb_release' which is " +
               "generally available for Debian or Ubuntu:\n" +
               "distro: lsb_release --short --id\n" +
               "release: lsb_release --short --release"
    )
    parser.add_argument(
        "orgfile",
        help="The .org file to parse, for the required format see examples.",
        type=argparse.FileType('r')
    )
    parser.add_argument(
        "distro",
        help="Linux distribution for which to extract the packages, e.g. 'Debian', 'Ubuntu'...",
        type=str
    )
    parser.add_argument(
        "release",
        help="Release for which to extract the packages, e.g. '10', '11', '18.04'...",
        type=str
    )
    parser.add_argument(
        "--sep", default=" ",
        help="Separator used between package names in the returned array.",
        type=str
    )

    args = parser.parse_args()
    file: Path = args.orgfile

    if not file.exists():
        print(f"Error: specified file '{file.resolve().as_posix()}' not found.")
        sys.exit(1)

    packages: list[str] = Parser.extract_deb_packages(file.resolve().as_posix(), args.distro, args.release)
    print(args.sep.join(packages))
    sys.exit(0)


if __name__ == '__main__':
    main()
