# Conjecture queue: quick start

Use these commands from the extracted workspace root on macOS or Linux.

## First-time setup

You can give the assistant this instruction:

> Read AGENTS.md, SETUP_AI_PROMPT.md, and TEACHER_QUEUE_QUICKSTART.md. Configure the research environment only. Run ./setup.sh --check and report the results. Obtain my authorization before any network installation. Do not start research.

Sign in to Codex with your own account. Then run:

```bash
./queue.sh check
```

When upgrading a workspace with existing projects:

```bash
./queue.sh state-init
./queue.sh state-audit
```

These commands initialize and check short recovery state without overwriting proofs, progress, or evidence ledgers.

## Add a conjecture

An assistant instruction:

> Add the following conjecture to the queue. Preserve its wording and mathematical meaning. Create the entry for my review without starting the queue. Problem: ...

Or run:

```bash
./queue.sh add hadwiger "Hadwiger conjecture"
```

Fill in `problems/important-conjectures/items/hadwiger/problem.md`, then set `ready = true` in the adjacent `config.toml`.

New items default to `search_contract = "affirmative-proof"`. This treats a complete affirmative proof as the search objective; it does not establish its existence or raise evidence levels. The default `stagnation_rounds_before_blocked = 0` prevents automatic termination for stagnation. Choose `counterexample` when that is the intended target.

For independent exploration before literature checking, use `information_mode = "offline"`, or `web_search = false` when the explicit information mode is empty. Save the route snapshot before switching to connected checking. Explicit information modes take precedence over the compatibility switch.

## Start a long run

An assistant instruction:

> Run ./queue.sh check. If it passes, start the background conjecture queue with ./queue.sh start. Do not start Rethlas. Report whether startup succeeded and how to view and stop it.

Manual commands:

```bash
./queue.sh check
./queue.sh start
```

`start` uses tmux, so the session can continue after you close the terminal or assistant conversation. Install tmux with Homebrew on macOS or your system package manager on Linux.

## Daily commands

```bash
./queue.sh status   # Inspect status.
./queue.sh watch    # View output; detach with Ctrl-b, then d.
./queue.sh stop     # Stop safely after the current research round.
```

You can also ask the assistant to summarize progress and required decisions without changing state, or to stop the queue safely without killing a Codex process while it writes files.

## Without tmux

```bash
./queue.sh once
```

This runs a single round. `./queue.sh run` polls in the foreground but needs the terminal and SSH connection to remain open. Use tmux for overnight or multi-day work.

Tmux cannot run computation while the computer is asleep or off. Restart with `./queue.sh start` to resume from disk, resolving any reported interrupted-execution recovery first.

## States requiring researcher attention

- `needs-human-review`: this problem is paused. Read its `progress.md` and `verification-ledger.md`.
- `needs-human-input`: the formal problem has a substantive ambiguity.
- `needs-escalation-approval`: further work depends on an external call that has not been authorized.
- `solved-awaiting-human-verification`: a complete main proof or decisive counterexample has triggered a global hold pending rigorous researcher review.

Ordinary polling never starts Rethlas automatically.

## Disk usage

```bash
./queue.sh hygiene report
```

This only reports usage. Cleanup commands for LaTeX intermediates and old queue logs are also dry runs unless explicitly authorized and given `--apply`. Project environments are not deleted automatically.
