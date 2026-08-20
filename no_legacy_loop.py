from ansiblelint.rules import AnsibleLintRule
from ansiblelint.utils import Task


class NoLegacyLoopRule(AnsibleLintRule):
    """Use loop instead of legacy with_* constructs."""

    id = "no-legacy-loop"
    description = (
        "Use loop and loop_control instead of legacy with_* constructs."
    )
    severity = "MEDIUM"
    tags = ["idiom"]
    version_changed = "1.0.0"

    def matchtask(self, task: Task, file=None):
        raw = task.raw_task

        legacy_loops = sorted(
            key
            for key in raw
            if isinstance(key, str) and key.startswith("with_")
        )

        if not legacy_loops:
            return False

        return (
            f"Replace legacy '{legacy_loops[0]}' with "
            "'loop' and, where appropriate, 'loop_control'."
        )
