.PHONY: lint test build verify

PYTHON ?= python3

lint:
	$(PYTHON) scripts/check_repository_contracts.py

test: lint

build: lint

verify: lint test build
