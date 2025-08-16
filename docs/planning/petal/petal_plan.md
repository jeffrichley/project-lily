Hey Jeff — Iris here. I’d build Lily’s **Petal** system using a *walking skeleton, center-out* approach: start with the **executor core + canonical schema**, prove end-to-end with one trivial tool, then layer the **short-form compiler**, **plugin system**, **built-ins**, **CLI**, and finally **LSP**. This gives you correctness and testability from day one, and every layer has a tight Definition of Done.

Below is a super-detailed, sequenced plan with tasks, tests, and acceptance criteria.

---

# Project Lily — Petal Implementation Plan (Center-Out, Walking Skeleton)

## Guiding Principles

* **Center-out:** executor & canonical schema first → compile short-form later.
* **Contracts everywhere:** tool I/O declared up front (schema + writes).
* **Determinism:** dry-run + explain mode before side effects.
* **Golden tests:** lock the compiler/executor behavior with snapshot tests.
* **Local-first:** no servers/daemons; one CLI entrypoint.

---

## Phase 0 — Repo Scaffolding & Foundations

**Goal:** Clean structure, typing, and CI from the start.

**Tasks**

* Create repo layout:

  ```
  lily/
  ├─ petal/               # runtime library
  │  ├─ core/             # executor, state, errors
  │  ├─ model/            # pydantic models (canonical schema)
  │  ├─ compile/          # short→canonical compiler
  │  ├─ plugins/          # hookspec + loader
  │  ├─ builtins/         # shell, sqlite, llm, http, slack, twitter
  │  └─ lsp/              # petal-lsp (later)
  ├─ cli/                 # CLI entrypoint (`petal`)
  ├─ tests/               # unit/integration/golden
  ├─ examples/            # demo .petal files
  └─ pyproject.toml
  ```
* Tooling: Ruff, MyPy (strict-ish), pytest, coverage, pre-commit.
* Decide Python ≥ 3.10, Pydantic v2, Jinja2, Pluggy.

**Tests**

* CI runs `ruff`, `mypy`, `pytest` green.

**DoD**

* Clean install with `uv` works; CI green.

---

## Phase 1 — Canonical Schema & Executor “Walking Skeleton”

**Goal:** Execute a **canonical** Petal document with one no-side-effect tool.

**Tasks**

1. **Canonical models (Pydantic)**

   * `PetalFile`, `Step`, `Retry`, enums for `if_error`.
   * JSON Schema export (`petal schema` CLI command stub).
2. **Executor core**

   * Load canonical YAML/JSON → validate → sequentially run steps.
   * State is a `dict[str, Any]` merged with each step’s result.
   * Persistence: `.runs/<run_id>/timestamp.json` snapshots.
   * Error policy: `fail|skip|retry` with simple backoff.
   * Dry-run mode: *validate only*, no tool execution.
3. **Minimal tool interface (no pluggy yet)**

   * In-process registry: `{name: Callable[ctx, with_] -> dict}`.
   * Implement **`debug.echo`** (returns inputs), **`python.eval`** (pure function call), both side-effect free.

**Tests**

* Unit: model validation (bad/missing keys), executor merges.
* Integration: canonical file with 2 steps reaches final state; dry-run prints plan.
* Golden: snapshot `.runs` JSON shape.

**DoD**

* `petal run canonical.yaml` executes and prints final state.
* `petal explain canonical.yaml` shows ordered steps & resolved retry.

---

## Phase 2 — Tool Contracts & Pluggy Plugin System

**Goal:** Externalize tools cleanly with declared inputs/outputs.

**Tasks**

1. **Hook spec**

   * `petal_tools() -> list[ToolInfo]` (name, input\_schema, writes, description)
   * `petal_execute(tool, with_, ctx) -> dict`
   * `StepContext`: `state`, `run_dir`, `env`, `logger`.
2. **Loader**

   * Discover entry points group `petal.plugins`; merge with built-ins.
   * Validate `with_` against `input_schema` before execute.
3. **Writes enforcement**

   * Record tool’s declared `writes`; executor verifies returned keys ⊆ declared (warn if extra, error if missing when required).
4. **Docs**

   * `petal list-tools`, `petal docs <tool>` prints schema & examples.

