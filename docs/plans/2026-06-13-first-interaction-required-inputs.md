---
title: "fix: Supply both first-interaction message inputs"
type: fix
date: 2026-06-13
---

# Supply Both First-Interaction Message Inputs

## Status: Completed

## Context

Successor PR #4 passed its Python verification matrix, but the Greetings
`pull_request_target` run failed before posting a comment. The pinned
`actions/first-interaction` v3.1.0 implementation reads both `issue_message`
and `pr_message` with `required: true` on every supported event. The existing
event-scoped jobs supplied only the message used by their own event.

## Requirements

- R1. Supply both non-secret greeting inputs in both event-scoped jobs.
- R2. Preserve distinct issue and pull-request write permissions.
- R3. Continue avoiding checkout and command execution on
  `pull_request_target`.
- R4. Fail locally when either input is absent or empty in either job.
- R5. Record the exact hosted failure and completed local verification.

## Implementation

- Added the same non-secret `Ahoy!` value for both action inputs in each job.
- Strengthened the workflow contract to require exactly two nonempty
  occurrences of each input.
- Preserved the immutable action pin, fixed runner, bounded timeout,
  event-specific jobs, and least-privilege permissions.

## Verification

- Hosted failure: pull-request-target run `27450669768`, job `81145057443`,
  failed with `Input required and not supplied: issue_message` at exact head
  `08cd7602d28e59b1666508440658a4ecf27abbea`.
- Upstream source audit: pinned commit
  `1c4688942c71f71d4f5502a26ea67c331730fa4d` calls `getInput` with
  `required: true` for both message inputs.
- `python3 -m py_compile scripts/check_repository_contracts.py`: passed.
- `python3 scripts/check_repository_contracts.py`: passed all nine groups.
- `make check`: passed all nine groups.
- External-directory absolute-Makefile `make check`: passed all nine groups.
- Four focused missing and empty input mutations were rejected.
- `git diff --check`: passed.

## Remaining Risks

- The first-interaction action can still fail for provider-side permission or
  availability errors.
- `pull_request_target` loads its workflow from the PR base branch and this
  workflow triggers only on `opened`, so the current branch cannot receive a
  hosted Greetings rerun before merge. Hosted confirmation requires a newly
  opened PR after this fix reaches the base branch.
