# Staged Secret Snapshot Scan

Status: Completed

## Context

The tracked-secret gate enumerated the Git index but read content only from the
worktree. A contributor could stage a real-looking Twilio credential and then
replace the worktree file with benign text before running the local gate. The
check would pass even though the next commit still contained the staged secret.

## Design

Preserve each canonical object ID returned by `git ls-files --stage`. Read the
immutable staged blob with `git cat-file`, reject non-regular modes, malformed
object IDs, unreadable objects, and blobs above the existing 1 MiB limit. Scan
that staged snapshot and the current worktree snapshot independently while
sharing the existing 16 MiB aggregate budget.

Keep the worktree scan because an unstaged secret must also fail locally. Its
existing `lstat`, `O_NOFOLLOW`, inode, type, and growth checks remain the safe
boundary for filesystem content.

## Alternatives Considered

- Scanning only `HEAD` would miss newly staged content.
- Scanning only the index would miss an unstaged secret about to be staged.
- Reconstructing a temporary checkout would add filesystem and cleanup risk
  without improving on immutable blob reads.

## Verification

- A staged token followed by a benign worktree edit must fail.
- A benign staged blob followed by an unstaged token must fail.
- Existing symlink, file-size, aggregate-size, and encoded-text tests stay
  green.
- `make check` runs the complete repository contract suite.
