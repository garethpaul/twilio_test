# Local Metadata Ignore

## Status: Completed

## Context

The placeholder repository already ignores local environment files, logs, HAR
captures, and Python bytecode. It did not yet ignore common local OS/editor
metadata, which can be accidentally staged while preparing future Twilio test
experiments.

## Objectives

- Ignore common macOS and IDE metadata files.
- Keep the repository placeholder-only and portable.
- Extend the static contract so the ignore rules stay in place.
- Document the guard in the maintenance plans.

## Work Completed

- Added `.DS_Store`, `.idea/`, `.vscode/`, and `*.iml` to `.gitignore`.
- Extended `scripts/check_repository_contracts.py` to require those patterns.
- Extended docs-plan coverage to require this completed plan.
- Updated README, VISION, and CHANGES.

## Verification

- Negative: source review showed the local metadata patterns were absent from
  `.gitignore`.
- `python3 scripts/check_repository_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add language-specific generated artifact rules once the repository chooses a
  runtime.
- Keep workflow changes separate because previous passes noted workflow update
  token limitations.
