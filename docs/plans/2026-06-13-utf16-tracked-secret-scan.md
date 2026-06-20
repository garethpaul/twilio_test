---
title: "fix: Scan UTF-16 tracked text for Twilio secrets"
type: fix
date: 2026-06-13
---

# Scan UTF-16 Tracked Text for Twilio Secrets

## Status: Completed

## Context

The repository checker scans UTF-8 tracked text for Twilio identifiers,
credential assignments, phone assignments, and private keys. It currently
skips every file containing a NUL byte, which also skips valid UTF-16 text and
creates an avoidable encoding bypass.

## Requirements

- R1. Decode BOM-marked UTF-16 little-endian and big-endian tracked text before
  applying the existing secret patterns.
- R2. Continue scanning UTF-8 text and skipping unrecognized binary or invalid
  text without crashing.
- R3. Keep one shared decoding helper for the repository scan and encoding
  self-tests.
- R4. Add boundary fixtures for both UTF-16 byte orders and ordinary binary
  data.
- R5. Preserve the sparse, runtime-free repository scope and existing secret
  patterns.
- R6. Document the expanded tracked-text boundary and actual verification.

## Scope Boundaries

This change does not add Twilio runtime code, inspect git history, scan
untracked files, or attempt arbitrary legacy encoding detection.

## Implementation Units

### U1. Decode Recognized Tracked Text

- **Files:** `scripts/check_repository_contracts.py`
- Add a helper that recognizes UTF-16 BOMs before the existing NUL-byte binary
  guard and otherwise retains UTF-8 decoding behavior.

### U2. Protect the Encoding Boundary

- **Files:** `scripts/check_repository_contracts.py`
- Add self-tests proving both UTF-16 byte orders expose secret assignments to
  the existing patterns while binary and malformed inputs remain skipped.

### U3. Document and Verify

- **Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`, this plan.
- Record the supported tracked-text encodings, mutation results, and full gate.

## Risks

- Treating arbitrary NUL-containing data as text could create binary false
  positives, so only explicit UTF-16 BOMs should bypass the binary guard.
- Decoder errors must leave the individual file unclassified without breaking
  all repository validation.

## Verification

- `python3 -m py_compile scripts/check_repository_contracts.py`: passed.
- `python3 -c 'import scripts.check_repository_contracts as c;
  c.check_secret_pattern_encodings()'`: passed UTF-16 LE/BE, malformed UTF-16,
  and binary fixtures.
- `/tmp/engineering-bar/mutate-twilio-utf16-secret-scan.sh`: rejected five BOM,
  endian, codec, and decoder-error mutations.
- `git diff --check`: passed.
- `make check`: passed all nine repository contract groups.
- `make -C /tmp/engineering-bar/twilio-utf16-secret-scan-external/repo check`:
  passed the same nine groups from an external temporary repository path.
