#!/usr/bin/env python3
"""Executable regressions for first-contributor pull-request greetings."""

from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import threading
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKFLOW = ROOT / ".github/workflows/greetings.yml"
FIRST_INTERACTION_SHA256 = "57adb4403a41c7fac012aa27fa9ff4336eb69d3cf84ff87c5af5f1dcbdf86e51"
FIRST_INTERACTION_URL = (
    "https://raw.githubusercontent.com/actions/first-interaction/"
    "1c4688942c71f71d4f5502a26ea67c331730fa4d/dist/index.js"
)
FIRST_INTERACTION_PIN = (
    "actions/first-interaction@1c4688942c71f71d4f5502a26ea67c331730fa4d # v3.1.0"
)
GITHUB_SCRIPT_PIN = "actions/github-script@ed597411d8f924073f98dfc5c65a23a2325f34cd # v8.0.0"


def fail(message: str) -> int:
    print(f"test_greetings_runtime.py: {message}", file=sys.stderr)
    return 1


def load_first_interaction_bundle(explicit_path: str | None) -> bytes:
    if explicit_path:
        data = Path(explicit_path).read_bytes()
    else:
        with urllib.request.urlopen(FIRST_INTERACTION_URL, timeout=30) as response:
            data = response.read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != FIRST_INTERACTION_SHA256:
        raise AssertionError(f"unexpected first-interaction bundle digest: {digest}")
    return data


class FirstInteractionApi(http.server.BaseHTTPRequestHandler):
    requests: list[tuple[str, str, object]] = []
    prior_issues: list[dict[str, object]] = []
    prior_pulls: list[dict[str, object]] = []

    def log_message(self, format_string: str, *arguments: object) -> None:
        return

    def send_json(self, status: int, payload: object) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        self.requests.append(("GET", parsed.path, query))
        if parsed.path.endswith("/issues"):
            self.send_json(200, self.prior_issues)
            return
        if parsed.path.endswith("/pulls"):
            self.send_json(200, self.prior_pulls)
            return
        self.send_json(404, {"message": "not found"})

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")
        parsed = urllib.parse.urlparse(self.path)
        self.requests.append(("POST", parsed.path, payload))
        if parsed.path.endswith("/issues/6/comments"):
            self.send_json(201, {"id": 1, "body": payload.get("body")})
            return
        self.send_json(404, {"message": "not found"})


def run_first_interaction(
    bundle: bytes,
    action: str,
    prior_issues: list[dict[str, object]],
    prior_pulls: list[dict[str, object]],
) -> tuple[subprocess.CompletedProcess[str], list[tuple[str, str, object]]]:
    FirstInteractionApi.requests = []
    FirstInteractionApi.prior_issues = prior_issues
    FirstInteractionApi.prior_pulls = prior_pulls
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), FirstInteractionApi)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    try:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            bundle_path = temporary_path / "first-interaction.mjs"
            event_path = temporary_path / "event.json"
            local_api = f"http://127.0.0.1:{server.server_port}".encode("utf-8")
            isolated_bundle = bundle.replace(b"https://api.github.com", local_api)
            bundle_path.write_bytes(isolated_bundle)
            event_path.write_text(
                json.dumps(
                    {
                        "action": action,
                        "number": 6,
                        "sender": {"login": "repeat-contributor"},
                        "repository": {"name": "twilio_test", "owner": {"login": "garethpaul"}},
                        "pull_request": {"number": 6, "user": {"login": "repeat-contributor"}},
                    }
                ),
                encoding="utf-8",
            )
            environment = os.environ.copy()
            environment.update(
                {
                    "GITHUB_ACTIONS": "true",
                    "GITHUB_ACTION": "first-interaction",
                    "GITHUB_API_URL": local_api.decode("utf-8"),
                    "GITHUB_EVENT_NAME": "pull_request_target",
                    "GITHUB_EVENT_PATH": str(event_path),
                    "GITHUB_REPOSITORY": "garethpaul/twilio_test",
                    "GITHUB_WORKSPACE": str(temporary_path),
                    "INPUT_REPO_TOKEN": "test-token",
                    "INPUT_ISSUE_MESSAGE": "Ahoy!",
                    "INPUT_PR_MESSAGE": "Ahoy!",
                    "RUNNER_TEMP": str(temporary_path),
                }
            )
            result = subprocess.run(
                ["node", str(bundle_path)],
                check=False,
                capture_output=True,
                text=True,
                env=environment,
                timeout=30,
            )
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=5)
    return result, list(FirstInteractionApi.requests)


