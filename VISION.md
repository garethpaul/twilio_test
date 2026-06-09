## Twilio Test Vision

Twilio Test is currently a sparse repository with a minimal README and
security metadata.

The repository is useful as a placeholder for Twilio-related experimentation,
but it does not yet define an implementation, runtime, or supported test flow.

The goal is to keep the repository honest and avoid implying Twilio behavior
that is not present in the codebase.

The current focus is:

Priority:

- Preserve the placeholder state
- Keep security-reporting metadata available
- Document intended test scope before adding code
- Avoid committing Twilio credentials or account data
- Ignore local environment files and debug logs
- Keep repository workflow behavior visible in static checks
- Keep live calls and messages opt-in until a real test harness exists

Next priorities:

- Choose a language and deterministic test strategy
- Add mock or sandbox examples before live-account examples
- Archive the repository if it is no longer needed

Contribution rules:

- One PR = one focused scope, test, code, or documentation change.
- Do not commit credentials, phone numbers, SIDs, or customer data.
- Keep live Twilio calls opt-in and clearly documented.
- Add tests for any claimed behavior.

## Security And Responsible Use

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Twilio tests can affect live accounts, phone numbers, messages, and calls.
Future work should keep credentials local and make side effects explicit.

## What We Will Not Merge (For Now)

- Checked-in credentials or account identifiers
- Live-call or live-message defaults
- Behavior claims without code
- Hidden telemetry or logging of customer payloads

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
