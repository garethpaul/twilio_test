#!/usr/bin/env python3
"""Static integrity checks for the sparse Twilio placeholder repository."""

from pathlib import Path
import os
import re
import stat
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
UTF16_SECRET_SCAN_PLAN = DOCS_PLANS / "2026-06-13-utf16-tracked-secret-scan.md"
UTF32_SECRET_SCAN_PLAN = DOCS_PLANS / "2026-06-13-utf32-tracked-secret-scan.md"
MAKE_ROOT_PROTECTION_PLAN = DOCS_PLANS / "2026-06-14-make-root-override-protection.md"
DEFAULT_GREETING_INPUTS_PLAN = DOCS_PLANS / "2026-06-14-default-context-greeting-inputs.md"
DEEP_REVIEW_PLAN = DOCS_PLANS / "2026-06-19-deep-review-boundaries.md"
MAKE_AUTHORITY_PLAN = DOCS_PLANS / "2026-06-21-make-authority-hardening.md"
STAGED_SECRET_SNAPSHOT_PLAN = DOCS_PLANS / "2026-06-25-staged-secret-snapshot-scan.md"
MAX_TRACKED_FILE_BYTES = 1024 * 1024
MAX_TRACKED_TOTAL_BYTES = 16 * 1024 * 1024
MAX_TRACKED_FILES = 4096
ALLOWED_SOURCE_PATHS = {
    "scripts/check_repository_contracts.py",
    "scripts/run-make.sh",
    "scripts/test_greetings_runtime.py",
    "scripts/test_makefile_authority.py",
    "tests/test_repository_contracts.py",
}
RUNTIME_MANIFESTS = {
    "Gemfile",
    "Package.swift",
    "Podfile",
    "build.gradle",
    "build.gradle.kts",
    "composer.json",
    "go.mod",
    "package.json",
    "pom.xml",
    "pyproject.toml",
    "requirements.txt",
}
RUNTIME_SUFFIXES = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".dart",
    ".ex",
    ".exs",
    ".fs",
    ".go",
    ".h",
    ".hpp",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".kts",
    ".lua",
    ".m",
    ".mm",
    ".mjs",
    ".php",
    ".pl",
    ".py",
    ".rb",
    ".rs",
    ".scala",
    ".sh",
    ".swift",
    ".ts",
    ".tsx",
}

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


def is_text_candidate(text):
    if not text:
        return False
    return all(character in "\t\n\r" or ord(character) >= 32 and ord(character) != 127 for character in text)


def matches_null_layout(data, width, significant_lane):
    if len(data) < width or len(data) % width:
        return False
    lanes = [data[index::width] for index in range(width)]
    for index, lane in enumerate(lanes):
        null_fraction = lane.count(0) / len(lane)
        if index == significant_lane:
            if null_fraction > 0.2:
                return False
        elif null_fraction < 0.75:
            return False
    return True


def decode_tracked_text(data):
    if data.startswith((b"\xff\xfe\x00\x00", b"\x00\x00\xfe\xff")):
        try:
            return data.decode("utf-32")
        except UnicodeDecodeError:
            return None
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        try:
            return data.decode("utf-16")
        except UnicodeDecodeError:
            return None
    if data.startswith(b"\xef\xbb\xbf"):
        try:
            return data.decode("utf-8-sig")
        except UnicodeDecodeError:
            return None
    for encoding, width, significant_lane in [
        ("utf-32-le", 4, 0),
        ("utf-32-be", 4, 3),
        ("utf-16-le", 2, 0),
        ("utf-16-be", 2, 1),
    ]:
        if not matches_null_layout(data, width, significant_lane):
            continue
        try:
            decoded = data.decode(encoding)
        except UnicodeDecodeError:
            continue
        if is_text_candidate(decoded):
            return decoded
    if b"\0" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def tracked_index_entries():
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "--stage", "-z"],
            check=True,
            capture_output=True,
            timeout=10,
        )
    except subprocess.SubprocessError as exc:
        raise AssertionError("unable to enumerate tracked files safely") from exc
    records = [record for record in result.stdout.split(b"\0") if record]
    require(len(records) <= MAX_TRACKED_FILES, f"tracked file count exceeds {MAX_TRACKED_FILES}")
    entries = []
    for record in records:
        try:
            metadata, path_bytes = record.split(b"\t", 1)
            mode, object_id, stage = metadata.split(b" ", 2)
            relative_path = path_bytes.decode("utf-8")
        except (UnicodeDecodeError, ValueError) as exc:
            raise AssertionError("tracked paths and index records must use canonical UTF-8") from exc
        path = Path(relative_path)
        require(not path.is_absolute() and ".." not in path.parts, "tracked path must remain repository-relative")
        require(stage == b"0", f"{relative_path} must not contain unresolved index stages")
        require(
            re.fullmatch(rb"(?:[0-9a-f]{40}|[0-9a-f]{64})", object_id) is not None,
            f"{relative_path} must reference a canonical Git object ID",
        )
        entries.append((mode.decode("ascii"), object_id.decode("ascii"), relative_path))
    return entries


