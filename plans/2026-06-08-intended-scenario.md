# Intended Scenario Gate

## Problem

The repository described itself as a placeholder but did not define the Twilio
test scenario future code should implement. That left too much room for a first
implementation to jump straight to live-account behavior.

## TDD Evidence

1. Extended `scripts/check_repository_contracts.py` to require an intended test
   scenario in the README.
2. Ran `make lint` before updating the README and confirmed the new check
   failed on the missing section.
3. Added mock/sandbox-first and live-opt-in scenario wording, then reran the
   full verification gate.

## Verification

- `make lint`
- `make test`
- `make build`
- `make verify`
- `make check`
- `git diff --check`
