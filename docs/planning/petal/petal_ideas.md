Got it, Jeff — Iris packaged everything into a clean markdown you can drop into config management.

---

# Project Lily — `.petal` File Design (Short-Form Spec)

**Owner:** Iris
**Status:** Draft v0.1 (no-server execution)
**Purpose:** Define a concise, human-friendly specification for Lily’s `.petal` workflow files, plus how the runner compiles short form → canonical form.

---

## 1) Goals & Non-Goals

**Goals**

* Minimal, readable YAML that’s Git-diffable.
* Pluggable tools with typed inputs/outputs.
* Shared, persistent state across steps (“pull from previous”).
* Local-first; no daemons/servers required.

**Non-Goals (v0)**

* Distributed execution / remote workers.
* Heavy web UI (TUI/LSP are fine).
* Long-running orchestration (Temporal-style).

---

## 2) File Format Overview

* Extension: **`.petal`**
* Syntax: **YAML + Jinja2** templating
* Two representations:

  * **Short form** (authoring) → compact, ergonomic
  * **Canonical** (internal) → fully expanded, validated

**Top-level keys (short form)**

```yaml
version: 0.1
name: <string>
description: <string?>              # optional
params: { ... }                     # user-supplied parameters, referenced directly (no params.*)
defaults: { ... }                   # global defaults; supports dotted keys (e.g., llm.model)
env: { VAR: $ENV_VAR }              # optional environment mapping
secrets: [ENV1, ENV2]               # names only; resolved from OS env/keyring
macros: { <name>: [ <short-steps> ] }  # reusable step groups
imports:                            # optional includes (merged before validation)
  - path: ./partials/foo.petal
  - package: petal-extras.email     # discovered via entry points
steps:                              # ordered list of short-form steps
  - <short-step>
```

---

## 3) Short-Form Step Syntax

A step is usually a single mapping whose **key** is `<tool>(modifiers)` and **value** is the inline `with` dict.

```yaml
<tool_name>(if_error=<policy>, when="<expr>"):
  <with-fields>...
```

* `tool_name`: e.g., `shell.run`, `llm.generate`, `sqlite.query`, `slack.post`
* `if_error`: `fail | skip | retry` (default `fail`)
* `when`: Jinja boolean expression; falsy skips step
* `with-fields`: tool inputs (flattened; no `with:` wrapper)

**Examples**

```yaml
shell.run: { cmd: "{{ cmd }}" }

llm.generate:
  prompt: "{{ prompt }}\n---\n{{ shell_out|truncate(800) }}"

slack.post(if_error=skip, when="{{ rows|rows>0 }}"):
  text: "Found {{ rows|rows }} rows"
```

---

## 4) Verbosity Reductions

1. **Implicit IDs**
   Derived from `uses` + order (e.g., `llm.generate#2`). Optionally overridden via `id:` inside the value map.

2. **Implicit `writes`**
   Pulled from the tool’s contract (plugin declares what it writes). Users can override by adding `writes:` explicitly.

3. **Implicit `reads`**
   Inferred by scanning templates in the step value for `state.*`, `steps.*`, or direct symbols (`shell_out`, `rows`, `prompt`) which resolve to `state.<name>`/`params.<name>`.

4. **Global `defaults`**
   Common knobs once at the top:

```yaml
defaults:
  llm.model: gpt-4o-mini
  retry: { max: 2, backoff: 1.5 }
```

5. **Inline `with`**
   No `with:` key unless nesting complex structures. Flat mappings are allowed directly under the step.

6. **Parameter Shortcuts**
   `params` are injected into template context at top level, so `{{ prompt }}` works (no `params.prompt`).

7. **Macros**
   Reusable sequences:

```yaml
macros:
  notify:
    - slack.post: { text: "{{ text }}" }
    - twitter.post: { text: "Update: {{ text }}" }

steps:
  - use: notify
    with: { text: "Found {{ rows|rows }} rows for '{{ llm_query }}'" }
```

