# Rethlas proof-agent guide

This guide introduces the workspace wrappers for Rethlas. Work from your research workspace; keep Rethlas in a separate directory such as `../Rethlas`. Each run requires explicit researcher authorization under `AGENTS.md`.

## Components

The generation agent reads a Markdown problem, searches references, tests examples and counterexamples, decomposes the task, and writes a candidate proof. The verification agent checks a complete argument step by step and returns `correct` or `wrong` with errors, gaps, and repair suggestions.

Rethlas writes `blueprint_verified.md` after its verifier reports success. The filename alone is not certification: inspect the report and bind it to the exact formal statement and proof snapshot. Generated drafts are at most `proof-draft`; a valid independent review may support `agent-verified`, never automatic human acceptance.

## Files

```text
projects/<project>/rethlas/
├── problems/
│   ├── <problem>.md
│   └── <problem>.refs/
├── results/
│   └── <problem>/
│       ├── blueprint.md
│       └── blueprint_verified.md
└── runs/
    └── <problem>/
        ├── memory/
        ├── logs/
        ├── downloads/
        └── run-info.txt
```

`problems/` holds authoritative input; `results/` holds readable drafts; `runs/` retains detailed execution evidence. Wrappers copy input to Rethlas and bring artifacts back at exit. Do not maintain the only copy of ordinary research material in the external repository.

## Before first use

```bash
codex --version
codex login
```

Use the installed version as the source of truth. Sign in personally. Check `graphlab`, the two Rethlas Python environments, optional Zola, and `pdftotext` for PDF sources. Follow `TEACHER_SETUP_README.md` and the external Rethlas README on a new machine; tools installed on the original author's machine are not included in the package.

## Prepare a problem

From the workspace root:

```bash
./tools/rethlas/init_project.sh example-project example-problem
```

Edit `projects/example-project/rethlas/problems/example-problem.md`. Include the complete statement, all symbols and nonstandard definitions, object class, every assumption, and the precise conclusion to prove or refute. For graph problems, specify finiteness, simplicity, connectedness, orientation, and weights as applicable. A context-free formula is insufficient.

Put optional references in `example-problem.refs/` alongside the statement. Supported forms are `.md`, `.tex`, `.txt`, and `.pdf`. Prefer text-based material. `pdftotext` may misread complex formulas, columns, or scans; inspect the extraction. Private notes may be supplied for an authorized run, but never include keys.

## Start the verifier

The workspace wrapper resolves an actual executable absolute Codex path and checks both service health and `CODEX_BIN`:

```bash
./tools/rethlas/start_verifier_tmux.sh
```

If an old service responds to health checks but has an invalid Codex executable, first confirm no generation is submitting verification, then run:

```bash
RESTART_STALE=1 ./tools/rethlas/start_verifier_tmux.sh
```

For manual foreground startup:

```bash
cd /path/to/Rethlas/agents/verification
source .venv/bin/activate
CODEX_BIN="$(command -v codex)"   uvicorn api.server:app --host 127.0.0.1 --port 8091
```

The resolved executable must be an absolute path. Do not rely on a stale PATH inherited before an editor-extension update. From another terminal:

```bash
curl http://127.0.0.1:8091/health
```

Expected response:

```json
{"status":"ok"}
```

Use Ctrl+C to stop a foreground service. A health response checks the HTTP service, not necessarily its ability to launch a verifier subprocess.

## Run an authorized problem

From another terminal at the workspace root:

```bash
MAX_ITERATIONS=10 ./tools/rethlas/run_problem.sh example-project example-problem
```

The first argument is the project directory under `projects/`; the second is the problem filename without `.md`. `MAX_ITERATIONS=10` allows up to ten continuations of the same Codex session. Runs consume quota and have no fixed mathematical completion time. The wrapper synchronizes available artifacts at exit even without a successful proof.

For long jobs:

```bash
MAX_ITERATIONS=6 ./tools/rethlas/run_problem_tmux.sh example-project example-problem rethlas_example
tmux attach -t rethlas_example
tmux attach -t rethlas_verifier
```

Detach with Ctrl-b, then d. Report the session names instead of repeatedly polling from chat.

## Inspect results

```bash
ls projects/example-project/rethlas/results/example-problem
```

Inspect `blueprint.md`, any `blueprint_verified.md`, and the matching report. Check hidden assumptions, consistent definitions, applicability of external theorems, circularity, and possible counterexamples. Use the full workspace proof-audit protocol.

Detailed records live under:

```text
projects/example-project/rethlas/runs/example-problem/memory/verification_reports.jsonl
projects/example-project/rethlas/runs/example-problem/logs/
projects/example-project/rethlas/runs/example-problem/memory/failed_paths.jsonl
```

They retain verdicts/repair suggestions, full iteration output, and failed approaches with specific obstacles.

## Common operations

To authorize a longer rerun:

```bash
MAX_ITERATIONS=20 ./tools/rethlas/run_problem.sh example-project example-problem
```

The wrapper creates a new Codex session while retaining that problem's memory and drafts. To select another supported model:

```bash
MODEL=<available-model> REASONING_EFFORT=xhigh   ./tools/rethlas/run_problem.sh example-project example-problem
```

Consult current wrapper defaults and account support before changing settings; do not globally increase effort without an evaluation.

For an unfinished problem, edit its formal input before an authorized rerun. If `blueprint_verified.md` already exists or the mathematical meaning changes substantially, use a new name such as `example-problem_v2` so old proofs and memory cannot be mistaken for evidence about the new statement.

Ctrl+C interrupts a foreground run; the exit hook attempts to synchronize existing artifacts and logs.

## Troubleshooting

### Verification service not reachable

Start the verifier, check port 8091, and query `/health`.

### Problem file not found

Check spelling or initialize the template:

```bash
./tools/rethlas/init_project.sh <project> <problem>
```

### Codex command not found

Follow the current official installation instructions. The framework's npm installation command is `npm install -g @openai/codex`; then sign in with `codex login`.

### Health works but verification returns HTTP 500

A traceback containing `PermissionError: [Errno 13] Permission denied: 'codex'` indicates that the service cannot execute Codex through its inherited path. After checking that no verification is active, use the stale-service restart command above to fix the absolute executable path.

### Iteration limit reached without a verified blueprint

This need not be a software fault. There may be a proof gap, open problem, missing definition, refuted route, or need for additional references/researcher judgment. Read reports and failed paths before choosing a revision, more context, another authorized run, or a different direction.

### PDF extraction failed

```bash
pdftotext -v
```

Scanned PDFs need OCR. The wrapper's text extraction does not provide automatic OCR.

## Direct Rethlas use

The wrappers cover ordinary work. For authorized debugging in the external repository:

```bash
cd /path/to/Rethlas/agents/generation
PROBLEM_FILE=data/example.md MAX_ITERATIONS=10 ./tests/run_example.sh
```

Generation artifacts live in its `results/`, `memory/`, and `logs/`; verification artifacts live in the verification agent's `results/` and `memory/`. Prefer wrappers for research so formal input and final evidence return to the workspace.

## Research workflow

Write the problem, add scoped references, obtain approval, start the verifier, run generation, and inspect drafts, reports, and failed routes. Auxiliary candidates require stronger checks and explicit conditional dependencies. A complete main candidate or decisive counterexample requires whole-problem certification and a pause for researcher review. Only accepted results may be incorporated at their verified level into project notes and authorized manuscripts. Rethlas assists search and checking; it does not guarantee theorem correctness.
