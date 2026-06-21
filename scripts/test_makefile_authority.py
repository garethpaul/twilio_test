#!/usr/bin/env python3
"""Exercise hostile Make inputs without running repository or provider code."""

from pathlib import Path
import os
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
MAKEFILE = ROOT / "Makefile"


def run_make(control, *arguments, environment=None):
    return subprocess.run(
        ["/usr/bin/make", "--no-print-directory", "-f", str(MAKEFILE), *arguments],
        cwd=control,
        env=environment,
        capture_output=True,
        text=True,
        timeout=10,
    )


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    with tempfile.TemporaryDirectory(prefix="twilio-test-make-authority-") as temporary:
        temporary_root = Path(temporary)
        control = temporary_root / "control"
        attacker_root = temporary_root / "attacker"
        marker = temporary_root / "make-syntax-expanded"
        tool_log = temporary_root / "tool.log"
        control.mkdir()
        attacker_root.mkdir()
        fake_python = temporary_root / "fake-python"
        fake_python.write_text(
            "#!/bin/sh\n"
            f"printf 'cwd=%s args=%s\\n' \"$PWD\" \"$*\" >> {tool_log!s}\n",
            encoding="utf-8",
        )
        fake_python.chmod(0o755)

        result = run_make(
            control,
            "lint",
            f"ROOT={attacker_root}",
            f"PYTHON={fake_python} --isolated",
        )
        require(result.returncode == 0, result.stderr)
        log = tool_log.read_text(encoding="utf-8")
        require(
            str(ROOT / "scripts/check_repository_contracts.py") in log,
            "ROOT redirected verification",
        )
        require("args=--isolated" in log, "multiword PYTHON override was not preserved")
        require(str(attacker_root) not in log, "attacker root reached the tool invocation")

        tool_log.write_text("", encoding="utf-8")
        result = run_make(control, "lint", "SHELL=/bin/false", f"PYTHON={fake_python}")
        require(result.returncode == 0, result.stderr)
        require(
            str(ROOT / "scripts/check_repository_contracts.py")
            in tool_log.read_text(encoding="utf-8"),
            "caller shell replaced repository shell",
        )

        result = run_make(
            control,
            "lint",
            f"PYTHON=$(shell /usr/bin/touch '{marker}')python3",
        )
        require(result.returncode != 0, "Make-syntax PYTHON unexpectedly passed")
        require(not marker.exists(), "Make-syntax PYTHON expanded before rejection")
        require("PYTHON must be literal command text" in result.stderr, "Make-syntax rejection was not explicit")

        result = run_make(control, "lint", "MAKEFLAGS=--just-print")
        require(result.returncode != 0, "MAKEFLAGS unexpectedly passed")
        require("MAKEFLAGS must not be overridden" in result.stderr, "MAKEFLAGS rejection was not explicit")

        startup = temporary_root / "startup.mk"
        startup.write_text("STARTUP_FILE_LOADED := yes\n", encoding="utf-8")
        environment = os.environ.copy()
        environment["MAKEFILES"] = str(startup)
        result = run_make(control, "lint", environment=environment)
        require(result.returncode != 0, "MAKEFILES unexpectedly passed")
        require("MAKEFILES must be empty" in result.stderr, "MAKEFILES rejection was not explicit")

        result = run_make(
            control,
            "lint",
            f"PYTHON={fake_python}",
            f"MAKEFILE_LIST={temporary_root / 'attacker.mk'}",
        )
        require(result.returncode != 0, "MAKEFILE_LIST unexpectedly passed")
        require("MAKEFILE_LIST must not be overridden" in result.stderr, "MAKEFILE_LIST rejection was not explicit")

    print("Make authority tests passed: root, shell, Python command, MAKEFLAGS, MAKEFILES, and MAKEFILE_LIST")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
