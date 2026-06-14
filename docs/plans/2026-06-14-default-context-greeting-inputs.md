# Default-Context Greeting Inputs

Status: Planned

## Problem

The pinned `actions/first-interaction` v3.1.0 action reads both
`issue_message` and `pr_message` on every invocation. The default-branch
pull-request greeting supplies only `pr_message`, so every newly opened pull
request fails in the privileged `pull_request_target` workflow before it can
post the greeting.

## Requirements

1. Supply both required message inputs to both event-scoped greeting jobs.
2. Preserve the immutable action pin, repository token, fixed runner, bounded
   timeout, event filters, and least-privilege job permissions.
3. Strengthen the dependency-free checker so each exact message input must
   appear once per action invocation, not merely somewhere in the workflow.
4. Reject missing issue or pull-request inputs in either job through focused
   mutations.
5. Land the narrow fix on the default branch so future
   `pull_request_target` runs load the corrected workflow definition.

## Verification

- Compile and run the dependency-free checker.
- Run local and external-directory `make check` gates.
- Reject four focused per-job missing-input mutations.
- Parse workflow YAML and audit the exact diff, artifacts, whitespace, and
  changed-line credentials.
- After the normal default-branch push, rerun the existing failed Greetings
  workflow and verify the pull-request job succeeds at the unchanged PR head.

## Scope Boundaries

- Do not add checkout, command execution, broader permissions, mutable action
  tags, Twilio credentials, or runtime behavior.
- Do not merge or close any pull request without explicit owner authorization.
