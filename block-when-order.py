from ansiblelint.rules import AnsibleLintRule
from ansiblelint.utils import Task


class BlockWhenOrderRule(AnsibleLintRule):
    """Place block conditions before block contents."""

    id = "block-when-order"
    description = (
        "When a block has a when condition, place when before block "
        "so the controlling condition is visible first."
    )
    severity = "MEDIUM"
    tags = ["readability", "house-style"]
    version_changed = "1.0.0"

    def matchtask(self, task: Task, file=None):
        raw = task.raw_task

        if "block" not in raw or "when" not in raw:
            return False

        keys = list(raw.keys())

        if keys.index("when") > keys.index("block"):
            return "Place 'when' before 'block'."

        return False
