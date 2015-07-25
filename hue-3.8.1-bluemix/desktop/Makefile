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

export ROOT := $(realpath ..)
DESKTOP_ROOT := $(realpath .)
include $(ROOT)/Makefile.vars.priv

APPS := core \
	libs/hadoop \
	libs/indexer \
	libs/liboauth \
	libs/liboozie \
	libs/libopenid \
	libs/librdbms \
	libs/libsaml \
	libs/libsentry \
	libs/libsolr \
	libs/libzookeeper

.PHONY: default
default:: hue syncdb

###################################
# Configuration
###################################



###################################
# Build apps
###################################


.PHONY: syncdb
syncdb: $(DESKTOP_DB)

$(DESKTOP_DB): $(BLD_DIR_BIN)/hue
	@echo "--- Regenerating database at $@"
	@if [ -n "$(DESKTOP_DEBUG)" ]; then \
	  echo 'Removing old database (DESKTOP_DEBUG is set)' ; \
	  rm -f $@ ; \
	fi
	@echo "--- Syncing/updating database at $@"
	@$(ENV_PYTHON) $(BLD_DIR_BIN)/hue syncdb --noinput
	@$(ENV_PYTHON) $(BLD_DIR_BIN)/hue migrate --merge

# Targets that simply recurse into all of the applications
ENV_INSTALL_TARGETS := $(APPS:%=.recursive-env-install/%)
.recursive-env-install/%: %
	$(MAKE) -C $< env-install

CLEAN_TARGETS := $(APPS:%=.recursive-clean/%)
.recursive-clean/%: %
	$(MAKE) -C $< clean

DISTCLEAN_TARGETS := $(APPS:%=.recursive-distclean/%)
.recursive-distclean/%: %
	$(MAKE) -C $< distclean

EXT_CLEAN_TARGETS := $(APPS:%=.recursive-ext-clean/%)
.recursive-ext-clean/%: %
	$(MAKE) -C $< ext-clean

.PHONY: env-install
env-install: $(ENV_INSTALL_TARGETS)

.PHONY: clean
clean: $(CLEAN_TARGETS)
	@rm -f $(BLD_DIR)/.devtools

.PHONY: distclean
distclean: clean $(DISTCLEAN_TARGETS)

.PHONY: ext-clean
ext-clean: $(EXT_CLEAN_TARGETS)


#
# hue target
#
.PHONY: hue
hue: env-install
	@# Make symlink for backward compatibility
	@ln -sf hue $(BLD_DIR_BIN)/desktop


###################################
# Distribution
###################################

INSTALL_BDIST_TARGETS := $(APPS:%=.recursive-install-bdist/%)
.recursive-install-bdist/%: %
	INSTALL_DIR=$(INSTALL_DIR)/desktop/$< \
		INSTALL_CONF_DIR=$(INSTALL_DIR)/desktop/conf \
		$(MAKE) -C $< install-bdist

.PHONY: install
install: install-source-parts $(INSTALL_BDIST_TARGETS)

#
# install-source-parts:
#     Installs the non-app parts (eg makefiles, conf) into
#     the INSTALL_DIR
#
# We should move all of the libs/* into some kind of container
# python app, or into core.
# TODO(todd) deal with these JS dependencies
#
SOURCE_PARTS = \
  $(wildcard *.mk) Makefile \
  conf

.PHONY: install-source-parts
install-source-parts:
	@mkdir -p $(INSTALL_DIR)/desktop
	@tar cf - $(SOURCE_PARTS) | tar -C $(INSTALL_DIR)/desktop -xf -
	@# Remove the application configuration files
	@find $(INSTALL_DIR)/desktop/conf -type l -exec rm {} \;

	
