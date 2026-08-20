## Role Documentation

### Maintain a role changelog

Each role should contain a `CHANGELOG.md` file documenting meaningful changes to the role.

The changelog is intended to explain the history and reasoning behind changes rather than act as a formal release log. Entries do not need to be dated.

Each meaningful entry should identify:

* **Who** made the change
* **What** was changed
* **Why** the change was made

Example:

```markdown
# Changelog

## Tristan Ziska

- Changed repository configuration to use the internal mirror rather than the upstream repository.
  This prevents production systems from requiring direct Internet access.

- Replaced the legacy shell-based package installation with `ansible.builtin.dnf`.
  This provides proper idempotency and more predictable failure handling.

## Jane Smith

- Added support for the new application service account.
  The service was separated from the previous shared account to meet the updated access-control requirements.
```

Changelog entries should focus on changes that affect the role's behavior, implementation, requirements, or operational expectations. Minor formatting changes, spelling corrections, and similar non-functional changes do not require an entry.

The changelog should explain **why** a change was made rather than merely repeating what can already be determined from the code.

This is a best-practice requirement and is not enforced by `ansible-lint`.
# Ansible Style and Development Guide

This document defines the conventions used when writing Ansible code.

Not every rule below is an official Ansible best practice. Some are environment-specific conventions chosen because they improve readability, maintainability, consistency, or predictability.

All Ansible code must pass the configured `ansible-lint` checks before being considered complete.

> **Note:** Examples intentionally focus on the rule being demonstrated. Other rules in this document still apply even when they are not illustrated in a particular example.

## General Rules

### Name every task

Every task must have a meaningful name.

Task names make playbook output useful and make tasks easier to find in source code and execution logs.

Bad:

```yaml
- ansible.builtin.set_fact:
    foo: bar
```

Good:

```yaml
- name: Set required variable
  ansible.builtin.set_fact:
    foo: bar
```

This is enforced by `ansible-lint`.

### Prefix task names in included task files

Tasks inside included role task files should use the task-file name as a prefix.

Format:

```text
<file_name> | <Description>
```

For example, in `tasks/configure_firewall.yml`:

```yaml
- name: configure_firewall | Open HTTP port
  ansible.posix.firewalld:
    service: http
    permanent: true
    state: enabled
```

This makes the source of an included task immediately identifiable in Ansible output.

This is enforced by `name[prefix]`.

### Use Fully Qualified Collection Names

Use Fully Qualified Collection Names (FQCNs) for modules and plugins.

Bad:

```yaml
- name: Run command
  command:
    cmd: foo
```

Good:

```yaml
- name: Run command
  ansible.builtin.command:
    cmd: foo
```

The same convention applies to lookup plugins.

Bad:

```yaml
foo: "{{ lookup('hashi_vault', 'secret/foo') }}"
```

Good:

```yaml
foo: "{{ lookup('community.hashi_vault.hashi_vault', 'secret/foo') }}"
```

FQCNs make the source of modules and plugins explicit and avoid ambiguity between collections.

### Prefer native Ansible modules

Whenever practical, use an Ansible module instead of invoking an operating-system command.

Bad:

```yaml
- name: Update package cache
  ansible.builtin.command:
    cmd: dnf makecache
```

Good:

```yaml
- name: Update package cache
  ansible.builtin.dnf:
    update_cache: true
```

Native modules generally provide better idempotency, error handling, check-mode support, and portability across operating-system versions.

### Use `true` and `false` for Boolean values

Always use `true` and `false` for Boolean YAML values.

Bad:

```yaml
- name: Set required variable
  ansible.builtin.set_fact:
    foo: yes
```

Good:

```yaml
- name: Set required variable
  ansible.builtin.set_fact:
    foo: true
```

### Use consistent Jinja formatting

Use spaces inside the outer Jinja delimiters, but do not add unnecessary spaces around indexing.

Bad:

```yaml
foo: "{{ bar [-1] }}"
bar: "{{baz[-1]}}"
```

Good:

```yaml
foo: "{{ bar[-1] }}"
```

This is enforced by `ansible-lint`.

### Separate tasks with a blank line

Place a blank line between adjacent tasks.

Bad:

```yaml
- name: Run foo
  ansible.builtin.command:
    cmd: foo
  changed_when: false
- name: Run bar
  ansible.builtin.command:
    cmd: bar
  changed_when: false
```

Good:

