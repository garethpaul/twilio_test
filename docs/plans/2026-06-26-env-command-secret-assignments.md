# Scan `env` command secret assignments

Status: Completed

## Problem

The tracked-secret scanner recognized bare assignments, shell declarations,
PowerShell environment assignments, dotenv, YAML, and JSON, but not the common
shell form `env TWILIO_AUTH_TOKEN=... command`. Adding `env` options such as
`-i --` also bypassed detection.

## Fix

- Recognize `env` and `/usr/bin/env` before protected Twilio assignments.
- Accept no-operand options, attached or separated operands for `-u`, `-C`,
  `-S`, and their long forms, plus the `--` option terminator.
- Preserve the existing exact variable names and real-looking token or phone
  value requirements to avoid broad secret-name matching.
- Add red-first fixtures for token and phone assignments.

## Validation

- Run the focused unit regression.
- Run `make check` from the checkout and an external path.
- Require hosted Python-matrix and CodeQL evidence before merge.
