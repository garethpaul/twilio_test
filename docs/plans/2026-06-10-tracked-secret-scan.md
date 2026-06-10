# Tracked Secret Pattern Scan

Status: Completed

## Problem

The repository strictly validated `.env.example`, but a real-looking Twilio SID,
populated token assignment, phone assignment, or private key could still be
committed in another tracked text file. Packet captures, traces, Wrangler local
secrets, and key files were also outside the ignore contract.

## Plan

1. Enumerate tracked files through Git rather than scanning ignored local data.
2. Skip binary and non-UTF-8 files while scanning every tracked text file.
3. Reject Twilio Account, API Key, Message, and Call SID shapes.
4. Reject populated Twilio auth-token and phone-variable assignments.
5. Reject private-key blocks.
6. Ignore packet captures, traces, `.dev.vars`, PEM, and key files.
7. Fix workflows to Ubuntu 24.04 with annotated immutable actions and make the
   local checker independent of the caller's working directory.

## Verification

- `make check`
- `make -f /path/to/twilio_test/Makefile check` outside the repository
- Planted SID, auth token, phone number, and private key mutations rejected
- Runner, action annotation, ignore rule, and Makefile mutations rejected
- Full Git history scanned for the same concrete secret shapes
- `git diff --check`
