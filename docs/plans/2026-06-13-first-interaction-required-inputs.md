# Supply Both First-Interaction Message Inputs

Status: Completed

## Context

The pinned `actions/first-interaction` v3.1.0 implementation reads both
`issue_message` and `pr_message` as required inputs on either supported event.
The event-scoped jobs supplied only the message they post, so pull-request
target runs failed before posting a comment.

## Implementation

- Supply both non-secret `Ahoy!` inputs in both event-scoped jobs.
- Require exactly two nonempty occurrences of each input in the portable
  workflow contract.
- Preserve the immutable action pin, fixed runner, bounded timeout, no-checkout
  execution boundary, and distinct least-privilege issue and pull-request
  permissions.

## Verification

- Pull-request-target run `27450669768` failed with missing
  `issue_message` at predecessor head `08cd7602d28e59b1666508440658a4ecf27abbea`.
- Pull-request-target run `27461296058` reproduced the same default-branch
  failure for PR #5 head `cea1d8fd29e6ed2a728078c376daf83526d3dd68`.
- `make check` and external-directory verification passed after supplying both
  inputs.
- Missing and empty input mutations are rejected by the strengthened contract.
- Hosted confirmation requires this direct-to-`master` delivery to be merged;
  `pull_request_target` loads the workflow from the default branch.

## Remaining Risks

- The first-interaction action can still fail for provider-side permission or
  availability errors.
- No merge or close action is authorized by this plan.
