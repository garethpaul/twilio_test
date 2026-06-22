#!/usr/bin/env python3
"""Exercise hostile Make inputs without running repository or provider code."""

from pathlib import Path
import os
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
MAKEFILE = ROOT / "Makefile"
WRAPPER = ROOT / "scripts/run-make.sh"


def find_gnu_make_4():
    candidates = [shutil.which("gmake"), "/usr/bin/make"]
    for candidate in candidates:
        if not candidate:
            continue
        result = subprocess.run(
            [candidate, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        first_line = result.stdout.splitlines()[0] if result.stdout else ""
        if result.returncode == 0 and first_line.startswith("GNU Make 4."):
            return Path(candidate)
    return None


GNU_MAKE_4 = find_gnu_make_4()


def run_make(control, *arguments, environment=None):
    return subprocess.run(
        ["/usr/bin/make", "--no-print-directory", "-f", str(MAKEFILE), *arguments],
        cwd=control,
        env=environment,
        capture_output=True,
        text=True,
        timeout=10,
    )


def run_gnu_make_4(control, *arguments, environment=None):
    return subprocess.run(
        [str(GNU_MAKE_4), "--no-print-directory", *arguments],
        cwd=control,
        env=environment,
        capture_output=True,
        text=True,
        timeout=10,
    )


def run_raw_make(control, *arguments, environment=None):
    return subprocess.run(
        ["/usr/bin/make", "--no-print-directory", *arguments],
        cwd=control,
        env=environment,
        capture_output=True,
        text=True,
        timeout=10,
    )


def run_wrapper(control, *arguments, environment=None, executable=None):
    return subprocess.run(
        [str(executable or WRAPPER), *arguments],
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

        if GNU_MAKE_4 is not None:
            result = run_gnu_make_4(
                control,
                "-n",
                "--eval=override MAKEFLAGS :=",
                "-f",
                str(MAKEFILE),
                "lint",
                f"PYTHON={fake_python}",
            )
            require(result.returncode == 0, result.stderr)
            require(not tool_log.exists(), "dry-run bypass unexpectedly executed verification")

            result = run_gnu_make_4(
                control,
                "-i",
                "--eval=override MAKEFLAGS :=",
                "-f",
                str(MAKEFILE),
                "lint",
                "PYTHON=/bin/false",
            )
            require(result.returncode == 0, "ignore-errors bypass did not reproduce")

            environment = os.environ.copy()
            environment["GNUMAKEFLAGS"] = "-n"
            result = run_gnu_make_4(
                control,
                "--eval=override MAKEFLAGS :=",
                "-f",
                str(MAKEFILE),
                "lint",
                f"PYTHON={fake_python}",
                environment=environment,
            )
            require(result.returncode == 0, result.stderr)
            require(not tool_log.exists(), "GNUMAKEFLAGS bypass unexpectedly executed verification")

        startup_marker = temporary_root / "startup-executed"
        startup = temporary_root / "startup.mk"
        startup.write_text(
            f"$(shell /usr/bin/touch '{startup_marker}')\n"
            "override MAKEFILES :=\n",
            encoding="utf-8",
        )
        environment = os.environ.copy()
        environment["MAKEFILES"] = str(startup)
        result = run_make(control, "lint", f"PYTHON={fake_python}", environment=environment)
        require(result.returncode == 0, result.stderr)
        require(startup_marker.exists(), "MAKEFILES execution bypass did not reproduce")

        earlier_marker = temporary_root / "earlier-file-executed"
        earlier = temporary_root / "earlier.mk"
        earlier.write_text(
            f"$(shell /usr/bin/touch '{earlier_marker}')\n",
            encoding="utf-8",
        )
        result = run_raw_make(
            control,
            "-f",
            str(earlier),
            "-f",
            str(MAKEFILE),
            "lint",
            f"PYTHON={fake_python}",
        )
        require(result.returncode == 0, result.stderr)
        require(earlier_marker.exists(), "earlier -f execution bypass did not reproduce")

        later_marker = temporary_root / "later-file-executed"
        later = temporary_root / "later.mk"
        later.write_text(
            f"$(shell /usr/bin/touch '{later_marker}')\n",
            encoding="utf-8",
        )
        result = run_raw_make(
            control,
            "-f",
            str(MAKEFILE),
            "-f",
            str(later),
            "lint",
            f"PYTHON={fake_python}",
        )
        require(result.returncode == 0, result.stderr)
        require(later_marker.exists(), "later -f execution bypass did not reproduce")

        require(WRAPPER.is_file(), "sanitized Make wrapper is missing")

        hostile_startup_marker = temporary_root / "wrapper-startup-executed"
        hostile_startup = temporary_root / "wrapper-startup.mk"
        hostile_startup.write_text(
            f"$(shell /usr/bin/touch '{hostile_startup_marker}')\n",
            encoding="utf-8",
        )
        tool_log.unlink(missing_ok=True)
        environment = os.environ.copy()
        environment.update(
            {
                "PYTHON": f"{fake_python} --isolated",
                "MAKEFILES": str(hostile_startup),
                "MAKEFLAGS": "--just-print",
                "MFLAGS": "-n",
                "MAKEOVERRIDES": "ROOT",
                "GNUMAKEFLAGS": "-n",
            }
        )
        result = run_wrapper(control, "lint", environment=environment)
        require(result.returncode == 0, result.stderr)
        require(not hostile_startup_marker.exists(), "wrapper allowed MAKEFILES execution")
        require(tool_log.exists(), "wrapper allowed a Make option channel to skip verification")
        log = tool_log.read_text(encoding="utf-8")
        require(str(ROOT / "scripts/check_repository_contracts.py") in log, "wrapper redirected repository root")
        require("args=--isolated" in log, "wrapper did not preserve literal multiword PYTHON")

        for arguments in [(), ("verify",), ("-n",), ("ROOT=/tmp",), ("lint", "check")]:
            result = run_wrapper(control, *arguments, environment=os.environ.copy())
            require(result.returncode != 0, f"wrapper accepted unsupported arguments: {arguments!r}")

        link_root = temporary_root / "external-links"
        link_root.mkdir()
        physical_link = link_root / "physical\n"
        entry_link = link_root / "run-make.sh"
        physical_link.symlink_to(WRAPPER)
        entry_link.symlink_to("physical\n")
        tool_log.unlink(missing_ok=True)
        environment = os.environ.copy()
        environment["PYTHON"] = str(fake_python)
        result = run_wrapper(control, "lint", environment=environment, executable=entry_link)
        require(result.returncode == 0, result.stderr)
        require(
            str(ROOT / "scripts/check_repository_contracts.py") in tool_log.read_text(encoding="utf-8"),
            "symlink invocation redirected repository root",
        )

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

        startup = temporary_root / "startup-detected.mk"
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

    print(
        "Make authority tests passed: raw bypass reproduction, sanitized wrapper, "
        "root, shell, Python command, Make controls, and physical symlinks"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
