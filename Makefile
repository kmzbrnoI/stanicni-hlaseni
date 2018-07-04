ROOT_DIR = $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
SERVICE_PATH = "/lib/systemd/system/sh.service"

all: global_config.ini

install:
	sed 's|$$WORKDIR|$(ROOT_DIR)|g' report.service.template > $(SERVICE_PATH)

uninstall:
	rm $(SERVICE_PATH)

global_config.ini: global_config.template
	cat global_config.template > global_config.ini

.PHONY: install uninstall all