```yaml
- name: Run foo
  ansible.builtin.command:
    cmd: foo
  changed_when: false

- name: Run bar
  ansible.builtin.command:
    cmd: bar
  changed_when: false
```

The intent is readability rather than YAML correctness.

## Variable Rules

### Use `defaults/` for configurable role values

Values intended to be overridden by callers belong in:

```text
defaults/main.yml
```

Use `vars/` for internal role constants that consumers should not normally override.

Environment-specific values should be stored in the appropriate location for the automation environment rather than hard-coded into role implementation logic unless the value is genuinely intrinsic to the role.

## Block Rules

### Put block-level conditions before the block

When a block has a `when` condition, place the condition before `block:`.

Bad:

```yaml
- name: Run conditional operations
  block:
    - name: Run foo
      ansible.builtin.command:
        cmd: foo
      changed_when: false

    - name: Run bar
      ansible.builtin.command:
        cmd: bar
      changed_when: false
  when: foo == bar
```

Good:

```yaml
- name: Run conditional operations
  when: foo == bar
  block:
    - name: Run foo
      ansible.builtin.command:
        cmd: foo
      changed_when: false

    - name: Run bar
      ansible.builtin.command:
        cmd: bar
      changed_when: false
```

This makes the condition controlling the block visible before the reader enters the block.

This is enforced by the custom `block-when-order` rule.

### Hoist common conditions to the block

If every direct task in a block uses the same condition, place that condition on the block instead.

Bad:

```yaml
- name: Run conditional operations
  block:
    - name: Run foo
      ansible.builtin.command:
        cmd: foo
      changed_when: false
      when: foo == bar

    - name: Run bar
      ansible.builtin.command:
        cmd: bar
      changed_when: false
      when: foo == bar
```

Good:

```yaml
- name: Run conditional operations
  when: foo == bar
  block:
    - name: Run foo
      ansible.builtin.command:
        cmd: foo
      changed_when: false

    - name: Run bar
      ansible.builtin.command:
        cmd: bar
      changed_when: false
```

Only identical conditions should be mechanically hoisted. Partially overlapping Boolean expressions should be reviewed manually.

This is enforced by the custom `block-common-when` rule.

## Command and Shell Rules

### Always use `cmd`

When using `ansible.builtin.command` or `ansible.builtin.shell`, commands must be supplied using the `cmd` argument.

Bad:

```yaml
- name: Run foo
  ansible.builtin.command: foo
```

Good:

```yaml
- name: Run foo
  ansible.builtin.command:
    cmd: foo
```

Bad:

```yaml
- name: Run shell command
  ansible.builtin.shell: echo foo
```

Good:

```yaml
- name: Run shell command
  ansible.builtin.shell:
    cmd: echo foo
```

This keeps command and shell tasks structurally consistent and makes additional module arguments easier to add and review.

This is enforced by the custom `command-cmd` rule.

### Prefer `command` over `shell`

Use `ansible.builtin.command` unless shell functionality is actually required.

Shell functionality includes pipes, redirection, command chaining, variable expansion, or other shell operators.

Bad:

```yaml
- name: Run foo
  ansible.builtin.shell:
    cmd: foo
  changed_when: false
```

Good:

```yaml
- name: Run foo
  ansible.builtin.command:
    cmd: foo
  changed_when: false
```

This is enforced by `command-instead-of-shell`.

### Prefer modules over commands

Do not use `command` or `shell` when an appropriate native Ansible module exists.

This is enforced where possible by `command-instead-of-module`.

### Explicitly define change behavior

Commands and shell tasks must explicitly define how Ansible determines whether they changed the system.

For commands that only inspect state:

```yaml
- name: Check current configuration
  ansible.builtin.command:
    cmd: foo --status
  changed_when: false
```

For commands whose output indicates whether a change occurred:

```yaml
- name: Update foo
  ansible.builtin.command:
    cmd: foo --update
  register: foo_update
  changed_when: "'updated' in foo_update.stdout"
```

`changed_when` controls whether Ansible reports a task as changed. It does not control whether the task failed.

This is enforced by `no-changed-when`.

### Use `creates` and `removes` where appropriate

When a command changes state by creating or removing a predictable path, prefer `creates` or `removes` where they accurately describe the operation.

Example:

```yaml
- name: Initialize foo
  ansible.builtin.command:
    cmd: foo --initialize
    creates: /etc/foo/config.yml
```

