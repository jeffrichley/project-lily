Hey Jeff — Iris reporting in 💜 Here’s a crisp, opinionated v1 design for **`.petal`** files plus an execution model and test plan. You can ship this as a spec today and grow it later without painting yourself into a corner.

---

# .petal v1 — Design & Implementation Guide

> *“Make it work, make it right, make it beautiful.”* — Kent Beck

## Core goals

* **Readable** for humans, **parsable** for machines.
* **Deterministic by default** (dry-runnable, cacheable).
* **Composable** (import other Petals), **testable** (LLM stubs), **secure** (sane sandboxing).

---

## Format choice

### ✅ v1: YAML + Jinja interpolation

* **Reason:** dead-simple to parse, diff, validate, and snapshot-test.
* **Interpolation:** `{{ var }}` using Jinja2 with a constrained sandbox.

### ✅ v1.1: “Literate Petal” (`.petal.md`) preprocessor (optional)

* Allow Markdown with fenced blocks that compile to the same YAML AST.
* Keeps docs, rationale, and code in one file for complex flows.

---

## Minimal spec (YAML)

```yaml
# hello-world.petal
petal: "1"
name: "Hello World"
description: "Small demo showing shell → llm → python → human gate."
params:
  name: {type: str, required: true, help: "Your name"}
  output_dir: {type: path, default: "./out"}

env:
  LILY_LOG_LEVEL: "INFO"

vars:
  run_id: "{{ now('%Y%m%d-%H%M%S') }}"
  outdir: "{{ abspath(output_dir) }}/{{ run_id }}"

steps:
  - id: prepare
    uses: shell
    run: |
      mkdir -p "{{ outdir }}"

  - id: greet_draft
    uses: llm
    model: "gpt-4o"
    system: "You are Lily, a concise assistant."
    prompt: |
      Write a one-line greeting to {{ name }}.
    outputs:
      text: greet_text  # stored into context.vars.greet_text

  - id: write_file
    uses: python
    code: |
      from pathlib import Path
      Path("{{ outdir }}/greeting.txt").write_text("{{ greet_text }}\n")

  - id: approve
    uses: human
    message: "Open {{ outdir }}/greeting.txt ? Approve to continue."
    default: true

  - id: finalize
    uses: shell
    run: |
      echo "Done for {{ name }} at {{ outdir }}" | tee "{{ outdir }}/status.log"

outputs:
  - path: "{{ outdir }}/greeting.txt"
  - path: "{{ outdir }}/status.log"

on_error:
  - uses: shell
    run: "echo 'failed {{ run_id }}' >> .lily/failures.log"
```

---

## Execution model (runtime)

* Load → **Validate** (Pydantic) → **Plan** (DAG) → **Dry-run** (optional) → **Execute**.
* `steps[*]` run **sequentially** by default; support `needs:` to form a DAG and parallelize.
* Context has **three scopes**:

  * `params`: user-supplied inputs (typed).
  * `vars`: computed/intermediate values.
  * `artifacts`: resolved file outputs (paths).
* Each step may declare:

  * `needs: [ids...]`
  * `timeout: "30s"`, `retries: {max: 2, backoff: "2s"}`
  * `cache_key: "render-{{ hash(inputs) }}"` (skip if cache hit)

---

## Step types (built-ins)

```yaml
# Common fields: id, uses, needs?, if?, timeout?, retries?, env?, cwd?,
#                inputs?, outputs?, cache_key?
```

1. **shell**

   * `run: |` multi-line script
   * Runs in `/bin/sh` (or `powershell` on Windows if detected)
   * Captures `stdout`, `stderr`, and `exit_code`
   * Optionally exposes `stdout` to `outputs.text`

2. **python**

   * `code: |` inline Python snippet
   * Executes in an isolated module namespace with a safe utility API (no `eval` of templates inside code)
   * Passes `ctx` (read-only params/vars/artifacts, plus helpers)

3. **llm**

   * `model`, `system?`, `prompt`, `tools?`, `temperature?`
   * **Determinism toggle:** `seed?`, `temperature: 0` for tests
   * `outputs: {text: var_name}` (primary), optionally `json: var_name` with strict schema

4. **human**

   * Gates the flow for approval or selection
   * `message`, `choices?`, `default?`
   * In non-interactive mode: auto-uses `default` (useful for CI)

5. **foreach**

   * Fan-out a subgraph over a list
   * `items: "{{ files }}"`, `do: [ ...steps... ]`
   * Aggregates artifacts/vars into lists

6. **include**

   * Import another Petal:

     ```yaml
     - uses: include
       from: "petal://media/transcode@^1.2.0"
       with: { input: "{{ video }}", preset: "web" }
     ```

---

## Templating rules (Jinja)

* **Allowed filters/helpers:** `now`, `hash`, `tojson`, `abspath`, `relpath`, `env`, `basename`, `dirname`, `uuid`, `joinpath`.
* **No Python in templates.** All computation in `python` steps.
* **Undefined → error** (fail fast). Provide `default()` when needed.

---

## Validation (Pydantic models)

Define a strong schema so you can `lily validate file.petal` and catch issues early.

