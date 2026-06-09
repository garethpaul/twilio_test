# Environment Example Guidance

## Status: Completed

## Context

The repository now includes a safe `.env.example` with empty Twilio placeholders
and live sends disabled. The template documented the variable names, but each
entry lacked inline guidance about why values must remain empty in git and what
future local experiments may fill.

## Objectives

- Keep `.env.example` placeholder-only.
- Add concise comments for credentials, phone placeholders, message body, and
  live-send opt-in.
- Preserve live sends disabled by default.
- Extend static checks so the guidance does not drift.

## Work Completed

- Added per-variable comments to `.env.example`.
- Kept all credential, phone, and message placeholders empty.
- Extended `scripts/check_repository_contracts.py` to require the comments.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_repository_contracts.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Choose a concrete mock or sandbox implementation strategy before adding
  executable Twilio code.
- Archive the repository if no Twilio smoke test is needed.
