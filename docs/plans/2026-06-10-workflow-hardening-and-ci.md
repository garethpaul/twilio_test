# Workflow Hardening and Hosted Verification

Status: Completed

## Problem

The placeholder contracts passed locally, but no hosted job enforced them.
The only automation used the mutable `actions/first-interaction@v1` tag, a
custom repository secret, legacy input names, and no explicit permissions.

## Plan

1. Update first-interaction to the verified v3.1.0 commit and current inputs.
2. Use the repository-scoped GitHub token with only contents-read and the
   issue/pull-request comment permissions the action needs.
3. Add immutable-pinned Python 3.10/3.12/3.14 CI for `make check`, including
   manual dispatch.
4. Use `pull_request_target` only for the static greeting action, with no
   checkout or execution of contributor-controlled code, and separate issue
   and pull-request jobs so each receives only its required write permission.
5. Extend local contracts so triggers, permissions, pins, timeouts, matrices,
   and commands cannot silently regress.

## Verification

- `make check`
- `python3 -m py_compile scripts/check_repository_contracts.py`
- Negative mutable-action and writable-check-workflow mutations rejected
- `git diff --check`
