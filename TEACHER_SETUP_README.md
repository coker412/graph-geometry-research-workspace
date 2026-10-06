# Environment setup

Use this guide to hand the framework to another researcher or their assistant. Read it together with `AGENTS.md`, which governs research, evidence, directories, and authorization.

`./setup.sh --check` performs local configuration and checks without downloading software. Only an authorized `./setup.sh --bootstrap` creates environments and optionally installs Rethlas outside the workspace.

To share the framework without research data, use:

```bash
./tools/export_teacher_framework.sh
```

The script produces an allowlisted archive, a SHA-256 file, and an internal manifest under `exports/`. Do not archive the entire private workspace. See [framework handoff](TEACHER_FRAMEWORK_HANDOFF.md) for the distribution boundary.

An assistant can follow [SETUP_AI_PROMPT.md](SETUP_AI_PROMPT.md), first reporting the local checks in `SETUP_REPORT.md`, then obtaining authorization for installation. The ordinary queue does not need Rethlas:

```bash
./setup.sh --bootstrap --without-rethlas
```

## Paths and customization

Directory names and example paths are configurable. You may adapt research rules, project names, model settings, iteration limits, and tmux session names to your own work. Keep the assistant's `AGENTS.md`, wrapper paths, and actual directory layout consistent.

Recommended layout:

```text
/path/to/research/
├── graph-geometry/
└── Rethlas/
```

Rethlas must be outside the workspace. `setup.sh` rejects an internal `RETHLAS_ROOT`. If it is elsewhere:

```bash
export RETHLAS_ROOT=/path/to/Rethlas
```

Run workspace commands from the workspace root unless stated otherwise. Project-specific instructions belong in each project's README or handoff guide. The public package contains no private projects; first execution of a new queue item creates `projects/conjecture-<slug>/`.

```text
projects/                          # One directory per research project.
projects/<project>/rethlas/         # Problem statements, results, and run records.
tools/rethlas/                      # Workspace wrappers for external Rethlas.
templates/rethlas-problem.md        # Problem template.
```

## Python

```bash
conda create -n graphlab python=3.11 -y
conda activate graphlab
```

Install additional dependencies according to the project's README or a diagnosed missing dependency. SAT experiments may, for example, need `python-sat`. Do not place API keys or private configuration in tracked files or edit `.env` files.

## References

```text
projects/<project>/references.md                  # Bibliography and reading index.
projects/<project>/notes/                         # Proofs, reading notes, calculations.
projects/<project>/rethlas/problems/<name>.refs/  # Context for one Rethlas problem.
shared/references/                                # Material shared across projects.
```

For material used throughout a project, update its reference index and store the source or notes in the project. For one Rethlas problem, use its `.refs/` directory; the wrapper copies it to the external generation agent. Prefer Markdown, LaTeX, or plain text. PDFs are supported when `pdftotext` is installed.

Shared material belongs under `shared/references/` with links from project indexes. Avoid scattering references across the workspace root. Record any alternative directory convention in `AGENTS.md`.

## Codex CLI

Codex CLI calls models to reason, write proofs, and resume sessions. Rethlas adds proof-generation and verification agents; it also depends on Codex CLI. These are tools rather than local model weights.

