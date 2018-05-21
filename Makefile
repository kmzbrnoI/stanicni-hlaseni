ROOT_DIR = $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
SERVICE_PATH = "/lib/systemd/system/sh.service"

all:
	$(error "There are no targets except 'install'!")

install:
	sed 's|$$WORKDIR|$(ROOT_DIR)|g' report.service.template > $(SERVICE_PATH)

uninstall:
	rm $(SERVICE_PATH)

.PHONY: install uninstall all
