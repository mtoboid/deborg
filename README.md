# deborg

**deborg** is a small utility script to extract .`deb` packages from an emacs
`org`mode file.

When setting up a new machine, one big task is to get all the functionality back
that one relied on for productivity on the old system, which also entails
installing the same packages. Furthermore, when using several computers with
slightly different setup requirements (one Debian, one Ubunt, another a netbook
which can't handle everything), this can become time consuming.

To be able to get a newly installed system into the state I want it in, I
started documenting all packages that I install on top of the default: for which
purpose I need them; if there where any quirks, and whatever notes might be
useful. For this I use a simple [orgmode][orgmode] file in which every section
refers to a task / functionality and a list in which all the packages needed for
this functionality are mentioned.

**deborg** can then be used to easily extract all packages for a system based on
distro and release as an array, which can then be passed to e.g. apt to do all
the work.

```
orgfile="my_package_file.org"
distro=$(lsb_release --short --id)
release=$(lsb_release --short --release)

packages_to_install=($(deborg "$orgfile" "$distro" "$release"))
apt install "${packages_to_install[@]}"
```

Done! New system has all specified packages installed (if they are available).


## Installation


## Expected org file input

The orgmode file can be written as a normal file with sections, subsections,
markup (~code~, =verbatim=, ...), and text (only tables may be a problem).

However, each list entry (only entries using `+` or `-` as bullets) will be
considered to contain information about packages. Each package line can contain
any number of comma separated *alternatives* - this means, from each line (=
list entry) at maximum one package will be returned. The choice here is from
most-specific-fit to least-specific-fit with regards to distro and release: If
an exact fit (distro & release) is found, this will be returned, otherwise if a
package is defined that has no release specified and matches the specified
distro, this will be returned, lastly if the line contains a package without any
further specification, this will be returned (a package will never be returned
if distro or release mis-match). Examples:

---

* `+ package` - 
  install package for all distros and all releases
* `+ package {Debian}` -
  install package *only* if distro=Debian
* `+ package1, package2 {Ubuntu}` -
  install package1 for *all* distros, **unless** distro=Ubuntu, then *don't*
  install package1 but package2 *instead*
* `+ package1 {Debian}, package2 {Ubuntu:18.04}` -
  install package1 for Debian, and *only for Ubuntu 18.04* install *package2*; for
  other releases of Ubuntu *no* package will be installed (returned by parsing
  the orgfile)

---

Example of a valid orgfile:


```
# File listing all packages that should be installed on a linux system
#+LANGUAGE: en
#+TITLE: Linux Packages

* Emacs
  These are some packages needed for the emacs config to work, and yes, comments
  like this one are perfectly ok, as are links as seen below.

** elpy ([[https://github.com/jorgenschaefer/elpy][github]])
   + python3-jedi
   + black
   + python3-autopep8
   + yapf3
   + python3-yapf
   + virtualenv

* Email
  + thunderbird
    
** Languages
  + thunderbird-l10n-en-gb {Debian}, thunderbird-locale-en-gb {Ubuntu} :: british english
  + thunderbird-l10n-de {Debian}, thunderbird-locale-de {Ubuntu} :: german
  + packagex-here :: this type of comment is ok
  
** Other
  Not sure about these packages, but want to keep them here for now, even if
  not installing them by commenting them out.
  # + package_not_returned :: as the line does not start with either - or +
  
```


## Output

**deborg** returns all extracted packages as a string separated by the specified
**sep**arator which defaults to space `' '`.

## Examples / Usage

Input orgmode file:
```
# this is the input file for the example (example.org)
* Some packages
  - package1
  - package2a {Debian}, package2b {Debian:11}, package2c {Ubuntu}
  - package3 {Debian}
  - package4 {Debian}, package4 {Ubuntu:20.04}
```

Output:
```
# Normally use lsb_release in a script to obtain 'distro' and 'release'
# we just set it here explicitly for clarity

# 1) on a Debian 10 system
deborg example.org "Debian" "10"
"package1 package2a package3 package4"

# 2) on a Debian 11 system
deborg example.org "Debian" "11"
"package1 package2b package3 package4"

# 3) on a Ubuntu 18.04 system
deborg example.org "Ubuntu" "18.04"
"package1 package2c"

# 4) on a Ubuntu 20.04 system
deborg example.org "Ubuntu" "20.04"
"package1 package2c package4"

# 5) setting sep
deborg example.org "Debian" "9" --sep=":::"
"package1:::package2a:::package3:::package4"
```

## License
**deborg** is released under the [MIT License][MIT spdx].


[orgmode]: https://orgmode.org/
[MIT spdx]: https://spdx.org/licenses/MIT.html
