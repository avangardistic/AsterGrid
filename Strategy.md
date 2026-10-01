# Strategy.md — Hyperliquid Perpetual Hedge Grid Bot

**Version 2.3-final — Canonical Specification (base v2.2 + approved decisions D-07(F), D-09(CAL), D-12…D-15 + dynamic defaults D-16/D-17)**
**Status: FINAL — APPROVED WITH DYNAMIC DEFAULTS (D-16/D-17; owner-overridable, calibration pending).**
**Target system:** a clean, engineered crypto buy/sell trading system on Hyperliquid perpetuals, operating on the **top 5 liquid crypto assets** — BTC, ETH, SOL, and the two most liquid native Hyperliquid perps at implementation time. Parameter defaults are conservative for these assets; **any other asset requires explicit re-parameterization** before use.
**Provenance:** merged from `STRATEGY.md` v1.0 and `AMEND-STRATEGY.md` (v2.0 run: 25 conflicts, resolution table, audit), then from the approved decision records `OWNER-DECISION-ANSWER-SHEET.md` (D-01…D-08), `OWNER-DECISIONS-D09-D11.md` (v2.2 run), and `OWNER-DECISIONS-REMAINING.md` (D-07(F), D-12…D-15). The three D-09(CAL) defaults are derived dynamic formulas marked `[DYNAMIC — CALIBRATION PENDING]` (§16, D-16), and the §5.4.1 reference-price tolerance (D-17) is `[DYNAMIC-CALIBRATABLE]`. Every merge decision is traceable to its decision ID in **§14 Parameter Reference**. Superseded artifacts are archived in `history/` (non-authoritative).
**[SD] residual-risk annotation:** the `[SD]` (Source-Derived) annotation remains in force document-wide — all `[SD]` claims reflect GridEA's DESCRIBED behavior, not verified code. Per the D-11 removal, no `.mq5` / `SAFETY_MECHANISMS.md` re-verification pass is performed and no evidence is requested; residual provenance risk is accepted by the Strategy Owner and recorded here.

**Change log v2.3-final (traceability of every structural change; nothing below is a silent override):**

| # | Decision | Change |
|---|----------|--------|
| 1 | D-01 | §4.1: return level = traversal-verified (highest opposite-group level reaching POSITION_VERIFIED in the recorded prior traversal of the current Generation); dynamic, not configured; missed-Cycle deferral rule added. |
| 2 | D-02 | §4.1: verification bar = POSITION_VERIFIED strategy fill (§6.1); hedge orders not eligible; exclusion list unchanged. |
| 3 | D-03 | §4.2: `EvolutionConfirmationSeconds = 60` approved as configuration value (calibratable). |
| 4 | D-04 | §4.1: fail-closed on skipped/partially-verified return; `INELIGIBLE_EVOLUTION_CANDIDATE` (reason `RETURN_LEVEL_UNVERIFIED`). |
| 5 | D-05 | §4.5: Dominance = origin/traversed group is Dominant; MaxReachedLevel comparison superseded. |
| 6 | D-06 | §13.4 precondition (a): approved formula `3 × (TotalSystemCosts + StepBps_as_USD)`; cost window fixed lifetime-to-date (D-15). |
| 7 | D-07 | §13.4 precondition (b): derived tolerance `round_to_min_tradable_size(f(StepBps, MaxBasketNotional))` with the functional form approved (D-07(F)). |
| 8 | D-08 | §3/§4.6: `MaxGenerations = 99`, `MaxCyclesPerGeneration = 99`; one-successor-per-Generation rule reinforced; Scenario 19 normative and reachable. |
| 9 | D-09 | Approved numeric values/formulas inserted (Groups A–E); the three CALIBRATE rows carry derived temporary defaults marked `[TEMPORARY — CALIBRATION PENDING]` (§16). |
| 10 | D-10 | §8: `ArmPolicy ∈ {AUTO, SEMI, WEBHOOK}` (default Testnet AUTO, Live SEMI), `ArmRequestTimeoutSeconds = 30`, five arm-gate invariants preserved. |
| 11 | D-11 | REMOVED per owner decision; `[SD]` residual-risk annotation stays in force document-wide. |
| 12 | D-12 | §7.3: `MaxLevelNotionalDominant := Gen2SizeMultiplier × (MaxBasketNotional / GridLevels)` — resolves the dominant-side volume vs. level-cap conflict (review finding R-01). |
| 13 | D-13 | §12.1: `MaxBasketNotional` inputs fixed — `CapitalBase` = account equity incl. unrealized PnL; `Leverage_user = 3`; `MaxSafeNotional_margin := CapitalBase × Leverage_effective / 2`; `MarketDepth` = book depth within ±(10 × StepBps) of mid. |
| 14 | D-14 | §7.3: `MaxActiveGenerations` / `MaxActiveCycles` := all non-closed Generations/Cycles (conservative divisor set). |
| 15 | D-15 | §13.4: `TotalSystemCosts` accumulation window = Basket lifetime-to-date. |
| 16 | — | Three derived temporary defaults replace the UNSET fail-closed state for spec completeness: `EmergencyTolerance = 50` bps, `ExposureTolerance = (0.1 × NotionalPerLevel)/MarkPrice`, `MaxExposureImbalance = (1.0 × NotionalPerLevel)/MarkPrice` — all marked `[TEMPORARY — CALIBRATION PENDING]` (§16). |
| 17 | — | §14 recast as the Parameter Reference (every parameter: value/formula, unit, §-reference, calibration status); §16 recast as Remaining Open Items and Temporary Defaults. Superseded artifacts archived in `history/` (non-authoritative). |
| 18 | D-16 | §5.2, §9.1, §11.2/§12.1, §14, §16: the three `[TEMPORARY — CALIBRATION PENDING]` defaults (`EmergencyTolerance`, `ExposureTolerance`, `MaxExposureImbalance`) replaced with dynamic formulas derived from existing parameters — no new free parameters; §16 retitled "Dynamic Defaults Pending Calibration"; front-matter status summary updated accordingly. |
| 19 | D-17 | New §5.4.1: Reference-Price Tolerance at Cycle/Generation fire — the captured reference (§5.4) must lie within `0.33 × StepBps` of the nominal expected reference, else the transition is BLOCKED (fail-closed) with `RECONCILIATION_REQUIRED`; §5.6 non-overlap remains the authoritative structural check. |

**Change log v2.0 (structural; applied since v2.2, unchanged here):**

Tag legend (unchanged from v1.0):

```
[SD]  SOURCE-DERIVED         — traceable to GridEA Path B's STRATEGY.md
[UR]  USER-REQUIREMENT       — stated directly by the Strategy Owner, not in GridEA
[HC]  HYPERLIQUID-CONSTRAINT — verified against current Hyperliquid documentation
[DD]  DESIGN-DECISION        — this document's own architectural choice
[OQ]  OPEN-QUESTION          — unresolved; implementation must not silently guess
[TEMP] TEMPORARY-DEFAULT      — derived placeholder value; tagged
                               [TEMPORARY — CALIBRATION PENDING]; overridable
                               by the Strategy Owner at any time and superseded
                               by calibration + owner confirmation (§16)
[DYN]  DYNAMIC-DEFAULT        — derived formula over parameters already
                               defined in this document (no new free
                               parameters); tagged [DYNAMIC — CALIBRATION
                               PENDING] (D-16) or [DYNAMIC-CALIBRATABLE]
                               (D-17); proposal-only per the §14 global
                               rule; overridable by the Strategy Owner at
                               any time and superseded by calibration +
                               owner confirmation (§16)
```

Rule-status tags (new in v2.0, applied to every normative rule):

```
[DEFINED]           — the rule is fully specified; no owner input required to execute it.
[DECISION_REQUIRED] — the rule is specified but its activation or numeric value is gated
                      on a §14 Parameter Reference entry; while gated, the affected capability is
                      BLOCKED (fail-closed). Implementation must not invent a value.
```

No rule in this document is gated: all owner decisions are resolved (§14). The only non-`[DEFINED]` values are the four dynamic defaults of §16 — three tagged `[DYNAMIC — CALIBRATION PENDING]` (D-16) and one tagged `[DYNAMIC-CALIBRATABLE]` (D-17).

**Change log (traceability of structural changes; nothing below is a silent override):**

| # | Change |
|---|--------|
| 1 | §4.1/§4.4: the v1.0 dual-group Evolution working default is **superseded** by the path-dependent Evolution rule `[UR]` adopted from the Amendment. The v1.0 OQ-BLOCKING question (§4.4) is **closed** — not silently: recorded in §16. |
| 2 | §4.3: Generation state model extended (`EVOLUTION_PENDING` transient retained; `SUCCESSOR_CREATED`, `DISABLED_AT_CYCLE_99`, `CLOSED_ONLY_AS_PART_OF_BASKET` added; v1.0 `EVOLVED` renamed and mapped — see state table note). |
| 3 | §5: Cycle-99 disable transition added; Cycle-completion ordering made explicit (reconcile before `COMPLETED`). |
| 4 | §13.4: net-profit closure gate added `[UR]` (Amendment §8/§10.4); risk precedence over the profit target made explicit. |
| 5 | New **§14 Parameter & Decision Register** inserted. Former §14 (State Machine Invariants) → **§15**; former §15 (Open Questions) → **§16**. Base section order is otherwise preserved; this renumbering is the only numbering change. |
| 6 | Cross-reference defects in v1.0 fixed and logged: §2's Generation definition cited "(§9)" for winding down — corrected to §13.4; §4.3 cited "§9.2" for Basket freeze — corrected to §13.3; invariant "Gxx-Cxx-DUxx" corrected to the §3 display format. |
| 7 | Non-authorization clauses are preserved verbatim (document footer, §16, §15 closure rules). |

---

## 1. Executive Summary

This strategy runs an asymmetric hedge-grid on a single Hyperliquid perpetual market at a time. It maintains two logically separate objectives over one shared position book:

- **`[DD]` A Hedge Layer** that seeks *symmetry* — its only job is keeping verified exposure inside a configured envelope, with authority to override the profit layer whenever risk crosses a boundary. `[DEFINED]`
- **`[DD]` A Profit Layer** that is *permitted to be asymmetric* — it places and manages the grid itself, and may deliberately skew geometry, timing, and sizing toward whichever side the market currently favors, provided the hedge layer's constraints are respected. `[DEFINED]`

The grid is organized as `[SD]` **Basket → Generation → Cycle → Level**. A **Generation** is a strategic directional epoch. A **Cycle** is one traversal of a Generation's ladder; a Cycle that reaches its Terminal Level is followed by a new Cycle **in the same Generation** `[UR]`, up to the Generation's Cycle limit (architectural maximum Cycle 99) `[UR]`. A **Generation successor** is created only by a verified, path-dependent traversal-and-return condition (§4.1) `[UR]`, at most once per Generation `[UR]`. A Generation whose Cycle limit is reached becomes `DISABLED_AT_CYCLE_99`: it stops all Profit Layer progression but remains economically live until the Basket is verified closed `[UR]`. `[DEFINED]`

Every order-state claim in this system is anchored on **verified position delta**, never on price-crossing or order-acknowledgement alone `[DD]`, because Hyperliquid's asynchronous fill model (§6) makes "order sent" a materially different fact from "position changed." `[DEFINED]`

---

## 2. Strategy Model — Formal Definitions