def read_tracked_regular_file(mode, relative_path):
    require(mode in {"100644", "100755"}, f"{relative_path} must be a tracked regular file, not a symlink or special entry")
    path = ROOT / relative_path
    try:
        metadata = path.lstat()
    except OSError as exc:
        raise AssertionError(f"{relative_path} must exist as a tracked regular file") from exc
    require(stat.S_ISREG(metadata.st_mode), f"{relative_path} must be a regular file, not a symlink or special entry")
    require(
        metadata.st_size <= MAX_TRACKED_FILE_BYTES,
        f"{relative_path} exceeds the {MAX_TRACKED_FILE_BYTES}-byte tracked-file size limit",
    )
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
        try:
            opened_metadata = os.fstat(descriptor)
            require(stat.S_ISREG(opened_metadata.st_mode), f"{relative_path} must remain a regular file while scanned")
            require(
                (opened_metadata.st_dev, opened_metadata.st_ino) == (metadata.st_dev, metadata.st_ino),
                f"{relative_path} changed while its type was validated",
            )
            data = bytearray()
            while len(data) <= MAX_TRACKED_FILE_BYTES:
                chunk = os.read(descriptor, min(65536, MAX_TRACKED_FILE_BYTES + 1 - len(data)))
                if not chunk:
                    break
                data.extend(chunk)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise AssertionError(f"{relative_path} could not be opened safely without following links") from exc
    require(len(data) <= MAX_TRACKED_FILE_BYTES, f"{relative_path} grew beyond the tracked-file size limit")
    return bytes(data)