```python
# sketch
class Param(BaseModel):
    type: Literal["str","int","float","bool","path","file","dir","json","secret"]
    required: bool = False
    default: Any | None = None
    help: str | None = None

class StepBase(BaseModel):
    id: str
    uses: str
    needs: list[str] = []
    if_: str | None = Field(alias="if", default=None)
    timeout: str | None = None
    retries: dict | None = None
    env: dict[str, str] | None = None

class Petal(BaseModel):
    petal: Literal["1"]
    name: str
    description: str | None
    params: dict[str, Param] = {}
    env: dict[str, str] = {}
    vars: dict[str, str] = {}
    steps: list[StepBase]
    outputs: list[dict] = []
    on_error: list[StepBase] = []
```

---

## Security & sandboxing

* **Shell:** default to a **restricted PATH** (tool allowlist), no network unless `allow_net: true`.
* **Python:** provide a **curated stdlib surface** (pathlib, json, re, datetime), no `os.system`, no raw `subprocess` (expose a safe wrapper).
* **Secrets:** never inline; reference from environment or keyring:

  ```yaml
  params:
    openai_key: {type: secret, required: true}
  ```

  At runtime, resolve from `env`/keyring; never echo in logs.

---

## Filesystem layout (XDG-aware)

* Config: `$XDG_CONFIG_HOME/lily/config.yaml`
* Cache: `$XDG_CACHE_HOME/lily/` (step caches by `cache_key`)
* Data/artifacts: `$XDG_DATA_HOME/lily/` (or project-local `./.lily/` with `--local`)

---

## CLI affordances

```bash
lily validate demo.petal         # schema & template validation
lily plan demo.petal --params name=Jeff
lily run demo.petal --params name=Jeff --dry-run
lily run demo.petal --params name=Jeff --explain   # prints planned DAG + variable binds
lily shell                       # persistent prompt (prompt_toolkit) using same runtime
```

* **Typer**: entry points & one-shots.
* **prompt\_toolkit**: persistent `lily shell` with:

  * command completion from `steps`
  * syntax highlighting for YAML & fenced blocks
  * quick “inspect step” popovers

---

## Testing strategy (what to lock down)

* **Schema tests:** invalid fields error messages (snapshot).
* **Planning tests:** DAG shape given `needs` and `if`.
* **Deterministic LLM:** inject `FakeLLM(model="test", responses=...)`.
* **Dry-run snapshots:** `lily plan` output (ANSI stripped).
* **E2E:** build wheel, `subprocess` run against a sample `.petal`.

---

## Rich & theming hooks

* Reuse the **Iris Bloom** palette:

  * Step IDs → `heading`
  * Shell lines → `muted`
  * Success/Warning/Error → mapped styles
* Honor `NO_COLOR=1` and fall back to plain text for snapshots.

---

## Example: Literate Petal (`.petal.md` → compiled AST)

````markdown
# Video Teaser Petal

```petal
petal: "1"
name: "Teaser Builder"
params:
  script: {type: file, required: true}
  music:  {type: file, required: true}
vars:
  outdir: "{{ abspath('./out') }}/{{ now('%Y%m%d-%H%M') }}"
steps:
  - id: prep
    uses: shell
    run: "mkdir -p {{ outdir }}"
  - id: draft_vo
    uses: llm
    model: "gpt-4o"
    prompt: |
      Turn this script into a punchy 15s VO:
      {{ file(script) }}
    outputs:
      text: vo_text
  - id: tts
    uses: tool
    name: "coqui_tts"
    with: { text: "{{ vo_text }}", voice: "iris", out: "{{ outdir }}/vo.wav" }
  - id: cut
    uses: tool
    name: "ffmpeg_concat"
    with: { audio: "{{ outdir }}/vo.wav", music: "{{ music }}", out: "{{ outdir }}/final.mp4" }
outputs:
  - path: "{{ outdir }}/final.mp4"
````

````

---

## Implementation sketch (executor core)

```python
# pseudo-code outline
def run_petal(petal: Petal, params: dict, *, dry_run=False):
    ctx = Context(params=params, vars=render_vars(petal.vars, params))
    dag = compile_steps_to_dag(petal.steps)
    for step in topo_sort(dag):
        if not passes_if(step, ctx):
            continue
        with step_context(step, ctx):
            if dry_run:
                render_preview(step, ctx); continue
            execute_step(step, ctx)  # dispatch by uses: shell/python/llm/...
    materialize_outputs(petal.outputs, ctx)
    return ctx
````

---

## Versioning & compatibility

* Top-level `petal: "1"` is the **only stability contract** in v1.
* Add new step fields as **backward-compatible optionals**.
* Breaking changes bump to `petal: "2"`; provide `lily migrate`.

---

## Nice-to-haves (soon, not now)

* **`when:`** (cron-like triggers), **watch mode** for directories.
* **Remote runners** (Docker, k8s) with resource hints.
* **`petal-lsp`** for schema-aware editor help.

---

### TL;DR plan

1. Ship YAML spec + Pydantic schema.
2. Build a tiny runtime (plan → dry-run → execute).
3. Add Typer commands + prompt\_toolkit shell.
4. Lock in tests (schema, plan snapshot, E2E with fake LLM).
5. Later: literate mode, imports, remote runners.
