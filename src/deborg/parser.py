from __future__ import annotations
from dataclasses import dataclass
import re


@dataclass
class DebPakInfo:
    """Basic information regarding a .deb package."""
    name: str
    distro: str = None
    release: str = None


class Parser:
    """Class that contains methods to parse an emacs .org file """
    LIST_BULLETS: str = "-+"
    # <package-name> {<distro-name>:<release>}
    PACKAGE_AND_INFO_RX: re.Pattern = re.compile(
        "\\s*(?P<package_name>[a-z0-9][-a-z0-9.+]+)" +
        "(\\s+[{]\\s*" +
        "(?P<distro_name>[\\w]+)" +
        "(\\s*:\\s*(?P<release>[\\w.]+))?" +
        "\\s*[}])?"
    )

    @staticmethod
    def _extract_deb_packages_from_line(line: str) -> list[DebPakInfo]:
        """
        Parse a line of the form:
        <list-bullet> <package-name1> {<distro-name1>:<release1>}, <package-name2> {...}, ... :: <comment>
        where:
            <list-bullet> is either '+' or '-'
            <package-name> - a valid Debian package name
                (see https://www.debian.org/doc/manuals/debian-reference/ch02.en.html#_debian_package_file_names)
            <distro-name> and <release> are strings containing any char apart from a ':' (colon)
        Only <list-bullet> and <package-name> are required, the other elements - content in {...} and ':: <comment>' -
        are optional.

        :param line: The line to parse
        :return: a list of DebPakInfo objects, or an empty list, if the line does not specify any deb packages.
        """
        out: list[DebPakInfo] = list()
        if Parser._is_package_line(line):
            # remove <list-bullet>
            _line: str = line.strip()[1:].strip()
            # remove :: <comment>
            _line = _line.split("::")[0].strip()
            # parse packages and info
            packages = _line.split(",")
            for pak in packages:
                out.append(Parser._get_package_info(pak))
        return out

    @staticmethod
    def _is_package_line(line: str) -> bool:
        check = re.match("^\\s*[" + Parser.LIST_BULLETS + "]\\s+\\w", line)
        return True if check else False

    @staticmethod
    def _get_package_info(line: str) -> DebPakInfo:
        pak = Parser.PACKAGE_AND_INFO_RX.match(line)
        if not pak:
            raise ValueError("Not a valid package line.")
        return DebPakInfo(
            name=pak.group("package_name"),
            distro=pak.group("distro_name"),
            release=pak.group("release")
        )
