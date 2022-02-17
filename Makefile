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
SHELL = /usr/bin/sh
PROJECT_DIR := $(realpath .)


# source files
DIST_DIR = $(PROJECT_DIR)/dist
TARBALL = $(DIST_DIR)/deborg-$(VERSION).tar.gz
DEB_TARBALL = $(DIST_DIR)/deborg_$(VERSION).orig.tar.gz

# python
PYTHON = /usr/bin/python3
VENV_DIR = $(PROJECT_DIR)/venv
VENV_ACTIVATE = $(VENV_DIR)/bin/activate
REQUIREMENTS = $(PROJECT_DIR)/requirements.txt

# git-buildpackage
GBP = gbp
GBP_BUILD = $(GBP) buildpackage
GBP_BUILD_DIR = $(PROJECT_DIR)/$$($(GBP) config buildpackage.export-dir | sed 's|^./||')

# destination
PACKAGE_DIR = $(DIST_DIR)/Debian


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

# Build the python package
.PHONY: python_package
python_package: $(VENV_ACTIVATE)
	@echo "Building the python package."
	$(SHELL) -c '. $(VENV_ACTIVATE); python3 -m build --outdir $(DIST_DIR)'

# Setup a Python virtual environment
$(VENV_ACTIVATE):
	$(PYTHON) -m venv $(VENV_DIR)
	$(PYTHON) -m pip install -r $(REQUIREMENTS)
	@echo "Finished setting up the python virtual environment."

# only allow with set VERSION variable.
ifdef VERSION
# Build a debian package
.PHONY: deb_package
deb_package: $(DEB_TARBALL)
	@echo "Building Debian package with VERSION = $(VERSION)"
	cd $(PROJECT_DIR) && $(GBP_BUILD)
	mv $(GBP_BUILD_DIR) $(PACKAGE_DIR)


# Create the tarball named as debian packaging tools expect it.
$(DEB_TARBALL): $(TARBALL)
	cp $< $@
else
.PHONY: deb_package
deb_package:
	@echo "VERSION is undefined, see 'make usage'"

# VERSION defined block
endif

# CLEANING
.PHONY: clean
clean: clean_all

.PHONY: clean_all
clean_all: clean_deb_packaging clean_python_build clean_python_venv

# Remove files created for debian package build process
.PHONY: clean_deb_packaging
clean_deb_packaging:
	@if [ -e $(DEB_TARBALL) ]; then rm $(DEB_TARBALL); fi

# Remove virtual environment
.PHONY: clean_python_venv
clean_python_venv:
	@if [ -e $(VENV_DIR) ]; then rm -rf $(VENV_DIR); fi

# Remove files created for python package build process
.PHONY: clean_python_build
clean_python_build:
	@if [ -e $(DIST_DIR) ]; then rm -rf $(DIST_DIR); fi


.PHONY: all
all: test

.PHONY: test
test:
	@:$(call ensure_var_VERSION_defined)
	@echo "DIST_DIR = $(DIST_DIR)"
	@echo "tarball = $(DIST_DIR)/deborg-$(VERSION).tar.gz"
	@echo "GBP_BUILD_DIR = $(GBP_BUILD_DIR)"
	@echo "PACKAGE_DIR = $(PACKAGE_DIR)"

