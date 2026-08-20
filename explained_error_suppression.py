from ansiblelint.constants import LINE_NUMBER_KEY
from ansiblelint.rules import AnsibleLintRule
from ansiblelint.utils import Task


class ExplainedErrorSuppressionRule(AnsibleLintRule):
    """Suppressed failures must be explained by a comment."""

    id = "explained-error-suppression"
    description = (
        "Tasks using ignore_errors: true, failed_when: false, or "
        "ignore_unreachable: true must include an explanatory comment."
    )
    severity = "HIGH"
    tags = ["idiom"]
    version_changed = "1.0.0"

    def matchtask(self, task: Task, file=None):
        raw = task.raw_task

        suppression = None

        if raw.get("ignore_errors") is True:
            suppression = "ignore_errors: true"
        elif raw.get("failed_when") is False:
            suppression = "failed_when: false"
        elif raw.get("ignore_unreachable") is True:
            suppression = "ignore_unreachable: true"

        if suppression is None:
            return False

        if file is None:
            return (
                f"{suppression} requires an explanatory comment."
            )

        lineno = raw.get(LINE_NUMBER_KEY)

        if not isinstance(lineno, int):
            return (
                f"{suppression} requires an explanatory comment."
            )

        lines = file.content.splitlines()

        # Look at up to three lines immediately preceding the task.
        start = max(0, lineno - 4)
        end = max(0, lineno - 1)

        preceding = lines[start:end]

        if any(line.lstrip().startswith("#") for line in preceding):
            return False

        return (
            f"{suppression} requires an explanatory comment "
            "immediately before the task."
        )
