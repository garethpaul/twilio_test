# Secret Assignment Syntaxes

Status: Completed

## Goal

Prevent tracked Twilio tokens and phone numbers from bypassing the repository
scanner when written in shell export, dotenv, YAML, or JSON syntax.

## Implementation

- Centralize tracked-secret regular expressions for reuse.
- Accept quoted keys and values plus `=`, `:`, and optional `export` syntax.
- Preserve SID and private-key detection.
- Add runtime-assembled fixtures for each supported assignment form without
  checking a secret-like literal into the scanner itself.

## Verification

- `make check`
- Mutation check: restoring equals-only matching must fail the YAML and JSON
  secret fixture contracts.
