#!/usr/bin/env python3
"""Behavioral tests for repository boundary enforcement."""

from contextlib import contextmanager
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = REPOSITORY_ROOT / "scripts/check_repository_contracts.py"
SPEC = importlib.util.spec_from_file_location("repository_contracts", CHECKER_PATH)
CONTRACTS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTRACTS)


def git(repository, *arguments):
    return subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )


@contextmanager
def temporary_repository(copy_checkout=False):
    with tempfile.TemporaryDirectory() as temporary_directory:
        repository = Path(temporary_directory) / "repository"
        if copy_checkout:
            shutil.copytree(
                REPOSITORY_ROOT,
                repository,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
            )
        else:
            repository.mkdir()
        git(repository, "init", "--quiet")
        git(repository, "config", "user.name", "Contract Tests")
        git(repository, "config", "user.email", "contracts@example.invalid")
        if copy_checkout:
            git(repository, "add", ".")
        with mock.patch.object(CONTRACTS, "ROOT", repository):
            yield repository


class TrackedTextDecodingTests(unittest.TestCase):
    def test_decodes_utf8_bom(self):
        text = "TWILIO_AUTH_TOKEN=" + "0123456789abcdef" * 2
        self.assertEqual(CONTRACTS.decode_tracked_text(text.encode("utf-8-sig")), text)

    def test_decodes_bomless_utf16_and_utf32(self):
        text = "TWILIO_AUTH_TOKEN=" + "0123456789abcdef" * 2
        for encoding in ("utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be"):
            with self.subTest(encoding=encoding):
                self.assertEqual(CONTRACTS.decode_tracked_text(text.encode(encoding)), text)


class TrackedFileBoundaryTests(unittest.TestCase):
    def test_rejects_tracked_symlink_without_following_it(self):
        with temporary_repository() as repository:
            outside = repository.parent / "outside.txt"
            outside.write_text("benign", encoding="utf-8")
            os.symlink(outside, repository / "linked.txt")
            git(repository, "add", "linked.txt")

            with self.assertRaisesRegex(AssertionError, "symlink|regular file"):
                CONTRACTS.check_tracked_secret_patterns()

    def test_rejects_oversized_tracked_file(self):
        with temporary_repository() as repository:
            (repository / "large.txt").write_bytes(b"a" * (1024 * 1024 + 1))
            git(repository, "add", "large.txt")

            with self.assertRaisesRegex(AssertionError, "size limit|too large|exceeds"):
                CONTRACTS.check_tracked_secret_patterns()

    def test_rejects_aggregate_scan_above_budget(self):
        with temporary_repository() as repository:
            for index in range(17):
                (repository / f"part-{index}.txt").write_bytes(b"a" * 1024 * 1024)
            git(repository, "add", ".")

            with self.assertRaisesRegex(AssertionError, "aggregate|budget|total"):
                CONTRACTS.check_tracked_secret_patterns()

    def test_rejects_bomless_utf32_secret_in_tracked_file(self):
        with temporary_repository() as repository:
            assignment = "TWILIO_AUTH_TOKEN=" + "0123456789abcdef" * 2
            (repository / "encoded.txt").write_bytes(assignment.encode("utf-32-be"))
            git(repository, "add", "encoded.txt")

            with self.assertRaisesRegex(AssertionError, "Twilio auth token"):
                CONTRACTS.check_tracked_secret_patterns()


class PlaceholderScopeTests(unittest.TestCase):
    def test_rejects_provider_runtime_source(self):
        with temporary_repository(copy_checkout=True) as repository:
            (repository / "send.py").write_text(
                "from twilio.rest import Client\nClient('account', 'token').messages.create()\n",
                encoding="utf-8",
            )
            git(repository, "add", "send.py")

            with self.assertRaisesRegex(AssertionError, "placeholder|runtime|provider"):
                CONTRACTS.check_placeholder_scope()


class WorkflowPolicyTests(unittest.TestCase):
    def test_uses_current_official_action_pins(self):
        check_workflow = (REPOSITORY_ROOT / ".github/workflows/check.yml").read_text(encoding="utf-8")
        greetings_workflow = (REPOSITORY_ROOT / ".github/workflows/greetings.yml").read_text(encoding="utf-8")

        self.assertIn(
            "actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7.0.0",
            check_workflow,
        )
        self.assertIn(
            "actions/github-script@3a2844b7e9c422d3c10d287c895573f7108da1b3 # v9.0.0",
            greetings_workflow,
        )

    def test_rejects_unreviewed_make_recipe(self):
        with temporary_repository(copy_checkout=True) as repository:
            with (repository / "Makefile").open("a", encoding="utf-8") as makefile:
                makefile.write("\nprovider-send:\n\tcurl https://api.twilio.com/send\n")

            with self.assertRaisesRegex(AssertionError, "Makefile|recipe|command|provider"):
                CONTRACTS.check_hosted_verification()

    def test_unittest_recipe_is_location_independent(self):
        makefile = (REPOSITORY_ROOT / "Makefile").read_text(encoding="utf-8")
        self.assertIn(
            '$(PYTHON) -m unittest discover -v -s "$(ROOT)/tests" -p "test_*.py"',
            makefile,
        )


if __name__ == "__main__":
    unittest.main()
