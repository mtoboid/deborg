========
 deborg
========

-------------------------------------------------------------
Extract Debian package information from an Emacs orgmode file
-------------------------------------------------------------

:Author: Tobias Marczewski
:Date: 2022-02-22
:Copyright: GPL-3+
:Manual section: 1

    
SYNOPSIS
========

**deborg** [*options*] *orgfile* *distro* *release*
    
DESCRIPTION
===========

**deborg** parses an Emacs orgmode file that contains lists of Debian packages,
and returns a list of matching packages depending on specified distro, release
and (optional) tags. This allows the maintanance of a common list of packages
that are to be installed on different systems, but allows differences between
distros and releases (see **INPUT FILE STRUCTURE**).

ARGUMENTS
=========
   
*orgfile*           The orgmode file to parse.

*distro*            Linux distro for which to extract packages.

*release*           Distro release for which to extract packages.

OPTIONS
=======

-h, --help
       Display general usage information.

--example-file
       Print an example orgmode file to stdout.

-v, --version
       Show version of **deborg**.

-s *sep*, --sep=\ *sep*
       Separator to use between package names in the output array. *sep* can be
       any string.
		       
-t *tags*, --tags=\ *tags*
       Comma-separated list of tags which are included in the filtering.

EXIT STATUS
===========

**deborg** will exit with exit status ``1`` if an error occurred while parsing the
file, otherwise the exit status will be ``0``.


INPUT FILE STRUCTURE
====================

For an example orgmode file please use ``deborg --example-file``.

The orgmode file can contain normal text and headings, but only list
items with either ``-`` or ``+`` are considered lines containing package
information; the file can still contain numbered lists, but they won't be parsed
for packages.

Package information consists of a package name followed by an
(optional) specification of distro, release and tags in curly braces ``{}``, and
separated by colons ``:``. When a preceding specifier is omitted, a colon still
has to be inserted, while trailing colons should be omitted:

::
   
  package {distro:release:tag1,tag2,tag3}

  package {distro}         - good
  package {distro:release} - good
  package {distro::}       - trailing colons unnecessary
  package {distro:release:}
  
  package {distro::tag1}   - double colons needed when release -
  package {::tag1,tag2}    - or distro and release are omitted
  
  package {tag1,tag2}      - bad! won't work (tags are interpreted as distro)
  
A line can contain one, or several packages separated by comma ``,``; packages
on the same line are alternatives for one package, and deborg will only *return
one* package per line (the most exact fit for the specified distro that has no
release conflict, also see **FILTERING BEHAVIOUR**).  A package line should have
the following format:

::
   
  -|+ package1 {<spec>}, package2 {<spec>}, ...

FILTERING BEHAVIOUR
===================

When **deborg** parses a file, the packages will be filtered according to the
provided *distro*, *release* and *tags* arguments. A package without any
specification in curly braces ``{<spec>}`` would be returned for any setting. When
*distro*, or *distro*:\ *release*, are specified in the file, these
packages will only be returned when the exact *distro* (and *release*) are
provided as arguments:

::
   
  (file)
  + package1
  + package2, package2a {distro_a}, package2x {distro_a, release_x}
  + package3a {distro_a}, package3x {distro_a:release_x}
  + package4x {distro_a:release_x}

  (commands and output)
  deborg file 'distro_any' 'release_any'
  > package1 package2

  deborg file 'distro_a' 'release_any'
  > package1 package2a package3a

  deborg file 'distro_a' 'release_x'
  > package1 package2x package3x package4x

For *tags* the behaviour is similar, but when several tags are attached to
a certain package, specifying one of them as argument is enough to include the
package in the returned output:

::
   
  (file)
  + package1a {::tag1}, package1b {::tag2,tag3}
  + package2 {::tag3}
  + package3 {::tag4}

  (commands and output)
  deborg file '' ''
  >                (no output)

  deborg file '' '' --tags=tag1
  > package1a

  deborg file '' '' --tags=tag2
  > package1b

  deborg file '' '' --tags=tag3
  > package1b package2

  deborg file '' '' --tags=tag2,tag4
  > package1b package3

NOTES
=====

For easier integration into scripts, it is advisable to use the exact strings
returned by a tool like **lsb_release** for *distro* and *release*:

::
   
  distro: lsb_release --short --id
  release: lsb_release --short --release

So that extraction of packages can be performed with:

::
   
  deborg packages.org $(lsb_release --short --id) $(lsb_release --short --release)

EXAMPLES
========

Using the example file ``deborg --example-file > examples.org``:

::
   
  $ deborg examples.org '' ''
  $ package foo foo-two baz thunderbird

  $ deborg examples.org 'distro1' ''
  $ package1 foo foo-two baz-alternative thunderbird

  $ deborg examples.org 'distro2' 'release_b'
  $ package2b foo foo-two baz thunderbird

  $ deborg examples.org '' '' --tags=server
  $ package foo foo-two baz apache thunderbird

  $ deborg examples.org 'distro1' '' --tags=desktop
  $ package1 foo foo-two baz-alternative office-app-x thunderbird

  $ deborg examples.org 'distro1' '' --tags=desktop,server
  $ package1 foo foo-two baz-alternative apache office-app-x thunderbird

  $ deborg examples.org 'Debian' ''
  $ package foo foo-two baz thunderbird thunderbird-l10n-xx thunderbird-l10n-zz

  $ deborg examples.org 'Ubuntu' ''
  $ package foo foo-two baz thunderbird thunderbird-locale-xx thunderbird-locale-zz

  $ deborg examples.org 'distro' 'any' --sep='::'
  $ package::foo::foo-two::baz::thunderbird


SEE ALSO
========

| lsb_release(8)
| Emacs orgmode `<https://orgmode.org/>`_.

DISCLAIMER
==========

This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it under the terms
of the GNU General Public License version 3 or later.

BUGS
====

For more information and bug reports please visit `<https://github.com/mtoboid/deborg>`_.
