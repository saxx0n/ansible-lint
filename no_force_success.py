import re

from ansiblelint.rules import AnsibleLintRule
from ansiblelint.utils import Task


class NoForceSuccessRule(AnsibleLintRule):
    """Do not force commands to return success."""

    id = "no-force-success"
    description = (
        "Do not use shell constructs such as '|| true' or '; exit 0' "
        "to hide command failures. Use failed_when to model acceptable "
        "return codes explicitly."
    )
    severity = "HIGH"
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

    FORCE_SUCCESS_RE = re.compile(
        r"""
        (?:
            \|\|            # foo || ...
            |
            ;               # foo ; ...
        )
        \s*
        (?:
            (?:/usr)?/bin/true
            |
            true
            |
            exit\s+0
        )
        (?:\s|$|;)
        """,
        re.VERBOSE,
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

        if isinstance(value, str):
            command = value

        elif isinstance(value, dict):
            command = value.get("cmd")

        else:
            return False

        if not isinstance(command, str):
            return False

        if self.FORCE_SUCCESS_RE.search(command):
            return (
                "Do not force commands to succeed. Preserve the real "
                "return code and use 'failed_when' for expected failures."
            )

        return False
