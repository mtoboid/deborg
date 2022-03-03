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
Provides the cli for the package 'deborg'.

Classes:

    PrintExampleFile
    Examples

Misc variables:

    __author__
    __version__
"""

from __future__ import annotations

__author__ = "Tobias Marczewski (mtoboid)"
__version__ = "1.0.0"

import argparse
from collections.abc import Sequence


class PrintExampleFile(argparse.Action):
    """Argparse action to display an example orgmode file that can be parsed by deborg."""

    EXAMPLE_FILE: str = "# This is an example file for 'deborg'\n" +\
        "# deborg was written to parse orgmode list items of the general format:\n" +\
        "+ package-name {distro:release:tag1,tag2,tag3}\n" +\
        "\n" +\
        "# where each item can specify alternative packages separated by comma for the\n" +\
        "# same requirement\n" +\
        "+ package, package1 {distro1}, package2b {distro2:release_b}\n" +\
        "\n" +\
        "# for lines with several comma-separated packages deborg will at most return one\n" +\
        "# package, as they are seen as alternatives; if more than one package matches the\n" +\
        "# specifications an error will be reported.\n" +\
        "\n" +\
        "# As can be seen from the comment lines it is no problem to write more information into\n" +\
        "# the file, as long as the package lines (list items with either '-' or '+')\n" +\
        "# have the correct format. This additional information does not have to be in\n" +\
        "# comment format as we see below:\n" +\
        "\n" +\
        "* System relevant packages\n" +\
        "  The following packages I always want installed as they provide foo for baz...\n" +\
        "  + foo\n" +\
        "  + foo-two\n" +\
        "  # we can comment on the packages using description list items like that:\n" +\
        "  + baz, baz-alternative {distro1} :: for distro1 baz is missing in the repos\n" +\
        "                                      but baz-alternative provides the same\n" +\
        "				      functionality.\n" +\
        "  # and we can use tags like here\n" +\
        "  + apache {::server} :: this should be installed for any distro, but only on a\n" +\
        "                         server\n" +\
        "  + office-app-x {::desktop,laptop} :: this will be installed when 'desktop' or\n" +\
        "                                       'laptop' is passed as tag, hence not on a\n" +\
        "                                       server.\n" +\
        "\n" +\
        "* Email\n" +\
        "** general\n" +\
        "   # we can also use '-' as list bullet\n" +\
        "   - thunderbird\n" +\
        "\n" +\
        "** language support\n" +\
        "   - thunderbird-locale-xx {Ubuntu}, thunderbird-l10n-xx {Debian} :: language xx\n" +\
        "   - thunderbird-locale-zz {Ubuntu}, thunderbird-l10n-zz {Debian} :: language zz\n" +\
        ""

    def __init__(self, option_strings,
                 dest=argparse.SUPPRESS, default=argparse.SUPPRESS, **kwargs):
        super(PrintExampleFile, self).__init__(
            option_strings=option_strings, dest=dest, default=default, nargs=0, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        print(self.EXAMPLE_FILE)
        parser.exit()


class Examples(object):
    """
    Example usage for deborg using the file defined in PrintExampleFile.
    (deborg --example-file > examples.org)

    Running `deborg 'examples.org' Examples.input[i]` should produce `Examples.output[i]`
    """
    _input: list[str] = []
    _output: list[str] = []
    _n: int = 0

    def __init__(self):
        # 0
        self.add("'' ''",
                 "package foo foo-two baz thunderbird")
        # 1
        self.add("'distro1' ''",
                 "package1 foo foo-two baz-alternative thunderbird")
        # 2
        self.add("'distro2' 'release_b'",
                 "package2b foo foo-two baz thunderbird")
        # 3
        self.add("'' '' --tags=server",
                 "package foo foo-two baz apache thunderbird")
        # 4
        self.add("'distro1' '' --tags=desktop",
                 "package1 foo foo-two baz-alternative office-app-x thunderbird")
        # 5
        self.add("'distro1' '' --tags=desktop,server",
                 "package1 foo foo-two baz-alternative apache office-app-x thunderbird")
        # 6
        self.add("'Debian' ''",
                 "package foo foo-two baz thunderbird thunderbird-l10n-xx thunderbird-l10n-zz")
        self.add("'Ubuntu' ''",
                 "package foo foo-two baz thunderbird thunderbird-locale-xx thunderbird-locale-zz")
        # 8
        self.add("'distro' 'any' --sep='::'",
                 "package::foo::foo-two::baz::thunderbird")

    @property
    def input(self) -> Sequence[str]:
        return self._input

    @property
    def output(self) -> Sequence[str]:
        return self._output

    @property
    def n(self) -> int:
        return self._n

    def add(self, args: str, output: str):
        self._input.append(args)
        self._output.append(output)
        self._n += 1


def cli_parser() -> argparse.ArgumentParser:
    """Build a commandline argument parser for deborg"""
    indent: str = 2*" "
    disclaimer: str = "\ndisclaimer:\n\n" + \
        indent + f"Copyright (C) 2022 {__author__}\n" + \
        indent + "This program comes with ABSOLUTELY NO WARRANTY.\n" + \
        indent + "This is free software, and you are welcome to redistribute it under the terms\n" + \
        indent + "of the GNU General General Public License version 3 or later.\n\n" + \
        indent + "For more information and bug reports please visit https://github.com/mtoboid/deborg\n"

    description: str = "\ndescription:\n\n" + \
        indent + "This program parses an orgfile with list entries (+ <item> or - <item>)\n" + \
        indent + "where each list item specifies one package or alternatives for the same package:\n" + \
        indent + " + package1, package1a {Ubuntu:18.04}, package1b {Debian:9}\n" + \
        indent + " + package2, package2a {Ubuntu}\n" + \
        indent + "...\n" + \
        indent + "where {<distro>:<release>} determine which package should be returned by deborg.\n" + \
        indent + "Also see '%(prog)s --example-file'.\n"

    ex: Examples = Examples()
    examples: str = "\nexamples:\n\n" + \
        indent + "For easier integration into scripts, it is advisable to use the exact strings returned\n" + \
        indent + "by a tool like 'lsb_release' for 'distro' and 'release'.\n" + \
        indent + "distro: lsb_release --short --id\n" + \
        indent + "release: lsb_release --short --release\n\n" + \
        indent + "$ deborg packages.org $(lsb_release --short --id) $(lsb_release --short --release)\n" + \
        indent + "$ package1 package2 package3\n\n" + \
        indent + "Using the example file 'deborg --example-file > examples.org' :\n\n"
    examples += ''.join(
        [f"{indent}$ deborg examples.org {ex.input[i]}\n{indent}$ {ex.output[i]}\n\n" for i in range(ex.n)])

    parser = argparse.ArgumentParser(
        prog="deborg",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Extract Debian package information from an emacs .org file.",
        epilog="" + description + examples + disclaimer

    )
    parser.add_argument(
        "--example-file",
        help="Print an example orgmode file to stdout.",
        action=PrintExampleFile
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
    parser.add_argument(
        "-t", "--tags", default=None,
        dest="tags",
        help="Comma separated list of tags, no spaces. (tag1,tag2,tag3)",
        type=str
    )
    return parser
