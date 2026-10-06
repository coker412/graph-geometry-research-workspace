# Geometry and mathematics research workspace

Start every reply with **Hi, mathematician!**
Workspace: `__WORKSPACE_ROOT__`. All geometry and related mathematics are in scope, including Riemannian geometry, geometric analysis, discrete/graph geometry and project-specific fields. Keep existing paths; the directory name neither limits topics nor makes graph reductions the default.

## Boundaries

- Actually attempt proofs or counterexamples, even for open problems; a survey or public status is not progress.
- Current research uses natural-language proofs and reproducible calculations, not Lean. Do not introduce formalization tasks or require formalization to continue research or review. Preserve historical formalized evidence labels; a future change of workflow requires an explicit researcher request.
- Separate exploration from certification. Important auxiliary candidates trigger stronger self-checks, counterexample tests and applicable certification, not automatic whole-problem pauses. Freeze their use as certified premises; explicit conditional/GAP exploration and independent routes may continue. Preserve dependency labels, propagate errors, and report important findings without waiting for routine human approval. Complete main-problem candidates and decisive main counterexamples require whole-problem certification and a pause; evidence upgrades still require the corresponding verification.
- Every substantive claim needs a level and direct evidence; definitions are in `agents/core/research-core.md`. Computation is not proof; self-review is not independent verification. Model strength and state maintenance cannot raise levels.
- agent-verified requires an independent verifier/Agent; human-verified requires the researcher's stepwise acceptance; formalized requires formal-system checks. Unqualified main results in paper abstracts/conclusions require one of the latter two levels AND researcher authorization.
- Rethlas and web Pro require explicit approval for each use. Prepare packets, but do not launch/submit them without approval. Check existing authorization before external writes, publication, added costs or permission expansion; ask if absent.
- No secrets, .env edits, overwriting existing changes or destructive cleanup. Check Git diffs before/after edits; without Git, save snapshots and inspect differences. No commits/pushes unless requested.

## Read on demand

Read only applicable modules before that work; list their paths in the first substantive update. Do not reread content included in RESEARCH_PACKET. Paths below are workspace-relative:

- Mathematics: `agents/core/research-core.md`, then the applicable phase protocol.
- New geometric objects/conventions: relevant sections of `agents/protocols/geometry-scope.md`; store conventions in the problem/project, not a new checklist each round.
- Personal workflow/model planning: `agents/instructions/personal-research.md`; omit company surveys from proof rounds.
- Exploration/routes: `agents/protocols/explore.md`.
- Persistent, identified bottlenecks: `agents/protocols/cross-field.md`; supports proofs, constructions and counterexamples, without changing the search contract.
- Proof candidates/audits/upgrades: `agents/protocols/proof-audit.md`; decisive counterexamples also `agents/protocols/counterexample-audit.md`.
- Literature: `agents/protocols/literature-check.md`. Experiments: `agents/protocols/computation.md`.
- Queue rounds: `agents/core/queue-core.md`; scheduler operations also `problems/important-conjectures/README.md`.
- Rethlas/web escalation: `agents/protocols/escalation.md`.
- Papers, LaTeX, public research writing: `agents/instructions/paper-writing.md`; prefer humanizer for polishing without mathematical changes.
- Public LaTeX manuscripts should use `\date{}` and display no manuscript date unless the researcher explicitly requests one.
- Workspace-wide paper-location gate: from the first write, every active or candidate manuscript source, bibliography, included manuscript file, and manuscript build output must live under the owning project's `paper/` directory. Never stage a manuscript at the project root for later cleanup. Keep teacher-supplied editable manuscript sources or frozen manuscript baselines under `paper/teacher-sources/`, and internal manuscript variants under a clearly named subdirectory of `paper/`. Learning editions, source literature, research notes, reports, talks, and posters may remain in their designated non-paper directories only when they are not the active/candidate manuscript. Before and after paper-facing work, run `python tools/workspace_hygiene.py paper-layout`; existing reported legacy exceptions are frozen and do not authorize new exceptions.
- Multi-agent work only when explicitly requested: `agents/protocols/multi-agent.md`. Tool availability is not authorization.

