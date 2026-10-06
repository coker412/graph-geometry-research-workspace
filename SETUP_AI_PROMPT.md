# Setup task for the researcher's AI assistant

Configure and check a new mathematics research workspace. Do not start mathematical research.

## Read first

1. `AGENTS.md`
2. `README.md`
3. `TEACHER_SETUP_README.md`
4. `RETHLAS使用教程.md`
5. `problems/important-conjectures/README.md`
6. `TEACHER_QUEUE_QUICKSTART.md`

## Goals

- Configure the extracted directory as a new workspace.
- Use Codex for ordinary research, without Danus or Claude Code.
- Leave research data directories such as `projects/` empty until the researcher supplies a problem.
- Install Rethlas outside the workspace, normally at `../Rethlas`.
- Do not copy another person's `.codex`, `.env`, tokens, API keys, cookies, Git history, or research data.
- Rethlas requires explicit authorization for each run. Installing it does not authorize research.

## Procedure

Start with the local check, which does not download software:

```bash
./setup.sh --check
```

Read `SETUP_REPORT.md`. If Conda or external Rethlas is missing, explain the downloads, destination paths, and purpose. After obtaining authorization, run:

```bash
./setup.sh --bootstrap
```

If Rethlas is not needed:

```bash
./setup.sh --bootstrap --without-rethlas
```

If Conda/Miniforge or tmux itself is missing, obtain authorization to install system tools using the operating system's official instructions, then rerun bootstrap. Do not bypass system permissions or silently change shell configuration.

Check the current official OpenAI documentation before installing Codex CLI and obtain installation authorization. The researcher must sign in personally. Do not request, read, print, or migrate authentication secrets.

Finally, run:

```bash
./setup.sh --check
./tools/conjecture_queue.sh doctor
```

Report the workspace and Conda paths, Codex version and login status, tmux, `graphlab`, external Rethlas path and environment, and unresolved issues. Do not start the conjecture queue unless separately requested.
