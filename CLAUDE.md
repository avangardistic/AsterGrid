# CLAUDE.md — Project Invariants (hypergrid)

`prompt.md` (Master Control Prompt v3.0) governs this program's entire workflow:
phases, gating, source governance, artifact discipline. Read it before acting.

## Authority order (from `prompt.md` `<instruction_priority>` — mandatory)

1. System / platform safety constraints
2. Explicit Owner decisions in the repository
3. `Strategy.md` — for strategy semantics
4. Current authoritative external venue evidence (Hyperliquid docs/API)
5. Accepted architecture decisions
6. Accepted implementation requirements
7. Tool / framework conventions
8. Your own proposals

Lower-priority material MUST NOT silently override higher-priority material.
When sources conflict, create an explicit conflict record; never resolve a
material strategy conflict silently.

## Immutable files

- **`Strategy.md` MUST NEVER be modified** — not rewritten, not reworded, not
  "normalized," not reinterpreted. It is the canonical strategy authority
  (v2.3-final; identity/hash in `research/strategy/STRATEGY_SOURCE_RECORD.md`).
  Derived artifacts never become the authority themselves.

## Owner-Gate-only actions (no action without an explicit Owner Gate)

The following MUST NOT happen without explicit Owner authorization:

- writing any production trading code
- selecting a framework / technology (Temporal, LangGraph, Redis, MCP, etc.)
- defining a permanent subsystem list or Agent roster
- connecting to Testnet or Live; submitting any order
- Live activation (a separate authority boundary — no prompt, Agent, or
  subagent may itself constitute Live authorization)

Runtime principle: the final trading system must be deterministic and
**AI-independent** (no LLM/agent/prompt runtime required at runtime), and must
**fail closed** on any ambiguity. Do ordinary reversible engineering work
without asking; open an Owner Gate only for the boundaries above.

## Research state

See **`research/README.md`** for phase status, artifact layout, and blockers.
