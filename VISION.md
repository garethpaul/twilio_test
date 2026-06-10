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
- Ignore local environment files, debug logs, and HAR captures
- Ignore packet captures, traces, local Worker secrets, and key material
- Scan all tracked text for real-looking Twilio identifiers and secrets
- Ignore local OS and IDE metadata
- Keep environment examples placeholder-only and live sends disabled
- Keep future message-body placeholders empty until an implementation exists
- Keep credential, phone-number, and message-body placeholders empty in git
- Keep future debug logging opt-in from an info default
- Keep environment placeholder comments clear about local-only values
- Keep environment placeholders unique and limited to documented Twilio keys
- Keep repository workflow behavior visible in static checks
- Keep live calls and messages opt-in until a real test harness exists
- Keep completed maintenance plans discoverable from the README

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
- `.env.example` values that look like real credentials or phone numbers
- Live-call or live-message defaults
- Behavior claims without code
- Local editor or OS metadata
- Hidden telemetry or logging of customer payloads

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
