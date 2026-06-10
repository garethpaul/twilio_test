.PHONY: build check lint test verify

ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PYTHON ?= python3

lint:
	$(PYTHON) "$(ROOT)/scripts/check_repository_contracts.py"

test: lint

build: lint

verify: lint test build

check: verify
