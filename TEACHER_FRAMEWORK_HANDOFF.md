# Mathematics research framework handoff

This package contains the reusable framework, public guides, writing skills, and a synthetic example. It excludes the author's private research, manuscripts, PDFs, runtime logs, installed environments, Git history, and authentication files. Codex handles ordinary research; Rethlas is optional and requires authorization for each run.

The package targets a Codex environment. Platform-specific Danus, Claude Code, and Copilot instructions are excluded; shared research rules live in `AGENTS.md`.

## Contents

- `AGENTS.md`: research discipline, evidence, certification, and queue rules.
- `TEACHER_SETUP_README.md`: environment setup and optional external Rethlas integration.
- `RETHLAS使用教程.md`: Rethlas preparation, execution, synchronization, and review. The existing filename is retained for compatibility.
- `SETUP_AI_PROMPT.md`: setup instructions for an assistant.
- `TEACHER_QUEUE_QUICKSTART.md`: everyday queue commands.
- `setup.sh`: local checks and optional bootstrap.
- `queue.sh`: the root queue entry point.
- `problems/important-conjectures/`: formal problem intake and queue configuration.
- `templates/`: problem, project-state, research-graph, and Rethlas templates.
- `tools/conjecture_queue.*`: the persistent Codex queue.
- `tools/research_runtime.py`, `tools/research_tasks.py`, and `tools/research_progress.py`: packets, persistent mathematical tasks, and progress assessment.
- `tools/project_state.py`: initialize and audit short state for projects outside the queue.
- `tools/workspace_hygiene.py`: report storage use and manuscript layout; cleanup requires explicit `--apply`.
- `tools/rethlas/`: optional Rethlas wrappers.
- `tools/configure_teacher_workspace.sh`: replace path placeholders with local paths.
- `tools/export_teacher_framework.sh`: produce another allowlisted framework package.
- `tools/verify_teacher_framework.sh` and `tools/update_manifest.py`: structure, public boundaries, checksums, and common secret-pattern checks.
- The allowlisted skills under `.agents/skills/`, public runtime guides under `shared/`, and synthetic `examples/tree-edge-count/` project.
- Placeholder directories for research, archives, references, and environments.

Private data directories, `.git/`, `.codex/`, `.claude/`, `.vscode/`, non-allowlisted hidden resources, installed environments, caches, logs, model sessions, credentials, datasets, experiment outputs, and private manuscript sources are excluded. The generic study-edition LaTeX template is an intentionally included skill resource.

## Verify and extract

Keep the archive and its `.sha256` file together:

```bash
# Linux
sha256sum -c graph-geometry-framework-YYYYMMDD-HHMMSS.tar.gz.sha256

# macOS
shasum -a 256 -c graph-geometry-framework-YYYYMMDD-HHMMSS.tar.gz.sha256

tar -xzf graph-geometry-framework-YYYYMMDD-HHMMSS.tar.gz
cd graph-geometry-framework-YYYYMMDD-HHMMSS
./setup.sh --check
```

Replace the timestamp with the actual archive name. Alternatively, ask your assistant to follow `SETUP_AI_PROMPT.md`.

## Configure local paths

`setup.sh --check` first verifies the distribution, then configures path placeholders and creates `SETUP_REPORT.md`. To specify paths manually:

```bash
CONDA_ROOT=/path/to/miniforge3 RETHLAS_ROOT=/path/to/Rethlas ./tools/configure_teacher_workspace.sh
./tools/verify_teacher_framework.sh
```

Omit `RETHLAS_ROOT` if you do not need it. Path configuration does not install software, sign in, or write secrets.

After authorizing downloads and environment creation:

```bash
./setup.sh --bootstrap
```

For the ordinary Codex queue without Rethlas:

```bash
./setup.sh --bootstrap --without-rethlas
```

## Local tools

Prepare Bash, Git, tmux, Python 3.11 in a Conda/Miniforge environment named `graphlab`, and Codex CLI authenticated with your own account. Rethlas and its environments are optional.

Consult the [official Codex CLI documentation](https://developers.openai.com/codex/cli/) for current installation and login instructions. Never copy another user's login directory.

```bash
conda create -n graphlab python=3.11 -y
conda activate graphlab
codex --version
tmux -V
./tools/conjecture_queue.sh doctor
./tools/conjecture_queue.sh state-audit
./tools/workspace_hygiene.py report
```

## Your own Git repository

The archive contains no Git history. After inspecting its contents, you may initialize a private repository:

```bash
git init
git add .
git status --short
git commit -m "Initialize mathematics research framework"
```

Committing is your decision. Exclude authentication files, `.env`, and any private data that should not enter the repository.

## First conjecture

```bash
./tools/conjecture_queue.sh add first-conjecture "First conjecture"
```

Fill in `problems/important-conjectures/items/first-conjecture/problem.md`, set `ready = true` in its `config.toml`, then run:

```bash
./tools/conjecture_queue.sh run --dry-run
./tools/conjecture_queue.sh start
```

The first actual execution creates `projects/conjecture-first-conjecture/` and maintains its state, routes, dependencies, and evidence under `AGENTS.md`.

## Rethlas boundary

Rethlas is not included and is not required for the queue. Install and call it only for a precise gap with the required authorization. Generated proofs begin as `proof-draft`; independent verification may support `agent-verified`, never automatic `human-verified` status.

```text
parent-directory/
├── graph-geometry-framework/
└── Rethlas/
```

Rethlas must remain outside the workspace.