These provide native idempotency without requiring custom result parsing.

### Use `pipefail` with shell pipelines

When using a shell pipeline, enable `pipefail` so failures from earlier commands are not hidden by successful commands later in the pipeline.

Bad:

```yaml
- name: Run pipeline
  ansible.builtin.shell:
    cmd: false | cat
  changed_when: false
```

Good:

```yaml
- name: Run pipeline
  ansible.builtin.shell:
    cmd: set -o pipefail && false | cat
    executable: /bin/bash
  changed_when: false
```

This is enforced by `risky-shell-pipe`.

### Never force commands to succeed

Commands must never artificially override or discard their real exit status simply to make Ansible consider the task successful.

The following patterns are prohibited:

```text
|| true
|| /bin/true
; true
; /bin/true
|| exit 0
; exit 0
```

Equivalent constructs whose purpose is to manufacture a successful return code are also prohibited.

Bad:

```yaml
- name: Run foo
  ansible.builtin.shell:
    cmd: foo || true
  changed_when: false
```

Bad:

```yaml
- name: Run foo
  ansible.builtin.shell:
    cmd: foo ; exit 0
  changed_when: false
```

Expected failures must instead be modeled explicitly using Ansible.

Good:

```yaml
- name: Run foo
  ansible.builtin.command:
    cmd: foo
  register: foo_out
  changed_when: false
  failed_when: foo_out.rc not in [0, 1]
```

If failure genuinely needs to be ignored, use Ansible's error-handling mechanisms and document why.

Do not alter the command itself merely to manufacture exit code `0`.

This is enforced by the custom `no-force-success` rule.

## Error Handling Rules

### Prefer `failed_when` for expected failures

Use `failed_when` when a command can legitimately return a non-zero status.

Example:

```yaml
- name: Query foo
  ansible.builtin.command:
    cmd: foo
  register: foo_out
  changed_when: false
  failed_when: foo_out.rc not in [0, 1]
```

This documents exactly which outcomes are acceptable rather than discarding failure information.

### Explain intentionally suppressed failures

Whenever normal failure handling is intentionally suppressed, add a comment explaining why.

This applies to:

* `ignore_errors: true`
* `failed_when: false`
* `ignore_unreachable: true`

Example:

```yaml
# The service may not exist on hosts upgraded from older releases.
- name: Check legacy service
  ansible.builtin.command:
    cmd: systemctl status legacy.service
  changed_when: false
  failed_when: false
```

A suppression without explanation should be treated as technical debt.

This is enforced by the custom `explained-error-suppression` rule.

### Avoid `ignore_errors: true`

Use `ignore_errors: true` only when the failure genuinely cannot or should not be modeled using `failed_when`.

Where possible, prefer:

```yaml
failed_when: <explicit condition>
```

rather than suppressing all failures.

## Loops

### Prefer `loop` over legacy `with_*` loops

Use `loop` and `loop_control` instead of legacy constructs such as `with_items`.

Bad:

```yaml
- name: Install packages
  ansible.builtin.dnf:
    name: "{{ item }}"
    state: present
  with_items:
    - vim
    - git
```

Good:

```yaml
- name: Install packages
  ansible.builtin.dnf:
    name: "{{ item }}"
    state: present
  loop:
    - vim
    - git
```

This is enforced by the custom `no-legacy-loop` rule.

### Name loop variables when needed for clarity

For nested loops, included tasks, or loops where `item` is ambiguous, define a descriptive `loop_var`.

```yaml
- name: Configure repositories
  ansible.builtin.include_tasks: configure_repository.yml
  loop: "{{ repository_definitions }}"
  loop_control:
    loop_var: repository
    label: "{{ repository.name }}"
```

Use `label` when displaying the complete loop object would make Ansible output unnecessarily difficult to read.

## Service and Package Management

### Prefer the platform-specific module when appropriate

Where platform behavior matters, use the module that directly represents the underlying service or package manager.

For systemd-managed services, prefer:

```yaml
ansible.builtin.systemd
```

For DNF-managed packages, prefer:

```yaml
ansible.builtin.dnf
```

This is an environment convention intended to make behavior explicit rather than a universal Ansible requirement.

## Handlers

### Use handlers for restart and reload actions

If a service restart or reload should occur only when another task changes something, notify a handler instead of restarting the service directly.

Example:

