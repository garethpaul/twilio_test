# Shell and PowerShell Secret Assignment Syntaxes

Status: Completed

## Context

The tracked snapshot scanner rejected bare, quoted, exported, dotenv, YAML,
and JSON Twilio assignments. Common shell declarations such as `readonly` and
`declare -x`, plus PowerShell `$env:` assignments, placed text before the
reviewed variable key and bypassed both token and phone patterns.

## Design

- Share one optional assignment-prefix grammar between auth-token and phone
  patterns.
- Accept `export`, `local`, `readonly`, `declare`, and `typeset`, with bounded
  repeated alphabetic `-`/`+` flags or `--`.
- Accept case-insensitive PowerShell `$env:` prefixes.
- Preserve the existing anchored key, separator, value, encoding, staged blob,
  worktree, size, and symlink boundaries.
- Keep the repository runtime-free and avoid generic entropy scanning.

## Test First

Focused end-to-end tests staged real-looking values under `readonly`,
`declare -x`, `typeset -xr`, and PowerShell `$env:` forms. All five original
fixtures passed through the old scanner and failed the test before the shared
prefix grammar was implemented. A `local` fixture completed the reviewed shell
declaration set. Follow-up red tests proved repeated `declare -x -r` options
and `readonly --` also required bounded option-sequence handling.

## Verification

- Run the focused shell and PowerShell unittest methods.
- Run sanitized `make check` through `./scripts/run-make.sh check` under `C`
  and `C.UTF-8`.
- Run every public Make target from the checkout and an external directory.
- Reject mutations that remove either shell declaration or PowerShell prefix
  coverage.
- Run shell/Python syntax checks and `git diff --check`.
- Use hosted Python 3.10/3.12/3.14 and CodeQL checks as exact-head authority.

## Scope Boundaries

- No Twilio SDK, dependency, network request, live send, environment loader,
  workflow trigger, greeting behavior, or Make authority change.
- Detection remains key-specific and pattern-based rather than a general secret
  scanner.

## Verification Completed

- The focused red-first tests failed for all five original bypass fixtures and
  passed after implementation; two follow-up option-form fixtures also failed
  before the final grammar and then passed. The full suite passed with 21 tests.
- Sanitized `make check` passed under `C` and `C.UTF-8`; all six public Make
  targets passed under both locales and from an external working directory.
- Mutations removing shell declaration or PowerShell prefix support were both
  rejected.
- Python compilation, shell syntax checking, and `git diff --check` passed.
- Hosted exact-head and review evidence will be recorded in the PR.
