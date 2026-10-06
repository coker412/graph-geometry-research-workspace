# Persistent Codex conjecture queue

The researcher supplies and prioritizes formal problems. Codex works through them in tmux, retaining research state on disk. The queue does not require Danus or Claude Code. Rethlas is an optional escalation path requiring explicit authorization.

## Workflow

```text
Researcher completes problem
    ↓ ready = true
Bounded Codex step: definitions, examples, approaches, or current gap
    ↓ Save project state
Next eligible problem
    ↓ Return to the remaining gap on a later pass
Complete main proof or decisive main counterexample
    ↓ Ten audit checks, global hold, queue exit
Researcher reviews and decides whether to finish, resume, or authorize escalation
```

A call is an execution step, not necessarily a completed mathematical task. Ordinary V2 and task-enabled mixed-isolated runs can preserve a task across calls, with its original objective and acceptance criteria.

```text
projects/conjecture-<slug>/
├── README.md
├── CURRENT_STATE.md
├── references.md
├── ideas.md
├── progress.md
├── verification-ledger.md
├── research-tree.md
├── proof-map.md
├── notes/
├── code/
├── rethlas/
├── input-snapshots/
├── CURRENT_INPUT.md
└── .conjecture-status
```

The original problem remains under `problems/important-conjectures/items/<slug>/`. The runner saves immutable input snapshots; agents must not change the researcher's statement.

The first actual execution creates missing project structure. `CURRENT_STATE.md` is the next round's short entry point: target 6 KiB, warning above 8 KiB, V2 limit 12 KiB/300 lines, legacy limit 32 KiB/300 lines. Follow its IDs and direct pointers instead of rereading whole ledgers. The researcher submits structured results; the V2 runner appends progress and updates state. Register substantive findings, important failures, or evidence changes in the ledger. Keep round logs out of README files.

For older projects:

```bash
./queue.sh state-init
./queue.sh state-audit
```

Initialization creates only missing files. A legacy project starts with `migration-status: pending`; establish a conservative summary from current state, the latest complete round, and exact evidence. Unread history remains unknown.

## V2 runtime

See the [runtime guide](../../shared/runtime-v2-guide.md) for phase protocols, evidence slices, ROUND_RESULT, writer ownership, compatibility, and recovery.

```bash
./queue.sh packet --slug <slug>
./queue.sh usage
./queue.sh usage --slug <slug> --json
```

`packet` previews without creating a project or calling a model. `status` also shows recorded usage. Missing historical telemetry remains unknown; token counts are not converted into subscription prices.

## Add and run a problem

Run all commands from the workspace root.

```bash
./tools/conjecture_queue.sh add hadwiger-conjecture "Hadwiger conjecture"
```

Complete `items/hadwiger-conjecture/problem.md` under this directory. Put references under that item's `references/`. Review its `config.toml` and set `ready = true`.

### Before startup

An explicit request for continuous/background research uses this queue. Do not substitute one manual round or a chat Goal. An explicit request for mix mode means `mixed-isolated` in the item's configuration, with two isolated branches and integration.

Use `project_path` to adopt an existing project. Check `ready`, `enabled`, `max_attempts`, and the state schema. `doctor --slug <slug>` checks the selected problem and required tools; unrelated format faults do not block a dedicated startup, but complete-candidate global holds still apply.

After explicit researcher acceptance, reconcile machine status through `set-status` within the accepted scope and record its evidence. Use `paused` if continued research was not requested. Do not retain a stale acceptance hold or remove one based on self-review.

```bash
./tools/conjecture_queue.sh doctor
./tools/conjecture_queue.sh list
./tools/conjecture_queue.sh run --dry-run
```

Dry runs show the next problem, project path, and Codex command. They neither invoke the model nor change attempt counts, budget state, or interrupted-execution recovery state.

### Background research

Fair rotation:

```bash
./tools/conjecture_queue.sh start
```

Dedicated concurrent problems:

```bash
./tools/conjecture_queue.sh start --slug problem-a
./tools/conjecture_queue.sh start --slug problem-b
```

Each dedicated runner has its own session and project. The fair queue and dedicated runners must not run simultaneously. Two slugs resolving to the same project cannot run concurrently either.

Before reporting successful startup, verify the tmux session and runner lock. A zero tmux exit code is insufficient. In chat, also inspect actual attempt logs and mixed branch processes; distinguish startup, active research, and a completed round. Do not concurrently edit shared project files from chat or another task while a runner owns them.

```bash
./queue.sh watch
./tools/conjecture_queue.sh status
./tools/conjecture_queue.sh stop
./tools/conjecture_queue.sh watch --slug problem-a
./tools/conjecture_queue.sh stop --slug problem-a
./tools/conjecture_queue.sh stop --all
```

Detach from tmux with `Ctrl-b`, then `d`. Safe stop waits for the current round rather than killing Codex while it writes files.

## Scheduling and progress

```bash
./queue.sh progress
./queue.sh progress --slug problem-a
```

