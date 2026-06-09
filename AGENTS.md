# AGENTS.md

## Repository purpose

`garethpaul/twilio_test` is a public sample, documentation, or utility project. Test

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `plans` - repository source or sample assets

## Development commands

- Install dependencies: no repository-specific install command is documented.
- Full baseline: `make check`
- Combined verification: `make verify`
- Lint/static checks: `make lint`
- Tests: `make test`
- Build: `make build`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Language mix noted in the README: no dominant source language detected.

## Testing guidance

- Test-related files detected: `docs/plans/2026-06-08-twilio-test-baseline.md`
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- No required secret or credential file was identified in the repository scan. Local `.env` files and debug logs are ignored so future Twilio experiments do not casually stage credentials, account identifiers, customer payloads, or HTTP archive captures.
- `.env.example` documents expected Twilio variable names with empty values and keeps live sends disabled by default, including a placeholder body for future message smoke tests and an `info` log-level default. Each placeholder includes a short comment describing what may be filled locally and what must stay empty in git. Static checks require credential, phone-number, and body placeholders to remain empty and reject duplicate or undocumented Twilio placeholder entries.
- Keep local Twilio credentials and debug output out of git; `.env` files and `*.log` and `*.har` files are intentionally ignored. Common local OS and IDE metadata files are ignored as well.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- See `docs/plans/2026-06-08-twilio-test-baseline.md` for the canonical placeholder contract baseline.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
