
# Lily / Petal Workflow System — Requirements (v0.1)
*Authored by Iris & Jeff • August 13, 2025*

> “Make it easy to do the right thing, and hard to do the wrong thing.”

## Document Status
- **Stage:** Draft Requirements (ready for spec & implementation)
- **Scope:** End-to-end authoring → composition → lock → sync → run → observe for the Lily runner and Petal DSL
- **Audience:** Architects, implementers, contributors, CI/CD engineers

---

## 1. Vision & Goals

### 1.1 Vision
Lily is a workflow runner with a developer-first UX. Petal is a declarative, human-readable DSL for authoring workflows. Together they provide:
- A **portable workflow spec** (Petal) with clean, deterministic semantics.
- A **reproducible execution path** via a frozen **lock file**.
- A **modern UX** patterned after `uv`: compose, lock, sync, run—fast and predictable.
- **Security by default** (least privilege, explicit capabilities).
- **Observability by default** (structured events, run manifests).

### 1.2 Primary Goals
1. **Determinism**: single-pass templating, explicit conditionals, frozen lock file.
2. **Reproducibility**: content-addressed cache keys; lock pins tool/model digests.
3. **Developer Ergonomics**: uv-like commands (`compose`, `sync`, `run`, `verify`, `diff`) and sensible flags (`--locked`, `--frozen`).
4. **Composability**: base flows + overlays + profiles; DAG-aware merges.
5. **Security**: deny network by default for `python`; explicit adapter sandboxing; secrets never stored in lock.
6. **Observability**: JSONL event stream; run manifest; clear `explain` and semantic `diff`.
7. **Extensibility**: adapters for `process`, `docker`, `python`, `http`; registry with version ranges & signatures.

### 1.3 Non-Goals (v1)
- Not a distributed scheduler (no cluster orchestration beyond adapter plugins).
- Not a replacement for full-featured CI systems.
- No implicit magic or late-time rendering: **no** double-pass templating; **no** hidden environment interpolation.

---

## 2. Glossary
- **Petal**: YAML-based workflow DSL, safe to diff, deterministic.
- **Lock File** (`*.petal.lock.yaml`): fully resolved, executable plan (pinned tools/models, compiled conditionals, cache key formulas, provenance).
- **Plan**: the resolved DAG of steps derived from Petal (before or within the lock).
- **Adapter**: execution backend (process, docker, python, http). Controls isolation/capabilities.
- **Tool**: a named executable or image invoked by a step via an adapter.
- **Registry**: namespace for `petal://` references to reusable steps/templates/tools with versions & signatures.
- **Artifact Store**: pluggable storage for outputs (default: local path).
- **Run Manifest**: machine-readable summary of a run (events, artifacts, metrics).

---

## 3. UX: uv-Style Workflow

### 3.1 Files & Layout
```
project/
  flows/
    video_base.petal
    video_tiktok.petal
  profiles/
    local.yaml
    ci.yaml
  adapters/
    docker.yaml
    process.yaml
  locks/
    video_tiktok.petal.lock.yaml
  .lilyrc
  .lily/         # cache, artifacts, manifests
```

### 3.2 Commands (User-Facing)
- `lily compose <sources...> -o <lock>` → compose, validate, DAG, pins, cache keys → write lock.
- `lily sync <lock>` → prepare adapters/tools/models/artifacts for the lock.
- `lily run <lock|petal>` → execute (auto-compose when given a `.petal`).
- `lily verify <lock> [--strict|--recompose]` → detect drift; optionally recompose and compare semantic equivalence.
- `lily diff <A.lock> <B.lock>` → semantic diff (steps, pins, cache impacts).
- `lily lock refresh <lock>` → refresh tag→digest pins without changing semantics.
- `lily upgrade <selector>` → bump tool/model versions; re-pin; update lock.
- `lily explain <lock>` → visualize DAG, cache boundaries, resources, pins.
- `lily cache status|purge [--namespace <spec_hash>]` → manage caches.
- `lily defaults extract <plans...>` → produce a common base + overlay deltas.