```
Basket        `[DD]` Top-level accounting/lifecycle container, one Hyperliquid
              perpetual market at a time. Exactly one active Basket per market.
              `[DEFINED]`

Generation    `[SD, extended UR]` A strategic directional epoch, containing an
              ordered sequence of Cycles. Generation 0 exists at Basket creation.
              GenerationID ∈ [0, 99] (§3). Generations never close individually —
              only the Basket closes them, and only by the verified closure
              sequence (§13.4). A Generation's positions, fees, funding, realized
              PnL, unrealized PnL, verified exposure, and hedge obligations remain
              part of the Basket until the Basket is verified closed. `[DEFINED]`

Group         `[SD]` One of the two directional halves of a Generation's
              ladder: BU (long) or SL (short), levels 1..N,
              N = GridLevels (config, default 6 `[SD]`, hard architectural
              max 12 `[SD]`). `[DEFINED]`

Cycle         `[DD, extended UR]` One traversal of the active Generation's ladder
              from its current execution-grounded reference price toward a
              terminal level. Cycle 0 exists at Generation creation.
              CycleID ∈ [0, 99], scoped to its Generation (§3). A completed
              Cycle never changes its Generation. `[DEFINED]`

Level         `[SD]` One priced, sized grid rung (BUk/SLk) within one Cycle
              within one Generation. `[DEFINED]`

Reference Price `[SD]` The price a Cycle's level distances are measured
              from. Every Cycle and every Generation computes its own.
              `[DEFINED]`

Evolution     `[UR]` The verified creation of a successor Generation after the
              path-dependent traversal-and-return condition (§4.1) is satisfied
              and confirmed. Evolution is NOT synonymous with terminal-level
              reach: a terminal-level reach creates a new Cycle in the same
              Generation (§5.1); only a verified return creates a Generation
              (§4.1). The event is `EvolutionTriggered`; the resulting object is
              a new `Generation`. `[DEFINED]`

Terminal Event `[DD, extended UR]` The verified event that completes the current
              Cycle and creates a successor Cycle within the same Generation
              (§5.1). No GridEA equivalent. `[DEFINED]`

Successor Lock `[UR]` The state of a Generation that has already created its one
              permitted successor Generation (§4.4). `[DEFINED]`

Disabled Generation `[UR]` A Generation in state `DISABLED_AT_CYCLE_99` (§5.3):
              no further Profit Layer progression, full accounting and protection
              eligibility retained, not closed until Basket closure (§13.4).
              `[DEFINED]`
```

### 2.1 Naming: "Soft Reset" → "Evolution" `[UR]` `[DEFINED]`

Adopted per Strategy Owner directive. "Reset" is rejected as a system-level term because nothing resets — old positions and old Generations survive (`[SD]` GridEA's own doc calls this "asymmetric" precisely because it isn't a reset). The event is `EvolutionTriggered`; the resulting object is a new `Generation`.

---

## 3. Canonical Identity Model `[UR]` `[DEFINED]`

Every Level/Cycle/Generation object carries independently-persisted fields — never a single encoded integer:

```
struct LevelIdentity {
    GenerationID: uint   // 0–99 inclusive
    CycleID:      uint   // 0–99 inclusive, scoped to its Generation
    Direction:    {BU, SL}
    LevelID:      uint   // 1–GridLevels, scoped to its Cycle+Direction
}
```

**Canonical display string** (derived only, never authoritative — never parsed back to reconstruct identity):

```
"G{GenerationID:02d}-C{CycleID:02d}-{Direction}{LevelID:02d}"
e.g. "G00-C00-BU01", "G12-C34-SL06", "G99-C99-SL06"
```

**Identity boundary rules `[UR, from Amendment §3]`:**

1. The system MUST reject any attempt to create `CycleID = 100` or `GenerationID = 100`.
2. The system MUST NOT wrap, overwrite, truncate, or recycle an existing identity.
3. Historical Cycles and Generations are immutable objects; they are never deleted, rewritten, or reused.

**Limits:** the hard architectural bound for both `GenerationID` and `CycleID` is **99** `[UR]`; the architecture MUST support the full 0–99 range regardless of configuration. `MaxGenerations` and `MaxCyclesPerGeneration` are configuration values; the **effective limit** for each axis is `min(configured value, 99)` `[DD, merge]`. Approved configuration (§14 D-08): `MaxGenerations = 99`, `MaxCyclesPerGeneration = 99` — the effective limit is therefore 99 on both axes and the full 0–99 lifecycle is reachable in normal configuration `[DEFINED]`. Reaching the effective Cycle limit triggers §5.3 (disable); reaching the effective Generation limit triggers §4.6.

---

## 4. Generation Lifecycle

### 4.1 Evolution trigger — path-dependent return `[UR]` `[DEFINED]`

The v1.0 dual-group threshold rule is **superseded** `[UR]` (closure of the v1.0 §4.4 OQ is recorded in §16). A new Generation may be created when **all** of the following are verified, in this order:

```
1. A prior directional traversal has been established in the active
   Generation (at least one level of one group has reached
   POSITION_VERIFIED (§6) within that Generation's lifecycle).
2. The traversed/origin group is recorded.
3. The market reverses toward the opposite group.
4. The market reaches the opposite group's established return level —
   the highest level of the opposite group that reached
   POSITION_VERIFIED during the recorded prior traversal in the current
   Generation (§16, D-01). The return level is dynamic and
   traversal-derived, not a configured value; `ReturnLevelBU` and
   `ReturnLevelSL` are not configuration keys of this system.
5. The return condition is verified by a strategy order at the return
   level reaching POSITION_VERIFIED — verified exchange order fill ∧
   corresponding authoritative position delta (§6.1); hedge orders are
   NOT eligible to satisfy this condition (§16, D-02) — and the verified
   condition holds continuously for the confirmation window (§4.2).
6. Exposure, reconciliation, risk, fillability, and transition guards
   pass (§11.1 ordering; the §8 gate list).
7. The current Generation is eligible to create a successor under §4.4
   (successor lock not set; GenerationID < effective Generation limit).
```

**The trigger is NOT** (each is individually insufficient):

```
terminal-level reach alone
level-number equality alone
requested order fill alone
raw price crossing alone
order acknowledgement alone
isolated fill message alone
unverified WebSocket evidence alone
```

**Minimum penetration `[DD, from Amendment Scenarios 02–04]`:** an intermediate level in one group, or directional progress into the opposite group without a verified return to the established return level, creates no Generation. The canonical trigger is the verified return to the established return level (Amendment Scenario 04). If no level of the opposite group reaches POSITION_VERIFIED in a Cycle — i.e., no verified traversal occurs in that Cycle — the return level remains undefined, the return condition is not satisfied, and **no new Generation is created in that Cycle**; the Evolution opportunity is **deferred to a later Cycle of the same Generation, not cancelled** (per-Cycle evaluated, carried forward) `[UR, D-01]`.

**Fail-closed on unverified return `[DD, D-04]`:** if the return level is skipped (§9.3) or only partially verified, no Evolution occurs. Record `INELIGIBLE_EVOLUTION_CANDIDATE` (reason `RETURN_LEVEL_UNVERIFIED`); the failed instance is never resurrected or retroactively completed (§9.3 skip semantics apply to the unverified portion — it contributes zero exposure and zero PnL), and a future complete re-formation of the return condition in a later Cycle may re-candidate. Every `EvolutionTriggered` event must pass the full condition list above — any apparent trigger that fails a condition is recorded as `INELIGIBLE_EVOLUTION_CANDIDATE` with a reason code, never silently discarded, never executed `[UR, Amendment invariant A18, extended DD]`.

**Rejected rules (carried from v1.0, unchanged) `[DD]`:** the legacy difference-based rule (`|B−S| ≥ MinLevelDifferenceForReset`); a `|BU_Count − SL_Count| == 1` rule (no source, formally disclaimed); the dual-group threshold rule (superseded by this section; its closure is recorded in the §16 closed ledger).

### 4.2 Evolution Confirmation Tolerance `[SD, extended]` `[DEFINED]`

```
The Evolution candidate (§4.1 conditions 1–4) must hold CONTINUOUSLY for
EvolutionConfirmationSeconds (config; approved value **60s**, §14 D-03)
before Evolution fires.

Evaluated only over POSITION_VERIFIED evidence (inherits §6's verification
requirement automatically — not a separately-tuned mechanism).

Hysteresis: once the candidate forms, the return-level boundary is latched
for the confirmation window; de-verification of the return condition
resets the window (prevents flip-flop at the boundary).

Only one Evolution transition may be in flight per Basket at a time
(state-transition locking).
```

### 4.3 Generation states `[DD, extended UR]` `[DEFINED]`

```
CREATED → ACTIVE → EVOLUTION_PENDING (transient, §4.2 window)
        → SUCCESSOR_CREATED            [created its one successor]
        → DISABLED_AT_CYCLE_99         [reached its effective Cycle limit]
        → CLOSED_ONLY_AS_PART_OF_BASKET [verified Basket closure, §13.4]

FROZEN: overlay from Basket FREEZE (§13.3) on any non-terminal state.
```

State semantics:

- **ACTIVE**: exactly one per Basket — the newest. Full progression capability: may open Levels, start Cycles, and (if eligible under §4.4) create its one successor.
- **EVOLUTION_PENDING**: transient; the §4.2 confirmation window is running. No new successor may be started elsewhere in the Basket while it is in flight.
- **SUCCESSOR_CREATED**: progression lock. May **continue its own Cycle progression** (create new Cycles below its effective Cycle limit, per §5.2) and manage existing Levels. May **not** create another successor, may **not** start a new Evolution, and may **not** be re-armed as a new strategic traversal beyond its Cycle mechanics. Its positions remain in Basket accounting and Hedge controls `[UR]`.
- **DISABLED_AT_CYCLE_99**: terminal progression state (§5.3). No new Cycles, no new Levels, no successor, ever. Remains eligible for: position reconciliation, Hedge Recovery, exposure correction, mirroring where required for protection, funding and fee accounting, realized/unrealized PnL accounting, and Basket closure `[UR]`. It is a strategy-progression state, **not** a position-closure state `[UR]`.
- **CLOSED_ONLY_AS_PART_OF_BASKET**: entered only when the Basket closure sequence (§13.4) verifies closure. Never entered individually.
- **FROZEN**: overlay only; it never erases the underlying lifecycle state.

**Terminology mapping (no silent rename) `[DD]`:** v1.0's `EVOLVED` state is **superseded**. In v2.0 every former "evolved parent" is `SUCCESSOR_CREATED` (if it created a successor and retains Cycle capability) or `DISABLED_AT_CYCLE_99` (if its Cycle limit is reached). The Amendment's `EVOLVED_PASSIVE` label is **deprecated as an alias**: implementers MUST treat any occurrence as `SUCCESSOR_CREATED` when the Generation has not reached its Cycle limit, and as `DISABLED_AT_CYCLE_99` when it has. No state may carry two names in persisted data.

### 4.4 One-Successor Constraint & Successor Lock `[UR]` `[DEFINED]`

1. A Generation may create a successor Generation **at most once** during its eligible pre-limit lifecycle `[UR]`.
2. After Generation `G` creates Generation `G+1`, `G` enters `SUCCESSOR_CREATED` (§4.3) `[UR]`.
3. While `G` is `SUCCESSOR_CREATED` and below its Cycle limit: it may continue its Cycle progression and create subsequent Cycles; it may not create another successor; no Cycle of `G` below its limit may create another successor `[UR]`.
4. Example (normative, Amendment Scenario 11/12): if Generation 0 creates Generation 1 at Cycle 0, Generation 0 cannot create Generation 2 from Cycle 1 through its Cycle limit; its progression boundary is its Cycle limit, then disable (§5.3).
5. The lock is per Generation: Generation 1 has its own independent eligibility and may itself create Generation 2 once, subject to the same rules and the global GenerationID limit `[UR]` (Amendment Scenario 18).
6. An apparent Evolution while the lock is active is recorded as an `INELIGIBLE_EVOLUTION_CANDIDATE` (reason `SUCCESSOR_LOCK_ACTIVE`), never executed `[UR]`.