**Tests**

* Fake plugin registers a tool; executor finds and runs it.
* Schema validation error on bad input.
* Mismatch between declared writes and actual output → diagnostic.

**DoD**

* Tools are pluggable via pip; `list-tools` shows them with schemas.

---

## Phase 3 — Built-in Tools v0

**Goal:** Useful set of tools with side-effects guarded.

**Tasks**

* `shell.run { cmd, cwd?, allow? }` (deny dangerous flags unless `allow=true`; capture stdout/stderr/rc).
* `http.request { method, url, headers?, params?, json?, data? }`.
* `sqlite.query { db_path, sql, params }`.
* `llm.generate { model, system?, prompt, tools?, json_mode?, temperature?, max_tokens? }` (wire to your current wrapper; allow stub).
* `slack.post { webhook_env, text }`.
* `twitter.post { token_env, text }`.
* Secrets resolution: name-only in file, pulled from env/keyring at runtime; redact in logs.

**Tests**

* Unit: each tool validates inputs; returns declared writes.
* Integration: demo canonical flow uses shell→llm(stub)→sqlite→slack.
* Security: shell denied without `allow`; secrets masked in snapshots.

**DoD**

* Example canonical flow runs end-to-end locally with env secrets.

---

## Phase 4 — Short-Form Compiler (YAML+Jinja → Canonical)

**Goal:** Author ergonomic short files and compile them deterministically.

**Tasks**

1. **Parser**

   * Detect short step keys: `toolName(when=..., if_error=...)`.
   * Value map becomes `with`.
   * Macro expansion (`macros`, `use:` with optional `with` merge).
2. **Templating**

   * Jinja env with helpers: `truncate`, `head`, `rows`, `now`, `json`.
   * Template context resolution order: `locals → params → state → env → secrets`.
3. **Inference**

   * `id`: auto `{tool}#{ordinal}` if absent.
   * `writes`: from tool contract (unless overridden).
   * `reads`: parse templates for bare symbols → map to `state.*`/`params.*`.
4. **Defaults & profiles**

   * `defaults:` dotted keys injected into matching tool inputs.
   * `env:` mapping.
   * Optional `profile` + `apply:` overlay.
5. **CLI**

   * `petal explain short.petal` → shows compiled canonical YAML.
   * `petal validate` renders and validates without executing.

**Tests**

* Golden: short→canonical snapshots for each construct (mods, macros, profiles, defaults).
* Template failure surfaces line/column with helpful message.
* Round-trip: canonical produced is valid for executor.

**DoD**

* Short examples from our docs compile & run via executor with `petal run`.

---

## Phase 5 — Caching, Snapshots, and Provenance

**Goal:** Performance and debuggability.

**Tasks**

* Content-addressed cache: key = hash of (`tool`, normalized `with`, selected `reads` from state).
* Cache store under `.runs/cache/…` with metadata: inputs, outputs, tool version.
* Explain shows cache hits/misses.
* Event log (`state.events`) appends `{step, phase, ts, writes, from_cache}`.

**Tests**

* Re-run identical flow hits cache.
* Changing input invalidates cache; different `model` or `sql` → miss.
* Cache poisoning prevention: secret values not hashed (use placeholder tokens only).

**DoD**

* `petal run --use-cache` speeds up repeat runs; explain shows hit/miss.

---

## Phase 6 — Error Handling & Human-in-the-Loop Primitives

**Goal:** Make failures recoverable and interactive (still local).

**Tasks**

* Retry policy: global default + per-step override; jitter/backoff.
* `ask.confirm { message }` tool that pauses for TTY input (`--yes` to auto).
* `if_error: skip|retry|fail` already supported; add `retry: {max, backoff, jitter}` per step.

**Tests**

* Induce http failure → retry then succeed.
* Confirm step pauses unless `--yes` passed to CLI.

**DoD**

* Controlled retries and local approvals work reliably.

---

## Phase 7 — CLI UX Polish

**Goal:** Daily usability.

**Tasks**

* Commands: `run`, `explain`, `validate`, `schema`, `list-tools`, `docs`.
* Flags: `--run-id`, `--dry`, `--use-cache`, `-p key=value` (param overrides), `--env-file`.
* Pretty plan output with step numbers, when conditions, inferred reads/writes.