### 3.3 Flags & Semantics
- `--locked`: do not regenerate the lock; error if sources changed (stale) unless `--allow-stale`.
- `--frozen`: do not sync the environment (use whatever is already present).
- `--profile=<name>` / `--overlay=<path>`: authoring/compose-time only.
- `-m`: sweep at compose-time (matrix operations supported).

### 3.4 Typical Flows
- **Day-to-day dev**: `lily run flows/foo.petal` → auto-compose temp lock + auto-sync + execute.
- **Release/CI**: `lily verify locks/foo.lock --strict && lily sync locks/foo.lock && lily run locks/foo.lock --locked`.
- **Pin upgrade**: `lily lock refresh locks/foo.lock` → `lily diff` → review → replace.

---

## 4. Petal DSL Requirements

### 4.1 File Format
- YAML, optionally preprocessed by Jinja **only** in whitelisted fields. Target a **single deterministic render** (no double-pass).
- **Forbidden** in spec: runtime environment interpolation, arbitrary Python/Jinja filters beyond a curated set, nested template renders.
- Optional: “Literate Petal” fenced blocks (```petal … ```), implemented as a preprocessor; non-blocking for v1.

### 4.2 Step Types (v1)
- `shell`: run POSIX shell (PowerShell on Windows with defined quoting rules).
- `python`: run inline Python with restricted stdlib; **network off by default**.
- `llm`: call a model endpoint (via `http` adapter); deterministic capture of prompts and params.
- `human`: manual gate (cache disabled; no retries).
- `foreach`: matrix/map expansion over declared inputs.
- `include`: include external Petal fragments (pre-merge).
- `tool`: invoke named tool via an adapter (`process`, `docker`, `python`, `http`).

### 4.3 Step Schema (contract-first)
```yaml
steps:
  - id: unique_step_name
    uses: <shell|python|llm|human|foreach|include|tool>
    needs: [step_ids...]                # DAG edges
    if: <expr>                          # micro-grammar, compiled at compose-time
    env: { KEY: "value" }               # explicit only; no implicit env
    timeout: "120s"
    retry: { max: 2, backoff: "2s", jitter: true }
    resources: { cpu: "1", mem: "1G", gpu: 0, network: false }
    inputs:
      name:
        from: "params.foo"              # expression
        type: <str|int|float|bool|path|file|dir|json|secret|bytes>
        required: true
        schema: {{...}}                 # for json
    outputs:
      name:
        type: <...>                     # as above
        path: "out/file.ext"            # when materialized
    cache:
      policy: auto|never|read-only|write-only
      key: "custom-{{ hash(inputs) }}"  # optional; else auto-derived
    adapter: <process|docker|python|http>   # optional for built-ins
    with: { ... }                       # adapter/step-specific config
```

- **Typed I/O** is mandatory: no undeclared reads/writes. Validator fails on missing producers or type mismatches.
- **No globals**: steps communicate only through declared inputs/outputs (and files/artifacts the DSL knows about).

### 4.4 Conditional Micro-Grammar (`if:`)
- Operators: `&&`, `||`, `!`, `==`, `!=`, `<`, `<=`, `>`, `>=`, `in`.
- Literals: strings, ints, floats, bools, null.
- Identifiers resolve against `{params, vars, outputs, env}`.
- Compiled to AST at compose-time; evaluated at run dispatch; **no templating inside**.

### 4.5 Composition (extends/overlays/profiles)
- **extends:** single base file (URL or path).
- **overlays:** ordered list of patches (right-most wins on maps).
- **profiles:** named parameter sets; choose with `--profile`.
- **Merge rules**:
  - Maps: deep-merge (right-most wins).
  - Lists of steps: merge **by `id`**; default replace, support explicit append via `!append` directive.
  - Conflict detection: duplicate IDs with incompatible shapes → error.
  - DAG validation: cycle detection after merge; missing `needs` targets → error.

