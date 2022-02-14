#!/usr/bin/make
#
# Makefile to build debian packages for deborg
#
#    Copyright (C) 2022 Tobias Marczewski
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#
SHELL = /bin/sh

# git-buildpackage command
GBP = gbp buildpackage --git-ignore-new

DIST_DIR = $(realpath ../dist)
TARBALL = $(DIST_DIR)/deborg-$(VERSION).tar.gz
DEB_TARBALL = $(DIST_DIR)/deborg_$(VERSION).orig.tar.gz

# only allow usage when VERSION is unset
.PHONY: usage
usage:
	@echo "Usage: make <ACTION> VERSION='<version>'"
	@echo ""
	@echo "Variable VERSION has to be set for actions other than 'usage'."
	@echo "If you didn't expect to see this, perhaps you forgot to set VERSION."
	@echo "For the build to work also a tarball with the right version has to be in"
	@echo "$(DIST_DIR)/deborg-<VERSION>.tar.gz"
	@echo ""
	@echo "ACTIONS:"
	@echo "usage       - display this information"
	@echo "deb_package - build a debian package for the specified VERSION."
	@echo "              The version in debian/changelog, and dist have to match!"
	@echo ""

# ensure the variable VERSION has been set
ifndef VERSION
# VERSION NOT set (always display usage)
.PHONY: *
*: usage

# VERSION has been SET
else

.PHONY: all
all: test

.PHONY: test
test: $(DEB_TARBALL)
	@echo "DIST_DIR = $(DIST_DIR)"
	@echo "tarball = $(DIST_DIR)/deborg-$(VERSION).tar.gz"


# Build a debian package
.PHONY: deb_package
deb_package: $(DEB_TARBALL)
	@echo "Building Debian package with VERSION = $(VERSION)"
	cd .. && $(GBP)


# Create the tarball named as debian packaging tools expect it.
$(DEB_TARBALL): $(TARBALL)
	cp $< $@

# Remove files created for build process
.PHONY: clean
clean:
	[ -e $(DEB_TARBALL) ] && rm $(DEB_TARBALL)

# VERSION set condition
endif

