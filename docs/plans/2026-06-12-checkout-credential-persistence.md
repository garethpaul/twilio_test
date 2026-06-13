# Checkout Credential Persistence

Status: Completed

## Problem

The canonical verification workflow has read-only permissions but uses the
default checkout behavior, which persists the workflow token in local Git
configuration for later steps. The repository check only reads tracked files,
so retaining credentials is unnecessary and broadens the impact of a future
command or dependency compromise.

## Plan

1. Disable checkout credential persistence in the canonical check workflow.
2. Extend the local repository contracts to require that setting.
3. Preserve the separate, pinned greetings workflow because it does not check
   out or execute pull-request code and has event-specific write permissions.
4. Verify the normal and external Make gates and reject credential-persistence
   regressions with an isolated mutation.

## Verification

- `make check` passed all eight repository contract groups.
- An external-working-directory Make invocation passed the same gate.
- Ruby parsed the updated workflow and Python compiled the checker.
- Isolated mutations removing the setting or changing it to `true` were both
  rejected.
- Exact-head hosted Python 3.10/3.12/3.14 checks
- `git diff --check` passed.