```yaml
- name: Configure nginx
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    mode: "0644"
  notify: Restart nginx
```

Handler:

```yaml
- name: Restart nginx
  ansible.builtin.systemd:
    name: nginx
    state: restarted
```

Use `ansible.builtin.meta: flush_handlers` only when later tasks require the notified changes to have already taken effect.

## Secrets

### Never commit plaintext secrets

Credentials, tokens, private keys, passwords, and similar secrets must never be committed to source control.

Retrieve secrets from the approved secret-management system or provide them through an approved external execution mechanism.

### Protect secret-bearing tasks with `no_log`

Use `no_log: true` when module arguments, command output, registered results, or failures could expose credentials or secret material.

Example:

```yaml
- name: Authenticate to service
  ansible.builtin.command:
    cmd: foo-login --token "{{ secret_token }}"
  no_log: true
  changed_when: false
```

`no_log` protects execution output. It does not make storing plaintext secrets in source code acceptable.

## Playbook Rules

### Keep entry-point playbooks thin

Top-level playbooks should primarily select targets, establish execution behavior, perform required prerequisite work, and invoke roles.

Complex implementation logic should normally live in roles rather than accumulating directly in entry-point playbooks.

### Disable implicit full fact gathering when unnecessary

Use:

```yaml
gather_facts: false
```

when full automatic fact gathering is not required.

Explicitly gather only the facts needed by the automation.

Example:

```yaml
pre_tasks:
  - name: Gather minimal facts
    ansible.builtin.setup:
      gather_subset:
        - min
```

## Role Documentation

### Maintain a role changelog

Each role should contain a `CHANGELOG.md` file documenting meaningful changes to the role.

Each changelog entry must identify:

* **Who** made the change
* **When** the change was made
* **What** was changed
* **Why** the change was made

Use the following format:

```markdown
## Tristan Ziska - 01/01/1976

- Changed repository configuration to use the internal mirror rather than the upstream repository. This prevents production systems from requiring direct Internet access.
- Replaced the legacy shell-based package installation with `ansible.builtin.dnf`. This provides proper idempotency and more predictable failure handling.
```

Use one heading per contributor/date combination:

```text
## <Name> - MM/DD/YYYY
```

Each meaningful change should be recorded as a separate bullet beneath that heading.

Changelog entries should focus on changes that affect the role's behavior, implementation, requirements, or operational expectations.

Minor formatting changes, spelling corrections, and other non-functional changes do not require an entry.

Each entry should explain **why** the change was made rather than merely describing the code modification. The purpose of the changelog is to preserve operational and design context that may not be obvious from the implementation itself.

Maintaining the changelog is a required development practice, but it is not enforced by `ansible-lint`.

## Dependencies

Declare required roles and collections in the appropriate `requirements.yml`.

Pin dependency versions where reproducibility matters, particularly for CI/CD and production automation.

Do not depend on collections or roles merely because they happen to exist on a developer or execution system.

## Testing and Validation

All Ansible code must pass the configured linting and validation checks before being considered complete.

At minimum:

```text
ansible-lint
yamllint
```

Roles with meaningful behavior should have automated tests where practical.

Molecule should be used where a role's behavior can reasonably be exercised in an isolated test environment.

Idempotency should be tested when the automation is expected to be idempotent.

## Lint Suppressions

### `noqa` is prohibited

`# noqa` and equivalent inline `ansible-lint` suppressions are not permitted.

Bad:

```yaml
- name: Install package
  ansible.builtin.dnf:
    name: foo
    state: latest  # noqa package-latest
```

Bad:

```yaml
- name: Ignore failure
  ansible.builtin.command:
    cmd: foo
  ignore_errors: true  # noqa ignore-errors
```

Lint violations must be corrected rather than suppressed.

If an upstream lint rule conflicts with an approved environment-wide convention, that rule must be addressed centrally in the lint configuration rather than bypassed at individual call sites.

The presence of an inline lint suppression is itself considered a lint failure.

This is enforced by the custom `no-noqa` rule.

## Long-Running and Delegated Operations

Use `async` and `poll` when an operation legitimately exceeds normal connection or task timeouts.

Prefer state-based polling such as `wait_for`, service checks, or API checks over fixed `pause` durations when the desired state can be observed.

Use `delegate_to`, `run_once`, `become_user`, `throttle`, and `add_host` deliberately.

Their execution scope and reason should be clear during code review.

