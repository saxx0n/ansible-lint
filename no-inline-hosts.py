import ipaddress

from ansiblelint.rules import AnsibleLintRule


class NoInlineHostsRule(AnsibleLintRule):
    """Use inventory groups instead of inline hosts."""

    id = "no-inline-hosts"
    description = (
        "Playbooks should target inventory groups rather than literal "
        "IP addresses or comma-separated inline host lists."
    )
    severity = "MEDIUM"
    tags = ["inventory", "house-style"]
    version_changed = "1.0.0"

    def matchplay(self, file, data):
        hosts = data.get("hosts")

        if not isinstance(hosts, str):
            return []

        # Templated hosts cannot be evaluated statically.
        if "{{" in hosts or "{%" in hosts:
            return []

        try:
            ipaddress.ip_address(hosts)
            return [
                self.create_matcherror(
                    message=(
                        "Use an inventory group instead of a literal IP "
                        "address in 'hosts'."
                    ),
                    filename=file,
                )
            ]
        except ValueError:
            pass

        if "," in hosts:
            return [
                self.create_matcherror(
                    message=(
                        "Use an inventory group instead of an inline "
                        "comma-separated host list."
                    ),
                    filename=file,
                )
            ]

        return []
