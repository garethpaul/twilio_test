---
title: "fix: Protect the Make repository root from overrides"
date: 2026-06-14
---

# Protect the Make Repository Root from Overrides

## Status: Completed

## Context

The Makefile derives `ROOT` from its own location, but GNU Make command-line
assignments take precedence over an ordinary `:=` definition. A caller can
therefore supply `ROOT=<other-directory>` and redirect the secret and workflow
contract checker away from the reviewed checkout.

## Requirements

- R1. Protect `ROOT` with GNU Make's `override` directive while continuing to
  derive it from the loaded Makefile path.
- R2. Preserve `PYTHON ?= python3` so callers and hosted jobs can select a
  compatible interpreter.
- R3. Require the exact protected root definition in the portable repository
  checker.
- R4. Prove local, external-directory, and hostile `ROOT=` invocations validate
  the intended checkout.
- R5. Reject mutations that remove protection, change the root source, weaken
  the checker, remove Python configurability, or reopen this plan.
- R6. Preserve the UTF-8, UTF-16, UTF-32, placeholder, workflow, and tracked
  secret contracts without adding runtime behavior or dependencies.

## Implementation Units

### Protect the internal Make root

**Files:** `Makefile`

Change the existing Makefile-derived assignment to `override ROOT := ...` and
leave the Python executable override unchanged.

### Enforce the protected definition

**Files:** `scripts/check_repository_contracts.py`

Require the exact root line and Python override so weaker assignments fail the
same portable gate used locally and in hosted CI.

### Record completed evidence

**Files:** `docs/plans/2026-06-14-make-root-override-protection.md`

Record actual focused, full-gate, hostile-root, mutation, artifact, and secret
audit results before shipment.

## Verification Plan

- focused hosted-verification contract check
- full `make check` under a hard timeout
- external-directory `make -C <checkout> check`
- hostile `make -C <checkout> ROOT=<empty-directory> check`
- mutations for ordinary, recursive, `CURDIR`, first-Makefile, weakened-checker,
  Python-override, and plan-status regressions
- Python compile, YAML/XML parsing, intended-path, generated-artifact,
  `git diff --check`, and changed-line secret audits

## Scope Boundaries

- Do not change secret patterns, supported encodings, workflows, dependencies,
  environment placeholders, or repository runtime scope.
- Do not merge or close any stacked pull request without owner authorization.

## Work Completed

- Protected the Makefile-derived repository root with GNU Make's `override`
  directive while preserving the configurable Python command.
- Strengthened the portable checker to require the protected root, Python
  override, checker invocation, and registered maintenance plan.

## Verification

- `python3 -m py_compile scripts/check_repository_contracts.py` passed.
- The focused `check_hosted_verification()` contract passed.
- Full local `make check`, external-directory `make -C <checkout> check`, and
  hostile `make -C <checkout> ROOT=<empty-directory> check` each passed under
  a 180-second timeout with all nine repository contract groups.
- Eight hostile mutations were rejected: removing `override`, using `CURDIR`,
  changing to recursive assignment, deriving from the first loaded Makefile,
  removing Python configurability, weakening either exact checker assertion,
  and reopening the completed plan.
- Python compile, workflow YAML, SVG XML, intended-path, generated-artifact,
  `git diff --check`, and changed-line secret audits passed before shipment.
- No Twilio credentials, live requests, or external service calls were used.
