# Changes

## 2026-06-26 16:56 PDT - P1 - Scan `env` command secret assignments

### Summary
Closed a tracked-secret scanner bypass for Twilio tokens and phone numbers
assigned through the shell `env` command.

### Work completed
- Added red-first token and phone fixtures for `env` assignments.
- Recognized `env`, `/usr/bin/env`, no-operand options, attached or separated
  option operands, and `--` before the existing exact Twilio patterns.
- Documented the scanner boundary without introducing Twilio runtime behavior.

### Threads
- Started: none; the bounded scanner change was completed directly.
- Continued: repository-wide tracked-secret hardening.
- Stopped: none.

### Files changed
- `scripts/check_repository_contracts.py` — scans `env` assignment prefixes.
- `tests/test_repository_contracts.py` — proves token and phone bypasses fail.
- `SECURITY.md`, `AGENTS.md`, and the completed plan — document the boundary.

### Validation
- Focused unit regression — failed twice before implementation for the expected
  missing token and phone detections.
- Manual exact-head review found `-u NAME` and `--chdir DIR` bypasses in the
  first patch; both new regressions failed before the explicit option grammar.
- `./scripts/run-make.sh check` — passed 22 unit tests, repository contracts,
  greeting runtime regressions, and Make authority tests.
- External-path `make -C /tmp -f <checkout>/Makefile check` — passed.
- Python compilation and `git diff --check` — passed.
- Hosted exact-head checks remain next.

### Bugs / findings
- P1 security: tracked shell files could hide populated protected variables
  behind `env` command invocation syntax.

### Blockers
- None.

### Next action
- Run local and hosted exact-head validation, review, and merge the focused PR.

## 2026-06-26 02:42 PDT - P2 - Scan shell declaration secrets

### Summary
Closed tracked-secret scanner gaps for common shell declaration prefixes and
PowerShell environment assignments without broadening the placeholder into a
provider runtime.

### Work completed
- Centralized the optional assignment prefix shared by Twilio auth-token and
  phone-number patterns.
- Added `local`, `readonly`, `declare`, and `typeset` shell declaration forms,
  including bounded repeated options such as `-x -r`, `-xr`, and `--`.
- Added case-insensitive PowerShell `$env:` assignment coverage.
- Preserved existing bare, quoted, `export`, dotenv, YAML, and JSON matching.
- Added end-to-end staged/worktree regressions and embedded syntax contracts.

### Threads
- Started: none.
- Continued: tracked secret hygiene — assignment grammar coverage complete.
- Stopped: none.

### Files changed
- `scripts/check_repository_contracts.py` — expands the shared secret assignment
  grammar and binds the completed plan into repository contracts.
- `tests/test_repository_contracts.py` — proves shell declarations and
  PowerShell environment assignments are rejected from tracked snapshots.
- Documentation and plan files — record the supported syntax and validation.

### Validation
- Red-first focused unittest command — five original shell/PowerShell fixtures
  bypassed the old scanner, then passed after implementation.
- Follow-up red-first shell test — repeated `declare -x -r` and `readonly --`
  options bypassed the first grammar, then passed after bounded option support.
- `./scripts/run-make.sh check` — passed with 21 behavioral tests under `C` and
  `C.UTF-8`.
- `make build|check|lint|root-test|test|verify` — passed under both locales and
  from `/tmp` through the absolute Makefile path.
- Shell-prefix and PowerShell-prefix removal mutations — both rejected.
- Python compilation, shell syntax, and `git diff --check` — passed.
- Hosted Python/CodeQL exact-head checks and review remain the next action.

### Bugs / findings
- P2: `readonly`, `declare`, `typeset`, and PowerShell `$env:` assignments could
  previously carry real-looking Twilio tokens or phone numbers undetected.

### Blockers
- None; this repository remains dependency-free and performs no live Twilio
  calls.

### Next action
- Open the focused PR, run exact-head hosted validation and review, then merge.

## 2026-06-25 07:01 PDT

- Closed the local staged-secret bypass by scanning immutable index blobs in
  addition to safely opened worktree files.
- Preserved Git object IDs from canonical index entries and bounded staged
  blobs with the same per-file and aggregate limits as worktree snapshots.
- Added regressions proving that neither a benign unstaged edit nor a benign
  staged snapshot can hide a secret in the other tracked state.

- Added a physical-root `check|lint` wrapper for hosted and contributor
  verification, clearing all five GNU Make control variables before Make starts
  and covering dry-run, ignore-errors, startup-file, `--eval`, and extra-`-f`
  authority paths.
