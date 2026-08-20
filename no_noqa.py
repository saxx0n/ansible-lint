import re

from ansiblelint.rules import AnsibleLintRule


class NoNoqaRule(AnsibleLintRule):
    """Inline ansible-lint suppressions are prohibited."""

    id = "no-noqa"
    description = (
        "Inline noqa suppressions are prohibited. Lint violations must "
        "be corrected or handled centrally in the lint configuration."
    )
    severity = "HIGH"
    tags = ["idiom"]
    version_changed = "1.0.0"

    NOQA_RE = re.compile(
        r"#\s*noqa\b",
        re.IGNORECASE,
    )

    def matchlines(self, file):
        matches = []

        if file.path.is_dir():
            return matches

        for lineno, line in enumerate(
            file.content.splitlines(),
            start=1,
        ):
            if not self.NOQA_RE.search(line):
                continue

            matches.append(
                self.create_matcherror(
                    message=(
                        "Inline '# noqa' suppressions are prohibited. "
                        "Fix the violation or change the central lint "
                        "configuration."
                    ),
                    lineno=lineno,
                    filename=file,
                )
            )

        return matches
