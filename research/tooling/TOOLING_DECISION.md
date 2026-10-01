# TOOLING_DECISION — graphify / Spec-Kit / paper-clip (Owner-ordered pass, 2026-10-01)

> Part 0.11 default is NOT_APPLICABLE; this record exists because the Owner
> explicitly ordered an adoption attempt for each tool in this pass. Per
> template: purpose, alternatives, decision, risk, reversibility.

## graphify — ADOPTED (structural/AST mode, zero-LLM)

- **Purpose:** persistent code knowledge graph (`graphify-out/`) so future
  agent sessions answer architecture questions (`graphify query`) and orient
  from `GRAPH_REPORT.md` without re-reading the tree — directly serving the
  Owner's "economic token usage for AI agents" goal.
- **Run record:** corpus 256 files (144 code, 112 docs, ~270K words) → AST
  graph **1,569 nodes / 4,139 edges / 80 communities**; **0 LLM tokens**
  (`graphify-out/cost.json`, run dated 2026-10-01, note "code-only fast path").
  God nodes: `State` (deg 100), `canonical_dumps()` (84), `GenerationState`
  (81), `_empty_state()` (80), `run_pass()` (59) — consistent with CAND-B.
- **Docs-layer caveat (honest):** semantic extraction for the 112 markdown
  documents was **not** run (no `GEMINI_API_KEY` on this host; the host agent
  runs without subagent dispatch, and inline extraction of 270K words of prose
  would be exactly the token cost this pass is meant to avoid). The graph is
  therefore **code-only**. Re-run with a Gemini key later to enrich it.
- **Alternatives considered:** none installed; manual architecture notes
  (already exist and go stale).
- **Risk:** graph drifts from code (mitigated: `--update` + manifest + cache
  committed); large artifacts bloat the repo (mitigated: only `GRAPH_REPORT.md`
  committed; `graph.json`/`graph.html`/`cache/` gitignored as regenerable).
- **Reversibility:** delete `graphify-out/` (one directory, not referenced by
  any engine code or test).

## Spec-Kit (`specify` CLI) — INSTALLED, not yet used for a live spec

- **Purpose:** spec-driven workflow (`/speckit.specify → plan → tasks →
  implement`) for the upcoming P2 engine-delta phases, whose subphase prompts
  (P2a–P2f) are exactly spec-then-tasks-shaped.
- **What was added:** 30 files, zero collisions with the existing tree —
  `.claude/skills/speckit-{specify,plan,tasks,implement,analyze,clarify,
  checklist,constitution,converge,taskstoissues}/SKILL.md` (agent-loadable
  skills) + `.specify/` templates/scripts/workflows (init via
  `specify init --here --integration claude`, mirrored manually from a temp
  dir because `--force` merge into a non-empty tree was not auditable).
- **Not done here:** no constitution, spec, or plan was authored — that is
  P2-prep work for the Owner/Architect, not a polish pass. Templates land
  unused-but-ready; `verify-and-stop` note: the integration is "installed",
  not "adopted into the workflow" until the first `/speckit.specify` runs.
- **Alternatives:** keep hand-written phase prompts (current practice —
  works, but each prompt re-states invariants at real token cost).
- **Risk:** template files imply a workflow the team may not follow;
  `.specify/scripts/` are PowerShell (Windows host — fine).
- **Reversibility:** delete `.claude/skills/speckit-*` and `.specify/`
  (nothing references them).

## paper-clip — NOT_INSTALLED (tool not found)

- **Finding:** no CLI/binary (`command -v paperclip paper-clip` → empty) and
  no matching installable skill (`npx skills find paper-clip` → unrelated
  hits: `paper-context-resolver`, `writing-shape`, `kami`). The migration
  prompt's Part 0.11 lists it as optional; it was optional then and remains
  undiscoverable now.
- **Decision:** NOT_APPLICABLE pending the Owner naming the source
  (package/repo) for "paper-clip". Nothing was installed under a guessed name.
- **Risk of forcing it:** installing a wrong "paper-clip" (e.g. an unrelated
  academic-paper skill) adds prompt surface for zero benefit — the exact
  anti-pattern this pass avoids.
- **Reversibility:** trivially reversible (nothing to reverse — not present).

## Aggregate token-economy notes (Owner's stated goal)

1. This pass itself was run at **zero LLM-extraction tokens** (AST-only
   graphify; docs-layer enrichment deliberately deferred).
2. Standing wins for future sessions: `graphify query` answers instead of
   tree re-reads; `GRAPH_REPORT.md` god-node map for orientation; Spec-Kit
   templates reduce per-phase prompt boilerplate; `report110/111.md` give
   session continuity without history re-derivation.
3. Deferred (needs Owner): Gemini key for graphify semantic enrichment of the
   112 research docs.