- Hardened `make check` against Make-syntax Python expansion, caller shell and
  Makefile identity replacement, execution-skipping flags, and startup-file
  configuration while preserving literal multiword Python overrides.

## 2026-06-19

- Bounded tracked secret scans, rejected symlinks and special entries, and
  covered UTF-8 BOM plus BOM-less UTF-16/UTF-32 encodings.
- Enforced the runtime-free placeholder and reviewed Make recipe boundary.
- Updated checkout and github-script to current official immutable pins.

## 2026-06-14

- Supplied both required first-interaction message inputs to each event-scoped
  default-branch greeting job and added count-sensitive regression contracts.

## 2026-06-13

- Extended tracked-secret scanning to BOM-marked UTF-32 little-endian and
  big-endian text before the overlapping UTF-16 BOM checks.
- Added self-tests for UTF-32 credential detection, byte-order handling, and
  malformed-input boundaries.
- Extended tracked-secret scanning to BOM-marked UTF-16 little-endian and
  big-endian text while continuing to skip unrecognized binary data.
- Supplied both required greeting-message inputs to each event-scoped
  first-interaction job so the pinned v3.1.0 action runs successfully while
  preserving least-privilege issue and pull-request permissions.
## 2026-06-12

- Disabled checkout credential persistence in the canonical verification job
  and added a fail-closed local workflow contract for the setting.

## 2026-06-10

- Extended tracked Twilio secret detection across shell exports, dotenv, YAML,
  and JSON assignment syntax with embedded regression fixtures.
- Added a tracked UTF-8 text scan for Twilio Account/API/Message/Call SIDs,
  populated auth-token and phone assignments, and private-key blocks.
- Expanded local artifact ignores to packet captures, traces, `.dev.vars`, PEM,
  and key files.
- Fixed verification and greeting workflows to Ubuntu 24.04, annotated all
  immutable action revisions, scoped verification concurrency, and made the
  Makefile root-independent.
- Replaced the legacy mutable first-interaction v1 workflow with the verified
  v3.1.0 commit, current inputs, repository token, explicit permissions, and a
  bounded runtime.
- Added immutable-pinned Python 3.10/3.12/3.14 GitHub Actions verification for the
  placeholder, secret-hygiene, and documentation contracts.
- Used `pull_request_target` for static greeting comments so forked pull
  requests work without checking out or executing contributor code.
- Split issue and pull-request greetings into event-scoped jobs with distinct
  write permissions.
- Extended local contracts to fail on workflow permission, trigger, pin,
  timeout, matrix, or command drift.

## 2026-06-09

- Ignored common local OS and IDE metadata and preserved those rules in static
  repository contracts.
- Required `.env.example` Twilio placeholders to appear exactly once with their
  safe checked-in values.
- Extended static repository contracts to reject duplicate or undocumented
  Twilio placeholder entries.
- Ignored local HAR capture files and preserved the ignore rule in static
  repository contracts.
- Required credential, phone-number, and message-body entries in `.env.example`
  to remain empty.
- Extended static repository contracts to preserve empty sensitive placeholders.
- Added a placeholder `TWILIO_LOG_LEVEL=info` default with guidance to use
  debug only locally after redaction review.
- Added per-variable comments to `.env.example` so future local Twilio values
  stay clearly placeholder-only.
- Extended static contracts to preserve the environment placeholder guidance.
- Added a placeholder `TWILIO_BODY` entry to `.env.example` for future message
  smoke tests.
- Extended static contracts to preserve message body placeholder coverage.
- Added a placeholder-only `.env.example` with live sends disabled by default.
- Extended static contracts to preserve safe Twilio environment placeholders.

## 2026-06-08

- Linked completed maintenance plans from the README and added static coverage
  for plan discoverability.
- Ignored Python bytecode caches produced by local checker syntax validation.
- Added `.gitignore` coverage for local environment files and debug logs, with
  static checks preserving the secret-hygiene patterns.
- Added canonical `docs/plans` coverage to the placeholder contract checker.
- Added an intended Twilio test scenario to the README without adding runtime
  behavior.
- Extended placeholder static checks to require mock/sandbox-first and
  live-opt-in scenario wording.
- Added `make verify` and `make check` static contract gates for placeholder docs and workflow presence.
- Kept workflow changes out of this pass because the available GitHub token cannot update workflow files.
- Documented the verification command without claiming runtime behavior that is not present.