def prove_pinned_first_interaction(bundle: bytes) -> None:
    first_result, first_requests = run_first_interaction(bundle, "opened", [], [])
    if first_result.returncode != 0:
        raise AssertionError(first_result.stdout + first_result.stderr)
    if len([request for request in first_requests if request[0] == "POST"]) != 1:
        raise AssertionError("pinned first-interaction must greet an eligible opened pull request")

    repeat_result, repeat_requests = run_first_interaction(
        bundle,
        "opened",
        [{"number": 2, "user": {"login": "repeat-contributor"}}],
        [{"number": 3, "user": {"login": "repeat-contributor"}}],
    )
    repeat_output = repeat_result.stdout + repeat_result.stderr
    if repeat_result.returncode != 0:
        raise AssertionError(repeat_output)
    if "Skipping...Not First Contribution" not in repeat_output:
        raise AssertionError("pinned first-interaction did not reject a repeat contributor")
    if any(request[0] == "POST" for request in repeat_requests):
        raise AssertionError("pinned first-interaction greeted a repeat contributor")

    for action in ("reopened", "synchronize"):
        skipped_result, skipped_requests = run_first_interaction(bundle, action, [], [])
        skipped_output = skipped_result.stdout + skipped_result.stderr
        if skipped_result.returncode != 0:
            raise AssertionError(skipped_output)
        if "Skipping...Not an Opened Event" not in skipped_output:
            raise AssertionError(f"pinned first-interaction did not skip {action}")
        if skipped_requests:
            raise AssertionError(f"pinned first-interaction called GitHub APIs for {action}")


def extract_github_script(workflow: str) -> str:
    lines = workflow.splitlines()
    action_index = next((index for index, line in enumerate(lines) if GITHUB_SCRIPT_PIN in line), None)
    if action_index is None:
        raise AssertionError("missing shared pinned github-script pull-request greeting")
    script_index = next(
        (index for index in range(action_index + 1, len(lines)) if lines[index].strip() == "script: |"),
        None,
    )
    if script_index is None:
        raise AssertionError("missing inline pull-request greeting script")
    indentation = len(lines[script_index]) - len(lines[script_index].lstrip())
    script_lines = []
    for line in lines[script_index + 1 :]:
        current_indentation = len(line) - len(line.lstrip())
        if line.strip() and current_indentation <= indentation:
            break
        script_lines.append(line)
    script = textwrap.dedent("\n".join(script_lines)).strip()
    if not script:
        raise AssertionError("empty pull-request greeting script")
    return script