8. **Profiles with `apply:`**
   Light overlay for environment-specific values:

```yaml
profile: dev
apply:
  dev:
    env: { SLACK_WEBHOOK_URL: $DEV_SLACK }
  prod:
    env: { SLACK_WEBHOOK_URL: $PROD_SLACK }
```

9. **Jinja helpers**
   Built-ins: `head(n)`, `lines`, `truncate(n)`, `json`, `yaml`, `rows`(len), `col(k)`, `now()`.

10. **Future sugar**
    `foreach` and `parallel` shorthands (to be added post-MVP).

---

## 5) Canonical Form (for runner)

The runner compiles short steps into a canonical schema before execution.

```yaml
version: 0.1
name: acme_demo
parameters: { ... }            # from params
defaults: { ... }
imports: [ ... ]
secrets: [ ... ]
state: { ... }                 # optional initial state
steps:
  - id: shell.run#1
    uses: shell.run
    reads: [cmd]
    writes: [shell_out]        # from tool contract (or override)
    with: { cmd: "{{ cmd }}" }
    when: null
    if_error: fail

  - id: llm.generate#1
    uses: llm.generate
    reads: [prompt, shell_out]
    writes: [llm_query, text]
    with:
      model: "gpt-4o-mini"     # injected from defaults unless overridden
      prompt: "{{ prompt }}\n---\n{{ shell_out|truncate(800) }}"
    when: null
    if_error: fail
```

---

## 6) Execution Model (No Server)

* **Runner**: single Python process (CLI command).
* **Order**: sequential (DAG/V1 later).
* **State**: dict merged after each step (`state.update(step_output)`).
* **Persistence**: snapshots to `./.runs/<run_id>/*.json`, artifacts in `./.runs/<run_id>/artifacts/`.
* **Dry Run**: `petal explain` renders templates, validates schema, shows plan (no side effects).
* **Caching (opt-in)**: deterministic hash of `(tool, with, selected inputs)` → cached outputs.

**Error Handling**

* `if_error=fail` (default): stop on exception.
* `if_error=skip`: log and continue.
* `if_error=retry`: exponential backoff using `defaults.retry` or step-level `retry`.

---

## 7) Tool & Plugin System

**Mechanism:** `pluggy` entry points (group `petal.plugins`).

**Hook spec**

```python
class ToolInfo(TypedDict):
    name: str                   # "slack.post"
    input_schema: dict          # JSON schema for 'with'
    writes: list[str]           # declared outputs
    description: str | None

class StepContext(TypedDict):
    state: dict
    run_dir: Path
    env: dict
    logger: Logger
```

```python
@hookspec
def petal_tools() -> list[ToolInfo]: ...

@hookspec
def petal_execute(tool: str, with_: dict, ctx: StepContext) -> dict: ...
```

**Built-ins (v0)**

* `shell.run { cmd }`
* `python.call { target: "module:function", args?, kwargs? }`
* `http.request { method, url, headers?, json?, params? }`
* `llm.generate { model, system?, prompt, tools?, json_mode?, max_tokens?, temperature? }`
* `sqlite.query { db_path, sql, params }`
* `slack.post { webhook_env, text }`
* `twitter.post { token_env, text }`

---

## 8) Security & Secrets

* Secrets are **names only** in `.petal`; resolved from env/OS keyring at runtime.
* Mask secret values in logs/snapshots.
* `shell.run` runs confined to `cwd` by default; dangerous flags require `allow: true`.

---

## 9) CLI

```
petal validate path/to/file.petal      # schema + tool existence + dry template render
petal explain  path/to/file.petal      # show compiled canonical plan
petal run      path/to/file.petal [-p key=val ...] [--run-id <id>] [--dry]
petal list-tools                       # enumerate discovered tools + contracts
petal docs <tool-name>                 # show tool schema & examples
```

**Parameter overrides**

* `-p key=value` merges into `params` (CLI > file).

---

## 10) LSP (“petal-lsp”) — Editor Ergonomics

**v0 features**

