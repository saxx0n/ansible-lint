from ansiblelint.rules import AnsibleLintRule
from ansiblelint.utils import Task


class BlockCommonWhenRule(AnsibleLintRule):
    """Hoist identical task conditions to their block."""

    id = "block-common-when"
    description = (
        "When every direct task in a block has the same when condition, "
        "move the condition to the block."
    )
    severity = "MEDIUM"
    tags = ["readability", "house-style"]
    version_changed = "1.0.0"

    def matchtask(self, task: Task, file=None):
        raw = task.raw_task

        if "block" not in raw:
            return False

        block = raw.get("block")

        if not isinstance(block, list):
            return False

        children = [
            child
            for child in block
            if isinstance(child, dict)
        ]

        if len(children) < 2:
            return False

        if not all("when" in child for child in children):
            return False

        first = children[0]["when"]

        if all(child["when"] == first for child in children[1:]):
            return (
                "All tasks in this block use the same 'when'; "
                "move it to the block."
            )

        return False