**Tests**

* CLI argument parsing; param overrides reflected in explain and run.

**DoD**

* Smooth DX; docs/examples match behavior.

---

## Phase 8 — LSP (petal-lsp) MVP

**Goal:** First-class authoring in editors.

**Tasks**

* Build with `pygls`.
* Capabilities:

  * YAML schema validation (use canonical JSON Schema behind the compiler).
  * Completions for tool names and `with` fields (read from registry).
  * Hover: tool docs, declared `writes`.
  * Diagnostics for unknown tools, missing required inputs.
  * Code actions: **Shorten ↔ Expand**, **Insert declared writes**.
* Command integration: run/validate from editor (optional).

**Tests**

* Protocol unit tests; snapshot completions for built-ins.

**DoD**

* VS Code can validate & complete `.petal` files using the LSP.

---

## Phase 9 — Guardrails & Security Hardening

**Goal:** Safe by default.

**Tasks**

* Shell sandbox defaults (cwd confinement, denylist).
* HTTP allowlist domains (configurable).
* Secrets never serialized; redaction middleware.
* Optional “dry-secrets” mode: require secrets to be present, but never expose.

**Tests**

* Attempt to print secrets in templates → redacted.
* Denied shell flag produces clear error + remediation hint.

**DoD**

* Security checks enabled by default; can be relaxed explicitly.

---

## Phase 10 — Docs, Examples, and Dogfooding

**Goal:** Real usage proves design.

**Tasks**

* Write **five** end-to-end example petals:

  1. shell → llm → sqlite → slack (from our spec)
  2. http GET → llm json\_mode → twitter
  3. foreach list of items → parallel shell checks (stub until parallel lands)
  4. human-in-loop confirm before posting
  5. pure-python toolchain (`python.call` with repo function)
* “How to write a plugin” doc with a Slack plugin example.
* FAQ: error policies, caching, secrets, templating gotchas.

**Tests**

* Each example has a corresponding integration test with fakes.

**DoD**

* Examples run locally and pass CI.

---

## Why “Executor First, Then Compiler” (Center-Out)?

* **Correctness early:** You can run real flows (canonical) before ergonomics work.
* **Test leverage:** The same executor underpins both forms; compiler only needs golden tests.
* **Risk isolation:** Tool execution, retries, secrets, and security are validated before parsing tricks complicate debugging.
* **Faster dogfooding:** You can script canonical petals for internal tasks immediately.

---

## Risk Register & Mitigations

* **Template variable inference (reads) is brittle.**
  *Mitigate:* treat as “best-effort” for explain/caching; allow explicit `reads` override when needed.
* **Secrets in templates.**
  *Mitigate:* redaction pass post-render; discourage direct interpolation—prefer tool fields referencing secret names.
* **LLM variability affects caching.**
  *Mitigate:* cache key excludes non-deterministic fields (temperature); support `json_mode` to stabilize outputs.

---

## Acceptance Checklist (High Level)

* [ ] Canonical executor runs sequential steps, with retries and snapshots.
* [ ] Pluggy tools load; `list-tools` and `docs` work.
* [ ] Built-ins: shell, http, sqlite, llm, slack, twitter.
* [ ] Short-form compiler produces canonical with golden tests.
* [ ] CLI: run/validate/explain/schema; param overrides.
* [ ] Caching + provenance log.
* [ ] LSP MVP: validation, completions, hovers, code actions.
* [ ] Security defaults (sandbox shell, redact secrets).

---

## Suggested Build Order (condensed)

1. **Phase 0–1:** Canonical schema + executor + debug tools (walking skeleton).
2. **Phase 2:** Pluggy contracts; move tools behind plugins.
3. **Phase 3:** Built-ins (useful set).
4. **Phase 4:** Short-form compiler + explain/validate.
5. **Phase 5–6:** Caching + error/confirm primitives.
6. **Phase 7:** CLI polish.
7. **Phase 8:** LSP MVP.
8. **Phase 9–10:** Security hardening, docs, dogfooding.

---

If you want, I can immediately turn this into a repo initializer (folders, stubs, tests, and a working canonical example) so Lily can start eating petals on day one.