Legacy indexes: `agents/instructions/research-workflow.md` and `queue-and-escalation.md`. More local AGENTS.md files apply.

## Memory and files

When authorized, at most 5 child agents, subject to lower session limits. The root allocates all slots; children cannot spawn descendants.

CURRENT_STATE.md is the sole short recovery entry: scope, levels, usable result IDs, active gaps/routes, next action and evidence pointers, never proof bodies. Target 6 KiB; warn above 8 KiB. V2 new writes: at most 12 KiB/300 lines; legacy: 32 KiB/300 lines. Never silently truncate evidence to fit.

Read state first, then evidence by stable ID and `file#Lstart-Lend` or SHA256-bound slices. Do not reread growing ledgers for general context. Summaries cannot replace ledgers/direct evidence. Initial migration checks only current state, the latest complete round and cited evidence; unread history remains unknown.

Under `projects/<name>/`: CURRENT_STATE.md (index), progress.md (append-only history), verification-ledger.md (evidence), proof-map.md (dependencies), ideas.md/research-tree.md (routes), README.md (stable description). Proofs: notes/; experiments: code/; formalization: lean/; Rethlas: rethlas/; paper sources only: paper/. Open problems: problems/; general definitions/examples: library/; cross-project material: shared/.

Update route/dependency files only for structural changes. No round logs in README. Queue write ownership and V2/manual closing duties are defined in `agents/core/queue-core.md`.

## Researcher communication

Use clear, natural English for replies and research summaries unless the researcher requests another language, normally 1–3 paragraphs. First explain the mathematical problem and extent solved, then this round's proof/construction/elimination, then the remaining gap and next action. Say when there is no new result.

Preserve objects, assumptions, dimension, quantifiers and scope. Distinguish full solutions, special cases, auxiliary results and numerical observations; separate literature results from this round's work. Explain evidence levels plainly while retaining formal levels and direct pointers. Explain a problem number, result ID or technical term on first use; internal IDs/jargon cannot replace its mathematical meaning.

Topic recommendations must explain prospects for solving the original problem and the main obstacle. Easy computations, many past rounds or more partial results alone do not justify priority.

Apply the same language preference to new/updated CURRENT_STATE.md; keep it an index without proofs, lost evidence or changed conclusions.

Queued CURRENT_STATE.md files must also pass `tools/project_state.py`: preserve schema/migration fields and use canonical or explicitly supported headings (canonical headings: Control, Problem and scope, Current mathematical status, Active proof frontier, Next bounded round, Evidence pointers; supported Chinese equivalents remain valid). Validate the actual saved file before reporting successful round closure; The selected language does not waive machine-schema requirements.

## Execution and delivery

- Explicit continuous/background research requests use this workspace's existing tmux queue: read `agents/core/queue-core.md` and `problems/important-conjectures/README.md`, register/adopt the target project, and run `./queue.sh start --slug <slug>`. Do not substitute a chat Goal or one manual round. Here an explicit “mix mode” request selects the documented `mixed-isolated` workflow (two isolated lanes then integration), not merely literature plus derivation in one chat. Verify item configuration, holds, focused health checks, tmux session, runner lock and actual attempt logs before reporting background research as running. Keep unrelated stopped projects stopped and avoid concurrent chat writes to a runner-owned project.
- When recording explicit researcher acceptance for a queued candidate, also reconcile its machine status through `set-status` within the accepted scope and record the evidence; do not leave an already accepted candidate imposing a stale global hold. Use `paused` when further queue research is not requested; `completed` requires the appropriate completion instruction. Never clear a hold from self-review alone. If no acceptance exists, report the exact hold rather than bypassing it.

Python: Conda graphlab. LaTeX: run `latexmk -xelatex main.tex` in the relevant paper/ and complete the paper protocol checks. Prefer tmux for long jobs; give session and viewing/exiting instructions.

For multistep work state goal, assumptions, artifacts and acceptance. Deliver paths, checks, gaps, evidence level and next action. Save concrete material before asking about substantial ambiguity, requested but unverified novelty, structural blockage after the search commitment, human acceptance of candidates, paper main results or project-goal changes.
