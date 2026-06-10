# Changes

## 2026-06-10

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