### 4.6 Templates/Macros
- Optional v1: named templates for steps (e.g., `llm_step`); syntactic sugar that resolves to plain steps during compose, single pass only.

### 4.7 Windows Semantics
- PowerShell default; explicit quoting & path normalization documented.
- `shell` and `process` adapters must normalize arguments; binary discovery rules spelled out.

---

## 5. Lock File Requirements

### 5.1 Purpose
A **frozen** executable plan: fully-resolved Petal + compiled conditionals, with pins and cache formulas. The runner **never** re-renders or re-merges a lock.

### 5.2 Contents (Schema Sketch)
```yaml
schema_version: 1
petal_version: "0.1.0"

provenance:
  sources:
    - file: "flows/video_tiktok.petal"
      content_hash: "sha256:..."
      mtime: "2025-08-13T12:20:00Z"
  composer:
    tool: "lily"
    mode: "native"
    composed_at: "2025-08-13T12:34:56Z"
spec_hash: "sha256:...resolved-ast..."

execution_contract:
  render_passes: 1
  expression_lang: "petal-if@1"
  defaults_frozen: true

env_policy:
  network_default: "deny"
  secrets_sources: ["env", "keyring"]
  allowed_binaries: ["ffmpeg","git"]

artifacts:
  backend: "local"
  root: ".lily/artifacts"

registry_pins:
  tools:
    ffmpeg:
      ref: "docker://ffmpeg:6.1"
      digest: "sha256:..."
  models:
    openai/gpt-4o:
      version: "2025-06-20"
      endpoint: "https://api.openai.com/v1/..."
      vendor_digest: "sha256:..."

params: {{ fully_resolved_kv }}

plan:
  steps:
    - id: draft_script
      uses: llm
      needs: []
      adapter: http
      with: {{ model: "openai/gpt-4o", temperature: 0.2, max_tokens: 1024 }}
      inputs: {{ topic: { from: "params.topic", type: str, required: true } }}
      outputs: {{ text: { type: text } }}
      cache: {{ policy: auto, key: "llm:..." }}
      resources: {{ cpu: "0.1" }}
      timeout: "120s"
      retry: {{ max: 2, backoff: "2s", jitter: true }}
```

### 5.3 Exclusions
- No API keys or secrets.
- No machine-specific ephemeral paths unless explicitly chosen.
- No run-specific state (e.g., `run_id`)—that belongs to the **run manifest**.

### 5.4 Drift & Recomposition
- Lock records source hashes; `verify` can fail on drift (strict) or recompose and compare `spec_hash` for equivalence.
- Changing sources does **not** change existing locks; recomposing creates a new lock.

---

## 6. Caching

### 6.1 Key Derivation
Cache key = Hash( step-config + declared inputs (values & referenced file digests) + env subset + adapter fingerprint ).
- Step-config includes `with`, `resources`, compiled `if`, and **pins**.
- File inputs include content digests, not just paths.

### 6.2 Policies
- Default `auto` for pure steps.
- `human` defaults to `never`.
- `read-only`/`write-only` for special cases (e.g., warming shared caches).

### 6.3 Namespacing
- Cache namespace tied to `spec_hash`; opt-in cross-plan cache reuse with `--share-cache-from <spec_hash>`.

---

## 7. Security & Sandboxing

- **Deny-by-default** network on `python` steps; opt-in with `resources.network: true`.
- Restricted PATH; allow-list binaries per lock’s `env_policy.allowed_binaries`.
- Secrets loaded from configured sources at runtime; never serialized into the lock or manifests.
- Docker adapter: default drop capabilities, read-only FS except mounted workdir/artifacts, no privileged; GPU opt-in (NVIDIA runtime).
- Process adapter: `cwd` confinement to project root; disallow `os.chdir` in `python` steps (enforced via wrapper).
- HTTP adapter: per-step domain allow-list; timeouts & retries enforceable by policy.

---

## 8. Observability