Each round saves a baseline and seals its plan and result. Ordinary rounds do not automatically add a reviewer call. Without independent REVIEW, progress remains self-reported/unknown, not verified progress or mathematical stagnation. Assessments distinguish reduced gaps, exclusions, tools, computational leads, reformulation, and repetition. Missing material is not evidence of wasted mathematical work. See the [progress guide](../../shared/research-progress-guide.md).

- Higher `priority` runs first.
- Each eligible problem receives at most one execution per scheduling pass.
- The runner rescans between passes, so problems and priorities can be updated.
- `max_attempts = 0` removes the cumulative execution limit. A trial may use `3` or `5`.
- `max_wall_hours` bounds one background run; `0` removes that bound. The public configuration defaults to 24 hours.
- The default call timeout is 90 minutes. Three consecutive CLI/timeout failures produce `runtime-error`.
- Dedicated slugs have separate sessions, locks, and stop files. The project lock rechecks status and remaining allowance before execution.

## Agents and evidence

Use one root researcher by default. Multi-agent work requires an explicit request. Agent authorization and information mode are separate. Explicit mixed-isolated configuration normally produces three calls: two branches and integration.

Initial independent explorers receive blind packets without favored approaches, failures, or persuasive discovery history. Later directed continuations may receive scoped failure/dependency evidence, with exposure recorded; they must not claim independent rediscovery. Auditor packets exclude author confidence and other reviewers' conclusions. Chat agents share a workspace, so allowed-read lists and separate output paths support procedural blindness. Mixed-isolated uses actual filesystem isolation.

Current research does not use formalization. Explicit conditional/GAP exploration may continue on unverified lemmas. Routine steps receive local checks. Important auxiliary candidates and high-risk dependencies require stronger self-checks and applicable certification; freeze their use as certified premises, retain conditional dependencies, and propagate errors. Missing independent review alone does not pause a problem. Complete main candidates require whole-problem certification and a pause.

## Information modes

- `offline`: no public internet or connectors.
- `connected`: external checks with source attribution.

Connected work reuses checked known results and establishes the covered scope before a long investment. Re-derivation needs a stated verification purpose or concrete extension; rediscovery is not new progress.

The manual `staged` workflow freezes a bounded independent exploration before an authorized connected step checks coverage and tool transfer. Prefer per-item mode overrides so other problems are unaffected. Change modes only at a safe boundary, retaining pre-connection snapshots and recording literature influence. `staged` is a workflow, not a configuration enum.

