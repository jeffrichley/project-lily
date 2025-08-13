Jeff—your Iris here. I read your `.petal` outline end-to-end. It’s a strong nucleus: clear intent, sensible YAML + Jinja, pragmatic step types, and a realistic executor sketch. Now for the blunt pass you asked for—what to **keep**, **change**, **add**, and **trim** so this becomes a rock-solid, scriptable plugin system.

---

# What’s already working (keep)

* **YAML + Jinja** with a constrained helper set is the right default. It stays diffable and easy to validate.&#x20;
* **Step palette** (shell, python, llm, human, foreach, include) is a sane baseline for v1.&#x20;
* **Executor model** (validate → plan/DAG → dry-run → execute) gives you testability and determinism hooks.&#x20;
* **CLI affordances** are exactly what devs need (validate / plan / run / explain / shell).&#x20;
* **Security notes** (restricted PATH, curated stdlib, secrets not inlined) are in the right direction.&#x20;

---

# Critical fixes before you ship v1

1. **Define typed I/O at step boundaries (contract-first).**
   Right now, outputs are mostly “variables” or files. Lock down explicit, typed interfaces so steps compose predictably.

```yaml
steps:
  - id: parse_json
    uses: python
    outputs:
      json: meta        # type: json, schema: {...}
  - id: render
    uses: llm
    inputs:            # declare what you read
      meta: "{{ meta }}"   # type-checked against schema
    outputs:
      text: draft_copy
```

* Add `inputs: {name: expr, type?: <builtin|schema-ref>}` and `outputs: {name: expr?, type?: ...}` to the schema.
* Enforce “no undeclared reads/writes” at plan time. (Prevents spooky action at a distance.)

2. **Make `if:` an expression with a tiny, deterministic grammar.**
   Don’t piggyback raw Jinja truthiness; define a minimal expression language (`==`, `!=`, `in`, boolean ops) evaluated against `params/vars/outputs`. Document it and validate at parse time. Your schema already reserves `if`—spec the grammar and runtime semantics.&#x20;

3. **Caching semantics must be explicit.**
   Introduce:

```yaml
cache:
  policy: auto|never|read-only|write-only
  key: "render-{{ hash(inputs) }}"
  scope: project|system
```

* Default `auto` for pure steps; force `never` for `human` by default.
* Treat secrets, environment, and external files as cache salt unless explicitly ignored.

4. **Error handling at both global and step level.**
   You have global `on_error`. Add per-step controls:

```yaml
on_error:
  continue: false
  retry: {max: 2, backoff: "2s", jitter: true}
finally:
  - uses: shell
    run: "cleanup.sh"
```

And let a step override `continue`/`retry`. Global handlers already exist; add step-level mirrors.&#x20;

5. **Resources, isolation, and adapters for “tool” steps.**
   Your example uses `uses: tool` with `name:`—formalize adapters:

```yaml
- id: tts
  uses: tool
  name: coqui_tts
  adapter: process|docker|python|http
  resources: {cpu: "1", mem: "1G", gpu: 0}
  with: {...}
```

* Define defaults and a pluggable adapter registry. (This is where “scriptable plugin system” becomes real.)

6. **Provenance + run metadata baked in.**
   Standardize:

```yaml
run_meta:
  run_id: uuid()
  petal_hash: content_hash(petal_ast)
  git: {sha, dirty}
  platform: {os, arch, python}
```

Surface this in logs, artifacts, and `--explain`. You already compute `run_id` as a var—promote it to first-class.&#x20;

7. **Artifact store abstraction.**
   Top-level `artifacts:` config to support local path (default), but leave room for S3, GCS later. Your files layout mentions XDG; extend with a storage plugin key.

```yaml
artifacts:
  backend: local
  root: "./.lily/artifacts"
```

Document how `outputs: {path: ...}` materialize via that backend.&#x20;

