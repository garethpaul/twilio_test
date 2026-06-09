# Secret Hygiene

## Status: Completed

## Context

The repository is still a placeholder for future Twilio tests, but future work
will likely use local credentials, account identifiers, phone numbers, and debug
logs. Without ignore rules, those files would be easy to stage accidentally.

## Objectives

- Preserve the sparse placeholder state.
- Ignore local `.env` files while still allowing a future `.env.example`.
- Ignore local debug logs.
- Extend static checks so credential/log ignore patterns stay present.

## Work Completed

- Added root `.gitignore` patterns for `.env`, `.env.*`, `.env.example`
  exemption, and log files.
- Extended `scripts/check_repository_contracts.py` with secret-hygiene checks.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_repository_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add a safe `.env.example` when a real mock or sandbox test harness exists.
- Archive the repository if it is no longer needed.
