"""Exercise real Git, Bash and jq against a fake GitHub CLI, without network access."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASELINE = json.loads((ROOT / "scripts/baseline.json").read_text())
BASH = shutil.which("bash")

FAKE_GH = r'''#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys

path = Path(os.environ["FAKE_STATE"])
state = json.loads(path.read_text())
args = sys.argv[1:]

def output(value):
    print(json.dumps(value))

def save(operation):
    state["writes"].append(operation)
    path.write_text(json.dumps(state))

if args[:2] == ["auth", "status"]:
    sys.exit(1 if state.get("auth_fail") else 0)
elif args[:2] == ["api", "user"]:
    if state.get("api_fail"):
        print("API unavailable", file=sys.stderr)
        sys.exit(1)
    print("tester")
elif args[:2] == ["repo", "view"]:
    if args[2] != "example/repo":
        raise RuntimeError("Wrong repository detected: " + args[2])
    output({"id": "repo-id", "nameWithOwner": "example/repo", "projectsV2": {"Nodes": state["links"]}})
elif args[:2] == ["project", "view"]:
    output(state["project"])
elif args[:2] == ["project", "create"]:
    if args[args.index("--title") + 1] != "repo":
        raise RuntimeError("Wrong Project title")
    state["project"] = {"id": "project-id", "number": 7, "closed": False,
                        "url": "https://github.com/users/example/projects/7"}
    state["options"] = [{"id":"todo", "name":"Todo", "color":"GRAY", "description":"factory"}]
    save("create")
    output(state["project"])
elif args[:2] == ["project", "link"]:
    if not state.get("drop_link"):
        state["links"] = [state["project"]]
        state["repositories"] = ["repo-id"]
    save("link")
elif args[0] == "api" and "labels?" in args[1]:
    output([[{"name": name} for name in state["labels"]]])
elif args[:2] == ["label", "create"]:
    name = args[2]
    if not state.get("drop_label"):
        state["labels"].append(name)
    save("label:" + name)
elif args[:2] == ["api", "graphql"]:
    if "--input" in args:
        data = json.load(sys.stdin)
        state["options"] = data["variables"]["input"]["singleSelectOptions"]
        save("statuses")
        output({"data": {"updateProjectV2Field": {"projectV2Field": {"id": "field-id"}}}})
    else:
        output({"data": {"node": {
            "fields": {
                "nodes": [{"id": "field-id", "name": "Status", "options": state["options"]}],
                "pageInfo": {"hasNextPage": False}
            },
            "repositories": {
                "nodes": [{"id": repo_id} for repo_id in state["repositories"]],
                "pageInfo": {"hasNextPage": False}
            }
        }}})
else:
    raise RuntimeError("Unexpected command: " + repr(args))
'''


class SetupTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.repository = self.directory / "repo"
        self.repository.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repository)], check=True)
        subprocess.run(["git", "-C", str(self.repository), "remote", "add", "origin",
                        "git@github.com:example/repo.git"], check=True)
        self.state_path = self.directory / "state.json"
        bin_dir = self.directory / "bin"
        bin_dir.mkdir()
        fake_gh = bin_dir / "gh"
        fake_gh.write_text(FAKE_GH)
        fake_gh.chmod(0o755)
        self.env = dict(
            os.environ,
            PATH=f"{bin_dir}:{os.environ['PATH']}",
            FAKE_STATE=str(self.state_path),
        )
        project = {
            "id": "project-id", "number": 7, "closed": False,
            "url": "https://github.com/users/example/projects/7",
        }
        self.save({
            "project": project,
            "links": [project],
            "repositories": ["repo-id"],
            "options": [dict(option, id=f"option-{i}") for i, option in enumerate(BASELINE["statuses"])],
            "labels": [label["name"] for label in BASELINE["labels"]] + ["custom"],
            "writes": [],
        })

    def save(self, state):
        self.state_path.write_text(json.dumps(state))

    def state(self):
        return json.loads(self.state_path.read_text())

    def run_setup(self, *args, env=None, cwd=None):
        return subprocess.run(
            [BASH, str(ROOT / "scripts/setup.sh"), *args],
            env=env or self.env, cwd=cwd or self.repository,
            capture_output=True, text=True, timeout=15,
        )

    def test_configured_repository_reruns_without_writes(self):
        for _ in range(2):
            result = self.run_setup("--apply")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Verified", result.stdout)
        self.assertEqual(self.state()["writes"], [])

    def test_preview_without_project_does_not_create_anything(self):
        state = self.state()
        state["links"] = []
        state["labels"] = []
        self.save(state)
        result = self.run_setup()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("No linked Project", result.stdout)
        self.assertIn("Missing status: Backlog", result.stdout)
        self.assertEqual(self.state()["writes"], [])

    def test_create_link_configure_and_rerun_without_recreation(self):
        state = self.state()
        state["project"] = None
        state["links"] = []
        state["repositories"] = []
        state["labels"] = []
        self.save(state)
        result = self.run_setup("--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        after = self.state()
        self.assertEqual(after["writes"][:2], ["create", "link"])
        self.assertEqual(len(after["links"]), 1)
        self.assertEqual(after["repositories"], ["repo-id"])
        self.assertTrue({s["name"] for s in BASELINE["statuses"]}.issubset({s["name"] for s in after["options"]}))
        result = self.run_setup("--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(after["writes"], self.state()["writes"])

    def test_apply_adds_missing_configuration_preserving_existing(self):
        state = self.state()
        extra = {"id": "special", "name": "Custom", "color": "RED", "description": "retain"}
        state["options"] = state["options"][:2] + [extra]
        state["labels"] = ["BUG", "custom"]
        self.save(state)
        result = self.run_setup("--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        after = self.state()
        self.assertEqual(after["options"][0]["id"], "option-0")
        self.assertIn(extra, after["options"])
        self.assertNotIn("label:bug", after["writes"])
        self.assertNotIn("create", after["writes"])

    def test_multiple_projects_are_not_modified(self):
        state = self.state()
        state["links"].append(dict(state["project"], id="other", number=8))
        self.save(state)
        result = self.run_setup("--apply")
        self.assertEqual(result.returncode, 2)
        self.assertIn("multiple Projects", result.stderr)
        self.assertEqual(self.state()["writes"], [])

    def test_shared_project_is_not_modified(self):
        state = self.state()
        state["repositories"].append("other-repo")
        self.save(state)
        result = self.run_setup("--apply")
        self.assertEqual(result.returncode, 2)
        self.assertIn("not linked exclusively", result.stderr)
        self.assertEqual(self.state()["writes"], [])

    def test_auth_failure_reports_without_writes(self):
        state = self.state()
        state["auth_fail"] = True
        self.save(state)
        result = self.run_setup("--apply")
        self.assertEqual(result.returncode, 2)
        self.assertIn("authentication", result.stderr)
        self.assertEqual(self.state()["writes"], [])

    def test_api_auth_check_failure_is_not_hidden(self):
        state = self.state()
        state["api_fail"] = True
        self.save(state)
        result = self.run_setup("--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Verified", result.stdout)
        self.assertEqual(self.state()["writes"], [])

    def test_missing_tools_are_reported(self):
        env = dict(self.env, PATH=str(self.directory / "absent"))
        result = self.run_setup(env=env)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Missing commands: git gh jq", result.stderr)

    def test_supported_remotes_and_nested_working_directory(self):
        nested = self.repository / "nested"
        nested.mkdir()
        for remote in ("https://github.com/example/repo.git", "ssh://git@github.com/example/repo.git"):
            subprocess.run(["git", "-C", str(self.repository), "remote", "set-url", "origin", remote], check=True)
            result = self.run_setup(cwd=nested)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Repository: example/repo", result.stdout)
        self.assertEqual(self.state()["writes"], [])

    def test_missing_origin_is_reported(self):
        subprocess.run(["git", "-C", str(self.repository), "remote", "remove", "origin"], check=True)
        result = self.run_setup("--apply")
        self.assertEqual(result.returncode, 2)
        self.assertIn("no origin", result.stderr)
        self.assertEqual(self.state()["writes"], [])

    def test_closed_project_is_not_replaced(self):
        state = self.state()
        state["project"]["closed"] = True
        self.save(state)
        result = self.run_setup("--apply")
        self.assertEqual(result.returncode, 2)
        self.assertIn("closed", result.stderr)
        self.assertEqual(self.state()["writes"], [])

    def test_case_conflict_stops_before_configuration_writes(self):
        state = self.state()
        state["options"][2]["name"] = "In progress"
        self.save(state)
        result = self.run_setup("--apply")
        self.assertEqual(result.returncode, 2)
        self.assertIn("only by case", result.stderr)
        self.assertEqual(self.state()["writes"], [])

    def test_verification_detects_unsaved_label(self):
        state = self.state()
        state["labels"].remove("ci")
        state["drop_label"] = True
        self.save(state)
        result = self.run_setup("--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Verified:", result.stdout)

    def test_failed_link_does_not_create_another_project(self):
        state = self.state()
        state["project"] = None
        state["links"] = []
        state["repositories"] = []
        state["drop_link"] = True
        self.save(state)
        result = self.run_setup("--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.state()["writes"], ["create", "link"])
        self.assertNotIn("Verified:", result.stdout)


if __name__ == "__main__":
    unittest.main()