Check the [current official installation instructions](https://developers.openai.com/codex/cli/) before installing. With Node/npm available, the setup command documented by this framework is:

```bash
npm install -g @openai/codex
codex --version
```

Complete login yourself. Never commit authentication files. If you use different models, update the applicable configuration or environment settings. Rethlas configuration locations include:

```text
/path/to/Rethlas/agents/generation/.codex/config.toml
/path/to/Rethlas/agents/verification/.codex/config.toml
/path/to/Rethlas/agents/generation/tests/run_example.sh
```

Typical per-run settings are:

```bash
MODEL=<model-name>
REASONING_EFFORT=xhigh
MAX_ITERATIONS=6
```

Use models and effort levels actually supported by your account and tools.

## Conjecture queue

See the [full queue guide](problems/important-conjectures/README.md).

```bash
./tools/conjecture_queue.sh add my-conjecture "My conjecture"
# Fill in items/my-conjecture/problem.md under problems/important-conjectures/.
# Review search_contract and set ready = true in its config.toml.
./tools/conjecture_queue.sh doctor
./tools/conjecture_queue.sh run --dry-run
./tools/conjecture_queue.sh start
```

View and stop:

```bash
./tools/conjecture_queue.sh status
./queue.sh watch
./tools/conjecture_queue.sh stop
```

Each call is bounded. Project files retain long-term state, and the queue rotates fairly. `needs-human-review` pauses one problem. A complete main candidate that has passed the ten audit checks enters `solved-awaiting-human-verification`, creating a global hold for researcher review. Rethlas never starts automatically.

New items default to `search_contract = "affirmative-proof"` and `stagnation_rounds_before_blocked = 0`. Use `counterexample` for a counterexample task. Explicit `information_mode` selects offline, connected, or mixed-isolated work; when empty, `web_search` supplies the compatibility setting. Preserve the provenance and route exposure of each stage.

## Optional external Rethlas installation

After authorization, clone Rethlas outside the workspace; substitute your own fork if appropriate:

```bash
cd /path/to/research
git clone https://github.com/frenzymath/Rethlas.git
```

Its core directories are `agents/verification/` (HTTP verifier service) and `agents/generation/` (generation agent).

Verification environment:

```bash
cd /path/to/research/Rethlas/agents/verification
python3 -m venv .venv
source .venv/bin/activate
pip install -r api/requirements.txt
```

Alternatively, use `uv venv` and `uv pip install -r api/requirements.txt` in that directory.

Generation environment:

```bash
cd /path/to/research/Rethlas/agents/generation
python3 -m venv .venv
source .venv/bin/activate
pip install -r mcp/requirements.txt
```

For PDF references on Ubuntu/Debian, install `poppler-utils` after authorizing the system installation:

```bash
sudo apt-get install poppler-utils
```

## Start the verifier

For an authorized Rethlas run, use the wrapper from the workspace root:

```bash
./tools/rethlas/start_verifier_tmux.sh
curl -sf http://127.0.0.1:8091/health
tmux attach -t rethlas_verifier
```

The wrapper checks `CODEX_BIN` and the service configuration. Detach without stopping with `Ctrl-b`, then `d`. See the [Rethlas guide](RETHLAS使用教程.md) for stale-service recovery.

## Prepare and run a problem

```bash
./tools/rethlas/init_project.sh example-project example-problem
```

This creates:

```text
projects/example-project/rethlas/problems/example-problem.md
projects/example-project/rethlas/problems/example-problem.refs/
projects/example-project/rethlas/results/
projects/example-project/rethlas/runs/
```

Write the precise statement and supply references. After approval and a successful verifier health check:

```bash
MAX_ITERATIONS=6 ./tools/rethlas/run_problem_tmux.sh example-project example-problem rethlas_example
tmux attach -t rethlas_example
```

The wrapper imports results into:

```text
projects/<project>/rethlas/results/<problem>/
projects/<project>/rethlas/runs/<problem>/
```

Key artifacts:

| File or directory | Meaning |
|---|---|
| `blueprint.md` | Candidate proof, at most `proof-draft` |
| `blueprint_verified.md` | A file whose certification must be checked against the actual independent verifier report and snapshot |
| `run-info.txt` | Problem ID, Rethlas path, synchronization time |
| `logs/` | Iteration logs |
| `memory/` | Intermediate material |
| `downloads/` | Retrieved references |

A filename does not establish `agent-verified`, and Rethlas cannot grant `human-verified`. Auxiliary candidates may support explicitly conditional exploration. Complete main candidates require certification and a pause under `AGENTS.md`.

## Reruns and result browser

If external generation results already contain `blueprint_verified.md` for the same problem ID, the wrapper refuses a same-name rerun because Rethlas would immediately stop. For a changed statement, use a new name such as `<problem>_v2` and preserve the old evidence.

To browse results with the optional Zola site:

```bash
cd /path/to/Rethlas/agents/generation
./site/serve.sh
```

Open `http://localhost:3264`.

## Historical Lean support

The current workflow uses natural-language proofs and reproducible calculations. Do not introduce formalization or make it a prerequisite for research or certification. A future change requires an explicit researcher request.

For historical projects, preserve `projects/<project>/lean/`, its `lean-toolchain`, `lakefile.lean`, and source files, together with the original evidence for any `formalized` labels. There is no required global Lean project. The earlier optional setup used elan, `lake init <PackageName> math`, `lake update`, and `lake build`; those instructions do not authorize installing or starting formalization now.

## Private project handoff

Sharing a particular research project is separate from exporting the public framework. With authorization, a private handoff should include the applicable rules, setup guide, project README, progress, route/dependency records, and Rethlas statements, results, and run records. For reproducible experiments, include the relevant `code/`, `data/`, `notes/`, and `references.md`.

Keep Rethlas as a separate clone. Preserve the original rules before adapting them, especially evidence levels, complete-candidate holds, and the distinction between verifier output and human acceptance.

## Health checks

From the workspace root:

```bash
test -f AGENTS.md
test -x tools/rethlas/init_project.sh
test -x tools/rethlas/run_problem.sh
test -x tools/rethlas/run_problem_tmux.sh
codex --version
./tools/conjecture_queue.sh doctor
```

If Rethlas has been installed and an authorized verifier is running, also check its generation/verification directories and `curl -sf http://127.0.0.1:8091/health`. Passing environment checks does not certify mathematical results.

Unqualified main results in papers require the applicable `human-verified` or `formalized` evidence and researcher authorization. See `AGENTS.md` and the paper rules for the complete requirements.
