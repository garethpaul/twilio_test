# Environment Example Unique Placeholders

## Status: Completed

## Context

`.env.example` keeps sensitive Twilio placeholders empty and live sends disabled
by default. The static checks proved those safe lines existed, but a later
duplicate line such as `TWILIO_ACCOUNT_SID=AC...` could still be added after
the empty placeholder and pass the presence checks.

## Objectives

- Require each documented Twilio environment placeholder to appear exactly once.
- Preserve empty credential, phone-number, and message-body placeholders.
- Preserve `TWILIO_LOG_LEVEL=info` and `TWILIO_SEND_LIVE=false`.
- Reject undocumented `TWILIO_` entries until a real mock or sandbox harness
  needs them.
- Preserve local HAR capture ignores alongside debug log ignores.
- Keep the completed plan required by `make check`.

## Work Completed

- Added `.env.example` parsing to `scripts/check_repository_contracts.py`.
- Required each documented Twilio key to appear exactly once with its safe
  checked-in value.
- Rejected extra undocumented Twilio placeholder keys.
- Preserved `*.har` in the local artifact ignore contract.
- Required this completed plan in the repository contract checker.
- Updated README, VISION, SECURITY, and CHANGES.

## Verification

- `python3 scripts/check_repository_contracts.py`
- `make check`
- `git diff --check`

## Follow-Up Candidates

- Choose a deterministic mock or sandbox test strategy.
- Add runtime examples only after the placeholder safety contract remains
  enforced.