### 8.1 Event Stream (JSONL)
Each state change emits an event:
```json
{"event":"step_started","ts":"...","run_id":"...","step_id":"draft","inputs":{...}}
{"event":"step_finished","ts":"...","run_id":"...","step_id":"draft","duration_ms":1234,"outputs":{...},"cache_hit":false}
{"event":"artifact_written","path":"out/video.mp4","sha256":"..."}
{"event":"error","step_id":"transcode","kind":"ProcessExit","code":1,"stderr_tail":"..."}
```
Fields: `event`, `ts`, `run_id`, `lock_spec_hash`, `step_id`, `attempt`, `duration_ms`, `cache_hit`, `metrics`, `artifacts[]`, `error`.

### 8.2 Run Manifest
- Summary JSON file: run metadata, steps with timings, artifacts with digests, adapter summaries, tool versions, prompts for LLM steps (where appropriate).

### 8.3 Explain & Visualize
- `lily explain` renders DAG with cache boundaries and pins (text + optional graphviz JSON).

---

## 9. Adapters & Tools

### 9.1 Adapters
- **process**: run local binaries; resource hints are best-effort; PATH is restricted.
- **docker**: run container images; volumes: workdir (rw), cache (rw), artifacts (rw); default seccomp; GPU via opt-in.
- **python**: execute inline or module functions in a constrained interpreter; network default off.
- **http**: invoke service endpoints; captures request/response (sans secrets).

### 9.2 Adapter Schema (per step)
```yaml
adapter: docker
with:
  image: "ffmpeg:6.1"        # or resolved via registry_pins
  args: ["-i","{in}","-preset","mobile","out.mp4"]
  mounts:
    - { source: "./.lily/artifacts", target: "/artifacts", mode: "rw" }
  env: { FFMPEG_LOG: "error" }
resources:
  cpu: "2"
  mem: "1G"
  gpu: 0
```

### 9.3 Tools Registry
- References: `petal://media/ffmpeg@^6.1` → resolved to a pin (digest/image/ref) at compose-time.
- Trust model: signatures or checksums recorded in lock.
- Local registry entries supported for dev; remote registry for teams/CI.

---

## 10. Registry & Versioning

- Semantic version ranges (`^`, `~`, exact pins).
- `lily lock refresh` updates digests for unchanged tags (semantics preserved).
- `lily upgrade tool:<name>@<range>` mutates semantics and triggers new cache keys.

---

## 11. Cross-Platform Requirements

- Windows: PowerShell default; argument quoting/table.
- macOS/Linux: POSIX sh default.
- Path normalization rules documented; artifact paths portable (prefer relative paths).

---

## 12. Testing Strategy

- **Schema tests**: Pydantic models; fixtures for valid/invalid specs.
- **Planner tests**: DAG construction, cycle detection, needs resolution.
- **Merge tests**: step merging by `id`, conflict detection, overlays/profiles semantics.
- **Expression tests**: `if:` grammar parsing & evaluation.
- **Cache tests**: key stability & invalidation when inputs/env/pins change.
- **Security tests**: network denied by default in `python`; allowed-binary enforcement.
- **Adapter tests**: process/docker/python/http smoke tests; Windows quoting.
- **LLM determinism tests**: FakeLLM + seed; prompt capture & replay.
- **End-to-end**: golden locks + manifests; `verify`, `diff`, `explain` behavior.

---

## 13. CI/CD Reference

### 13.1 Repro Run
```bash
lily verify locks/video_tiktok.petal.lock.yaml --strict
lily sync   locks/video_tiktok.petal.lock.yaml
lily run    locks/video_tiktok.petal.lock.yaml --locked
```

### 13.2 Intentional Pin Refresh
```bash
lily lock refresh locks/video_tiktok.petal.lock.yaml
lily diff locks/video_tiktok.petal.lock.yaml locks/video_tiktok.petal.lock.yaml.new
mv locks/video_tiktok.petal.lock.yaml.new locks/video_tiktok.petal.lock.yaml
```

