# Empty Environment Placeholders

## Status: Completed

## Context

`.env.example` documents future Twilio configuration names, but sensitive
entries should stay empty in git. Presence checks alone would still allow a
sample account SID, auth token, phone number, or message body to be committed
after the key name. The placeholder contract should assert the empty-value
shape directly.

## Objectives

- Require Twilio credential placeholders to remain empty.
- Require sender, recipient, and message body placeholders to remain empty.
- Preserve the existing `info` log-level default and disabled live-send flag.
- Extend `make check` to enforce the empty-placeholder shape.
- Document the completed guard under `docs/plans`.

## Work Completed

- Added empty-value regex checks for sensitive `.env.example` entries.
- Required this plan in the repository contract checker.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_repository_contracts.py`
- `make check`
- `git diff --check`

## Follow-Up Candidates

- Choose a deterministic mock or sandbox test strategy.
- Add runtime examples only after the placeholder safety contract remains
  enforced.
