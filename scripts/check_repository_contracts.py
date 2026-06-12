#!/usr/bin/env python3
"""Static integrity checks for the sparse Twilio placeholder repository."""

from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DOCS_PLANS = ROOT / "docs/plans"
CANONICAL_PLAN = DOCS_PLANS / "2026-06-08-twilio-test-baseline.md"
EMPTY_ENV_PLACEHOLDERS_PLAN = DOCS_PLANS / "2026-06-09-empty-env-placeholders.md"
UNIQUE_ENV_PLACEHOLDERS_PLAN = DOCS_PLANS / "2026-06-09-env-example-unique-placeholders.md"
HAR_ARTIFACT_IGNORE_PLAN = DOCS_PLANS / "2026-06-09-har-artifact-ignore.md"
LOCAL_METADATA_IGNORE_PLAN = DOCS_PLANS / "2026-06-09-local-metadata-ignore.md"
WORKFLOW_HARDENING_PLAN = DOCS_PLANS / "2026-06-10-workflow-hardening-and-ci.md"
TRACKED_SECRET_SCAN_PLAN = DOCS_PLANS / "2026-06-10-tracked-secret-scan.md"
SECRET_SYNTAX_PLAN = DOCS_PLANS / "2026-06-10-secret-assignment-syntaxes.md"

TRACKED_SECRET_PATTERNS = [
    (re.compile(r"(?<![0-9A-Za-z])(AC|SK|SM|CA)[0-9a-fA-F]{32}(?![0-9A-Za-z])"), "Twilio SID"),
    (
        re.compile(
            r'''(?im)^[ \t]*(?:export[ \t]+)?["']?TWILIO_AUTH_TOKEN["']?[ \t]*(?:=|:)[ \t]*["']?[0-9a-f]{32}(?![0-9a-f])'''
        ),
        "Twilio auth token assignment",
    ),
    (
        re.compile(
            r'''(?im)^[ \t]*(?:export[ \t]+)?["']?TWILIO_(FROM|TO)["']?[ \t]*(?:=|:)[ \t]*["']?\+?[0-9][0-9 ()-]{5,}'''
        ),
        "Twilio phone assignment",
    ),
    (re.compile(r"-{5}BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-{5}"), "private key"),
]


def fail(message):
    print(f"check_repository_contracts.py: {message}", file=sys.stderr)
    return 1


