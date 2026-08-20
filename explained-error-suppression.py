from ansiblelint.rules import AnsibleLintRule
from ansiblelint.utils import Task


class ExplainedErrorSuppressionRule(AnsibleLintRule):
    """Require comments for intentionally suppressed failures."""

    id = "explained-error-suppression"
    description = (
        "Tasks using ignore_errors: true, failed_when: false, or "
        "ignore_unreachable: true must have an explanatory comment."
    )
    severity = "MEDIUM"
    tags = ["maintainability", "house-style"]
    version_changed = "1.0.0"

    def matchtask(self, task: Task, file=None):
        raw = task.raw_task

        suppresses_failure = (
            raw.get("ignore_errors") is True
            or raw.get("failed_when") is False
            or raw.get("ignore_unreachable") is True
        )

        if not suppresses_failure:
            return False

        if file is None:
            return False

        lineno = raw.get("__line__")

        if not isinstance(lineno, int) or lineno <= 1:
            return (
                "Suppressed failure handling requires an explanatory comment."
            )

        lines = file.content.splitlines()

        # __line__ is 1-based. Start immediately before the task.
        index = lineno - 2

        while index >= 0 and not lines[index].strip():
            index -= 1

        if index >= 0 and lines[index].lstrip().startswith("#"):
            return False

        return (
            "Suppressed failure handling requires an explanatory "
            "comment immediately before the task."
        )