### 4.5 Post-Evolution Dominance `[DD, D-05]` `[DEFINED]`

Post-Evolution geometry (§7.1) requires a Dominant side. Under the path-dependent trigger, Dominance is determined by the approved rule (§16, D-05):

```
Dominance(successor) := the origin/traversed group of the parent
    Generation's recorded prior traversal is Dominant.

    The traversed group is the side the market first moved toward
    during the parent Generation's traversal (e.g., the market
    traversed BU1→BU2→BU3 and then returned to SL3: BU is the
    origin/traversed group and becomes Dominant).

    The Dominant side is fixed at Evolution time (this §4.5)
    and never recomputed per Cycle.
```

The v2.0 MaxReachedLevel-comparison working default (former option (c)) is **superseded** by this approved rule — it is recorded as superseded in §16 (D-05) and carries no fallback status. No other dominance source may be used `[DD]`.

### 4.6 Generation 99 `[UR, DD]` `[DEFINED]`

Generation 99 is the final representable Generation. It may continue through its Cycles until its Cycle limit, subject to all risk and exposure controls, but it cannot create Generation 100. If Generation 99 reaches its Cycle limit it becomes `DISABLED_AT_CYCLE_99` (§5.3) and remains open only for management and Basket closure. The Basket MUST NOT silently wrap to Generation 0 or create an out-of-range successor `[UR]`. A successor attempt at `GenerationID = 99` is rejected and recorded as `INELIGIBLE_EVOLUTION_CANDIDATE` (reason `GENERATION_ID_LIMIT`) `[DD, Amendment Scenario 19]`. With the approved limits `MaxGenerations = 99`, `MaxCyclesPerGeneration = 99` (§3, §14 D-08), Scenario 19 is **normative and reachable in normal configuration** — it is no longer an architectural-only bound — and G99–C99 is the deepest valid lifecycle point `[DEFINED, D-08]`.

If the effective Generation limit is below 99 (config), the same semantics apply at that limit: the newest Generation cannot create a successor; the Basket continues with Cycle progression inside existing Generations and with risk/management/closure operations only `[DD, merge — generalizes Amendment §5.3 without changing its semantics]`. Under the approved configuration (§14 D-08) the effective limit is 99, so this generalization is inactive by default but remains the specified behavior if configuration is ever lowered.

With the approved limits, the one-successor rule spans the full lifecycle: **each Generation has exactly one child across its entire 99-Cycle lifecycle** — spanning all Cycles up to the Cycle limit. After a Generation creates its one successor, it enters `SUCCESSOR_CREATED` (§4.3) and may never create another successor, regardless of how many Cycles remain below its limit. All Cycles of a Generation below its limit remain valid progression even after that Generation has created its one successor — the parent's Cycle axis continues independently of the successor lock `[DD, D-08]`. The maximum representable chain is exactly 100 Generations (G0…G99), each creating at most one successor — Generation growth is linear, not exponential; the PASSIVE-exposure growth concern that previously motivated a smaller `MaxGenerations` default is structurally addressed by the one-successor rule `[DD, D-08]`.

### 4.7 Deterministic precedence for simultaneous Generation/Cycle events `[DD]` `[DEFINED]`

All state transitions are evaluated in passes. Within one pass, the following total order applies; no event may execute twice, and any event not executed in this pass is re-evaluated in the next:

```
P0  POSITION VERIFICATION & RECONCILIATION (feeds everything; §11.1)
P1  RISK / EXPOSURE PROTECTION & HEDGE RECOVERY (may block or divert
    every transition below; §11.1, §11.2)
P2  LOCKS: at most one Evolution transition in flight per Basket (§4.2);
    at most one Cycle transition per Generation per pass.
P3  SAME-GENERATION CONFLICT: if, for the same Generation G, both a
    Cycle-limit disable condition (§5.3) and an Evolution condition
    (§4.1) are verified in the same pass, the DISABLE executes and the
    Evolution candidate is recorded INELIGIBLE_EVOLUTION_CANDIDATE
    (reason CYCLE_LIMIT_REACHED). Rationale: successor eligibility ends
    at the Cycle limit `[UR, Amendment §5.2 "eligible pre-Cycle-99
    lifecycle"]`.
P4  ACROSS GENERATIONS: an Evolution transition executes BEFORE Cycle
    transitions (extends §11.1's ordering GENERATION EVOLUTION → CYCLE
    CREATION). If two Evolutions were eligible in one pass (impossible
    under the single-in-flight lock, but stated for determinism), the
    lower GenerationID executes first.
P5  CYCLE TRANSITIONS execute (standard §5.2 and disable §5.3), including
    the parent Generation's continued Cycle progression after its own
    successor creation (§4.4 item 3).
P6  LEVEL ARMING / ORDER PLACEMENT proceeds only after all transitions
    in this pass are complete.
```

---

## 5. Cycle Lifecycle

### 5.1 Terminal Event `[DD, extended UR]` `[DEFINED]`

```
TerminalEvent(G, C, group) :=
    the configured terminal level of the traversed group (the highest
    configured level, e.g. BU6/SL6 with GridLevels = 6) reaches
    POSITION_VERIFIED in Cycle C of Generation G.

POSITION_VERIFIED requires BOTH:
    verified exchange order fill
    AND corresponding authoritative position delta.
A price crossing, order acknowledgement, isolated fill message, or
requested order quantity is insufficient. `[UR, Amendment §4.1]`
```

### 5.2 Standard Cycle Transition (CycleID < effective Cycle limit) `[DD, extended UR]` `[DEFINED]`

When `TerminalEvent(G, C, group)` occurs and `C < min(MaxCyclesPerGeneration, 99)`, the transition executes strictly in this order:

```
1.  Cycle G-C → TERMINAL_PENDING
2.  Cancel all pending (not POSITION_VERIFIED) orders belonging to the
    exhausted traversal of Cycle C
3.  Reconcile authoritative position and order state
    (clearinghouseState / webData2)
4.  Compute the ladder non-overlap test (§5.6); on failure the
    transition is BLOCKED: Cycle stays TERMINAL_PENDING, a
    RECONCILIATION_REQUIRED condition is raised (fail-closed)
5.  Cycle G-C → COMPLETED
6.  Create Cycle G-(C+1) → CREATED → ACTIVE (same Generation)
7.  Capture the new execution-grounded reference price (§5.4),
    subject to the §5.4.1 reference-price tolerance
8.  Issue a fresh ladder for BOTH groups relative to the new reference,
    subject to all strategy gates (§8, §10)
```

This transition:

- does not create a new Generation by itself `[UR]`;
- does not close the completed Cycle's positions `[UR]`;
- does not erase the completed Cycle's history `[UR]`;
- does not remove completed Cycle exposure from Generation or Basket accounting `[UR]`;
- prevents unintended overlap between the old and new ladder (§5.6) `[UR]`;
- remains blocked or diverted to Hedge Recovery if ExposureDelta is outside tolerance `[UR]` — explicitly: `|ExposureDelta| ≤ ExposureTolerance` AND no Hedge Recovery is in progress AND the Basket is not in ERROR/RECOVERY/FREEZE (entry intents blocked under FREEZE per §13.3). `ExposureTolerance` is a **base-asset-quantity** bound (the unit of §11.1's ExposureDelta) with the dynamic default `(0.001 × StepBps / 10) × NotionalPerLevel / MarkPrice`, where `NotionalPerLevel := MaxBasketNotional / GridLevels` `[DYNAMIC — CALIBRATION PENDING]` (derivation, worked example, and status: §16, D-16).

### 5.3 Cycle-Limit Disable Transition (`DISABLED_AT_CYCLE_99`) `[UR]` `[DEFINED]`

Trigger: the effective Cycle limit is **99** (`MaxCyclesPerGeneration = 99`, §3/§14 D-08).

When `TerminalEvent(G, 99, group)` occurs (or `TerminalEvent(G, limit, group)` at a lower effective limit, §3):

```
1.  Cycle G-99 → TERMINAL_PENDING
2.  Cancel ALL pending Profit Layer progression orders associated with
    Generation G (both groups) — broader than §5.2's exhausted-side
    cancellation, because no further progression exists
3.  Reconcile authoritative state
4.  Cycle G-99 → COMPLETED
5.  Generation G → DISABLED_AT_CYCLE_99
6.  No Cycle 100 is created; no successor may ever be created by G;
    all identities and history are preserved
```

The disabled Generation remains open for: position reconciliation, Hedge Recovery, exposure correction, mirroring where required for protection, funding and fee accounting, unrealized and realized PnL accounting, and Basket-level closure `[UR]`. The Generation is not considered closed until the Basket closure sequence (§13.4) verifies the required residual exposure condition `[UR]`.

If no progression-capable Generation remains in the Basket (all `DISABLED_AT_CYCLE_99`), Profit Layer progression halts Basket-wide; Hedge, reconciliation, accounting, and closure operations continue `[DD, from Amendment Scenarios 15–17]`. Reaching Cycle 99 does not close the Generation and does not close the Basket `[UR]`.

### 5.4 Cycle Reference Price `[DD, extended per §33.4 of the roadmap]` `[DEFINED]`

```
CycleReferenceDerivation (config) :=
    TERMINAL_EXECUTION  (default) — verified average fill price of the
                          Terminal Level itself. New Level distances
                          (§7) compose with this automatically — no
                          separate offset needed; adding one would
                          double-apply spacing.
    TERMINAL_VWAP        — VWAP over the Terminal Level's OWN fill
                          window only (not a market-wide lookback —
                          avoids an arbitrary free parameter)
    TERMINAL_MID          — mid-price at the moment POSITION_VERIFIED
                          is reached for the Terminal Level
    TERMINAL_PLUS_STEP    — Terminal execution price ± one configured
                          step (non-default; explicit-buffer option)
```

All four remain execution-grounded (never a raw last-tick/trigger price). Tick-size rounding applies when converting to Level prices, not at capture time — the reference is stored at full precision. The selected policy is configuration and MUST be explicit. At the moment a new Cycle or Generation fires, the captured reference is additionally gated by the §5.4.1 reference-price tolerance.

### 5.4.1 Reference-Price Tolerance at Cycle/Generation Fire `[DD→D-17]` `[DEFINED]`

```
[DYNAMIC] When a new Cycle (§5.2) or a new Generation (§4.1) fires, the
reference price is captured per §5.4. The captured reference price MUST
lie within a tolerance of the nominal expected reference price:

    ReferencePriceToleranceBps := 0.33 × StepBps

    |captured_reference_price − nominal_reference_price|
        ≤ ReferencePriceToleranceBps / 10000 × nominal_reference_price

If the captured reference price is within this tolerance:
    - the Cycle/Generation fires normally;
    - the captured reference price is used as-is (§5.4);
    - the event is logged with the deviation magnitude (for audit).

If the captured reference price exceeds this tolerance:
    - the transition is BLOCKED (fail-closed, consistent with §5.2
      step 4 and §5.6): reference capture and ladder issuance
      (§5.2 steps 7–8) do not complete;
    - a RECONCILIATION_REQUIRED condition is raised;
    - no fallback reference price is auto-selected;
    - the transition is re-evaluated on the next pass after
      reconciliation (§4.7 P0).

Relationship to §5.6: the non-overlap test (§5.6) remains the
authoritative structural check on the new ladder. The reference-price
tolerance does not replace it — it gates the reference capture itself,
upstream of ladder construction. Both must pass for a transition to
complete.

Default values:
    StepBps = 10 → ReferencePriceToleranceBps = 3.3 bps
    StepBps = 5  → ReferencePriceToleranceBps = 1.65 bps
    StepBps = 20 → ReferencePriceToleranceBps = 6.6 bps

The 0.33 coefficient is DYNAMIC-CALIBRATABLE (proposal-only per §14
global rule). It is strictly smaller than 1.0 by construction, so a
captured reference can never drift a full step and violate §5.6.
```

**Worked example (defaults; BTC):** `StepBps = 10`, nominal reference = 100,000 USD → `ReferencePriceToleranceBps = 3.3` bps → allowed band = 100,000 × (1 ± 0.00033) = [99,967, 100,033] USD. Captured = 100,010 (deviation 1 bps) → within band → the Cycle/Generation fires normally. Captured = 100,040 (deviation 4 bps) → outside band → BLOCKED, `RECONCILIATION_REQUIRED` raised, no fallback reference, re-evaluated on the next pass after reconciliation (§4.7 P0).

### 5.5 Generation vs. Cycle — formal distinction `[DD]` `[DEFINED]`

```
GENERATION asks: "Has the market completed a verified path-dependent
    traversal-and-return, so that a strategic successor epoch should
    begin?" → path-dependent return (§4.1) → new epoch; old epoch
    survives as SUCCESSOR_CREATED (Cycle-capable) and later
    DISABLED_AT_CYCLE_99.

CYCLE asks: "Has the ladder in ONE direction been fully consumed,
    requiring a fresh anchor?" → single-group terminal reach (§5.1) →
    new traversal, SAME epoch.
```

Cycle numbering restarts at 0 for every new Generation; Generation and Cycle counters are independent axes (§3) `[UR]`.

### 5.6 Ladder Non-Overlap Test `[DD]` `[DEFINED]`

The v1.0 invariant "Cycle transition must not create unintended level overlap" is now a computable gate, no longer OQ-dependent:

```
For the exhausted group's new ladder (relative to the new reference):
  N1. Every new level price MUST be strictly monotonic in level index
      in the traversal direction (BU ascending, SL descending).
  N2. The new Level-1 price MUST lie strictly beyond the old Cycle's
      terminal-level execution price by more than zero ticks — i.e.,
      no new level price may lie within the closed interval spanned by
      the old Cycle's reference price and the old terminal execution
      price.
  N3. No new level price may equal any still-live level price of the
      same group within the same Generation.
Cross-group overlap is not applicable (BU prices lie above, SL prices
lie below their own references by construction).

On failure of N1–N3: the Cycle transition is BLOCKED (fail-closed,
§5.2 step 4); RECONCILIATION_REQUIRED is raised; no fallback reference
derivation is auto-selected. If the configured derivation structurally
cannot satisfy N1–N3 (e.g., TERMINAL_MID inside the old ladder), that is
a configuration error surfaced at validation time, not a runtime choice.
```

### 5.7 Normative Generation/Cycle scenarios `[UR, Amendment §9, compressed — the rules above are authoritative; these pin interpretation]` `[DEFINED]`

```
01  No verified traversal → no Generation; continue G0-C0.
02  SL1→SL2 verified, no return → no Generation.
03  SL2→BU1→BU2 verified, no terminal, no verified return → no Generation.
04  SL2→BU1→BU2→ verified return to established SL2 → create G1-C0
    [DEFINED, D-01/D-02 approved].
05  Raw price touch of the return level → no Generation; reconcile.
06  Return order acknowledged, delta unverified → no Generation;
    RECONCILIATION_REQUIRED or wait for POSITION_VERIFIED.
07  Partial return verification → no Generation; mirror verified
    exposure, manage remainder.
08  BU6 verified (terminal) → complete C0; create G0-C1. No new Generation.
09  BU6 terminal with pending orders → cancel relevant pending orders,
    reconcile, create G0-C1. No Generation change.
10  BU6 terminal in C0, verified return in C1 → G1-C0 created; G0
    passive/locked. Cycle and Generation transitions remain separate events.
11  G0 creates G1 at C0 → G0 enters SUCCESSOR_CREATED; no G2 from C1..98.
12  G0-C2 attempts another Evolution → rejected (SUCCESSOR_LOCK_ACTIVE);
    apparent path recorded as ineligible candidate.
13  G0-C50 after successor creation → valid terminal event creates G0-C51;
    Generation creation remains prohibited for G0.
14  G0-C98 terminal verified → create G0-C99; Generation creation prohibited.
15  G0-C99 terminal verified → G0 DISABLED_AT_CYCLE_99; no Cycle 100.
16  Disabled G0, BasketNetPnL below closure target → stays open, inactive
    for progression; hedge/reconciliation/management only.
17  Disabled G0, ExposureDelta breaches acute threshold → Hedge Recovery
    takes priority; bounded urgent correction; Profit Layer stays disabled.
18  G1 performs its own eligible traversal+return → create G2-C0; G1 enters
    SUCCESSOR_CREATED. G0's lock does not block G1.
19  G99 otherwise-valid Evolution → rejected (GENERATION_ID_LIMIT); recorded;
    never wraps to G0; progression continues per §4.6.
20  G99-C99 terminal verified; BasketNetPnL reaches the approved
    closure target (D-06 formula) →
    run §13.4 closure sequence; Basket CLOSED only after both the
    net-profit condition and verified residual-exposure condition pass
    [D-07(F) approved: the residual precondition is computable —
    worked example in §13.4].
```

---

## 6. Execution Assurance

### 6.1 State pipeline `[SD principle, HC mechanism]` `[DEFINED]`

```
INTENT_CREATED → ORDER_SUBMITTED → ORDER_ACKNOWLEDGED → ORDER_ACTIVE
    → PARTIALLY_FILLED → FILLED → POSITION_VERIFIED
                        ↘ CANCELLED
    → EMERGENCY (trigger-without-fill) → SKIPPED (tolerance/economics fail)
    → ERROR (unrecoverable exchange error)

Protection-locked levels additionally start: LOCKED → IDLE
```

**Hard rule:** `LEVEL FILLED ⇔ ORDER FILLED ∧ POSITION DELTA VERIFIED`. No state reaches `FILLED` in this strategy's own bookkeeping from a bare `userFills` message or REST ack alone — a subsequent authoritative position-state read (`clearinghouseState`/`webData2`) must confirm the delta.

### 6.2 Hyperliquid mechanisms relied on `[HC]` `[DEFINED]`

`cloid` (128-bit client order ID, idempotent order identity) · REST `POST /exchange` ack (`resting`/`filled`/`error`) · `orderStatus` info endpoint · WS `orderUpdates` (order lifecycle) · WS `userFills` (fill-level, snapshot-tagged on reconnect) · REST `userFills`/`userFillsByTime` (durable history, ≤10,000 retained) · `clearinghouseState`/`webData2` (authoritative position/margin state) · TIF: `Gtc`/`Ioc`/`Alo` · trigger orders evaluated against oracle mark price, not last trade.

### 6.3 Precision `[HC]` `[DEFINED]`

Prices: ≤5 significant figures **and** ≤ (`MAX_DECIMALS − szDecimals`) decimal places, `MAX_DECIMALS = 6` for perps; integer prices always valid. Sizes: rounded to the asset's `szDecimals` (from `meta`). Normalization happens in the Execution Engine before every signed order — never left to the exchange to reject-and-retry (this is the single most common third-party-SDK bug class on this venue).

---

## 7. Grid Geometry

### 7.1 Distance model `[DD]` `[DEFINED]`

```
[DD] Basis points (bps), not pips — converted to an absolute price at
order-build time, then tick-rounded (§6.3). Rejected: absolute price
distance (fails identically to pips across assets of different
magnitude), plain percentage (bps is the less ambiguous convention and
matches Hyperliquid's own TWAP-slippage unit).

[DD→D-09 Group C] Approved anchor geometry (defaults):
    StepBps                 = 10 (approved default; calibratable
                              per §14 D-09 Group E, except as noted)
    GridLevels              = 6  (approved; NOT calibratable —
                              hard-excluded from the optimizer
                              allowlist per §14 D-09 Group E)
    FirstLevelDistanceBps   = 2 × StepBps = 20 (approved default)
    All bps-based defaults below compose from these anchors.

[SD] Level-1 distance rule (v2.0 clarification of a v1.0 gap):
    For every Cycle of Generation 0, and for every continuation Cycle
    (any Cycle ≥ 1 inside any Generation): Level 1 of BOTH groups is
    placed FirstLevelDistanceBps from that Cycle's reference price
    (approved default: `FirstLevelDistanceBps = 2 × StepBps = 20` bps
    when `StepBps = 10` — §14 D-09 Group C);
    Levels 2..N use normal StepBps spacing from the preceding level of
    the same group.

[SD, extended] Successor Generation (post-Evolution) Cycle 0 AND every
    subsequent Cycle of that Generation — the asymmetric posture
    persists for the Generation's lifetime, with the dominant side
    fixed at Evolution time (§4.5) and never recomputed per Cycle:
    Dominant side's Level 1: Gen2DistanceMultiplier × StepBps from the
        Cycle's reference price
    Weak side's Level 1: LOCKED until weak side's Level 2 fills
        (POSITION_VERIFIED) — re-applied per Cycle ladder
    Weak side's Level 2: READY (unlock trigger)
    All other levels: normal StepBps spacing from their own Level 1
```

**Approved successor-Generation geometry (G1+), §14 D-09 Group C** `[DD→D-09]` `[DEFINED]`:

```
Dominant side:  BU1 = Gen2DistanceMultiplier × StepBps from reference
                BU2 = BU1 + StepBps
                BU3+ = previous level + StepBps
                Volume of ALL dominant-side levels =
                    Gen2SizeMultiplier × (MaxBasketNotional / GridLevels)
Weak side:      SL1 = WeakSideFirstLevelMultiplier × StepBps from
                    reference — LOCKED until SL2 fills (POSITION_VERIFIED)
                SL2 = SL1 + StepBps — READY (unlock trigger)
                SL3+ = previous level + StepBps
                Volume = MaxBasketNotional / GridLevels (unchanged
                    vs. base levels)
```

`[DD, corrects a doc-internal ambiguity in GridEA's own text]` `Gen2LotMultiplier` is split into two independent, single-purpose parameters — GridEA's source text overloaded one config value to control both grid spacing and position size simultaneously, which silently couples two unrelated risk decisions:

```
Gen2DistanceMultiplier  (approved default 2, approved range 1.1–2.0
    `[DD→D-09]`) — scales ONLY the dominant side's Level-1 distance
WeakSideFirstLevelMultiplier (approved default 2 `[DD→D-09]`) — scales
    ONLY the weak side's Level-1 distance (LOCKED until its Level 2
    fills, §7.1 above)
Gen2SizeMultiplier      (approved default 1.5 `[DD→D-09]`) — scales
    ONLY the USD notional of Generation-2+ Levels
```

### 7.2 Protection Level Locking → Fillability-Gated Unlock `[SD, redesigned]` `[DEFINED]`

Unlock condition unchanged from GridEA (next level fills → protection level unlocks). Unlocking makes the level eligible to arm, but arming still passes through the full Pending Order Architecture gate list (§8) — including the Fillability Analyzer and Cost Analyzer — before any live order is placed.

### 7.3 Position sizing `[DD]` `[DEFINED]`

```
[DD] USD-notional-per-level, converted to base-asset size at order-build
time using live mark price, rounded to szDecimals. Rejected: fixed
base-asset quantity (reintroduces the "0.01 lot" problem across assets
of different price magnitude); fixed margin-at-config-time (conflates
sizing with a leverage choice that may itself change).

Exposure caps (USD notional, hard — reject rather than silently clip):
    MaxLevelNotional           = MaxBasketNotional / GridLevels
    MaxLevelNotionalDominant   = Gen2SizeMultiplier ×
                                 (MaxBasketNotional / GridLevels)
    MaxCycleNotional           = MaxBasketNotional / MaxActiveCycles
    MaxGenerationNotional      = MaxBasketNotional / MaxActiveGenerations
    MaxBasketNotional          (sum across ALL Generations, ACTIVE +
        PASSIVE — the number that matters most, since PASSIVE exposure
        is fully live; approved formula and input definitions: §12.1,
        D-13)

    Divisor definitions (D-14 — conservative set, chosen because
    superseded objects still hold live exposure):
    MaxActiveGenerations := the count of all Generations in the Basket
        not yet CLOSED_ONLY_AS_PART_OF_BASKET — including
        DISABLED_AT_CYCLE_99 Generations (their exposure is fully
        live, §5.3).
    MaxActiveCycles := the count of all Cycles of the counted
        Generations not yet closed as part of the Basket — including
        COMPLETED Cycles (their exposure is retained, §5.2).

    Resolution of the dominant-side volume vs. level-cap conflict
    (D-12): §7.1's dominant-side successor volume
    (Gen2SizeMultiplier × MaxLevelNotional) is a legitimate level size
    governed by its own derived cap MaxLevelNotionalDominant;
    MaxLevelNotional binds every other level. A dominant-side
    successor level above MaxLevelNotionalDominant is rejected like
    any other cap breach.

    Worked example (defaults): MaxBasketNotional = 30,000 USD,
    GridLevels = 6, Gen2SizeMultiplier = 1.5 →
    MaxLevelNotional = 5,000 USD; MaxLevelNotionalDominant = 7,500 USD.
```

---

## 8. Pending Order & Fillability Architecture `[DD]` `[DEFINED]`

Levels within `PendingArmDistance` (approved default 5 × StepBps = 50
bps when StepBps = 10; §14 D-09 Group D) of mark price pre-arm as
resting `Alo`/`Gtc` limit orders. Before arming, ALL gates must pass.
Per the approved arm policy (§14 D-10, below), arming additionally
depends on the ArmPolicy mode — including, where applicable, human or
delegate approval:

```
ArmPolicy (config) ∈ {AUTO, SEMI, WEBHOOK}   [DD→D-10]
    AUTO     — no human approval: a Level arms automatically the
               moment all §8 gates pass.
    SEMI     — the Level enters AWAITING_ARM after all §8 gates pass;
               it arms only on explicit operator approval; if
               ArmRequestTimeoutSeconds elapses → cancel, return to
               IDLE/PRECHECK (logged). Timeout NEVER auto-executes.
    WEBHOOK  — an external approving service must approve within
               ArmRequestTimeoutSeconds; timeout or error →
               fail-closed (IDLE/PRECHECK). A webhook failure NEVER
               converts to auto-approval. Operator identity = service
               identity, recorded per request.

Approved defaults (§14 D-10): Testnet = AUTO (fast testing);
Live = SEMI (human confirmation).
ArmRequestTimeoutSeconds = 30 (required configuration for SEMI/WEBHOOK).
```

**Arm-gate invariants (hold under EVERY ArmPolicy) `[UR, D-10]`:**

1. The arm gate NEVER applies to `EXPOSURE_CORRECTION_INTENT` — hedge/survival paths are never gated on human or service latency (§11.2 acute branch, §13.3).
2. The arm gate NEVER overrides FREEZE — Freeze blocks `ENTRY_INTENT` regardless of approval state (§13.3).
3. Human/delegate approval is an **additional** gate — it can only further restrict arming, never bypass any §8 gate or §10 economics floor.
4. Every arm request, approval, denial, and expiry is persisted with identity and timestamp — §15 invariant 19 (reconstructability) extends to the arm workflow.
5. `ArmRequestTimeoutSeconds` is a required configuration value — UNSET keeps all arming BLOCKED (fail-closed).

```
1. Order-book depth at target price ≥ MinDepthMultiple (approved
   default 10; §14 D-09 Group D) × order size
2. Distance-to-market within the approved sane band:
   DistanceBand = [StepBps/2, 10 × StepBps] (approved default
   [5, 100] bps when StepBps = 10; §14 D-09 Group D)
3. Order size ≥ asset minimum `[HC]`
4. Margin available ≥ required initial margin + MarginSafetyBuffer
   (approved default 0.20 × required initial margin; §14 D-09 Group D)
5. Exposure caps (§7.3) not exceeded
6. Open-order count has headroom below Hyperliquid's per-account cap
   (`[HC]` default ~1000; reduce-only/trigger orders rejected above that
   threshold, so exposure caps must preserve headroom specifically for
   hedge orders)
7–8. Price/size normalized (§6.3)
9. Market/Basket not in FREEZE/ERROR/RECOVERY
10. `[DD, §33.1 of roadmap]` Cost Analyzer: NetExpectedEdge >
    NetExpectedEdgeFloor (approved default StepBps/10 = 1 when
    StepBps = 10; §14 D-09 Group D) (see §10)
```

Any gate failure → Level stays `IDLE`/`PRECHECK`, logged, not an error state.

**Generation-state arming rule `[UR, DD]`:** Levels of a `DISABLED_AT_CYCLE_99` Generation can never arm `ENTRY_INTENT` orders. `EXPOSURE_CORRECTION_INTENT` orders (§13.3) are exempt from gate 9's FREEZE block and from this progression prohibition, but pass every other gate `[DEFINED]`.

**Fillability Analyzer** `[DD]`: walks live L2 book from best price outward, computes VWAP-execution-price slippage for the order's size; explicitly a *snapshot estimate*, not a guarantee — defense-in-depth via (1) gating arming, (2) `Ioc` pricing when immediate execution matters, (3) `POSITION_VERIFIED` reconciliation catching any bad estimate, (4) Level Skip as a safe fallback.

---

## 9. Emergency Execution & Level Skip

### 9.1 Emergency Execution `[SD principle, DD mechanism]` `[DEFINED]`

Replaces GridEA's unbounded Market-Order catch-up. Triggered when a pending order's trigger fires but doesn't fill within the bounded wait `EmergencyBoundedWaitSeconds = 30` s (approved value; §14 D-09 Group A):

```
tolerance := EmergencyTolerance = 0.005 × (10000 / Leverage_effective)
               bps [DYNAMIC — CALIBRATION PENDING]
               (derivation and status: §16, D-16 — e.g.
               Leverage_effective = 2 → 25 bps, 3 → 17 bps,
               5 → 10 bps; auto-tightens at higher leverage)
Breach of the wait bound is alerted as part of the standard
three-layer breach response (Alert → Soft Protective Action →
Operator Decision, §12.1).
band := [TargetPrice × (1−tolerance), TargetPrice × (1+tolerance)]
IF Fillable(size, side, tolerance) AND best executable price within band
   AND NetExpectedEdge (§10) clears the configured floor:
       submit Ioc at the tolerance-band edge (never unbounded market order)
ELSE: → LEVEL_SKIPPED
```

Hard invariant: never chase price beyond `tolerance`, and never accept a fillable-but-uneconomic fill.

### 9.2 Maker→Taker re-evaluation `[UR, corrects an earlier draft's implied two-branch escalation]` `[DEFINED]`

At timeout, the system performs a genuine four-way re-evaluation, not an automatic maker-to-taker escalation:

```
WAIT    — maker path's NetExpectedEdge still positive; extend the wait
Ioc     — taker path justified AND within tolerance band
REPRICE — neither justified at current price, but a repriced Alo order
          (closer to market, still non-crossing) would be — cancel and
          re-arm rather than force a taker fill
SKIP    — none justified
```

### 9.3 Level Skip Model `[SD principle, DD formalization]` `[DEFINED]`

`LEVEL_SKIPPED` is a first-class terminal state, not an error: per-level (never blocks or holds subsequent levels), no automatic retry within the same Cycle, contributes zero exposure and zero PnL, may recur naturally in a future Cycle/Generation at a new reference price but the specific skipped instance is never resurrected or retroactively filled.

---

## 10. Execution Economics `[UR]` `[DEFINED]`

```
NetExpectedEdge(path) :=
    GrossGridEdge(level, bps)
    − Fee(path)                    [`[HC]` pulled live from userFees —
                                     Tier-0 base ≈ taker 0.045%, maker
                                     0.015%, but NEVER hardcoded; moves
                                     with volume tier/staking/promotions]
    − EstimatedSlippage(path)      (Fillability Analyzer, §8)
    − FundingCostEstimate(holding_period)
    − OtherExecutionCosts(path)

Path selection:
    Normal Level arming → prefer MAKER (Alo) — lower fee, and Alo's
        reject-instead-of-cross semantics mean it can never accidentally
        take
    Emergency Execution/Hedge only → TAKER (Ioc) — fill certainty is
        the point
    floor := NetExpectedEdgeFloor (approved default StepBps/10 = 1 when
        StepBps = 10; §14 D-09 Group D)
    NetExpectedEdge ≤ floor (either path) → do not arm / do not attempt
        (§9.3 Skip applies)
```

A Level that is fillable but not economically justified is skipped for the same reason an unfillable one is — capital preservation governs over fill-chasing.

---

## 11. Hedge & Mirroring

### 11.1 Expected vs. Actual Exposure `[SD principle, DD formalization]` `[DEFINED]`

```
ExpectedExposure(Basket) := Σ over Levels in {PARTIALLY_FILLED, FILLED,
    POSITION_VERIFIED} of their VERIFIED filled quantity (not requested_qty)
ActualExposure(Basket) := net position size from clearinghouseState/
    webData2 ONLY — never derived from local order bookkeeping
ExposureDelta := ExpectedExposure − ActualExposure
```

Classification of a nonzero delta (normal/transient/escalate) and priority ordering (extended in v2.0 with the v2.0 transition classes; ordering is total and deterministic, consistent with §4.7):

```
POSITION VERIFICATION (continuous, underlies everything)
    ↓ feeds
RISK / EXPOSURE PROTECTION (classify ExposureDelta)
    ↓ if unresolved
HEDGE RECOVERY (permitted even under FREEZE — tagged
    EXPOSURE_CORRECTION_INTENT, distinct from ENTRY_INTENT)
    ↓ only once |ExposureDelta| ≤ ExposureTolerance
CYCLE-LIMIT DISABLE TRANSITION (§5.3)
    ↓
GRID EXECUTION → GENERATION EVOLUTION (§4.1) → CYCLE CREATION (§5.2)
```

Grid progression is hard-gated on exposure being within tolerance — not a soft preference.

### 11.2 Hedge cost-awareness `[UR]` `[DEFINED]`

```
IF risk of leaving ExposureDelta unresolved is ACUTE (approaching
   maintenance margin, or beyond MaxExposureImbalance §12.1):
       hedge immediately via Ioc regardless of cost — unconditional
ELSE:
       evaluate via §10's NetExpectedEdge model; prefer a maker-side
       correction when risk isn't acute enough to justify the taker spread
```

### 11.3 Mirroring `[SD, re-scoped]` `[DEFINED]`

GridEA's Mirroring is narrowly a symmetric hedge-pair (SU1/BL1) trigger-price adjustment. Re-scoped as one input into the Hedge Layer (§11.1), Basket-scoped (not Generation-scoped), driven by verified cumulative fill (recomputes on every incremental partial fill, not just 0%/100%):

```
Mirror Event (opposite hedge leg fired)
    → recompute opposite leg's trigger/target price (symmetric formula)
    → produces a Mirror INTENT (updated target price), not an immediate order
    → the updated level re-enters the NORMAL Pending Order Architecture
      (§8) and Cost Analyzer (§10) gates before any order is placed —
      Mirroring never bypasses precheck/liquidity/precision/exposure/
      economics/reconciliation
```

**Eligibility `[UR, DD]`:** Mirroring for protection remains available for `ACTIVE`, `SUCCESSOR_CREATED`, and `DISABLED_AT_CYCLE_99` Generations; it never creates `ENTRY_INTENT` orders.

### 11.4 Partial fill ↔ hedge interaction `[DD]` `[DEFINED]`

While a Level sits `PARTIALLY_FILLED`: exposure contribution = verified filled quantity so far; Mirroring recomputes on every incremental fill; the unfilled remainder is not independently hedged while still actively working within its normal timeout (not-yet-exposure); only once the remainder times out into Emergency Execution (§9.1) does it become subject to tolerance/economics/Skip — a skipped residual permanently contributes zero, requiring no hedge for exposure that was never taken.

---

## 12. Risk Model

### 12.1 Range Survivability `[UR]` `[DEFINED]` `[DD→D-09 Group B, extended D-16]`

A ranging market must degrade gracefully, not corrupt state or produce catastrophic drawdown. Continuously monitored, Basket-scoped bounds with **approved values and formulas (§14 D-09 Group B)**.

**Approved breach-response pattern (applies to EVERY bound below):** breach of any bound follows the three-layer response — **(1) Alert** (persisted, with identity and timestamp), **(2) Soft Protective Action** (the least-aggressive intervention that addresses the breach — typically Hedge Recovery per §11.1, order-cancellation, or arming suspension), **(3) Operator Decision** (the system never auto-terminates on a Group B breach; escalation beyond the soft action is a human decision). Calibration-proposed changes to these bounds are **proposal-only** — they are never applied automatically (§14 D-09 Group E: Group B is not calibratable).

```
MaxRangeInducedDD    — DD attributable to range-churn specifically,
                        tracked separately from directional-move DD.
                        APPROVED value: 100% of Basket equity, i.e.
                        total basket loss — the bound is reached only
                        when the Basket's equity is fully consumed.
MaxExposureImbalance — |ExposureDelta| bound forcing unconditional
                        Hedge Recovery (§11.2's acute branch).
                        Base-asset quantity. DYNAMIC default (D-16):
                        (0.25 × 0.5 / Leverage_effective) ×
                        NotionalPerLevel / MarkPrice, where
                        NotionalPerLevel := MaxBasketNotional /
                        GridLevels [DYNAMIC — CALIBRATION PENDING]
                        (derivation and status: §16, D-16).
MaxExecutionCost     — cumulative fees+slippage bound. APPROVED
                        dynamic rule: 30% of BasketNetPnL when
                        BasketNetPnL > 0; 100 bps of MaxBasketNotional
                        when BasketNetPnL ≤ 0 (the two-regime form
                        resolves the previously-open denominator
                        question).
MaxFailedLevelRate   — fraction of Levels reaching SKIPPED. APPROVED
                        value: 5%. APPROVED window: ALL Levels of the
                        ACTIVE Basket (not a rolling time window).
                        Sustained breach → Market Selection
                        re-evaluation at next Basket INITIALIZING.
MaxHedgeCost         — cumulative Emergency Hedge cost. APPROVED
                        default: 2% of MaxBasketNotional. High value
                        under range conditions signals mistuned
                        confirmation/exposure tolerance for current
                        volatility regime.
MaxBasketNotional    — APPROVED formula (§14 D-09 Group B; primary
                        mechanical control against range-induced
                        state corruption; restated from §7.3):

    MaxBasketNotional := min(
        Leverage_effective × CapitalBase × (1 − HedgeReserveRatio),
        MaxSafeNotional_margin,
        k_liquidity × MarketDepth )

    Input definitions (D-13 — every input is fully defined):
    Leverage_effective     = min(Leverage_user, MaxLeverage_asset)
    Leverage_user          = 3  (fixed owner choice, D-13)
    CapitalBase            = account equity including unrealized PnL,
                             read from clearinghouseState accountValue
                             at computation time (D-13)
    MaxSafeNotional_margin = CapitalBase × Leverage_effective / 2
                             (D-13; the divisor 2 keeps the
                             margin-account liquidation distance at
                             ≈ half the 3×-leverage distance —
                             see §16's margin mechanics)
    HedgeReserveRatio      = 0.10  (approved, D-09 Group B)
    k_liquidity            = 0.10  (approved, D-09 Group B)
    MarketDepth            = sum of USD bid+ask book depth within
                             ±(10 × StepBps) of mid at computation
                             time (D-13; matches the DistanceBand
                             upper bound, §8)

    Computed ONCE to produce the proposed value; the confirmed value
    is binding and the formula is NOT re-executed while the system
    runs (§14 global rule).

    Worked example (defaults; illustrative inputs):
    CapitalBase = 20,000 USD equity, Leverage_user = 3 →
    Leverage_effective = min(3, 40) = 3;
    term1 = 3 × 20,000 × (1 − 0.10) = 54,000 USD;
    MaxSafeNotional_margin = 20,000 × 3 / 2 = 30,000 USD (binding);
    MarketDepth = 500,000 USD → third term = 50,000 USD;
    MaxBasketNotional = min(54,000, 30,000, 50,000) = 30,000 USD.
```

Explicit goal: these bounds do not guarantee profitability in a range — they guarantee a range cannot force an unrecoverable state.

### 12.2 Two-Layer framing (restated) `[UR/DD]` `[DEFINED]`

Hedge Layer seeks symmetry, has override authority; Profit Layer may be asymmetric, is bounded by Hedge Layer's exposure caps and never overrides them. §11.1's priority ordering is the formal boundary between the two.

**Risk precedence over the closure target `[UR, Amendment §8]`:** if risk becomes acute before the Basket net-profit closure target is reached, Hedge Layer authority, Freeze, Recovery, and emergency closure rules take precedence over waiting for profit. The net-profit target is not permission to tolerate unrecoverable exposure `[DEFINED]`.

---

## 13. Basket Lifecycle

### 13.1 PnL `[SD principle, extended]` `[DEFINED]`

```
BasketNetPnL = BasketRealizedPnL + BasketUnrealizedPnL
               − BasketFees + BasketFunding
```

**NET, never gross, controls every lifecycle decision** (restart target, freeze trigger, closure target §13.4). Gross retained only as an observability metric — funding is not the negligible background cost MT5 swap was in GridEA's model.

### 13.2 States `[SD]` `[DEFINED]`

```
INITIALIZING → ACTIVE → FREEZE_REQUESTED → FREEZING → FROZEN
    → RESTARTING → (new Basket) → INITIALIZING
                  ↓                    ↓
                ERROR ⇄ RECOVERY      CLOSED
```

### 13.3 Freeze `[SD principle, DD resolution]` `[DEFINED]`

During FROZEN: no new Levels/Cycles/Generations. Every order is tagged `ENTRY_INTENT` or `EXPOSURE_CORRECTION_INTENT` at creation; FREEZE blocks only the former. An opposite-direction hedge is `EXPOSURE_CORRECTION_INTENT` even without `reduceOnly=true`, classified by projected `ExposureDelta` before/after, not by the exchange's reduce-only flag alone.

### 13.4 Closure `[SD principle extended, UR: not atomic]` `[DEFINED]`

**Closure preconditions (both required for a profit-target closure `[UR]`):**

```
(a) BasketNetPnL ≥ BasketNetProfitClosureTarget. Approved formula
    (§14 D-06):

        BasketNetProfitClosureTarget
            = 3 × (TotalSystemCosts + StepBps_as_USD)
        StepBps_as_USD = StepBps × MaxBasketNotional / 10000

    TotalSystemCosts includes maker+taker fees, slippage, hedge cost,
    funding, closing costs, and all other execution costs, accumulated
    over the Basket's LIFETIME-TO-DATE — from Basket INITIALIZING to
    the evaluation instant (D-15). The formula is used ONCE to compute
    the proposed value; the confirmed value is binding and the formula
    is NOT re-executed while the system runs (§14 global rule). Final
    value confirmed by the Strategy Owner at first eligibility.
    Worked example (illustrative inputs): TotalSystemCosts = 90 USD,
    StepBps = 10, MaxBasketNotional = 30,000 USD →
    StepBps_as_USD = 10 × 30,000 / 10000 = 30 USD →
    BasketNetProfitClosureTarget = 3 × (90 + 30) = 360 USD.
(b) residual ActualExposure ≤ ResidualExposureToleranceAtClosure.
    Approved form (§14 D-07): the tolerance is DERIVED, not fixed:

        ResidualExposureToleranceAtClosure
            := round_to_min_tradable_size(
                   f(StepBps, MaxBasketNotional) )

    Functional form (D-07(F), approved):
        f := (StepBps × MaxBasketNotional / 10000) / GridLevels
    — one grid step's USD notional divided across the level count —
    resolved onto the asset's minimum-tradable-size grid (szDecimals,
    §6.3). Exact zero may be unreachable given szDecimals rounding;
    this derivation is the motivation for a small non-zero tolerance.
    Worked example (defaults; BTC at 100,000 USD, szDecimals = 5):
    f = (10 × 30,000 / 10000) / 6 = 5 USD → 0.00005 BTC.
```

**Closure sequence (verified state machine; never equivalent to "close order submitted"):**

```
stop new Profit Layer progression
→ cancel resting progression orders
→ reconcile authoritative state
→ protect or correct acute exposure (Hedge Recovery if required)
→ close positions (per BasketCloseMode)
→ reconcile fills and actual position state
→ verify residual exposure within tolerance (D-07(F), defined)
→ verify BasketNetPnL has reached the closure target (D-06)
→ mark Basket CLOSED only after ALL required conditions pass
```

Gross PnL MUST NOT substitute for the configured net-profit target `[UR]`.

**Indefinite management rule `[UR]`:** if the net-profit target has not been reached and no acute risk exists, the Basket — including any `DISABLED_AT_CYCLE_99` Generations — remains open for management indefinitely. It MUST NOT resume forbidden Profit Layer progression merely because the Basket remains open. Hedge Recovery and exposure-correction actions remain permitted when required for survivability.

```
BasketCloseMode (config) `[DD]`:
    IMMEDIATE_IOC — every leg via bounded-tolerance Ioc; fastest,
        highest worst-case slippage
    TWAP          — legs above a threshold via Hyperliquid's native
        TWAP `[HC]` (parent order sliced ≥30s intervals, ≤3%
        per-suborder slippage); TWAP parent → child fills → actual
        position → remaining quantity is tracked explicitly, never
        assumed closed on submission
    HYBRID (default) — per-leg classification by size vs. book depth
```

Every leg, regardless of mode, passes Fillability Analyzer gating and `POSITION_VERIFIED` confirmation before being counted closed.

---

## 14. Parameter Reference

Every parameter in this document with its binding value or formula, unit, defining section, and calibration status. Numeric values are never invented by the implementation: formulas are used ONCE to compute the proposed value, which the Strategy Owner confirms or rejects; once confirmed the value is binding and the formula is not re-executed while the system runs.

> **Global rule (approved; applies to every value and formula in this document):** All values and formulas in this document are for **proposal to the Strategy Owner only**. Formulas are used **once** to compute the proposed value. The proposed value is confirmed or rejected by the Strategy Owner. Once confirmed, the value is **binding** until (i) the owner requests a change, or (ii) the system shuts down (automatic or manual). While the system continues its loop, confirmed values are treated as correct — the formula is **not** re-executed. Formulas never change values automatically.

**Calibration-status vocabulary:**

```
FIXED                             — structural/owner choice; not calibratable
CALIBRATABLE                      — in the optimizer allowlist (Group E below);
                                    the confirmed value is binding
[TEMPORARY — CALIBRATION PENDING] — derived default; overridable by the
                                    owner at any time; superseded by
                                    calibration + owner confirmation (§16);
                                    historical — replaced by D-16
[DYNAMIC — CALIBRATION PENDING]   — derived dynamic formula over
                                    parameters already defined in this
                                    document (D-16); no new free
                                    parameters; overridable by the owner
                                    at any time; superseded by
                                    calibration + owner confirmation (§16)
[DYNAMIC-CALIBRATABLE]            — derived dynamic formula, calibratable
                                    (D-17); proposal-only per the §14
                                    global rule (§5.4.1)
DERIVED                           — computed from other parameters;
                                    never independently configured
```

**Lifecycle & evolution**

| Parameter | Value | Unit | Defined in | Calibration status |
|-----------|-------|------|------------|--------------------|
| `EvolutionConfirmationSeconds` | 60 | s | §4.2 (D-03) | CALIBRATABLE |
| `MaxGenerations` | 99 | count | §3 (D-08) | FIXED |
| `MaxCyclesPerGeneration` | 99 | count | §3 (D-08) | FIXED |

**Grid geometry (§7)**

| Parameter | Value | Unit | Defined in | Derived from | Calibration status |
|-----------|-------|------|------------|--------------|--------------------|
| `StepBps` | 10 | bps | §7.1 (D-09 C) | — | CALIBRATABLE |
| `GridLevels` | 6 | count | §7.1 (D-09 C) | — | FIXED — NOT calibratable |
| `FirstLevelDistanceBps` | 2 × StepBps = 20 | bps | §7.1 (D-09 C) | — | CALIBRATABLE (formula-fixed default) |
| `ReferencePriceToleranceBps` | 0.33 × StepBps — e.g. StepBps = 10 → 3.3 bps; 5 → 1.65; 20 → 6.6 | bps | §5.4.1 (D-17) | StepBps (§7.1) | [DYNAMIC-CALIBRATABLE] |
| `Gen2DistanceMultiplier` | 2 (range 1.1–2.0) | ratio | §7.1 (D-09 C) | — | CALIBRATABLE |
| `WeakSideFirstLevelMultiplier` | 2 | ratio | §7.1 (D-09 C) | — | CALIBRATABLE |
| `Gen2SizeMultiplier` | 1.5 | ratio | §7.1 (D-09 C) | — | CALIBRATABLE |
| `CycleReferenceDerivation` | TERMINAL_EXECUTION (default of the four §5.4 options) | policy | §5.4 | — | FIXED |

**Arming & order gates (§8)**

| Parameter | Value | Unit | Defined in | Calibration status |
|-----------|-------|------|------------|--------------------|
| `PendingArmDistance` | 5 × StepBps = 50 | bps | §8 (D-09 D) | CALIBRATABLE |
| `MinDepthMultiple` | 10 | ratio | §8 (D-09 D) | CALIBRATABLE |
| `DistanceBand` | [StepBps/2, 10 × StepBps] = [5, 100] | bps | §8 (D-09 D) | CALIBRATABLE |
| `MarginSafetyBuffer` | 0.20 × required initial margin | fraction | §8 (D-09 D) | CALIBRATABLE |
| `NetExpectedEdgeFloor` | StepBps / 10 = 1 | bps | §8/§10 (D-09 D) | CALIBRATABLE |
| `ArmPolicy` | {AUTO, SEMI, WEBHOOK}; default Testnet = AUTO, Live = SEMI | policy | §8 (D-10) | FIXED |
| `ArmRequestTimeoutSeconds` | 30 | s | §8 (D-10) | FIXED (required for SEMI/WEBHOOK) |

**Execution & emergency (§9, §10)**

| Parameter | Value | Unit | Defined in | Derived from | Calibration status |
|-----------|-------|------|------------|--------------|--------------------|
| `EmergencyTolerance` | 0.005 × (10000 / Leverage_effective) — e.g. 2→25, 3→17, 5→10 | bps | §9.1 (D-09 A → D-16) | Leverage_effective (§12.1) | [DYNAMIC — CALIBRATION PENDING] (§16) |
| `EmergencyBoundedWaitSeconds` | 30 | s | §9.1 (D-09 A) | — | FIXED |

**Exposure & risk bounds (§7.3, §11, §12.1)**

| Parameter | Value | Unit | Defined in | Derived from | Calibration status |
|-----------|-------|------|------------|--------------|--------------------|
| `ExposureTolerance` | (0.001 × StepBps / 10) × NotionalPerLevel / MarkPrice, NotionalPerLevel = MaxBasketNotional / GridLevels — e.g. 0.00005 BTC at defaults | base-asset quantity | §5.2/§11.1 (D-09 A → D-16) | StepBps (§7.1), MaxBasketNotional (§12.1), GridLevels (§7.1), MarkPrice (live) | [DYNAMIC — CALIBRATION PENDING] (§16) |
| `MaxExposureImbalance` | (0.25 × 0.5 / Leverage_effective) × NotionalPerLevel / MarkPrice, NotionalPerLevel = MaxBasketNotional / GridLevels — e.g. 0.00208 BTC at defaults (3×) | base-asset quantity | §11.2/§12.1 (D-09 A → D-16) | Leverage_effective (§12.1), MaxBasketNotional (§12.1), GridLevels (§7.1), MarkPrice (live) | [DYNAMIC — CALIBRATION PENDING] (§16) |
| `MaxRangeInducedDD` | 100% of Basket equity (total basket loss) | % of equity | §12.1 (D-09 B) | — | FIXED — NOT calibratable |
| `MaxExecutionCost` | 30% of BasketNetPnL when BasketNetPnL > 0; 100 bps of MaxBasketNotional when BasketNetPnL ≤ 0 | two-regime (fraction / bps) | §12.1 (D-09 B) | BasketNetPnL (§13.1), MaxBasketNotional (§12.1) | FIXED — NOT calibratable |
| `MaxFailedLevelRate` | 5%, window = ALL Levels of the ACTIVE Basket | % of Levels | §12.1 (D-09 B) | — | FIXED — NOT calibratable |
| `MaxHedgeCost` | 2% of MaxBasketNotional | % of USD notional | §12.1 (D-09 B) | MaxBasketNotional (§12.1) | FIXED — NOT calibratable |
| `MaxBasketNotional` | min(Leverage_effective × CapitalBase × (1 − HedgeReserveRatio), MaxSafeNotional_margin, k_liquidity × MarketDepth); inputs defined at the formula (D-13): Leverage_user = 3, CapitalBase = account equity incl. unrealized PnL (clearinghouseState accountValue), MaxSafeNotional_margin = CapitalBase × Leverage_effective / 2, MarketDepth = bid+ask depth within ±(10 × StepBps) of mid, HedgeReserveRatio = 0.10, k_liquidity = 0.10 | USD notional | §12.1 (D-09 B + D-13) | inputs defined at the formula itself (D-13) | DERIVED — computed once, then binding |
| `MaxLevelNotional` | MaxBasketNotional / GridLevels | USD notional | §7.3 | MaxBasketNotional (§12.1), GridLevels (§7.1) | DERIVED |
| `MaxLevelNotionalDominant` | Gen2SizeMultiplier × (MaxBasketNotional / GridLevels) | USD notional | §7.3 (D-12) | Gen2SizeMultiplier (§7.1), MaxBasketNotional (§12.1), GridLevels (§7.1) | DERIVED |
| `MaxCycleNotional` | MaxBasketNotional / MaxActiveCycles; MaxActiveCycles = count of all Cycles of the counted Generations not yet closed as part of the Basket, incl. COMPLETED (D-14) | USD notional | §7.3 (D-14) | MaxBasketNotional (§12.1), MaxActiveCycles (D-14 count) | DERIVED |
| `MaxGenerationNotional` | MaxBasketNotional / MaxActiveGenerations; MaxActiveGenerations = count of all Generations not yet CLOSED_ONLY_AS_PART_OF_BASKET, incl. DISABLED_AT_CYCLE_99 (D-14) | USD notional | §7.3 (D-14) | MaxBasketNotional (§12.1), MaxActiveGenerations (D-14 count) | DERIVED |

**Basket closure & economics (§13)**

| Parameter | Value | Unit | Defined in | Calibration status |
|-----------|-------|------|------------|--------------------|
| `BasketNetProfitClosureTarget` | 3 × (TotalSystemCosts + StepBps_as_USD); StepBps_as_USD = StepBps × MaxBasketNotional / 10000; TotalSystemCosts = approved cost set (maker+taker fees, slippage, hedge cost, funding, closing costs, all other execution costs) accumulated lifetime-to-date (D-15) | USD | §13.4 (D-06) | DERIVED — computed once at first eligibility, owner-confirmed, then binding |
| `ResidualExposureToleranceAtClosure` | round_to_min_tradable_size(f), f = (StepBps × MaxBasketNotional / 10000) / GridLevels (D-07(F)) | USD notional → resolved to base-asset size (szDecimals, §6.3) | §13.4 (D-07) | DERIVED |
| `BasketCloseMode` | HYBRID (default of the three §13.4 options) | policy | §13.4 | FIXED |

**Calibration allowlist (D-09 Group E):** Group A rows — all CALIBRATABLE. Group C rows — all CALIBRATABLE except `GridLevels`. Group D rows — all CALIBRATABLE. Group B rows — NOT calibratable (proposal-only). The four dynamic defaults of §16/§5.4.1 — D-16: `EmergencyTolerance`, `ExposureTolerance`, `MaxExposureImbalance`; D-17: `ReferencePriceToleranceBps` — are calibratable and are the priority calibration targets.

**Units:** bps are dimensionless ratios (× 10⁻⁴); base-asset quantities are in the asset's `szDecimals` precision (§6.3); USD notionals are absolute USD; durations are seconds; counts are integers.

---

## 15. State Machine Invariants

**Core invariants `[DD]` (carried from v1.0, §-references updated):**

Level FILLED ⇔ Order Fill ∧ Position Delta Verified · Actual Exposure only from authoritative exchange state · Expected Exposure never treated as Actual · Grid progression blocked while ExposureDelta exceeds tolerance, unless Hedge Recovery is the active transition · Emergency execution cannot exceed EmergencyTolerance · Every order has a persistent unique client identifier (`cloid`), persisted BEFORE network submission · Price/size normalized before signing · Maker/Taker decisions account for actual execution economics (§10) · Taker execution never occurs solely because a maker order timed out (§9.2) · Mirror Intent always passes normal execution validation (§11.3) · Basket CLOSED requires verified residual exposure within tolerance AND the net-profit closure precondition where applicable (§13.4) · Evolution cannot be triggered by an unverified price crossing · Cycle transition must not create unintended level overlap (computable test: §5.6) · GenerationID/CycleID are independent internal fields, never encoded together · Range oscillation must not inherently corrupt the state machine · Hedge symmetry and profit asymmetry are separate concepts · Profit asymmetry permitted only inside the Basket risk/DD envelope · Basket economic decisions use NET PnL · A skipped level is preferable to an unsafe or economically irrational execution · A slower verified transition is preferable to a fast unverified one · Human-readable identity remains deterministic (`G{GenerationID:02d}-C{CycleID:02d}-{Direction}{LevelID:02d}`) · No state transition depends solely on intended orders · Every state transition is reconstructable from persisted state and authoritative exchange events.

**Invariants added by the Generation/Cycle Continuation Amendment `[UR, DD]` (numbering added here only for the amendment set; base invariants remain unnumbered prose above):**

1. `CycleID` is always in `0..99` (and always below the effective limit).
2. `GenerationID` is always in `0..99` (and always below the effective limit).
3. No Cycle 100 may ever be created.
4. No Generation 100 may ever be created.
5. Terminal-level reach creates a new Cycle in the same Generation when CycleID < the effective limit.
6. Terminal-level reach alone does not create a new Generation.
7. A path-dependent verified return may create a successor Generation only when the Generation is eligible.
8. Each Generation may create at most one successor before its Cycle-limit boundary. With `MaxGenerations = 99` and `MaxCyclesPerGeneration = 99` (§14 D-08), the one-successor rule spans the full lifecycle: a parent Generation has exactly one child — ever — across all of its Cycles; it may continue its own Cycle progression after creating that child, but the successor lock is permanent for that Generation `[DEFINED, D-08]`.
9. After a Generation creates a successor, later Cycles below the Cycle limit cannot create another successor from that Generation.
10. Reaching the Cycle limit disables the Generation's further Profit Layer progression.
11. `DISABLED_AT_CYCLE_99` does not mean the Generation's positions are closed.
12. A disabled Generation remains in Basket exposure, PnL, funding, fee, hedge, and reconciliation accounting.
13. Basket closure requires the approved net-profit target and the verified residual exposure condition.
14. Acute Hedge Recovery may override waiting for the net-profit target.
15. A raw price crossing, order acknowledgement, or isolated fill message cannot trigger Cycle completion or Generation creation.
16. GenerationID and CycleID remain independent fields.
17. Historical Cycles and Generations are never deleted, overwritten, or recycled.
18. An apparent Evolution after the one-successor lock is recorded as an ineligible Evolution candidate, not silently executed.
19. Every Generation/Cycle transition is reconstructable from persisted events and authoritative exchange observations.
20. No transition may bypass normal risk, exposure, fillability, economics, precision, and reconciliation gates.

---

## 16. Dynamic Defaults Pending Calibration

All owner decisions D-01…D-15 are resolved (§14). The only non-final values in this document are the four dynamic defaults below: the three derived dynamic formulas of D-16 and the D-17 reference-price tolerance (§5.4.1). They exist so the specification is complete and implementable; they are **explicitly temporary pending calibration** and are superseded by future offline calibration plus owner confirmation.

**Status and handling of the temporary defaults (binding on the implementation):**

1. Each is tagged `[DYNAMIC — CALIBRATION PENDING]` (D-16) or `[DYNAMIC-CALIBRATABLE]` (D-17) at every point of use (§5.2, §9.1, §12.1, §5.4.1) and in §14.
2. Each carries its derivation below, derived from Hyperliquid's actual contract mechanics — no number is invented.
3. They are listed here as **temporary defaults pending calibration**.
4. They are overridable by the Strategy Owner at any time (owner override requires no recalibration cycle).
5. They supersede the previous `[TEMPORARY — CALIBRATION PENDING]` defaults (D-16) and the previously ungated reference capture (D-17). The implementation MUST still treat them as dynamic: every read of a dynamic default is logged with its tag, and a run using dynamic defaults is distinguishable in the audit trail from a run using calibrated, owner-confirmed values.

**Hyperliquid contract mechanics used by the derivations** `[HC]`:

```
Maintenance margin = half of initial margin at max leverage.
Funding is paid hourly, at 1/8 of the 8-hour funding rate.
BTC/ETH max leverage = 40x → initial margin fraction 2.5%,
    maintenance margin fraction 1.25%.
At 3x effective leverage: initial margin fraction = 33.3%,
    maintenance margin fraction = 16.7% (half of 1/3);
    liquidation distance ≈ 16.7% (≈ 1670 bps) adverse move.
Mark price is used for margin accounting and liquidation triggers.
```

```
[DYNAMIC — CALIBRATION PENDING] (D-16)
EmergencyTolerance := 0.005 × (10000 / Leverage_effective) bps

    Inputs: Leverage_effective (§12.1, D-13).
    Examples: Leverage_effective = 2 → 25 bps;
              Leverage_effective = 3 → 16.7 bps (≈ 17);
              Leverage_effective = 5 → 10 bps.

    Derivation: 0.5% of the initial-margin distance
    (10000 / Leverage_effective bps), i.e. 1% of the liquidation
    buffer (the maintenance margin distance ≈ half the
    initial-margin distance, §16 mechanics above). Auto-tightens at
    higher leverage: a single emergency fill (§9.1) can never
    meaningfully erode the liquidation buffer at any configured
    leverage. Strictly tighter than the previous 50 bps temporary
    default at every configured leverage (50 bps corresponds to
    the old value only below Leverage_effective ≈ 1.1 — below any
    approved input). The band remains wide enough to permit a fill
    under normal volatility (on Hyperliquid, BTC's spread is ≈ 1 USD
    with deep book depth).

    Supersedes the 50 bps [TEMPORARY — CALIBRATION PENDING]
    default (D-16). Must be calibrated.
```

```
[DYNAMIC — CALIBRATION PENDING] (D-16)
ExposureTolerance := (0.001 × StepBps / 10) × NotionalPerLevel / MarkPrice
    where NotionalPerLevel := MaxBasketNotional / GridLevels

    Unit: base-asset quantity (the unit of ExposureDelta, §11.1).

    Inputs: StepBps (§7.1), MaxBasketNotional (§12.1), GridLevels
    (§7.1), MarkPrice (live).

    Derivation: tolerates the szDecimals rounding residue of a
    level-sized order (§6.3) plus fill-sequencing micro-variance —
    0.1% of a level's notional at the default StepBps, scaled
    linearly with StepBps (wider grids tolerate proportionally
    larger residue). Strictly tighter than the previous
    (0.1 × level) temporary default: 100× tighter at the defaults
    (0.00005 vs 0.005 BTC). Mutual ordering with the other dynamic
    defaults (ExposureTolerance < MaxExposureImbalance < one level)
    is stated and verified in the consistency note below.

    Worked example (defaults): BTC at MarkPrice = 100,000 USD,
    StepBps = 10, MaxBasketNotional = 30,000 USD, GridLevels = 6 →
    NotionalPerLevel = 5,000 USD → ExposureTolerance =
    0.001 × 5,000 / 100,000 = 0.00005 BTC — one minimum-lot
    equivalent on BTC (szDecimals = 5 on Hyperliquid).

    Supersedes the (0.1 × level) [TEMPORARY — CALIBRATION
    PENDING] default (D-16). Must be calibrated.
```

```
[DYNAMIC — CALIBRATION PENDING] (D-16)
MaxExposureImbalance := (0.25 × 0.5 / Leverage_effective)
                        × NotionalPerLevel / MarkPrice
    where NotionalPerLevel := MaxBasketNotional / GridLevels
          0.5 / Leverage_effective = MaintenanceMarginFraction

    Unit: base-asset quantity (the unit of ExposureDelta, §11.1).

    Inputs: Leverage_effective (§12.1), MaxBasketNotional (§12.1),
    GridLevels (§7.1), MarkPrice (live).

    Derivation: 25% of the maintenance margin buffer expressed as a
    level-notional fraction (0.5 / Leverage_effective is the
    maintenance margin fraction per the §16 mechanics above —
    maintenance margin = half of initial margin at max leverage
    [HC]). Auto-tightens at higher leverage: the maintenance
    fraction shrinks, so the acute hedge trigger (§11.2 acute
    branch, §12.1) fires before the buffer is meaningfully eroded.
    Strictly tighter than the previous (1.0 × level) temporary
    default: 24× tighter at the defaults (0.00208 vs 0.05 BTC).

    Worked example (defaults): same inputs as ExposureTolerance
    above, Leverage_effective = 3 → coefficient 0.25 × 0.5 / 3 =
    0.0417 → MaxExposureImbalance = 0.0417 × 5,000 / 100,000 =
    0.00208 BTC.

    Supersedes the (1.0 × level) [TEMPORARY — CALIBRATION
    PENDING] default (D-16). Must be calibrated.
```

**D-17 entry (dynamic, calibratable):** §5.4.1 `ReferencePriceToleranceBps = 0.33 × StepBps` — the reference-price tolerance at Cycle/Generation fire, tagged `[DYNAMIC-CALIBRATABLE]` (proposal-only per the §14 global rule). It composes with the three defaults above: it gates the reference capture upstream of ladder construction, while the §5.6 non-overlap test remains the authoritative structural check; the 0.33 coefficient is strictly below 1.0, so a captured reference can never drift a full step and pre-violate §5.6.

**Consistency note:** the three dynamic defaults are mutually coherent — the progression guard (§5.2) fires at 0.1% of a level (at the default StepBps), the acute hedge trigger (§11.2/§12.1) fires at ≈ 4.17% of a level (at 3× effective leverage), and the emergency band (§9.1) can never consume more than 1% of the liquidation buffer per fill. Mutual ordering (must hold at every input set): `ExposureTolerance < MaxExposureImbalance < NotionalPerLevel / MarkPrice` — guard < acute trigger < one full level. It holds at the default inputs and at `Leverage_effective ∈ {2, 3, 5}` and `StepBps ∈ {5, 10, 20}` (verified in `CALIBRATION-REPORT.md`); if it ever fails at a candidate input set, the failure is reported — coefficients are never adjusted silently. They also compose coherently with the derived D-07(F) closure tolerance (a fraction of one grid step, §13.4) and with the §5.4.1 reference-price tolerance (0.33 × StepBps — strictly below one step).

**Closed ledger (for traceability; every item resolved, none silent):**

```
v1.0 §4.4 OQ-BLOCKING (Evolution trigger topology) — closed since
     v2.0 in favor of the path-dependent rule (§4.1).
D-01  traversal-verified return level, deferred-not-cancelled (§4.1).
D-02  POSITION_VERIFIED strategy fill; hedge orders not eligible (§4.1).
D-03  EvolutionConfirmationSeconds = 60 + latching hysteresis (§4.2).
D-04  fail-closed on skipped/partial return (§4.1).
D-05  origin/traversed group is Dominant (§4.5).
D-06  BasketNetProfitClosureTarget = 3 × (TotalSystemCosts +
      StepBps_as_USD) (§13.4).
D-07  ResidualExposureToleranceAtClosure derived, functional form
      approved (D-07(F)) (§13.4).
D-08  MaxGenerations = 99, MaxCyclesPerGeneration = 99; one-successor
      rule across the full lifecycle (§3, §4.6).
D-09  Groups A–E approved; Group A remainder resolved by the three
      temporary defaults above.
D-10  ArmPolicy {AUTO, SEMI, WEBHOOK}; ArmRequestTimeoutSeconds = 30
      (§8).
D-11  REMOVED per owner decision; [SD] annotation in force
      document-wide (header note).
D-12  MaxLevelNotionalDominant derived cap (§7.3).
D-13  MaxBasketNotional inputs fixed (§12.1).
D-14  MaxActiveGenerations / MaxActiveCycles = all non-closed (§7.3).
D-15  TotalSystemCosts = lifetime-to-date (§13.4).
D-16  the three temporary defaults replaced by dynamic formulas
      over existing parameters — no new free parameters (§5.2,
      §9.1, §11.2/§12.1, §14, §16).
D-17  §5.4.1 reference-price tolerance at Cycle/Generation fire:
      0.33 × StepBps, fail-closed above tolerance (§5.4.1).
```

No other open items remain. The implementation must not invent a value for anything not in §14 `[UR]`.

---

*This document defines the strategy. It does not constitute an implementation plan (implementation proceeds through phased planning, testing, and adapter architecture defined separately) and does not authorize writing production trading code. This document does not authorize live trading. The four values tagged `[DYNAMIC — CALIBRATION PENDING]` (§16: the three dynamic formulas, D-16) or `[DYNAMIC-CALIBRATABLE]` (§5.4.1: the reference-price tolerance, D-17) are derived defaults, not calibrated constants: the implementation must log their use, and the Strategy Owner may override them at any time. Superseded project artifacts are archived in `history/` for traceability only and are non-authoritative.*