def read_text(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def env_entries(env_text):
    entries = {}
    for line in env_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        name, value = stripped.split("=", 1)
        entries.setdefault(name, []).append(value)
    return entries


def check_required_files():
    for relative_path in [
        ".gitignore",
        ".env.example",
        "README.md",
        "SECURITY.md",
        "VISION.md",
        "docs/readme-overview.svg",
        ".github/workflows/check.yml",
        ".github/workflows/greetings.yml",
    ]:
        require((ROOT / relative_path).exists(), f"{relative_path} must stay checked in")

    ET.parse(ROOT / "docs/readme-overview.svg")


def check_placeholder_scope():
    readme = read_text("README.md")
    vision = read_text("VISION.md")
    require("No single runtime entry point was identified" in readme, "README must not claim missing runtime behavior")
    require("## Intended Test Scenario" in readme, "README must define the intended Twilio test scenario")
    require("mock or sandbox Twilio test doubles" in readme, "README must prefer mock or sandbox test paths")
    require("live calls and messages must remain opt-in" in readme, "README must keep live Twilio side effects opt-in")
    require("does not yet define an implementation" in vision, "VISION must preserve sparse repository scope")
    require("Do not commit credentials" in vision, "VISION must preserve Twilio credential guardrails")
    require(
        "docs/plans/2026-06-08-twilio-test-baseline.md" in readme,
        "README must link the canonical placeholder plan",
    )
    require(
        "docs/plans/2026-06-08-secret-hygiene.md" in readme,
        "README must link the secret hygiene plan",
    )


def check_secret_hygiene():
    gitignore = read_text(".gitignore")
    ignore_entries = {
        line.strip()
        for line in gitignore.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    env_example = read_text(".env.example")
    expected_env_entries = {
        "TWILIO_ACCOUNT_SID": "",
        "TWILIO_AUTH_TOKEN": "",
        "TWILIO_FROM": "",
        "TWILIO_TO": "",
        "TWILIO_BODY": "",
        "TWILIO_LOG_LEVEL": "info",
        "TWILIO_SEND_LIVE": "false",
    }
    parsed_env = env_entries(env_example)
    for pattern in [
        ".env",
        ".env.*",
        "!.env.example",
        "*.log",
        "twilio-debug*.log",
        "*.har",
        "*.pcap",
        "*.pcapng",
        "*.trace",
        ".dev.vars",
        "*.pem",
        "*.key",
        "__pycache__/",
        "*.pyc",
        ".DS_Store",
        ".idea/",
        ".vscode/",
        "*.iml",
    ]:
        require(pattern in ignore_entries, f".gitignore must include exact rule {pattern}")

    for name in [
        "TWILIO_ACCOUNT_SID=",
        "TWILIO_AUTH_TOKEN=",
        "TWILIO_FROM=",
        "TWILIO_TO=",
        "TWILIO_BODY=",
        "TWILIO_LOG_LEVEL=info",
        "TWILIO_SEND_LIVE=false",
    ]:
        require(name in env_example, f".env.example must document {name}")

    for name, expected_value in expected_env_entries.items():
        require(
            parsed_env.get(name) == [expected_value],
            f".env.example must define {name} exactly once with a safe placeholder value",
        )
    for name in parsed_env:
        require(
            not name.startswith("TWILIO_") or name in expected_env_entries,
            f".env.example must not introduce undocumented Twilio placeholder {name}",
        )

    for name in [
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_FROM",
        "TWILIO_TO",
        "TWILIO_BODY",
    ]:
        require(
            re.search(rf"^{name}=$", env_example, re.MULTILINE),
            f".env.example must keep {name} empty",
        )

    for comment in [
        "# Twilio account identifier placeholder. Leave empty in git.",
        "# Twilio auth token placeholder. Leave empty in git.",
        "# Twilio sender phone placeholder. Leave empty in git.",
        "# Twilio recipient phone placeholder. Leave empty in git.",
        "# Future message body placeholder. Leave empty until a mock harness exists.",
        "# Default logging placeholder. Use debug only locally after redaction review.",
        "# Live Twilio side effects must remain disabled by default.",
    ]:
        require(comment in env_example, f".env.example must preserve guidance: {comment}")

    require(
        not re.search(r"TWILIO_ACCOUNT_SID=AC[0-9A-Za-z]+", env_example),
        ".env.example must not contain a real-looking account SID",
    )
    require(
        not re.search(r"TWILIO_(FROM|TO)=\+1[0-9]+", env_example),
        ".env.example must not contain a real-looking phone number",
    )


def check_tracked_secret_patterns():
    tracked = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z"],
        check=True,
        capture_output=True,
    ).stdout.split(b"\0")
    for relative_bytes in tracked:
        if not relative_bytes:
            continue
        relative_path = relative_bytes.decode("utf-8")
        data = (ROOT / relative_path).read_bytes()
        if b"\0" in data:
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        for pattern, description in TRACKED_SECRET_PATTERNS:
            require(
                pattern.search(text) is None,
                f"{relative_path} contains a real-looking {description}",
            )


def check_secret_pattern_syntaxes():
    token = "0123456789abcdef" * 2
    first_phone = "+1555" + "1234567"
    second_phone = "+1555" + "7654321"
    third_phone = "+1555" + "9876543"
    secret_fixtures = [
        "TWILIO_AUTH_TOKEN: " + token,
        '"TWILIO_AUTH_TOKEN": "' + token + '"',
        "export TWILIO_AUTH_TOKEN=" + token,
        "TWILIO_FROM: '" + second_phone + "'",
        '"TWILIO_TO": "' + third_phone + '"',
        "export TWILIO_TO=" + first_phone,
    ]
    for fixture in secret_fixtures:
        require(
            any(pattern.search(fixture) for pattern, _ in TRACKED_SECRET_PATTERNS),
            f"tracked-secret patterns must reject assignment syntax: {fixture}",
        )


def check_greetings_workflow():
    workflow = read_text(".github/workflows/greetings.yml")
    require("issues:\n    types:\n      - opened" in workflow, "greetings workflow must greet newly opened issues")
    require("pull_request_target:\n    types:\n      - opened" in workflow, "greetings workflow must greet newly opened pull requests, including forks")
    require("contents: read" in workflow, "greetings workflow must keep contents read-only")
    require("issues: write" in workflow, "greetings workflow must allow issue comments")
    require("pull-requests: write" in workflow, "greetings workflow must allow pull-request comments")
    require("timeout-minutes: 2" in workflow, "greetings workflow must have a bounded runtime")
    require("runs-on: ubuntu-24.04" in workflow, "greetings workflow must use Ubuntu 24.04")
    require("ubuntu-latest" not in workflow, "greetings workflow must not use a floating runner")
    require(workflow.count("runs-on: ubuntu-24.04") == 2, "both greeting jobs must use Ubuntu 24.04")
    require(workflow.count("actions/first-interaction@1c4688942c71f71d4f5502a26ea67c331730fa4d # v3.1.0") == 2, "both greeting jobs must use the annotated first-interaction pin")
    require("repo_token: ${{ github.token }}" in workflow, "greetings workflow must use the repository token")
    require("TWILIO_" not in workflow, "placeholder workflow must not reference Twilio credentials")
    require("issue_message:" in workflow, "greetings workflow must keep issue greeting explicit")
    require("pr_message:" in workflow, "greetings workflow must keep pull-request greeting explicit")
    require("@v" not in workflow, "greetings workflow action must use an immutable commit")
    require("actions/checkout" not in workflow, "pull_request_target workflow must not check out contributor code")
    require(not re.search(r"^\s*run:", workflow, re.MULTILINE), "pull_request_target workflow must not execute commands")
    require("if: github.event_name == 'issues'" in workflow, "issue greeting must be event-scoped")
    require("if: github.event_name == 'pull_request_target'" in workflow, "pull-request greeting must be event-scoped")
    require(workflow.count("uses:") == 2, "greetings workflow must run only the two pinned greeting actions")
    require(workflow.count("issues: write") == 1, "only the issue greeting may write issues")
    require(workflow.count("pull-requests: write") == 1, "only the pull-request greeting may write pull requests")


def check_hosted_verification():
    workflow = read_text(".github/workflows/check.yml")
    for contract in [
        "pull_request:",
        "workflow_dispatch:",
        "branches:\n      - master",
        "permissions:\n  contents: read",
        "group: check-${{ github.workflow }}-${{ github.ref }}",
        "cancel-in-progress: true",
        "runs-on: ubuntu-24.04",
        "timeout-minutes: 5",
        'python-version: ["3.10", "3.12", "3.14"]',
        "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3",
        "persist-credentials: false",
        "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405 # v6.2.0",
        "run: make check",
    ]:
        require(contract in workflow, f"hosted verification must include {contract!r}")
    require("ubuntu-latest" not in workflow, "hosted verification must not use a floating runner")
    require("@v" not in workflow, "hosted verification actions must use immutable commits")
    makefile = read_text("Makefile")
    require(
        "ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))" in makefile,
        "Makefile must resolve the repository root from its own location",
    )
    require(
        '$(PYTHON) "$(ROOT)/scripts/check_repository_contracts.py"' in makefile,
        "Makefile must run the checker independently of the caller's directory",
    )


def check_docs_plans():
    require(DOCS_PLANS.is_dir(), "docs/plans must exist")
    plans = sorted(DOCS_PLANS.glob("*.md"))
    require(plans, "docs/plans must contain completed maintenance plans")
    require(CANONICAL_PLAN in plans, f"{CANONICAL_PLAN.relative_to(ROOT)} must be present")
    require(
        EMPTY_ENV_PLACEHOLDERS_PLAN in plans,
        f"{EMPTY_ENV_PLACEHOLDERS_PLAN.relative_to(ROOT)} must be present",
    )
    require(
        UNIQUE_ENV_PLACEHOLDERS_PLAN in plans,
        f"{UNIQUE_ENV_PLACEHOLDERS_PLAN.relative_to(ROOT)} must be present",
    )
    require(
        HAR_ARTIFACT_IGNORE_PLAN in plans,
        f"{HAR_ARTIFACT_IGNORE_PLAN.relative_to(ROOT)} must be present",
    )
    require(
        LOCAL_METADATA_IGNORE_PLAN in plans,
        f"{LOCAL_METADATA_IGNORE_PLAN.relative_to(ROOT)} must be present",
    )
    require(
        WORKFLOW_HARDENING_PLAN in plans,
        f"{WORKFLOW_HARDENING_PLAN.relative_to(ROOT)} must be present",
    )
    require(
        TRACKED_SECRET_SCAN_PLAN in plans,
        f"{TRACKED_SECRET_SCAN_PLAN.relative_to(ROOT)} must be present",
    )
    require(
        SECRET_SYNTAX_PLAN in plans,
        f"{SECRET_SYNTAX_PLAN.relative_to(ROOT)} must be present",
    )

    for plan in plans:
        text = plan.read_text(encoding="utf-8")
        require("Status: Completed" in text, f"{plan.name} must be completed")
        require("make check" in text, f"{plan.name} must document make check verification")


def main():
    checks = [
        check_required_files,
        check_placeholder_scope,
        check_secret_hygiene,
        check_tracked_secret_patterns,
        check_secret_pattern_syntaxes,
        check_greetings_workflow,
        check_hosted_verification,
        check_docs_plans,
    ]
    try:
        for check in checks:
            check()
    except (AssertionError, ET.ParseError) as exc:
        return fail(str(exc))

    print(f"Repository contracts passed ({len(checks)} checks).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
