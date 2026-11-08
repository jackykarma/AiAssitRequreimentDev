import json
import tempfile
import unittest
from pathlib import Path

from aiassitrequreimentdev.board import adopt_role, refresh_board
from aiassitrequreimentdev.gates import init_feature
from aiassitrequreimentdev.roles import menu_text, resolve_menu_choice


class RoleTests(unittest.TestCase):
    def test_resolve_chinese_and_number(self) -> None:
        self.assertEqual(resolve_menu_choice("产品经理").id, "product")
        self.assertEqual(resolve_menu_choice("2").id, "architect")
        self.assertEqual(resolve_menu_choice("tester").id, "tester")

    def test_menu_lists_five_roles(self) -> None:
        text = menu_text()
        for label in ("产品经理", "架构师SE", "开发", "测试", "部署"):
            self.assertIn(label, text)

    def test_adopt_writes_state_and_board(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = init_feature(Path(tmp), "FEAT-ROLE")
            refresh_board(feature)
            adopt_role(feature, "产品经理")
            state = json.loads((feature / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["actorRole"], "product")
            self.assertEqual(state["actorLabel"], "产品经理")
            board = (feature / "BOARD.md").read_text(encoding="utf-8")
            self.assertIn("产品经理", board)
            self.assertIn("aiassitrequreimentdev-product", board)
            self.assertIn("prd.md", board)


if __name__ == "__main__":
    unittest.main()
