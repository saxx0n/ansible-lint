from ansiblelint.rules import AnsibleLintRule
from ansiblelint.utils import Task


class NoLegacyLoopRule(AnsibleLintRule):
    """Use loop instead of legacy with_* constructs."""

    id = "no-legacy-loop"
    description = "Use loop/loop_control instead of legacy with_* loops."
    severity = "MEDIUM"
    tags = ["modernization", "house-style"]
    version_changed = "1.0.0"

    def matchtask(self, task: Task, file=None):
        raw = task.raw_task

        legacy = sorted(
            key for key in raw
            if isinstance(key, str) and key.startswith("with_")
        )

        if not legacy:
            return False

        return (
            f"Replace legacy '{legacy[0]}' with loop/loop_control."
        )
