#!/usr/bin/env python3
"""Static integrity checks for the sparse Twilio placeholder repository."""

from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DOCS_PLANS = ROOT / "docs/plans"
CANONICAL_PLAN = DOCS_PLANS / "2026-06-08-twilio-test-baseline.md"
EMPTY_ENV_PLACEHOLDERS_PLAN = DOCS_PLANS / "2026-06-09-empty-env-placeholders.md"
UNIQUE_ENV_PLACEHOLDERS_PLAN = DOCS_PLANS / "2026-06-09-env-example-unique-placeholders.md"
HAR_ARTIFACT_IGNORE_PLAN = DOCS_PLANS / "2026-06-09-har-artifact-ignore.md"
LOCAL_METADATA_IGNORE_PLAN = DOCS_PLANS / "2026-06-09-local-metadata-ignore.md"


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
        "__pycache__/",
        "*.pyc",
        ".DS_Store",
        ".idea/",
        ".vscode/",
        "*.iml",
    ]:
        require(pattern in gitignore, f".gitignore must include {pattern}")

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


def check_greetings_workflow():
    workflow = read_text(".github/workflows/greetings.yml")
    require("actions/first-interaction@v1" in workflow, "greetings workflow must keep first-interaction action explicit")
    require("repo-token:" in workflow, "greetings workflow must keep token wiring explicit")
    require("TWILIO_" not in workflow, "placeholder workflow must not reference Twilio credentials")
    require("issue-message:" in workflow, "greetings workflow must keep issue greeting explicit")


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

    for plan in plans:
        text = plan.read_text(encoding="utf-8")
        require("Status: Completed" in text, f"{plan.name} must be completed")
        require("make check" in text, f"{plan.name} must document make check verification")


def main():
    checks = [
        check_required_files,
        check_placeholder_scope,
        check_secret_hygiene,
        check_greetings_workflow,
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
