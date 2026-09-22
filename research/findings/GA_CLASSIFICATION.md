# GA_CLASSIFICATION.md — Status of the genetic-algorithm study (Phase 4.7)

- **Purpose:** Fix the epistemic status of `ga_arena.py` (SRC-207), `ga_results.json` (SRC-207), and `genetic_calibration_report.md` (SRC-206) so no downstream phase mistakes the "Golden Genome" for a production calibration value or a normative strategy input.
- **Producer:** Claude Code (Opus 4.8), Phase 4.7. **Status:** classification only — no value adopted, no decision created.
- **Inputs (read-only):** SRC-206, SRC-207; `Strategy.md` §14/§16 (immutable authority).

---

## 1. What the GA engine is

`ga_arena.py` is an **offline evolutionary search** (deterministic, seed 20260921): a population of parameter genomes is scored in a **synthetic tick-level arena** — 60 ticks/s over **four stress scenarios** (Wick, Funding-Spike, Venue-Cap-4%/hr, Liquidity-Void) — and evolved (tournament selection, crossover, adaptive mutation, elitism + Hall-of-Fame) for 50 generations. The "Golden Genome" `G* = {A,B,C,D,E}` is the fittest genome **within that simulator**, reported with full provenance in `genetic_calibration_report.md`.

## 2. Its synthetic nature (decisive)

The arena's price/fill/spread dynamics are **axiom-calibrated proxies**, NOT historical Hyperliquid ticks. Its edge model (μ = 0.9·GGE, ~30-s horizon, clipped stops) is a **selection device, not a P&L oracle** — the report itself states absolute fitness levels are meaningless and only relative selection / cliff locations / survival mechanics are deliverables. The venue *hard limits* it enforces (AA-4 4%/hr funding cap, AA-6 $10 minimum, AA-7 lot lattice, AA-8 rate budget) are real; the *market behaviour* it simulates is not.

## 3. What it IS

Exploratory evidence · a falsification tool (it empirically reproduced the F-1\* dead-band contact — 86% below the tradability floor, 0% above) · sensitivity analysis (which genes are fitness-driving vs survival-driving) · a candidate-generation mechanism for later, evidence-based calibration.

## 4. What it is NOT

NOT production calibration truth · NOT a normative strategy specification (`Strategy.md` remains the sole strategy authority) · NOT venue authority (the venue docs remain the venue authority) · NOT a runtime dependency (the runtime is deterministic and AI/GA-independent; the GA is strictly offline) · NOT the independent reference model (that role belongs to **CAP-0024**, which derives expected behaviour from the normative contract, not from a fitness search).

## 5. The Golden Genome's status

The Golden Genome is a **CALIBRATION PROPOSAL**. Its values remain **`[DYNAMIC — CALIBRATION PENDING]`** per `Strategy.md` §16 / §14. Confirmation requires real tick / backtest / shadow evidence (Phases 10–12) **and an explicit Owner decision**. No dynamic default may be frozen on the basis of this report alone (§14 global rule; `CLAUDE.md` never-freeze rule). Even the report concedes Gene B is fitness-neutral above the tradability floor and should ship at the audit's minimal admissible value, not at the GA's evolved `$31.15` — underlining that the GA does not fix the value.

## 6. The F-1\* claim inside the GA report is empirical only

The report's demonstration that the legacy exposure tolerance produces a dead-band is an **EMPIRICAL OBSERVATION inside the simulator**. It does **not** substitute for an independent mathematical verification of the audit's F-1\* claim against `Strategy.md` and venue evidence — that verification is performed separately in [`F1_VERIFICATION.md`](F1_VERIFICATION.md) (Phase 4.7 Part C) and is the record of authority for the F-1\* question.

---

## Validation hierarchy (GA sits alongside, never above)

```
Normative Strategy Contract (authority)
  → Independent Reference Model (CAP-0024)
    → Implementation
      → Replay / Differential Validation
        → Real / Shadow Evidence
```

The GA study is positioned **alongside** this chain as an offline exploratory input to the calibration step — never above the Strategy Contract, the reference model, or venue authority. Any use of a GA value in the runtime would require it to first pass upward through this chain and an explicit Owner decision.
