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


# source file directory
DIST_DIR = $(PROJECT_DIR)/dist
# normal tarball produced during python package build
TARBALL = $(wildcard $(DIST_DIR)/deborg-*.tar.gz)
# tarball format expected by Debian build tools
DEB_TARBALL = $(patsubst $(DIST_DIR)/deborg-%.tar.gz,deborg_%.orig.tar.gz,$(TARBALL))
# obtain the version of the tarball (e.g. 'deborg-1.0.0.tar.gz' -> '1.0.0')
VERSION = $(patsubst $(DIST_DIR)/deborg-%.tar.gz,%,$(TARBALL))


TESTING = "XXX XXX"

# python
PYTHON = /usr/bin/python3
VENV_DIR = $(PROJECT_DIR)/venv
VENV_ACTIVATE = $(VENV_DIR)/bin/activate
VENV_REQUIREMENTS = $(PROJECT_DIR)/requirements.txt

# execute a command within the python virtual environment
define execute_in_venv
	$(SHELL) -c '. $(VENV_ACTIVATE); $(1)'
endef

# git-buildpackage
GBP = gbp
GBP_BUILD = $(GBP) buildpackage
GBP_BUILD_DIR = $(PROJECT_DIR)/$$($(GBP) config buildpackage.export-dir | sed 's|^./||')

# destination
PACKAGE_DIR = $(DIST_DIR)/Debian


####################################################################################################

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


### Python Package ###

# Wrapper to test venv setup
.PHONY: venv
venv: $(VENV_DIR)

# Setup a Python virtual environment and install requirements
$(VENV_DIR): $(VENV_REQUIREMENTS)
	$(PYTHON) -m venv $(VENV_DIR)
	$(call execute_in_venv,\
		pip install --upgrade pip;\
		pip install -r $(VENV_REQUIREMENTS))
	@rm -rf build  # remove the build folder that gets created
	@echo "Finished setting up the python virtual environment."

# Build the python package
.PHONY: build_python_package
build_python_package: $(VENV_DIR)
	$(call execute_in_venv,\
		python3 -m build --outdir $(DIST_DIR))
	@echo "Finished building the python package."

# The original tarball is produced during the build
$(TARBALL): build_python_package

## CLEAN (python)
# Remove virtual environment
.PHONY: clean_venv
clean_venv:
	@if [ -e $(VENV_DIR) ]; then rm -rf $(VENV_DIR); fi

# Remove files created for python package build process
.PHONY: clean_python_build
clean_python_build:
	@if [ -e $(DIST_DIR) ]; then\
		rm $(DIST_DIR)/*.tar.gz;\
		rm $(DIST_DIR)/*.whl;\
		rmdir $(DIST_DIR);fi

.PHONY: clean_all_python
clean_all_python: clean_python_build clean_venv




### Debian Package ###

# Create a tarball named as debian packaging tools expect it.
$(DEB_TARBALL): $(TARBALL)
	cp $< $@

# Build a debian package
.PHONY: deb_package
deb_package: $(DEB_TARBALL)
	@echo "Building Debian package with VERSION = $(VERSION)"
	cd $(PROJECT_DIR) && $(GBP_BUILD)
	mv $(GBP_BUILD_DIR) $(PACKAGE_DIR)
	rm $(DEB_TARBALL)



# CLEANING
.PHONY: clean
clean: clean_all

.PHONY: clean_all
clean_all: clean_deb_packaging clean_python_build clean_python_venv

# Remove files created for debian package build process
.PHONY: clean_deb_packaging
clean_deb_packaging:
	@if [ -e $(DEB_TARBALL) ]; then rm $(DEB_TARBALL); fi
	@if [ -e $(GBP_BUILD_DIR) ]; then rm -rf $(GBP_BUILD_DIR); fi
	@if [ -e $(PACKAGE_DIR) ]; then rm -rf $(PACKAGE_DIR); fi



.PHONY: all
all: test


.PHONY: test
test:
	@echo "DIST_DIR = $(DIST_DIR)"
	@echo "TARBALL = $(TARBALL)"
	@echo "VERSION = $(VERSION)"
	@echo "GBP_BUILD_DIR = $(GBP_BUILD_DIR)"
	@echo "PACKAGE_DIR = $(PACKAGE_DIR)"
	@echo "TESTING = $(TESTING)"

