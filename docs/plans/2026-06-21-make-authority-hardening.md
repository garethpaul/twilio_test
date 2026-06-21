# Make Authority Hardening

## Status: Completed

## Context

The portable `make check` gate protected its root after parsing, but GNU Make
could process execution-skipping flags, `--eval`, startup files, and additional
`-f` files before repository policy ran.

## Requirements

- Preserve literal, multiword Python command overrides.
- Reject Make-syntax commands before expansion and keep root/shell authority local.
- Add a fixed-target physical-root wrapper for hosted and contributor checks.
- Clear every inherited GNU Make control variable before Make starts.
- Prove repository and external-directory `make check` behavior.
- Keep all Twilio credentials unset and make no live provider calls.

## Work Completed

- Bound root, shell, Python command, flag, startup-file, and Makefile identity authority.
- Added Python-native adversarial regression coverage to `make check`.
- Added `scripts/run-make.sh` with byte-preserving bounded symlink resolution,
  exact `check|lint` target selection, fixed tools, and five-variable Make
  sanitization.
- Bound hosted CI to the wrapper and documented direct Make, literal `PYTHON`,
  and caller `PATH` as explicit local trust boundaries.

## Verification

- Sanitized repository and external-directory `make check` passed offline
  through `./scripts/run-make.sh check`.
- No Twilio credentials, provider endpoints, recipients, or live calls were used.

## Scope Boundaries

No provider runtime, dependency, credential handling, publishing, or deployment
changed. Direct GNU Make startup files, `--eval`, and earlier or later `-f`
files remain caller authority; hosted CI no longer exposes those channels.
Literal `PYTHON` and executable lookup through `PATH` remain caller-controlled.