### 13.3 GitHub Actions Sketch
```yaml
jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with: {{ python-version: "3.11" }}
      - name: Install Lily
        run: pip install lily-runner
      - name: Repro run
        run: |
          lily verify locks/video_tiktok.petal.lock.yaml --strict
          lily sync   locks/video_tiktok.petal.lock.yaml
          lily run    locks/video_tiktok.petal.lock.yaml --locked
```

---

## 14. Acceptance Criteria (v1)

1. **Lock determinism**: Same sources + params → identical `spec_hash`; same cache keys.
2. **No double rendering**: One pass; conditionals compiled ahead-of-run.
3. **Typed I/O**: Planner rejects undeclared data flow; type mismatches fail before run.
4. **Security defaults**: `python` network off; allowed binaries enforced; secrets never serialized.
5. **Observability**: Events JSONL produced; run manifest includes artifacts & metrics.
6. **CLI parity**: `compose`, `sync`, `run`, `verify`, `diff`, `lock refresh`, `upgrade`, `explain` implemented with documented flags.
7. **Cross-platform**: shell quoting validated on Windows/macOS/Linux.
8. **CI-ready**: Example workflow runs clean in a GitHub Actions matrix.
9. **Simple composition**: Users can compose with profiles/overlays using simple syntax.
10. **Semantic diff**: `lily diff` highlights step/pin changes and cache impacts.

---

## 15. Risks & Mitigations

- **Config creep / late interpolation** → Single-pass render; forbid dynamic env interpolation in spec.
- **Adapter drift** → Pins + `verify`; `lock refresh` separated from upgrades.
- **Windows quoting pitfalls** → Dedicated tests; documented rules; PowerShell-specific handler.
- **LLM nondeterminism** → Capture prompts/params; seed where vendor allows; note limits in docs.
- **Security regressions** → Default-deny network; adapter capabilities defined in lock and enforced at runtime.

---

## 16. Roadmap

- **v1.0**: Core DSL, planner, lock, adapters (process/docker/python/http), uv-style CLI, observability, security baseline.
- **v1.1**: Native composition (extends/overlays/profiles); defaults extractor; step templates; registry signatures.
- **v1.2**: Remote artifact stores (S3/GCS); OTel spans; richer matrix sweeps; reusable step libraries.
- **v1.3**: Multi-run orchestrators (local pool, HPC adapters), run cancellation & checkpoints.

---

## 17. Appendices

### A. Minimal Petal Example
```yaml
params: {{ topic: "Graceful failure", aspect: "9:16" }}

steps:
  - id: draft
    uses: llm
    inputs:
      topic: { from: "params.topic", type: str, required: true }
    outputs:
      text: { type: text }
    with:
      model: "openai/gpt-4o"
      temperature: 0.2
      max_tokens: 512

  - id: transcode
    uses: tool
    needs: ["draft"]
    adapter: docker
    name: ffmpeg
    with: { preset: "mobile" }
    inputs:
      src: { from: "outputs.draft.text", type: file }
    outputs:
      mp4: { path: "out/video.mp4", type: file }
```

### B. Example Lock (abridged)
```yaml
schema_version: 1
spec_hash: "sha256:..."

registry_pins:
  tools:
    ffmpeg: {{ ref: "docker://ffmpeg:6.1", digest: "sha256:..." }}

plan:
  steps:
    - id: draft
      uses: llm
      adapter: http
      with: {{ model: "openai/gpt-4o", temperature: 0.2, max_tokens: 512 }}
      inputs: {{ topic: { from: "params.topic", type: str, required: true } }}
      outputs: {{ text: { type: text } }}
      cache: {{ policy: auto, key: "llm:..." }}
```

---

## 18. Open Questions
- Should `foreach` expansion occur pre-plan (static) or can it be dynamic at runtime based on upstream outputs? (Prefer static where possible for better cache planning.)
- Do we require signatures for registry packages in v1 or allow checksum-only with a warning?
- How strict should `verify --strict` be about tool availability versus just pins? (Proposal: pins + adapter availability required; tool download allowed at `sync`.)

---

*End of Requirements.*