def test_pull_request_script(script: str, legacy_opened_path: bool) -> None:
    runner = r"""
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const source = JSON.parse(process.argv[2]);
const legacyOpenedPath = process.argv[3] === 'true';
const marker = '<!-- twilio-test:first-contributor-greeting:v1 -->';
const greetingBody = `Ahoy!\n\n${marker}`;
const failures = [];

function fixture({ priorIssues = [], priorPulls = [], comments = [] } = {}) {
  const state = { comments: structuredClone(comments), creates: [], calls: [] };
  const methods = {
    listForRepo: Symbol('listForRepo'),
    listPulls: Symbol('listPulls'),
    listComments: Symbol('listComments'),
  };
  const github = {
    paginate: async (method, parameters) => {
      state.calls.push({ method, parameters });
      if (parameters.owner !== 'garethpaul' || parameters.repo !== 'twilio_test' || parameters.per_page !== 100) {
        throw new Error(`wrong pagination parameters: ${JSON.stringify(parameters)}`);
      }
      if (method === methods.listForRepo) return structuredClone(priorIssues);
      if (method === methods.listPulls) return structuredClone(priorPulls);
      if (method === methods.listComments) {
        if (parameters.issue_number !== 6) throw new Error('wrong issue number');
        return state.comments;
      }
      throw new Error('wrong pagination method');
    },
    rest: {
      issues: {
        listForRepo: methods.listForRepo,
        listComments: methods.listComments,
        createComment: async (parameters) => {
          if (JSON.stringify(parameters) !== JSON.stringify({
            owner: 'garethpaul', repo: 'twilio_test', issue_number: 6,
            body: legacyOpenedPath ? 'Ahoy!' : greetingBody
          })) throw new Error(`wrong create parameters: ${JSON.stringify(parameters)}`);
          state.creates.push(parameters);
          state.comments.push({ body: parameters.body, user: { login: 'github-actions[bot]' } });
        },
      },
      pulls: { list: methods.listPulls },
    },
  };
  return { state, github };
}

async function invokeShared(github, action) {
  const context = {
    issue: { number: 6, owner: 'garethpaul', repo: 'twilio_test' },
    payload: {
      action,
      pull_request: { number: 6, user: { login: 'first-contributor' } },
      sender: { login: action === 'opened' ? 'first-contributor' : 'maintainer' },
    },
  };
  const core = { info: () => {} };
  const run = new AsyncFunction('github', 'context', 'core', source);
  await run(github, context, core);
}

async function invokeLegacyOpened(state) {
  state.creates.push({ body: 'Ahoy!' });
  state.comments.push({ body: 'Ahoy!', user: { login: 'github-actions[bot]' } });
}

async function invokeEvent(testFixture, action) {
  if (legacyOpenedPath && action === 'opened') await invokeLegacyOpened(testFixture.state);
  else await invokeShared(testFixture.github, action);
}

{
  const repeat = fixture({
    priorIssues: [{ number: 2, user: { login: 'repeat-contributor' } }],
    priorPulls: [{ number: 3, user: { login: 'repeat-contributor' } }],
  });
  const context = {
    issue: { number: 6, owner: 'garethpaul', repo: 'twilio_test' },
    payload: {
      action: 'reopened',
      pull_request: { number: 6, user: { login: 'repeat-contributor' } },
      sender: { login: 'maintainer' },
    },
  };
  const run = new AsyncFunction('github', 'context', 'core', source);
  await run(repeat.github, context, { info: () => {} });
  if (repeat.state.creates.length !== 0) failures.push('repeat contributor received a recovery greeting');
}

for (const order of [['opened', 'synchronize'], ['synchronize', 'opened']]) {
  const first = fixture();
  for (const action of order) await invokeEvent(first, action);
  if (first.state.creates.length !== 1) {
    failures.push(`${order.join(' then ')} created ${first.state.creates.length} greetings`);
  }
}

if (legacyOpenedPath && failures.length) throw new Error(failures.join('; '));

{
  const paginated = fixture({
    comments: Array.from({ length: 204 }, (_, index) => ({ body: `comment-${index}`, user: { login: 'human' } }))
      .concat([{ body: `  ${greetingBody}  `, user: { login: 'github-actions[bot]' } }]),
  });
  await invokeShared(paginated.github, 'reopened');
  if (paginated.state.creates.length !== 0) throw new Error('late marker greeting was duplicated');
}

for (const comments of [
  [{ body: greetingBody, user: { login: 'human' } }],
  [{ body: greetingBody, user: { login: 'github-actions-bot' } }],
]) {
  const hostile = fixture({ comments });
  await invokeShared(hostile.github, 'synchronize');
  if (hostile.state.creates.length !== 1) throw new Error('untrusted marker suppressed greeting');
}

if (failures.length) throw new Error(failures.join('; '));
"""
    with tempfile.TemporaryDirectory() as temporary_directory:
        runner_path = Path(temporary_directory) / "test-greeting-script.mjs"
        runner_path.write_text(runner, encoding="utf-8")
        result = subprocess.run(
            ["node", str(runner_path), json.dumps(script), str(legacy_opened_path).lower()],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--first-interaction-bundle")
    parser.add_argument("--workflow", type=Path, default=DEFAULT_WORKFLOW)
    arguments = parser.parse_args()
    try:
        bundle = load_first_interaction_bundle(
            arguments.first_interaction_bundle or os.environ.get("FIRST_INTERACTION_BUNDLE")
        )
        prove_pinned_first_interaction(bundle)
        workflow = arguments.workflow.read_text(encoding="utf-8")
        script = extract_github_script(workflow)
        legacy_opened_path = workflow.count(FIRST_INTERACTION_PIN) > 1
        test_pull_request_script(script, legacy_opened_path)
    except (AssertionError, OSError, subprocess.SubprocessError) as exc:
        return fail(str(exc))
    print("Greeting runtime regressions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
