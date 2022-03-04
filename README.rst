======
deborg
======

-------------------------------------------------------------
Extract Debian package information from an Emacs orgmode file
-------------------------------------------------------------


About
=====

**deborg** is personal package management made easy. Maintain a list of
packages that you would like installed after a fresh OS install. Different packages can be
installed depending on system (distro & release) or requirement (tags), and the
list can be maintained as part of a well structured document with headings,
paragraphs of text and comments. Then to install you only need one command to
install them all::
  dpkg -i $(deborg my_packages.org 'Debian' '10' --tags=server)

  
Usage
=====

**deborg** is a python commandline tool to parse an
`Emacs <https://www.gnu.org/software/emacs/>`_
`orgmode <https://orgmode.org/>`_ file containing package specifications in
unordered lists (example.org):

::
   
  + package-foo
  + package-baz, package-baz-alt {Ubuntu}, package-baz-x {Ubuntu:20.04}
  + apache {::server}
  + office-app-a {::desktop}, office-app-b {Debian::desktop}

    
(example output):

::
   
  deborg example.org Debian any_release
  > package-foo package-baz

  deborg example.org Debian any_release --tags=server
  > package-foo package-baz apache

  deborg example.org Debian any_release --tags=desktop
  > package-foo package-baz office-app-b

  deborg example.org Ubuntu any_release
  > package-foo package-baz-alt

  deborg example.org Ubuntu 20.04
  > package-foo package-baz-x
  
  deborg example.org Ubuntu 20.04 --tags=server,desktop
  > package-foo package-baz-x apache office-app-a
  

Pre-requisites
==============

+ Python 3.8 or above


Installation
============

Just install the debian package. As mentioned in the **Pre-requisites** the
default system python3 (/usr/bin/python3) has to be >=3.8 for the package to
install correctly. That means that Debian >11 (bullseye) and Ubuntu from 20.04
(focal) should work.

``dpkg -i python3-deborg.deb``


Building
========

Python Package
--------------
::
   # clone the git repository
   # go into project folder
   cd deborg
   # setup a virtual environment
   python3 -m venv venv
   source venv/bin/activate
   python3 -m pip install --upgrade pip
   python3 -m pip install -r requirements.txt
   # build the package and wheel
   python3 -m build

Debian Package
--------------

Switch the git branch to ``debian/master`` and see the README there.



License
=======

**deborg** is released under the GNU General Public License version 3 or later
`GPL-3+ <https://spdx.org/licenses/GPL-3.0-or-later.html>`_
