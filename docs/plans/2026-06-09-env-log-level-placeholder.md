# Environment Log-Level Placeholder

## Status: Completed

## Context

This repository does not yet define a Twilio runtime, but future experiments
will likely need a logging knob. The placeholder environment template should
default logging to `info` and make debug logging an explicit local choice after
redaction review.

## Objectives

- Preserve the sparse placeholder repository scope.
- Keep `.env.example` free of credentials, phone numbers, and account data.
- Add a default log-level placeholder without enabling verbose debug output.
- Extend static checks so the placeholder and guidance remain present.

## Work Completed

- Added `TWILIO_LOG_LEVEL=info` to `.env.example`.
- Added guidance that debug should only be used locally after redaction review.
- Extended `scripts/check_repository_contracts.py` to require the placeholder
  and guidance.
- Updated README, VISION, and CHANGES.

## Verification

- Negative check before implementation:
  `python3 scripts/check_repository_contracts.py` failed with
  `.env.example must document TWILIO_LOG_LEVEL=info`.
- `python3 scripts/check_repository_contracts.py`
- `make check`
- `make verify`
- `git diff --check`
