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

__author__ = "Tobias Marczewski (mtoboid)"
__version__ = "1.0.0"

import argparse
import sys
from pathlib import Path

from deborg.parser import Parser


def usage() -> argparse.ArgumentParser:
    indent: str = 2*" "
    disclaimer: str = "\ncopyright:\n\n" + \
        indent + f"Copyright (C) 2022 {__author__}\n" + \
        indent + "This program comes with ABSOLUTELY NO WARRANTY.\n" + \
        indent + "This is free software, and you are welcome to redistribute it\n" + \
        indent + "under the terms of the GNU General General Public License version 3 or later.\n\n" + \
        indent + "For more information and bug reports please visit https://github.com/mtoboid/deborg\n"

    description: str = "\ndescription:\n\n" + \
        indent + "This program parses an orgfile with list entries (+ <item> or - <item>)\n" + \
        indent + "where each list item specifies one package or alternatives for the same package:\n" + \
        indent + " + package1, package1a {Ubuntu:18.04}, package1b {Debian:9}\n" + \
        indent + " + package2, package2a {Ubuntu}\n" + \
        indent + "...\n" + \
        indent + "where {<distro>:<release>} determine which package should be returned by deborg.\n"

    examples: str = "\nexamples:\n\n" + \
        indent + "To obtain distro and release information use a tool like 'lsb_release'.\n" + \
        indent + "distro: lsb_release --short --id\n" + \
        indent + "release: lsb_release --short --release\n\n" + \
        indent + "$ deborg packages.org $(lsb_release --short --id) $(lsb_release --short --release)\n" + \
        indent + "$ package1 package2 package3\n\n" + \
        indent + "$ deborg packages.org 'Debian' '11' --sep='::'\n" + \
        indent + "$ package1::package2::package3\n\n"

    parser = argparse.ArgumentParser(
        prog="deborg",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Extract Debian package information from an emacs .org file.",
        #       *                                                                               *
        epilog=" \n" + description + examples + disclaimer

    )
    parser.add_argument(
        "-v", "--version",
        help="Display the version of deborg.",
        action='version',
        version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "orgfile",
        help="The .org file to parse.",
        type=str
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
        "-s", "--sep", default=" ",
        help="Separator used between package names in the returned array.",
        type=str
    )
    return parser


def main():
    parser: argparse.ArgumentParser = usage()
    args = parser.parse_args()
    file: Path = Path(args.orgfile)

    if not file.exists():
        print(f"Error: specified file '{file.resolve().as_posix()}' not found.")
        sys.exit(1)

    packages: list[str] = Parser.extract_deb_packages(file, args.distro, args.release)
    print(args.sep.join(packages))
    sys.exit(0)


if __name__ == '__main__':
    main()
