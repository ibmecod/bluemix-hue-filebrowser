#
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


###################################
# Global variables
###################################
ROOT := $(realpath .)

include $(ROOT)/Makefile.vars.priv


###################################
# Error checking
###################################


.PHONY: default
default:
	@echo 'The build targets for Hue $(DESKTOP_VERSION) are:'
	@echo '  install     : Install at $$PREFIX ($(INSTALL_DIR)); need desktop'
	@echo '  apps        : Build and register all desktop apps; need desktop'
	@echo '  desktop     : Build desktop core only'
	@echo '  clean       : Remove desktop build products'
	@echo '  distclean   : Remove desktop and thirdparty build products'

.PHONY: all
all: default


###################################
# Install parent POM
###################################
parent-pom:
	cd $(ROOT)/maven && mvn install $(MAVEN_OPTIONS)

.PHONY: parent-pom

###################################
# virtual-env
###################################
virtual-env: $(BLD_DIR_ENV)/stamp
$(BLD_DIR_ENV)/stamp:
	@echo "--- Creating virtual environment at $(BLD_DIR_ENV)"
	$(SYS_PYTHON) $(VIRTUAL_BOOTSTRAP) \
		$(VIRTUALENV_OPTS) --system-site-packages $(BLD_DIR_ENV)
	@touch $@
	@echo "--- $(BLD_DIR_ENV) ready"

.PHONY: virtual-env

###################################
# Build desktop
###################################
.PHONY: desktop

desktop: virtual-env
	@$(MAKE) -C desktop

###################################
# Build apps
###################################
.PHONY: apps
apps: desktop
	@$(MAKE) -C $(APPS_DIR) env-install

###################################
# Install binary dist
###################################
INSTALL_CORE_FILES = \
	Makefile* $(wildcard *.mk) \
	ext \
	tools/app_reg \
	tools/virtual-bootstrap \
	tools/relocatable.sh \
	VERS* LICENSE* README*

.PHONY: install
install: virtual-env install-check install-core-structure install-desktop install-apps install-env

.PHONY: install-check
install-check:
	@if [ -n '$(wildcard $(INSTALL_DIR)/*)' ] ; then \
	  echo 'ERROR: $(INSTALL_DIR) not empty. Cowardly refusing to continue.' ; \
	  false ; \
	fi

.PHONY: install-core-structure
install-core-structure:
	@echo --- Installing core source structure...
	@mkdir -p $(INSTALL_DIR)
	@tar cf - $(INSTALL_CORE_FILES) | tar -C $(INSTALL_DIR) -xf -
	@# Add some variables to Makefile to make sure that our virtualenv
	@# in the install root is the same one we built from - this also
	@# disables the check for python-devel packages which are no longer
	@# needed
	@echo "SYS_PYTHON=$(ENV_PYTHON_VERSION)" > $(INSTALL_DIR)/Makefile.buildvars
	@echo "SKIP_PYTHONDEV_CHECK=1" >> $(INSTALL_DIR)/Makefile.buildvars

.PHONY: install-desktop
install-desktop:
	@echo --- Installing Desktop core...
	INSTALL_DIR=$(realpath $(INSTALL_DIR)) $(MAKE) -C desktop install

.PHONY: install-apps
install-apps:
	@echo '--- Installing Applications...'
	INSTALL_DIR=$(realpath $(INSTALL_DIR)) $(MAKE) -C apps install

.PHONY: install-env
install-env:
	@echo --- Creating new virtual environment
	$(MAKE) -C $(INSTALL_DIR) virtual-env
	@echo --- Setting up Desktop core
	$(MAKE) -C $(INSTALL_DIR)/desktop env-install
	@echo --- Setting up Applications
	$(MAKE) -C $(INSTALL_DIR)/apps env-install
	@echo --- Setting up Desktop database
	$(MAKE) -C $(INSTALL_DIR)/desktop syncdb

###################################
# Internationalization
###################################



###################################
# Cleanup
###################################

.PHONY: clean
clean:
	@$(MAKE) -C desktop clean
	@$(MAKE) -C apps clean
	@rm -rf $(BLD_DIR_ENV)
	@rm -rf $(STATIC_DIR)

#
# Note: It is important for clean targets to *ONLY* clean products of the
#       build, and not misc runtime generated files. Don't abuse Makefile.
#
.PHONY: distclean
distclean: clean
	@# Remove the other directories in build/
	@$(MAKE) -C desktop distclean
	@$(MAKE) -C apps distclean
	@rm -rf $(BLD_DIR)

.PHONY: ext-clean
ext-clean:
	@$(MAKE) -C desktop ext-clean
	@$(MAKE) -C apps ext-clean