def read_tracked_index_blob(mode, object_id, relative_path):
    require(mode in {"100644", "100755"}, f"{relative_path} must be a tracked regular file, not a symlink or special entry")
    try:
        size_result = subprocess.run(
            ["git", "-C", str(ROOT), "cat-file", "-s", object_id],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        size = int(size_result.stdout.strip())
    except (subprocess.SubprocessError, ValueError) as exc:
        raise AssertionError(f"{relative_path} staged blob size could not be read safely") from exc
    require(size <= MAX_TRACKED_FILE_BYTES, f"{relative_path} staged blob exceeds the tracked-file size limit")
    try:
        blob_result = subprocess.run(
            ["git", "-C", str(ROOT), "cat-file", "blob", object_id],
            check=True,
            capture_output=True,
            timeout=10,
        )
    except subprocess.SubprocessError as exc:
        raise AssertionError(f"{relative_path} staged blob could not be read safely") from exc
    require(len(blob_result.stdout) == size, f"{relative_path} staged blob size changed while scanned")
    return blob_result.stdout


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
        "scripts/run-make.sh",
        "scripts/test_greetings_runtime.py",
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
    require(
        "docs/plans/2026-06-25-staged-secret-snapshot-scan.md" in readme,
        "README must link the staged secret snapshot plan",
    )
    for _mode, _object_id, relative_path in tracked_index_entries():
        path = Path(relative_path)
        is_runtime_surface = path.name in RUNTIME_MANIFESTS or path.suffix.lower() in RUNTIME_SUFFIXES
        require(
            not is_runtime_surface or relative_path in ALLOWED_SOURCE_PATHS,
            f"placeholder repository must not add provider runtime surface: {relative_path}",
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
    total_bytes = 0
    for mode, object_id, relative_path in tracked_index_entries():
        snapshots = [
            ("staged", read_tracked_index_blob(mode, object_id, relative_path)),
            ("worktree", read_tracked_regular_file(mode, relative_path)),
        ]
        for snapshot_name, data in snapshots:
            total_bytes += len(data)
            require(
                total_bytes <= MAX_TRACKED_TOTAL_BYTES,
                f"tracked-file aggregate scan exceeds the {MAX_TRACKED_TOTAL_BYTES}-byte budget",
            )
            text = decode_tracked_text(data)
            if text is None:
                continue
            for pattern, description in TRACKED_SECRET_PATTERNS:
                require(
                    pattern.search(text) is None,
                    f"{relative_path} {snapshot_name} snapshot contains a real-looking {description}",
                )


def check_secret_pattern_syntaxes():
    token = "0" * 32
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


def check_secret_pattern_encodings():
    token_assignment = "TWILIO_AUTH_TOKEN: " + "0" * 32
    encoded_fixtures = {
        "UTF-8 BOM": token_assignment.encode("utf-8-sig"),
        "UTF-16 LE": b"\xff\xfe" + token_assignment.encode("utf-16-le"),
        "UTF-16 BE": b"\xfe\xff" + token_assignment.encode("utf-16-be"),
        "UTF-32 LE": b"\xff\xfe\x00\x00" + token_assignment.encode("utf-32-le"),
        "UTF-32 BE": b"\x00\x00\xfe\xff" + token_assignment.encode("utf-32-be"),
        "UTF-16 LE without BOM": token_assignment.encode("utf-16-le"),
        "UTF-16 BE without BOM": token_assignment.encode("utf-16-be"),
        "UTF-32 LE without BOM": token_assignment.encode("utf-32-le"),
        "UTF-32 BE without BOM": token_assignment.encode("utf-32-be"),
    }
    for encoding, fixture in encoded_fixtures.items():
        decoded = decode_tracked_text(fixture)
        require(decoded == token_assignment, f"{encoding} tracked text must decode consistently")
        require(
            any(pattern.search(decoded) for pattern, _ in TRACKED_SECRET_PATTERNS),
            f"tracked-secret patterns must reject {encoding} credential assignments",
        )
    require(decode_tracked_text(b"\x00\x01\x02\x03") is None, "binary data must remain skipped")
    require(decode_tracked_text(b"\xff\xfe\x00") is None, "malformed UTF-16 must remain skipped")
    require(
        decode_tracked_text(b"\xff\xfe\x00\x00\x00") is None,
        "malformed UTF-32 must remain skipped",
    )


def check_greetings_workflow():
    workflow = read_text(".github/workflows/greetings.yml")
    require("issues:\n    types:\n      - opened" in workflow, "greetings workflow must greet newly opened issues")
    require(
        "pull_request_target:\n    types:\n      - opened\n      - reopened\n      - synchronize" in workflow,
        "greetings workflow must recover pull-request greetings after opening, reopening, and synchronization",
    )
    require("contents: read" in workflow, "greetings workflow must keep contents read-only")
    require("issues: write" in workflow, "greetings workflow must allow issue comments")
    require("pull-requests: write" in workflow, "greetings workflow must allow pull-request comments")
    require("timeout-minutes: 2" in workflow, "greetings workflow must have a bounded runtime")
    require("runs-on: ubuntu-24.04" in workflow, "greetings workflow must use Ubuntu 24.04")
    require("ubuntu-latest" not in workflow, "greetings workflow must not use a floating runner")
    require(workflow.count("runs-on: ubuntu-24.04") == 2, "both greeting jobs must use Ubuntu 24.04")
    require(
        workflow.count("actions/first-interaction@1c4688942c71f71d4f5502a26ea67c331730fa4d # v3.1.0") == 1,
        "only the issue greeting may use the annotated first-interaction pin",
    )
    require(
        workflow.count("actions/github-script@3a2844b7e9c422d3c10d287c895573f7108da1b3 # v9.0.0") == 1,
        "pull-request greetings must use the annotated github-script pin",
    )
    require("repo_token: ${{ github.token }}" in workflow, "greetings workflow must use the repository token")
    require("github-token: ${{ github.token }}" in workflow, "pull-request greeting must use the repository token")
    require("TWILIO_" not in workflow, "placeholder workflow must not reference Twilio credentials")
    require(workflow.count("issue_message: 'Ahoy!'") == 1, "issue greeting must provide the required issue message")
    require(workflow.count("pr_message: 'Ahoy!'") == 1, "issue action must receive its required pull-request input")
    require("@v" not in workflow, "greetings workflow action must use an immutable commit")
    require("actions/checkout" not in workflow, "pull_request_target workflow must not check out contributor code")
    require(not re.search(r"^\s*run:", workflow, re.MULTILINE), "pull_request_target workflow must not execute commands")
    require("if: github.event_name == 'issues'" in workflow, "issue greeting must be event-scoped")
    require("if: github.event_name == 'pull_request_target'" in workflow, "pull-request greeting must be event-scoped")
    require(
        "group: greetings-${{ github.repository }}-${{ github.event.pull_request.number || github.event.issue.number }}" in workflow,
        "all greeting events must share deterministic per-item serialization",
    )
    require("cancel-in-progress: false" in workflow, "greeting serialization must not cancel an active run")
    require("const marker = '<!-- twilio-test:first-contributor-greeting:v1 -->'" in workflow, "pull-request greeting must use the deterministic marker")
    require("context.payload.pull_request?.user?.login" in workflow, "eligibility must use the trusted pull-request author")
    require("context.payload.sender" not in workflow, "recovery eligibility must not depend on the event sender")
    require(workflow.count("github.paginate(") == 3, "pull-request greeting must paginate comments, issues, and pull requests")
    require("github.rest.issues.listComments" in workflow, "pull-request greeting must inspect existing comments")
    require("github.rest.issues.listForRepo" in workflow, "pull-request greeting must inspect issue history")
    require("github.rest.pulls.list" in workflow, "pull-request greeting must inspect pull-request history")
    require(workflow.count("per_page: 100") == 3, "all greeting history queries must request full pages")
    require("comment.user?.login === 'github-actions[bot]'" in workflow, "only the automation identity may satisfy greeting state")
    require("comment.body?.includes(marker)" in workflow, "pull-request greeting must recognize the deterministic marker")
    require("comment.body?.trim() === greeting" in workflow, "pull-request greeting must recognize legacy exact greetings")
    require("issue.pull_request === undefined && issue.number < issueNumber" in workflow, "eligibility must reject prior authored issues")
    require("pull.user?.login === author && pull.number < issueNumber" in workflow, "eligibility must reject prior authored pull requests")
    require("hasPriorIssue || hasPriorPullRequest" in workflow, "any prior contribution must suppress the greeting")
    require("github.rest.issues.createComment" in workflow, "eligible pull requests must receive the greeting comment")
    require(workflow.count("uses:") == 2, "greetings workflow must run only the two pinned greeting actions")
    require(workflow.count("issues: write") == 1, "only the issue greeting may write issues")
    require(workflow.count("pull-requests: write") == 1, "only the pull-request greeting may write pull requests")
    write_permissions = re.findall(r"^\s+([a-z-]+): write$", workflow, re.MULTILINE)
    require(sorted(write_permissions) == ["issues", "pull-requests"], "greeting jobs must not gain additional write permissions")
    require("${{ secrets." not in workflow, "greetings workflow must not read repository secrets")


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
        "actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7.0.0",
        "persist-credentials: false",
        "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405 # v6.2.0",
        "run: ./scripts/run-make.sh check",
    ]:
        require(contract in workflow, f"hosted verification must include {contract!r}")
    require("ubuntu-latest" not in workflow, "hosted verification must not use a floating runner")
    require("@v" not in workflow, "hosted verification actions must use immutable commits")
    require("run: make check" not in workflow, "hosted verification must not invoke raw Make")
    require(workflow.count("run:") == 1, "hosted verification must expose only the reviewed Make wrapper command")
    wrapper = read_text("scripts/run-make.sh")
    wrapper_lines = set(wrapper.splitlines())
    for wrapper_contract in [
        "#!/bin/sh",
        "set -eu",
        "while [ -L \"$SCRIPT_PATH\" ]; do",
        "  if ! LINK_TARGET_WITH_SENTINEL=$(/usr/bin/readlink -n \"$SCRIPT_PATH\" && printf x); then",
        "ROOT_DIR=$(CDPATH='' cd -P \"$SCRIPT_DIR/..\" && /bin/pwd -P)",
        "  check|lint) TARGET=$1 ;;",
        'exec /usr/bin/env -u MAKEFILES -u MAKEFLAGS -u MFLAGS -u MAKEOVERRIDES -u GNUMAKEFLAGS /usr/bin/make --no-print-directory -f "$ROOT_DIR/Makefile" "$TARGET"',
    ]:
        require(wrapper_contract in wrapper_lines, f"Make wrapper must include {wrapper_contract!r}")
    require("$@" not in wrapper, "Make wrapper must not forward unrestricted arguments")
    require("LINK_COUNT=0" in wrapper and '"$LINK_COUNT" -gt 40' in wrapper, "Make wrapper must bound symlink resolution")
    makefile = read_text("Makefile")
    makefile_lines = set(makefile.splitlines())
    require(
        "override ROOT := $(REPOSITORY_ROOT)" in makefile_lines,
        "Makefile must protect the repository root derived from its own location",
    )
    require(
        "PYTHON ?= python3" in makefile_lines,
        "Makefile must preserve the Python command override",
    )
    require(
        "override PYTHON := $(value PYTHON)" in makefile_lines,
        "Makefile must preserve Python command text without Make re-expansion",
    )
    for authority_contract in [
        "override SHELL := /bin/sh",
        "MAKEFLAGS must not be overridden for repository verification",
        "MAKEFILES must be empty; repository verification requires this Makefile to be loaded alone",
        "MAKEFILE_LIST must not be overridden",
    ]:
        require(authority_contract in makefile, f"Makefile must include {authority_contract!r}")
    require(
        '$$PYTHON "$$ROOT/scripts/check_repository_contracts.py"' in makefile,
        "Makefile must run the checker independently of the caller's directory",
    )
    require(
        '$$PYTHON "$$ROOT/scripts/test_greetings_runtime.py"' in makefile,
        "Makefile must run the executable greeting regressions independently of the caller's directory",
    )
    require(
        '$$PYTHON "$$ROOT/scripts/test_makefile_authority.py"' in makefile,
        "Makefile must run the adversarial authority regressions independently of the caller's directory",
    )
    expected_recipes = {
        "@:",
        '$$PYTHON "$$ROOT/scripts/check_repository_contracts.py"',
        '$$PYTHON -m unittest discover -v -s "$$ROOT/tests" -p "test_*.py"',
        '$$PYTHON "$$ROOT/scripts/test_greetings_runtime.py"',
        '$$PYTHON "$$ROOT/scripts/test_makefile_authority.py"',
    }
    recipes = {line.strip() for line in makefile.splitlines() if line.startswith("\t")}
    require(recipes == expected_recipes, "Makefile recipes must remain limited to reviewed verification commands")


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
    require(
        UTF16_SECRET_SCAN_PLAN in plans,
        f"{UTF16_SECRET_SCAN_PLAN.relative_to(ROOT)} must be present",
    )
    require(
        UTF32_SECRET_SCAN_PLAN in plans,
        f"{UTF32_SECRET_SCAN_PLAN.relative_to(ROOT)} must be present",
    )
    require(
        MAKE_ROOT_PROTECTION_PLAN in plans,
        f"{MAKE_ROOT_PROTECTION_PLAN.relative_to(ROOT)} must be present",
    )
    require(
        DEFAULT_GREETING_INPUTS_PLAN in plans,
        f"{DEFAULT_GREETING_INPUTS_PLAN.relative_to(ROOT)} must be present",
    )
    require(DEEP_REVIEW_PLAN in plans, f"{DEEP_REVIEW_PLAN.relative_to(ROOT)} must be present")
    require(MAKE_AUTHORITY_PLAN in plans, f"{MAKE_AUTHORITY_PLAN.relative_to(ROOT)} must be present")
    require(
        STAGED_SECRET_SNAPSHOT_PLAN in plans,
        f"{STAGED_SECRET_SNAPSHOT_PLAN.relative_to(ROOT)} must be present",
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
        check_secret_pattern_encodings,
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
