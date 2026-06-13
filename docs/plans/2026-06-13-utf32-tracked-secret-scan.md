---
title: "fix: Scan UTF-32 tracked text for Twilio secrets"
date: 2026-06-13
---

# Scan UTF-32 Tracked Text for Twilio Secrets

## Status: Completed

## Context

The tracked-file scanner recognizes BOM-marked UTF-16, but UTF-32 little-endian
begins with the UTF-16 little-endian BOM prefix and is therefore misdecoded.
UTF-32 big-endian is treated as binary. Both cases can hide otherwise detected
Twilio credentials in tracked text.

## Requirements

- R1. Decode BOM-marked UTF-32 little-endian and big-endian tracked text before
  checking UTF-16 BOMs.
- R2. Apply the existing Twilio SID, auth-token, phone-number, and private-key
  patterns to successfully decoded UTF-32 text.
- R3. Keep malformed UTF-32 and arbitrary NUL-containing binary skipped rather
  than guessing encodings.
- R4. Preserve UTF-8 and UTF-16 behavior through one shared decoder.
- R5. Add self-tests for both UTF-32 byte orders, malformed UTF-32, BOM-ordering
  precedence, and ordinary binary.
- R6. Register a completed plan and update security and operator guidance.
- R7. Mutation tests must reject removed UTF-32 support, reversed BOM ordering,
  missing byte-order coverage, and weakened malformed-input handling.

## Scope Boundaries

- Do not attempt heuristic legacy-encoding detection, scan untracked files, or
  inspect repository history.
- Do not add dependencies or introduce real credential fixtures.
- Do not reinterpret arbitrary binary as text.

## Implementation Units

### U1. Extend the shared tracked-text decoder

- **Files:** `scripts/check_repository_contracts.py`
- Recognize the four-byte UTF-32 BOMs before the overlapping UTF-16 prefixes.

### U2. Add encoding-boundary self-tests

- **Files:** `scripts/check_repository_contracts.py`
- Build synthetic token assignments at runtime and verify detection in both
  byte orders without checking secret material into the repository.

### U3. Preserve repository contracts and guidance

- **Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`
- Document explicit BOM support and the remaining binary/history boundary.

## Verification

- `python3 -c 'import scripts.check_repository_contracts as c;
  c.check_secret_pattern_encodings()'` passed UTF-16 LE/BE, UTF-32 LE/BE,
  malformed UTF-16/UTF-32, and arbitrary-binary boundaries.
- Full local, external-directory, and space-containing-path `make check` runs
  passed all nine repository contract groups.
- Eight hostile mutations covering removed UTF-32 support, the wrong codec,
  missing LE/BE BOM handling, accepted malformed input, reduced byte-order
  fixtures, and stale plan status were rejected.
- Workflow YAML, Python syntax, SVG XML, `git diff --check`, generated-artifact,
  and focused secret reviews are included in final validation.
