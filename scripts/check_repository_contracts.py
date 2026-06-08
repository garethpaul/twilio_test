#!/usr/bin/env python3
"""Static integrity checks for the sparse Twilio placeholder repository."""

from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]


def fail(message):
    print(f"check_repository_contracts.py: {message}", file=sys.stderr)
    return 1


def read_text(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def check_required_files():
    for relative_path in [
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


def check_greetings_workflow():
    workflow = read_text(".github/workflows/greetings.yml")
    require("actions/first-interaction@v1" in workflow, "greetings workflow must keep first-interaction action explicit")
    require("repo-token:" in workflow, "greetings workflow must keep token wiring explicit")
    require("TWILIO_" not in workflow, "placeholder workflow must not reference Twilio credentials")
    require("issue-message:" in workflow, "greetings workflow must keep issue greeting explicit")


def main():
    checks = [
        check_required_files,
        check_placeholder_scope,
        check_greetings_workflow,
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
