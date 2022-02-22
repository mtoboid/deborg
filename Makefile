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
PROJECT_DIR := $(realpath .)

# use the version from the setup config file
VERSION = $(shell sed -E -n 's/^version *= *([0-9\.]+)/\1/p' $(PROJECT_DIR)/setup.cfg)

# source file directory
DIST_DIR = $(PROJECT_DIR)/dist
# normal tarball produced during python package build
TARBALL = $(DIST_DIR)/deborg-$(VERSION).tar.gz
# tarball format expected by Debian build tools
DEB_TARBALL = $(DIST_DIR)/deborg_$(VERSION).orig.tar.gz

# git tags
VERSION_TAG = v$(VERSION)

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

# ensure git-buildpackage is actually installed
GBP_AVAILABLE := $(shell type $(GBP) >/dev/null 2>&1; echo "$$?")
ifneq ($(GBP_AVAILABLE),0)
$(error "gbp (git-buildpackage) is not available")
endif

# default build command for git-buildpackage
GBP_BUILD = $(GBP) buildpackage --git-ignore-new

# build directory (from settings file)
GBP_BUILD_DIR_BASE := $(shell $(GBP) config buildpackage.export-dir | sed 's|^.*=||')
# ensure a build directory is set
# (otherwise GBP_BUILD_DIR points to the project root!)
ifeq ($(GBP_BUILD_DIR_BASE),)
$(error "Build directory for gbp (GBP_BUILD_DIR_BASE) is not set!")
endif

GBP_BUILD_DIR := $(abspath $(GBP_BUILD_DIR_BASE))

# destination for debian package
PACKAGE_DIR := $(DIST_DIR)/Debian


define USAGE

    Usage: make <TARGET>

    TARGETS

      *General Targets*

      usage                     Display this information.

      version                   Display the version of the package as determined
                                by the Makefile.

      all                       Build a Python- and a Debian-package.

      clean                     Remove all files and folders created by the calls in
                                this Makefile. (Does not remove the git tag if one
                                was created!)

      *Specific Targets*

      python_venv               Set-up a python virtual environment according to the
                                requirements.txt

      build_python_package      Build the Python package and wheel.

      clean_python_venv         Remove the virtual environment.

      clean_python_build        Remove folders and files created for Python packaging

      clean_python_all          clean_python_build & clean_python_venv

      git_version_tag           Create a git tag for the corresponding version if none
                                exists.

      deb_tarball               Copy the original tarball and rename it according to
                                debian standard.

      deb_package               Make a .deb package.

      clean_deb_tarball         Remove the debian tarball.

      clean_deb_packaging       Remove all files and folders created to produce the
                                .deb package (including the package itself).

      clean_all_deb_packaging   clean_deb_tarball & clean_deb_packaging

endef
export USAGE
####################################################################################################

# only allow usage when VERSION is unset
.PHONY: usage
usage:
	@echo "$$USAGE"

# display the version determined by the Makefile
.PHONY: version
version:
	@echo "Package version: $(VERSION)"

### General targets ###
.PHONY: all
all: deb_package

# CLEANING
.PHONY: clean
clean: clean_all

.PHONY: clean_all
clean_all: clean_all_deb_packaging clean_all_python


### Python Package ###

# Wrapper to test venv setup
.PHONY: python_venv
python_venv: $(VENV_DIR)

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
	@if [ ! -e "$(TARBALL)" ]; then\
		$(call execute_in_venv,\
		python3 -m build --outdir $(DIST_DIR));\
		echo "Finished building the python package.";\
	fi

# The original tarball is produced during the build
$(TARBALL): build_python_package

## CLEAN (python)
# Remove virtual environment
.PHONY: clean_python_venv
clean_python_venv:
ifeq ($(VENV_DIR),)
	@echo "WARNING! Trying to run clean while VENV_DIR is not set!"
else
	@if [ -e $(VENV_DIR) ]; then rm -rf $(VENV_DIR); fi
endif

# Remove files created for python package build process
.PHONY: clean_python_build
clean_python_build:
	@if [ -e $(DIST_DIR) ]; then\
		rm $(DIST_DIR)/*.tar.gz;\
		rm $(DIST_DIR)/*.whl;\
		rmdir $(DIST_DIR);fi

.PHONY: clean_all_python
clean_all_python: clean_python_build clean_python_venv


### Debian Package ###

# git version tag (for git-buildpackage)
# check if a tag for the current version already exists,
# if not, create one.
# TODO: add dependency 'version'!
.PHONY: git_version_tag
git_version_tag:
	@if git rev-parse $(VERSION_TAG) >/dev/null 2>&1; then\
		echo "Tag $(VERSION_TAG) exists.";\
	else\
		git tag -a $(VERSION_TAG)\
		-m "Tag automatically created by Makefile (git_version_tag)";\
		echo "Created git tag $(VERSION_TAG) for HEAD.";\
	fi

# Create a tarball named as debian packaging tools expect it.
$(DEB_TARBALL): $(TARBALL)
	cp $< $@

# wrapper for the debian specific tarball
.PHONY: deb_tarball
deb_tarball: $(DEB_TARBALL)
	@echo "Created deb tarball: $(DEB_TARBALL)."

# Build a debian package
.PHONY: deb_package
deb_package: $(DEB_TARBALL) git_version_tag | clean_deb_packaging
	@cd $(PROJECT_DIR) && $(GBP_BUILD)
	@mv $(GBP_BUILD_DIR) $(PACKAGE_DIR)
	@echo "Finished building Debian package for version = $(VERSION)"
	@echo "Files were placed in $(PACKAGE_DIR)."

# CLEAN (deb packaging)
.PHONY: clean_deb_tarball
clean_deb_tarball:
	@if [ -e $(DEB_TARBALL) ]; then rm $(DEB_TARBALL); fi

.PHONY: clean_deb_packaging
clean_deb_packaging:
ifeq ($(GBP_BUILD_DIR),)
	@echo "WARNING! Trying to run clean while GBP_BUILD_DIR is not set!"
else
	@if [ -e $(GBP_BUILD_DIR) ]; then rm -rf $(GBP_BUILD_DIR); fi
endif
ifeq ($(PACKAGE_DIR),)
	@echo "WARNING! Trying to run clean while PACKAGE_DIR is not set!"
else 
	@if [ -e $(PACKAGE_DIR) ]; then rm -rf $(PACKAGE_DIR); fi
endif


.PHONY: clean_all_deb_packaging
clean_all_deb_packaging: clean_deb_packaging clean_deb_tarball