Offline work does not establish novelty. At important findings, strategy reviews, or batch boundaries, reuse existing comparisons and follow the [offline-to-literature handoff](../../agents/protocols/literature-check.md#reconcile-offline-exploration-with-literature). Pass only substantive uncovered questions to the next authorized connected step and test whether the tool applies to the original problem. Without network authorization, preserve pending checks and overlap risks rather than silently switching mode.

### Mixed-isolated

The offline branch works in the real project without web search. The connected branch searches from a frozen starting copy in a system temporary directory. Once both finish, the runner imports the connected report to `notes/mixed-isolated/attempt-<n>/connected/RESULT.md` and starts an integration audit without fresh browsing. Preserve `internal-offline`, `web-source`, and `mixed` provenance.

Linux `bubblewrap` hides the actual workspace and parallel branch directories. If `bwrap` is unavailable, the runner refuses this mode; it does not fall back to prompt-only separation. Branches have separate temporary Codex homes with minimal authentication material, not shared sessions or state databases.

One mixed execution normally uses three calls and more quota than an ordinary round. It must be explicitly selected. A problem required to remain offline must keep every branch offline.

Problem-level concurrency and branch concurrency are separate. Two dedicated mixed problems each run their own branches and integration, with separate project ownership and no early cross-branch reading.

## State machine

| State | Automatic continuation | Meaning |
|---|---|---|
| `queued` | Yes | Awaiting first execution |
| `pushing` | Yes | Concrete next research action |
| `paused` | No | Researcher pause |
| `needs-human-review` | No | Incomplete main-candidate audit, a required researcher decision, or integrity recovery |
| `solved-awaiting-human-verification` | No | Complete main candidate; global hold |
| `needs-human-input` | No | Substantive ambiguity or missing decision |
| `needs-escalation-approval` | No | Further work depends on an unauthorized external call |
| `blocked` | No | Structural route exhaustion with the required renewed exploration |
| `attempt-limit` | No | Cumulative execution limit reached |
| `runtime-error` | No | Consecutive runtime failures reached the limit |
| `completed` | No | Researcher has instructed that queue research is finished |

```bash
./tools/conjecture_queue.sh set-status hadwiger-conjecture paused
./tools/conjecture_queue.sh set-status hadwiger-conjecture pushing
./tools/conjecture_queue.sh set-status hadwiger-conjecture completed
```

`needs-human-review` pauses only that problem. Read its progress, candidate, and proof map before a researcher-directed status change. Important auxiliary results and absent independent review do not alone justify that state.

`solved-awaiting-human-verification` means the main claim has a complete candidate proof or decisive counterexample with all ten checks completed. It triggers a global hold. One agent's self-check still supports at most `proof-draft`; resuming or completing the queue item does not itself create `human-verified` evidence.

`set-status` accepts only `queued`, `pushing`, `paused`, `blocked`, and `completed`. Research-return states such as `needs-human-review` and `solved-awaiting-human-verification` go through V2 ROUND_RESULT validation, or the root writer in manual/compatibility rounds. Check subcommand `--help` before suggesting a command; not every table entry is a CLI argument.

## Configuration

Global `runner.toml`:

- `model`: an explicit available model, or empty to use the CLI default.
- `reasoning_effort`, `[phase_effort]`, and optional `[phase_model]`: actual overrides can differ from built-in defaults. The synchronized research effort is medium; first decisions and strategy reviews use high. Triage/audit/stuck-escalation use high and critical-audit uses xhigh. Check your account's supported models.
- `phase`: the current phase, optionally overridden per item.
- `research_task_version = 1`: persistent tasks for new ordinary V2 and mixed-isolated runs. V2 also accepts structured route changes. Mixed integration supplies a task in RESULT for runner sealing and saving, without extra calls. Old START=0 rounds retain their protocol.
- `runtime_version = 2`: packets and structured closing for ordinary rounds; mixed-isolated retains compatibility closing.
- `[context_budget]`: initial packet and evidence-slice limits; see the runtime guide.
- `attempt_timeout_minutes`: per-call timeout; `0` disables it.
- `max_wall_hours`: total time for one start; `0` means continuous.
- `idle_seconds`: rescan delay with no eligible work.
- `information_mode`: `offline`, `connected`, or `mixed-isolated`; empty uses `web_search` for compatibility.
- `web_search`: false removes search and requires agents to ignore external literature in references/project files; true permits connected checks. Blind exploration is not a mandatory prerequisite for connected research.
- `max_consecutive_runtime_failures`: failure threshold.
- `codex_path`: absolute executable path, needed only if Codex is absent from `PATH`.

Per-item `items/<slug>/config.toml`:

- `ready`: the researcher has approved the problem for execution.
- `enabled`: scheduling eligibility, separate from research status.
- `search_contract`: `affirmative-proof`, `counterexample`, or `either`. It controls the search objective, not evidence.
- `stagnation_rounds_before_blocked`: required consecutive renewed-exploration rounds without a new mechanism after all current families fail. `0` forbids automatic stagnation blocking.
- `information_mode`: optional override; empty inherits the global setting.
- `project_path`: existing workspace-relative project under `projects/`; empty uses `projects/conjecture-<slug>/`. Only missing structure is initialized.
- `priority`: scheduling order.
- `max_attempts`: cumulative executions, not completed mathematical tasks. A mixed execution may contain three calls.

## Proof and escalation boundaries

The queue inherits `AGENTS.md`:

- Attempt proofs or counterexamples even for open problems; a survey alone does not satisfy proof work.
- An affirmative search assumption is not evidence. A decisive counterexample still requires certification and reporting.
- Group routes by mechanism, not renamed approaches. Authorized multi-agent work uses blind starts, dynamic reassignment, and adversarial audits.
- Computation initially supports only `experimental` evidence.
- Auxiliary candidates receive stronger checks without automatically pausing the whole problem. Keep explicit conditions and report important findings and outstanding checks.
- Only a complete main candidate can enter `solved-awaiting-human-verification` after the required audit.
- Preparing a Rethlas packet does not pause other authorized routes. Use `needs-escalation-approval` only for a real dependency on an unauthorized external run. Once approved, follow the escalation protocol without requesting the same permission again.
- The queue does not invoke web Pro or grant `human-verified` status.

## Logs and recovery

```text
agents/important-conjectures/history.jsonl
agents/important-conjectures/logs/<slug>/
```

Each call has JSONL events and a final response. `.queue-runtime.json` retains cumulative attempts, recent errors, and log paths.

After a restart, completed rounds resume from saved state. An `active_execution` marker or unfinished transaction requires inspection and recovery first; do not silently rerun or reset counts. See [execution counts and abnormal exits](../../shared/runtime-v2-guide.md#execution-counts-and-abnormal-exits).

```bash
./queue.sh hygiene report
./queue.sh hygiene latex
./queue.sh hygiene logs --older-than-days 30 --keep-latest-per-slug 5
```

Cleanup defaults to a dry run. Only explicit `--apply` removes reproducible LaTeX intermediates or losslessly compresses old logs. Environments are reported, never deleted automatically.

## Limitations

- Fair rotation is serial. Problem-level concurrency requires explicit dedicated starts; the system does not choose a concurrency count.
- Additional agents require a researcher request. V2 shared ledgers belong to the transaction writer; compatibility rounds follow root ownership.
- Self-review is not independent certification. The current workflow does not use Lean. Complete main results await stepwise researcher acceptance; technical holds follow the specific recovery issue.
- `stop` takes effect at a round boundary. For an immediate stop, the operator must interrupt the tmux process and inspect possible partial writes.
