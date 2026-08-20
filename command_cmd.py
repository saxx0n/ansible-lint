from ansiblelint.rules import AnsibleLintRule
from ansiblelint.utils import Task


class CommandCmdRule(AnsibleLintRule):
    """Command and shell modules must use the cmd argument."""

    id = "command-cmd"
    description = (
        "Command and shell tasks must use the explicit cmd argument."
    )
    severity = "MEDIUM"
    tags = ["command-shell"]
    version_changed = "1.0.0"

    MODULES = (
        "ansible.builtin.command",
        "ansible.builtin.shell",
        "ansible.legacy.command",
        "ansible.legacy.shell",
        "command",
        "shell",
    )

    def matchtask(self, task: Task, file=None):
        raw = task.raw_task

        module_name = next(
            (name for name in self.MODULES if name in raw),
            None,
        )

        if module_name is None:
            return False

        value = raw[module_name]

        if not isinstance(value, dict) or "cmd" not in value:
            return (
                "Command and shell tasks must use the explicit "
                "'cmd:' argument."
            )

        return False
