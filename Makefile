.PHONY: build check lint test verify

PYTHON ?= python3

lint:
	$(PYTHON) scripts/check_repository_contracts.py

test: lint

build: lint

verify: lint test build

check: verify
