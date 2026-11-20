"""验收执行器与闭环门禁测试：真实执行、假绿检测、自动提单、QA 签收。"""

import json
import tempfile
import unittest
from pathlib import Path

import yaml

from aiassitrequreimentdev.gates import evaluate, init_feature
from aiassitrequreimentdev.progress import accept_gate
from aiassitrequreimentdev.verify import (
    auto_fix_failures,
    is_fake_green,
    mark_verification_success,
    run_verification,
    verification_next,
    verification_status,
)
from aiassitrequreimentdev.verify_match import (
    commands_match,
    verify_hash,
)


def _write_yaml(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n", encoding="utf-8")


def _write_spec(feature: Path, verify: str = "python -c 'print(1)'") -> None:
    _write_yaml(
        feature / "spec.yaml",
        f"""
id: FEAT-001-demo
problem: 测试
nonGoals: []
acceptance:
  - id: A1
    given: 给定环境
    when: 当执行
    then: 则通过
    verify: "{verify}"
    covers: [P0]
openQuestions: []
uiRequired: false
uiReason: 无 UI
""",
    )


class VerifyMatchTests(unittest.TestCase):
    def test_fake_green_patterns(self) -> None:
        for command in ("true", "exit 0", "echo ok", "", "echo x && exit 0"):
            self.assertTrue(is_fake_green(command), command)
        self.assertFalse(is_fake_green("python -m unittest test_a"))

    def test_commands_match_is_strict(self) -> None:
        self.assertTrue(commands_match("python -m pytest -q", "python -m pytest"))
        self.assertTrue(commands_match("python -m pytest", "python -m pytest"))
        self.assertFalse(commands_match("echo ok", "python -m pytest"))
        self.assertFalse(commands_match("true", "TODO_SET_VERIFY"))

    def test_verify_hash_tracks_spec_change(self) -> None:
        self.assertNotEqual(verify_hash("python -m pytest"), verify_hash("python -m unittest"))


class VerifyRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.feature = init_feature(self.root, "FEAT-001-demo")
        _write_spec(self.feature, "python -c 'print(1)'")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_runner_executes_real_command_and_enables_runner_mode(self) -> None:
        payload = run_verification(self.feature)
        self.assertEqual(payload["failed"], [])
        evidence = yaml.safe_load((self.feature / "evidence.yaml").read_text(encoding="utf-8"))
        result = evidence["results"][0]
        self.assertEqual(result["executedBy"], "runner")
        self.assertEqual(result["exitCode"], 0)
        self.assertEqual(result["verifyHash"], verify_hash("python -c 'print(1)'"))
        self.assertEqual(verification_status(self.feature)["mode"], "runner")

    def test_runner_captures_nonzero_exit(self) -> None:
        _write_spec(self.feature, "python -c 'import sys; sys.exit(3)'")
        payload = run_verification(self.feature)
        self.assertEqual(payload["failed"], ["A1"])
        self.assertEqual(payload["results"][0]["exitCode"], 3)

    def test_dry_run_does_not_write_evidence(self) -> None:
        before = (self.feature / "evidence.yaml").read_text(encoding="utf-8")
        payload = run_verification(self.feature, dry_run=True)
        self.assertTrue(payload["dryRun"])
        self.assertEqual((self.feature / "evidence.yaml").read_text(encoding="utf-8"), before)
        self.assertEqual(verification_status(self.feature)["mode"], "self-report")

    def test_failed_run_auto_ticket_with_bounded_attempts(self) -> None:
        _write_spec(self.feature, "python -c 'import sys; sys.exit(3)'")
        payload = run_verification(self.feature)
        fix = auto_fix_failures(self.feature, payload["failed"], max_attempts=1)
        self.assertEqual(fix["action"], "auto-fix")
        self.assertEqual(fix["attempts"], 1)
        state = json.loads((self.feature / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["gates"]["G3"], "pending")
        changes = yaml.safe_load((self.feature / "change.yaml").read_text(encoding="utf-8"))
        self.assertEqual(changes["changes"][0]["level"], "C0")
        blocked = auto_fix_failures(self.feature, payload["failed"], max_attempts=1)
        self.assertEqual(blocked["action"], "blocked")
        self.assertEqual(blocked["nextRole"], "human")
        self.assertEqual(blocked["interrupt"], "I_TEST_STUCK")

    def test_failure_dispatches_dev_fix_task_and_next_routes_to_dev(self) -> None:
        _write_spec(self.feature, "python -c 'import sys; sys.exit(3)'")
        payload = run_verification(self.feature)
        fix = auto_fix_failures(
            self.feature, payload["failed"], max_attempts=3, results=payload["results"]
        )
        self.assertEqual(fix["nextRole"], "dev")
        self.assertIn("主控自动派 dev", fix["dispatch"])
        task = yaml.safe_load((self.feature / "fix-tasks.yaml").read_text(encoding="utf-8"))
        self.assertEqual(task["status"], "open")
        self.assertEqual(task["assignTo"], "dev")
        self.assertEqual(task["items"][0]["acceptanceId"], "A1")
        self.assertEqual(task["items"][0]["exitCode"], 3)
        self.assertIn("禁止", " ".join(task["done"]) + " " + task["items"][0]["hint"])
        nxt = verification_next(self.feature)
        self.assertEqual(nxt["nextRole"], "dev")
        self.assertEqual(nxt["fixTask"], "fix-tasks.yaml")

    def test_success_closes_fix_task_and_routes_to_human_qa(self) -> None:
        _write_spec(self.feature, "python -c 'import sys; sys.exit(3)'")
        payload = run_verification(self.feature)
        auto_fix_failures(self.feature, payload["failed"], results=payload["results"])
        # 模拟 dev 已在写集内修好：spec 的 verify 改为通过命令，重跑
        _write_spec(self.feature, "python -c 'print(1)'")
        passed = run_verification(self.feature)
        self.assertEqual(passed["failed"], [])
        mark_verification_success(self.feature)
        accept_gate(self.feature, "G4")
        task = yaml.safe_load((self.feature / "fix-tasks.yaml").read_text(encoding="utf-8"))
        self.assertEqual(task["status"], "fixed")
        nxt = verification_next(self.feature)
        self.assertEqual(nxt["nextRole"], "human")
        self.assertIn("qa.yaml", nxt["reason"])

    def test_next_without_runner_mode_routes_to_lead(self) -> None:
        nxt = verification_next(self.feature)
        self.assertEqual(nxt["nextRole"], "lead")
        self.assertIn("verify run", nxt["reason"])


class QAGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.feature = init_feature(self.root, "FEAT-001-demo")
        _write_spec(self.feature)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _codes(self, gate: str) -> set[str]:
        return {item.code for item in evaluate(self.feature).violations if item.gate == gate}

    def test_old_features_do_not_require_qa(self) -> None:
        self.assertNotIn("QA_MISSING", self._codes("GQA"))

    def test_runner_mode_requires_human_signoff(self) -> None:
        state = json.loads((self.feature / "state.json").read_text(encoding="utf-8"))
        state["verification"] = {"mode": "runner", "attempts": 0, "maxAttempts": 3,
                                 "lastFailure": None, "blocked": False}
        (self.feature / "state.json").write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
        (self.feature / "qa.yaml").unlink()
        self.assertIn("QA_MISSING", self._codes("GQA"))
        _write_yaml(
            self.feature / "qa.yaml",
            """
environment: staging
signOff:
  role: tester
  name: 张三
  at: "2026-11-20T16:00:00+08:00"
scope:
  checklist: [主路径回归]
  exploratory: true
  regression: true
  crossDevice: false
blockingOpen: 0
conclusion: pass
""",
        )
        self.assertEqual(self._codes("GQA"), set())

    def test_ai_cannot_signoff_qa(self) -> None:
        state = json.loads((self.feature / "state.json").read_text(encoding="utf-8"))
        state["verification"] = {"mode": "runner", "attempts": 0, "maxAttempts": 3,
                                 "lastFailure": None, "blocked": False}
        (self.feature / "state.json").write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
        _write_yaml(
            self.feature / "qa.yaml",
            """
environment: staging
signOff:
  role: agent
  name: AI
  at: "2026-11-20T16:00:00+08:00"
scope:
  checklist: [主路径回归]
  exploratory: true
  regression: true
  crossDevice: false
blockingOpen: 0
conclusion: pass
""",
        )
        self.assertIn("QA_SIGN", self._codes("GQA"))


if __name__ == "__main__":
    unittest.main()