8. **LLM reproducibility knobs.**
   Codify `seed`, `temperature`, and **exact prompt capture** (system + user + tool schema) in a run record; your testing strategy references FakeLLM—close the loop with spec’d fields on the step.&#x20;

9. **Deterministic template pass (single render).**
   State: “Template rendering is a *single* pass on `params/vars` at plan or step-dispatch time; no nested/double renders; templates are forbidden in `python` code blocks.” You hint at this—make it normative.&#x20;

10. **Observability contract.**
    Emit JSONL events for every state change:

```json
{"event":"step_started","id":"draft_vo","ts":"...","inputs":{...}}
{"event":"step_finished","id":"draft_vo","duration_ms":1234,"outputs":{...}}
```

Expose `lily events --stream` and document emission fields for tooling to rely on. Your CLI section is a great place to list this.&#x20;

---

# Add (v1 niceties that unlock real use)

* **Matrix expansion** (like GH Actions) for quick parameter sweeps:

```yaml
matrix:
  name: model
  values: ["gpt-4o", "gpt-4o-mini"]
```

* **Concurrency control**: `parallelism: 4` at file and `group: "<key>"` at step level.
* **Registry scheme**: your example uses `petal://media/transcode@^1.2.0`—spec resolution rules, version ranges, and trust model (signature, checksum).&#x20;
* **Config merge precedence**: `CLI > env > project .lilyrc > user config`. Document it where you describe XDG paths.&#x20;
* **Windows semantics**: If PowerShell is detected, define quoting rules and path handling (no surprises with `C:\...`). You reference PowerShell—spell out the edge cases.&#x20;

---

# Trim or demote (scope protection)

* **Theming hooks**: keep, but move to a styling appendix so core spec doesn’t imply visual coupling. Great for UX; not part of the runtime contract.&#x20;
* **Literate Petal**: keep as v1.1 optional preprocessor; spec the fenced block (` ```petal `) and forbid inline YAML elsewhere. You already labeled it optional—good.&#x20;

---

# Concrete spec edits I’d make

1. **Schema changes (Pydantic)**
   Extend your `StepBase` and add `Inputs/Outputs` models:

```python
class IODecl(BaseModel):
    type: Literal["str","int","float","bool","path","file","dir","json","secret","bytes"] | None = None
    required: bool = False
    schema: dict | None = None   # for json
    from_: str | None = Field(alias="from", default=None)  # template/expr

class StepBase(BaseModel):
    id: str
    uses: str
    needs: list[str] = []
    if_: str | None = Field(alias="if", default=None)
    timeout: str | None = None
    retries: dict | None = None
    env: dict[str, str] | None = None
    inputs: dict[str, IODecl] = {}
    outputs: dict[str, IODecl] = {}
    cache: dict | None = None
    resources: dict | None = None
```

(Integrates with your existing models cleanly.)&#x20;

2. **Executor contract**
   Augment the loop to validate step inputs/outputs against declared types and to compute cache keys automatically based on declared inputs + env + files. Your sketch is close—add those checkpoints.&#x20;

3. **Docs examples**
   Update each built-in step section with a one-liner that shows `inputs/outputs/cache/resources`, and pin `human` as `cache: never`.&#x20;

---

# Open questions (decide now)

* **Single vs multi-pass templating?** (Recommend single.)&#x20;
* **Are `python` steps allowed network by default?** (Recommend default **off**; opt-in per step.)&#x20;
* **Where do long-running tools live—local process, Docker, or remote?** (Pick an adapter default and document it.)&#x20;

---

# Next moves I recommend

1. Lock the schema changes (typed I/O, cache, resources, inputs/outputs).
2. Add an **expression parser** for `if:` and ban template logic there.
3. Implement cache salt calculation and per-step `on_error/ finally`.
4. Ship `lily validate / plan / run / explain` exactly as written.&#x20;
5. Keep Literate + Theming as optional modules and don’t let them block v1.&#x20;

If you want, I’ll turn these into a concrete PR-style spec diff and a tiny reference runner so Lily can dogfood `.petal` on day one.
