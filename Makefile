.PHONY: build check lint test verify

override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PYTHON ?= python3

lint:
	$(PYTHON) "$(ROOT)/scripts/check_repository_contracts.py"

test: lint
	$(PYTHON) -m unittest discover -v -s "$(ROOT)/tests" -p "test_*.py"
	$(PYTHON) "$(ROOT)/scripts/test_greetings_runtime.py"

build: lint

verify: lint test build

check: verify
