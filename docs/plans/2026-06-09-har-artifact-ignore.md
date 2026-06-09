# HAR Artifact Ignore

## Status: Completed

## Context

Future Twilio debugging may involve browser or proxy captures. HAR files can
contain request URLs, auth-adjacent headers, phone numbers, and message payload
details, so they should be treated like local debug logs and kept out of git.

## Objectives

- Ignore local HAR capture artifacts.
- Keep the ignore rule covered by `make check`.
- Preserve the sparse placeholder repository scope.
- Document the completed safety guard under `docs/plans`.

## Work Completed

- Added `*.har` to `.gitignore`.
- Extended `scripts/check_repository_contracts.py` to require the HAR ignore
  pattern.
- Made this completed plan required by the repository contract checker.
- Updated README, VISION, and CHANGES.

## Verification

- Negative check before implementation:
  `make check` failed with `.gitignore must include *.har`.
- `python3 scripts/check_repository_contracts.py`
- `make check`
- `git diff --check`

## Follow-Up Candidates

- Choose a deterministic mock or sandbox test strategy.
- Add runtime examples only after placeholder safety checks remain enforced.
