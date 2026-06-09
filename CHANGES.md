# Changes

## 2026-06-09

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
