# Plan Discoverability

## Status: Completed

## Context

The placeholder repository already keeps completed maintenance plans under
`docs/plans` and verifies they are completed. The README mentioned the plan
directory generally, but did not link the concrete baseline and secret-hygiene
plans from Maintenance Notes.

## Objectives

- Preserve the sparse placeholder scope.
- Make the completed baseline and secret-hygiene plans easy to find.
- Add static coverage so README plan links do not drift.
- Avoid changing GitHub workflow files in this pass.

## Work Completed

- Linked the canonical placeholder baseline plan from README Maintenance Notes.
- Linked the secret-hygiene plan from README Maintenance Notes.
- Extended `scripts/check_repository_contracts.py` to require both links.
- Updated VISION and CHANGES.

## Verification

- `python3 scripts/check_repository_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add a safe `.env.example` when a real mock or sandbox test harness exists.
- Archive the repository if it is no longer needed.
