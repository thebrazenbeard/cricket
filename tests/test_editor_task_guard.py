"""Prevent concealed editor-on-open commands from returning to the source tree."""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class EditorTaskGuardTests(unittest.TestCase):
    def test_disguised_node_loader_is_absent(self):
        self.assertFalse((ROOT / "public" / "fonts" / "fa-solid.lkf").exists())

    def test_no_automatic_editor_tasks(self):
        config = json.loads((ROOT / ".vscode" / "tasks.json").read_text(encoding="utf-8"))
        for task in config.get("tasks", []):
            with self.subTest(task=task.get("label")):
                self.assertNotEqual(task.get("runOptions", {}).get("runOn"), "folderOpen")
                self.assertNotIn("fa-solid.lkf", task.get("command", ""))

    def test_workspace_does_not_impersonate_user_task_consent(self):
        settings = json.loads((ROOT / ".vscode" / "settings.json").read_text(encoding="utf-8"))
        self.assertNotIn("task.allowAutomaticTasks", settings)
        self.assertNotIn("tasks", settings)


if __name__ == "__main__":
    unittest.main()
