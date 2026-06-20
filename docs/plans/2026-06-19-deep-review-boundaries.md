# Deep Review Boundary Hardening

Status: Completed

## Context

The stacked pull requests added useful placeholder, workflow, and encoded-secret
contracts, but the scanner still followed tracked symlinks, read files without
size limits, and skipped UTF-8 BOM plus BOM-less UTF-16/UTF-32 text. The
repository also described itself as runtime-free without enforcing that claim.

## Design

Keep the repository dependency-free and fail closed at the tracked-file
boundary. Enumerate canonical index entries, reject symlinks and special modes,
open regular files without following links, and cap both individual and total
bytes. Decode UTF-8 BOM and strongly identified UTF-16/UTF-32 layouts before
applying the existing Twilio patterns. Preserve binary skipping when no safe
text layout is identified.

Keep the placeholder invariant explicit with an allowlist for the three review
and test source files. Restrict Make recipes to those verification commands so
hosted checks cannot acquire an accidental provider-send path. Pin current
official Actions releases by full commit SHA and keep least-privilege workflow
permissions.

## Alternatives Considered

- Adding a YAML or secret-scanning dependency would broaden supply-chain and
  bootstrap risk for a 100 KiB placeholder repository.
- Skipping oversized or special files would leave an intentional bypass, so
  the checker rejects them instead.
- Allowing arbitrary runtime source with only pattern scanning would not prove
  that live Twilio sends remain impossible.

## Verification

- Behavioral tests cover UTF-8 BOM, BOM-less UTF-16/UTF-32, tracked symlinks,
  per-file and aggregate limits, runtime source, Make recipes, and action pins.
- `make check` runs the checker, behavioral tests, and greeting runtime proof.
- External-directory execution with a hostile `ROOT` override remains covered.