* YAML schema validation/diagnostics.
* Autocomplete for tool names & `with` fields (from tool registry).
* Hover docs (tool description, writes).
* Code actions:

  * “Shorten to compact form”
  * “Expand to canonical form”
  * “Insert declared `writes`”
* Go-to definition for `imports.path`.

**Implementation**: Python + `pygls`, tool registry introspection.

---

## 11) Short-Form Example (End-to-End)

```yaml
version: 0.1
name: acme
description: Shell → LLM → DB → Slack → X
params: { prompt: "acme report", cmd: "ls -la" }
defaults:
  llm.model: gpt-4o-mini
  retry: { max: 2 }

steps:
  - shell.run: { cmd: "{{ cmd }}" }

  - llm.generate:
      prompt: "{{ prompt }}\n---\n{{ shell_out|truncate(800) }}"

  - sqlite.query:
      db_path: "app.db"
      sql: "SELECT id, name FROM items WHERE name LIKE :q"
      params: { q: "%{{ llm_query }}%" }

  - slack.post(if_error=skip, when="{{ rows|rows>0 }}"):
      text: "Found {{ rows|rows }} rows for '{{ llm_query }}'"

  - twitter.post: { text: "Update: {{ text }}" }
```

---

## 12) Canonical Result (Excerpt)

```yaml
steps:
  - id: shell.run#1
    uses: shell.run
    reads: [cmd]
    writes: [shell_out]
    with: { cmd: "{{ cmd }}" }
    when: null
    if_error: fail

  - id: llm.generate#1
    uses: llm.generate
    reads: [prompt, shell_out]
    writes: [llm_query, text]
    with:
      model: gpt-4o-mini
      prompt: "{{ prompt }}\n---\n{{ shell_out|truncate(800) }}"
```

---

## 13) Parser Rules (Short → Canonical)

1. **Normalize keys**

   * If mapping key matches `^(?P<tool>[\w\.]+)(?:\((?P<mods>.*)\))?$`:

     * `uses = tool`
     * Parse `mods` as `k=v` pairs → assign to `if_error`/`when`.
2. **Lift `with`**

   * If value is a mapping and **not** `use: <macro>`:

     * Treat that mapping as `with`.
3. **Macros**

   * A step with `use: <macro>`:

     * Clone macro steps, template-merge `with` into each.
4. **Defaults/Env**

   * Merge dotted `defaults` into step `with` when keys match.
5. **Reads/Writes**

   * `writes` from tool contract unless present.
   * `reads` inferred from template variables + explicit `with` dependencies.
6. **IDs**

   * Auto-generate `id = "{uses}#{ordinal}"` if none given.
7. **Validation**

   * Pydantic validation against tool input schemas; Jinja render “dry” for syntax check.
8. **Security**

   * Secret names validated exist in env if required by tools.

---

## 14) Testing Strategy

* **Golden tests** on `petal explain` output (canonical YAML).
* **Tool contract tests** per plugin (schema → example inputs → outputs).
* **Integration**: demo flow with faked Slack/Twitter and stubbed LLM.
* **LSP**: snapshot tests for completions, hovers, diagnostics.

---

## 15) Roadmap (Post-MVP)

* `foreach` / `parallel` blocks with joins.
* DAG inference from `reads`/`writes` with cycle checks.
* Content-addressed caching & artifact store.
* Human-in-the-loop: `ask.confirm`, `ask.edit`, `wait.event`.
* Hydra profile import shim.
* Rich TUI (purple Lily theme).

---

## 16) Change Log

* **v0.1** — Initial short-form spec, compiler to canonical, runner model, plugin hooks, LSP plan.

---

**Notes**

* This spec assumes Python ≥ 3.10, `pluggy`, `pydantic v2`, `jinja2`.
* Keep secrets in env/keyring; never commit secrets to VCS.
* The runner remains a single-process CLI for portability.

---

If you want, I can also generate a matching **JSON Schema** for the canonical form and a skeletal **`petal-lsp`** stub to ship alongside this doc.
