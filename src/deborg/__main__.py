#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
from deborg.parser import Parser


def main():
    parser = argparse.ArgumentParser(
        description="Extract package information from an emacs .org file."
    )
    # TODO: add info to use lsb_release
    # distro: lsb_release --short --id
    # release: lsb_release --short --release
    parser.add_argument(
        "orgfile",
        help="The .org file to parse, for the required format see examples.",
        type=Path
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
