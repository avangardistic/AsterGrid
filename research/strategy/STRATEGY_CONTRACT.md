# STRATEGY_CONTRACT.md

> **Authoritative source note (DECISION-002, 2026-09-21):** ActualExposure and CapitalBase MUST be read ONLY from clearinghouseState. webData2/webData3 MUST NOT be used as state authority anywhere in this program.
> **Historical UNVERIFIED notes:** two non-field `UNVERIFIED` strings remain in this file at the field-legend and the Phase-1 STEP-5 report. Both are historical prose, not live requirement statuses. All 17 [HC] requirement fields were resolved in Phase 2/2.5+2b.

- **Purpose:** Derived, traceable contract of every normative requirement in `Strategy.md` v2.3-final, each with a stable `STR-*` ID. This is a DERIVED artifact — `Strategy.md` remains the sole authority. No requirement here invents semantics; ambiguities are surfaced in the OPEN section, never guessed.
- **Version:** 1.0 (Phase 1)
- **Producer:** Claude Code (Opus 4.8), Phase 1 — Strategy Forensics.
- **Inputs:** `Strategy.md` (SRC-001, SHA-256 `085044e72efa75e7dd7e812588d8247c8e60152eecb233bd6969f6545a825e18`, 1368 lines (1-based; authoritative)); `prompt.md` (SRC-002) `<strategy_forensics>`, `<strategy_contract>`.
- **Source references:** every entry cites `strategy_section` + `source_lines` + verbatim `wording`.
- **Status:** COMPLETE for Phase 1 (343 requirements, STR-0001..STR-0343).
- **Validation status:** self-consistency checks reported at end (STEP 5). All `implementation_status`/`verification_status` = NOT_STARTED in Phase 1.

---

## Field legend (compact block format)

Each requirement is one block. Fields per the Phase-1 spec (none omitted; `NONE`/`N/A` where empty):
`section` · `lines` · `type` · `strength` (MUST/MUST_NOT/SHOULD/MAY) · `tag` (preserved verbatim) · `wording` (≤30-word verbatim quote) · `inputs` · `outputs` · `preconditions` · `postconditions` · `state_effects` · `formula` · `units` · `invariants` · `failure_behavior` · `safety_impact` (LOW/MEDIUM/HIGH/CRITICAL) · `dependencies` · `impl` (=NOT_STARTED) · `verif` (=NOT_STARTED).
Extra fields where required: `[HC]` → `venue_evidence_status: UNVERIFIED`; `[DYN]`/`[TEMP]` → `dynamic_note: must remain dynamic — never freeze to a constant`.

Tag semantics are exactly as recorded in `STRATEGY_SOURCE_RECORD.md` §4. Tags are NOT collapsed: `[DEFINED]` is a rule-status tag shown alongside content tags `[SD]/[UR]/[HC]/[DD]/[DYN]/[TEMP]/[OQ]`.

---

## §1 Executive Summary (L82–L94)

### STR-0001 — Hedge Layer seeks symmetry, has override authority
- section: §1 Executive Summary | lines: L86 | type: INVARIANT | strength: MUST | tag: [DD][DEFINED]
- wording: "A Hedge Layer that seeks symmetry — its only job is keeping verified exposure inside a configured envelope, with authority to override the profit layer"
- inputs: verified exposure; configured envelope | outputs: override signals to Profit Layer | preconditions: verified exposure available | postconditions: exposure kept within envelope | state_effects: Hedge Layer authority
- formula: NONE | units: NONE
- invariants: Hedge symmetry and profit asymmetry are separate concepts; Hedge Layer may override on risk boundary | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0199, STR-0231 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0002 — Profit Layer permitted asymmetric, bounded by Hedge constraints
- section: §1 Executive Summary | lines: L87 | type: INVARIANT | strength: MUST | tag: [DD][DEFINED]
- wording: "A Profit Layer that is permitted to be asymmetric … provided the hedge layer's constraints are respected."
- inputs: market state; hedge-layer constraints | outputs: grid geometry/timing/sizing decisions | preconditions: hedge constraints respected | postconditions: asymmetric grid within envelope | state_effects: grid placement
- formula: NONE | units: NONE
- invariants: Profit asymmetry permitted only inside Basket risk/DD envelope; never overrides Hedge Layer | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0001, STR-0231 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0003 — Grid organized as Basket → Generation → Cycle → Level
- section: §1 Executive Summary | lines: L88–L89 | type: IDENTITY_RULE | strength: MUST | tag: [SD][UR][DEFINED]
- wording: "The grid is organized as Basket → Generation → Cycle → Level … A Generation successor is created only by a verified, path-dependent traversal-and-return condition (§4.1), at most once per Generation"
- inputs: NONE | outputs: hierarchy of objects | preconditions: NONE | postconditions: 4-level containment hierarchy | state_effects: Basket/Generation/Cycle/Level objects
- formula: NONE | units: NONE
- invariants: terminal reach → new Cycle same Generation; verified return → new Generation; ≤1 successor per Generation | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0005, STR-0025, STR-0049 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0004 — Every order-state claim anchored on verified position delta
- section: §1 Executive Summary | lines: L91 | type: INVARIANT | strength: MUST | tag: [DD][DEFINED]
- wording: "Every order-state claim in this system is anchored on verified position delta, never on price-crossing or order-acknowledgement alone"
- inputs: order events; authoritative position reads | outputs: verified state claims | preconditions: authoritative position delta available | postconditions: no state claim from price/ack alone | state_effects: POSITION_VERIFIED gating
- formula: NONE | units: NONE
- invariants: LEVEL FILLED ⇔ ORDER FILLED ∧ POSITION DELTA VERIFIED | failure_behavior: fail-closed (no unverified claim) | safety_impact: CRITICAL
- dependencies: STR-0129, STR-0131 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §2 Strategy Model — Formal Definitions (L95–L148)

### STR-0005 — Basket definition (top-level container, one market at a time)
- section: §2 Strategy Model | lines: L98–L100 | type: LIFECYCLE_STATE | strength: MUST | tag: [DD][DEFINED]
- wording: "Basket … Top-level accounting/lifecycle container, one Hyperliquid perpetual market at a time. Exactly one active Basket per market."
- inputs: market selection | outputs: Basket object | preconditions: a chosen perpetual market | postconditions: exactly one active Basket per market | state_effects: Basket container
- formula: NONE | units: NONE
- invariants: exactly one active Basket per market | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: NONE | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0006 — Generation definition (strategic directional epoch; G0 at Basket creation)
- section: §2 Strategy Model | lines: L102–L108 | type: LIFECYCLE_STATE | strength: MUST | tag: [SD][UR][DEFINED]
- wording: "Generation … A strategic directional epoch, containing an ordered sequence of Cycles. Generation 0 exists at Basket creation. GenerationID ∈ [0, 99]"
- inputs: Basket creation; evolution events | outputs: Generation objects | preconditions: Basket exists | postconditions: Generation 0 exists at creation; IDs in [0,99] | state_effects: Generation object; ordered Cycle sequence
- formula: NONE | units: NONE (GenerationID: count)
- invariants: Generations never close individually — only the Basket closes them via §13.4; exposure/PnL remain in Basket | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0005, STR-0243 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0007 — Group definition (BU/SL directional halves, levels 1..N)
- section: §2 Strategy Model | lines: L110–L114 | type: IDENTITY_RULE | strength: MUST | tag: [SD][DEFINED]
- wording: "Group … One of the two directional halves of a Generation's ladder: BU (long) or SL (short), levels 1..N, N = GridLevels (config, default 6, hard architectural max 12)."
- inputs: GridLevels config | outputs: BU/SL groups | preconditions: Generation exists | postconditions: two groups each with levels 1..N | state_effects: group structure
- formula: NONE | units: N: count (default 6, max 12)
- invariants: N = GridLevels | failure_behavior: NONE | safety_impact: LOW
- dependencies: STR-0006, STR-0140 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0008 — Cycle definition (one traversal; C0 at Generation creation; CycleID ∈ [0,99] scoped to Generation)
- section: §2 Strategy Model | lines: L115–L119 | type: LIFECYCLE_STATE | strength: MUST | tag: [DD][UR][DEFINED]
- wording: "Cycle … One traversal of the active Generation's ladder … Cycle 0 exists at Generation creation. CycleID ∈ [0, 99], scoped to its Generation. A completed Cycle never changes its Generation."
- inputs: Generation creation; terminal events | outputs: Cycle objects | preconditions: Generation exists | postconditions: Cycle 0 exists; IDs in [0,99] scoped to Generation | state_effects: Cycle object
- formula: NONE | units: CycleID: count
- invariants: a completed Cycle never changes its Generation; Cycle axis independent of Generation axis | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0006 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0009 — Level definition (one priced, sized grid rung)
- section: §2 Strategy Model | lines: L121–L122 | type: IDENTITY_RULE | strength: MUST | tag: [SD][DEFINED]
- wording: "Level … One priced, sized grid rung (BUk/SLk) within one Cycle within one Generation."
- inputs: reference price; sizing | outputs: Level object | preconditions: Cycle exists | postconditions: level within Cycle within Generation | state_effects: Level object
- formula: NONE | units: NONE
- invariants: level belongs to exactly one Cycle+Generation+Direction | failure_behavior: NONE | safety_impact: LOW
- dependencies: STR-0008 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0010 — Reference Price definition (each Cycle and Generation computes its own)
- section: §2 Strategy Model | lines: L124–L126 | type: FORMULA | strength: MUST | tag: [SD][DEFINED]
- wording: "Reference Price … The price a Cycle's level distances are measured from. Every Cycle and every Generation computes its own."
- inputs: execution-grounded price capture (§5.4) | outputs: reference price | preconditions: Cycle/Generation fire | postconditions: per-Cycle/per-Generation reference stored | state_effects: reference price field
- formula: NONE (see STR-0091..0095) | units: price (USD)
- invariants: level distances measured from own reference | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0091 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0011 — Evolution definition (verified successor creation; NOT terminal-reach)
- section: §2 Strategy Model | lines: L128–L134 | type: EVENT_SEMANTICS | strength: MUST | tag: [UR][DEFINED]
- wording: "Evolution … The verified creation of a successor Generation after the path-dependent traversal-and-return condition (§4.1) … Evolution is NOT synonymous with terminal-level reach"
- inputs: §4.1 verified return condition | outputs: EvolutionTriggered event; new Generation | preconditions: §4.1 satisfied and confirmed | postconditions: new Generation created | state_effects: new Generation; EvolutionTriggered event
- formula: NONE | units: NONE
- invariants: terminal reach ≠ Evolution; only verified return creates a Generation | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0025, STR-0071 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0012 — Terminal Event definition (completes Cycle, creates successor Cycle same Generation)
- section: §2 Strategy Model | lines: L136–L138 | type: EVENT_SEMANTICS | strength: MUST | tag: [DD][UR][DEFINED]
- wording: "Terminal Event … The verified event that completes the current Cycle and creates a successor Cycle within the same Generation (§5.1)."
- inputs: terminal-level POSITION_VERIFIED | outputs: Cycle completion; successor Cycle | preconditions: terminal level verified | postconditions: new Cycle in same Generation | state_effects: Cycle transition
- formula: NONE | units: NONE
- invariants: successor Cycle stays in same Generation | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0071, STR-0074 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0013 — Successor Lock definition (Generation that created its one successor)
- section: §2 Strategy Model | lines: L140–L142 | type: LIFECYCLE_STATE | strength: MUST | tag: [UR][DEFINED]
- wording: "Successor Lock … The state of a Generation that has already created its one permitted successor Generation (§4.4)."
- inputs: successor creation event | outputs: locked state | preconditions: Generation created a successor | postconditions: no further successor from that Generation | state_effects: SUCCESSOR_CREATED / lock flag
- formula: NONE | units: NONE
- invariants: at most one successor per Generation | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0049 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0014 — Disabled Generation definition (DISABLED_AT_CYCLE_99, not closed)
- section: §2 Strategy Model | lines: L143–L146 | type: LIFECYCLE_STATE | strength: MUST | tag: [UR][DEFINED]
- wording: "Disabled Generation … no further Profit Layer progression, full accounting and protection eligibility retained, not closed until Basket closure (§13.4)."
- inputs: Cycle-limit reach | outputs: DISABLED_AT_CYCLE_99 state | preconditions: effective Cycle limit reached | postconditions: no progression; accounting/protection retained | state_effects: Generation state
- formula: NONE | units: NONE
- invariants: disabled ≠ closed; exposure fully live until Basket closure | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0084 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0015 — Naming: "Soft Reset" renamed "Evolution"; nothing resets
- section: §2.1 Naming | lines: L149–L154 | type: EVENT_SEMANTICS | strength: MUST | tag: [UR][DEFINED]
- wording: "'Reset' is rejected as a system-level term because nothing resets — old positions and old Generations survive … The event is EvolutionTriggered; the resulting object is a new Generation."
- inputs: NONE | outputs: terminology | preconditions: NONE | postconditions: term "Evolution" used; old objects survive | state_effects: naming/semantics
- formula: NONE | units: NONE
- invariants: old positions/Generations survive Evolution | failure_behavior: NONE | safety_impact: LOW
- dependencies: STR-0011 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §3 Canonical Identity Model (L155–L184)

### STR-0016 — Identity carried as independently-persisted fields, never a single encoded integer
- section: §3 Canonical Identity Model | lines: L155–L166 | type: IDENTITY_RULE | strength: MUST | tag: [UR][DEFINED]
- wording: "Every Level/Cycle/Generation object carries independently-persisted fields — never a single encoded integer"
- inputs: NONE | outputs: LevelIdentity{GenerationID,CycleID,Direction,LevelID} | preconditions: object creation | postconditions: fields persisted independently | state_effects: identity fields
- formula: NONE | units: NONE
- invariants: GenerationID/CycleID are independent internal fields, never encoded together | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: NONE | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0017 — GenerationID range 0–99 inclusive
- section: §3 Canonical Identity Model | lines: L161 | type: IDENTITY_RULE | strength: MUST | tag: [UR][DEFINED]
- wording: "GenerationID: uint   // 0–99 inclusive"
- inputs: NONE | outputs: GenerationID | preconditions: NONE | postconditions: 0≤GenerationID≤99 | state_effects: GenerationID field
- formula: NONE | units: count
- invariants: GenerationID always in 0..99 (and below effective limit) | failure_behavior: reject out-of-range | safety_impact: HIGH
- dependencies: STR-0016 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0018 — CycleID range 0–99 inclusive, scoped to its Generation
- section: §3 Canonical Identity Model | lines: L162 | type: IDENTITY_RULE | strength: MUST | tag: [UR][DEFINED]
- wording: "CycleID: uint   // 0–99 inclusive, scoped to its Generation"
- inputs: NONE | outputs: CycleID | preconditions: NONE | postconditions: 0≤CycleID≤99 per Generation | state_effects: CycleID field
- formula: NONE | units: count
- invariants: CycleID always in 0..99 (and below effective limit); scoped per Generation | failure_behavior: reject out-of-range | safety_impact: HIGH
- dependencies: STR-0016 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0019 — Direction {BU,SL}; LevelID 1..GridLevels scoped to Cycle+Direction
- section: §3 Canonical Identity Model | lines: L163–L164 | type: IDENTITY_RULE | strength: MUST | tag: [UR][DEFINED]
- wording: "Direction: {BU, SL} … LevelID: uint // 1–GridLevels, scoped to its Cycle+Direction"
- inputs: GridLevels | outputs: Direction, LevelID | preconditions: NONE | postconditions: LevelID in 1..GridLevels per Cycle+Direction | state_effects: identity fields
- formula: NONE | units: count
- invariants: LevelID scoped to Cycle+Direction | failure_behavior: reject out-of-range | safety_impact: MEDIUM
- dependencies: STR-0016, STR-0140 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0020 — Canonical display string is derived-only, never parsed back to reconstruct identity
- section: §3 Canonical Identity Model | lines: L168–L173 | type: IDENTITY_RULE | strength: MUST_NOT | tag: [UR][DEFINED]
- wording: "Canonical display string (derived only, never authoritative — never parsed back to reconstruct identity): 'G{GenerationID:02d}-C{CycleID:02d}-{Direction}{LevelID:02d}'"
- inputs: identity fields | outputs: display string | preconditions: identity exists | postconditions: string derived; never source of truth | state_effects: display only
- formula: "G{GenerationID:02d}-C{CycleID:02d}-{Direction}{LevelID:02d}" | units: NONE
- invariants: human-readable identity deterministic; never parsed back | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0016 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0021 — MUST reject creation of CycleID=100 or GenerationID=100
- section: §3 Canonical Identity Model | lines: L177 | type: GUARD | strength: MUST | tag: [UR][DEFINED]
- wording: "The system MUST reject any attempt to create CycleID = 100 or GenerationID = 100."
- inputs: create request | outputs: rejection | preconditions: attempted ID=100 | postconditions: creation rejected | state_effects: no object created
- formula: NONE | units: NONE
- invariants: no Cycle 100; no Generation 100 | failure_behavior: reject (fail-closed); INELIGIBLE_EVOLUTION_CANDIDATE (GENERATION_ID_LIMIT) where applicable | safety_impact: HIGH
- dependencies: STR-0017, STR-0018 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0022 — MUST NOT wrap, overwrite, truncate, or recycle an existing identity
- section: §3 Canonical Identity Model | lines: L178 | type: IDENTITY_RULE | strength: MUST_NOT | tag: [UR][DEFINED]
- wording: "The system MUST NOT wrap, overwrite, truncate, or recycle an existing identity."
- inputs: NONE | outputs: NONE | preconditions: existing identity | postconditions: identity preserved intact | state_effects: identity immutability
- formula: NONE | units: NONE
- invariants: no wrap/overwrite/truncate/recycle | failure_behavior: reject | safety_impact: HIGH
- dependencies: STR-0016 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0023 — Historical Cycles/Generations are immutable (never deleted, rewritten, reused)
- section: §3 Canonical Identity Model | lines: L179 | type: PERSISTENCE_RULE | strength: MUST_NOT | tag: [UR][DEFINED]
- wording: "Historical Cycles and Generations are immutable objects; they are never deleted, rewritten, or reused."
- inputs: NONE | outputs: NONE | preconditions: historical object exists | postconditions: object retained immutably | state_effects: history persistence
- formula: NONE | units: NONE
- invariants: historical objects never deleted/overwritten/recycled | failure_behavior: reject mutation | safety_impact: HIGH
- dependencies: STR-0022 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0024 — Effective limit = min(configured, 99); approved config 99/99; limit reach routes to §5.3 / §4.6
- section: §3 Canonical Identity Model | lines: L181 | type: GUARD | strength: MUST | tag: [DD][UR][DEFINED]
- wording: "the effective limit for each axis is min(configured value, 99) … Reaching the effective Cycle limit triggers §5.3 (disable); reaching the effective Generation limit triggers §4.6."
- inputs: MaxGenerations, MaxCyclesPerGeneration (=99 approved) | outputs: effective limits | preconditions: config present | postconditions: effective limit computed; routing on reach | state_effects: limit enforcement
- formula: effective_limit = min(configured_value, 99) | units: count
- invariants: architecture must support full 0–99 regardless of config | failure_behavior: reach Cycle limit → DISABLE (§5.3); reach Gen limit → §4.6 | safety_impact: HIGH
- dependencies: STR-0017, STR-0018, STR-0259, STR-0260 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §4.1 Evolution trigger — path-dependent return (L187–L231)

### STR-0025 — Evolution created only when ALL conditions verified, in order
- section: §4.1 Evolution trigger | lines: L189–L212 | type: STATE_TRANSITION | strength: MUST | tag: [UR][DEFINED]
- wording: "A new Generation may be created when all of the following are verified, in this order"
- inputs: conditions 1–7 (§4.1) | outputs: new Generation (EvolutionTriggered) | preconditions: all 7 conditions verified in order | postconditions: successor Generation created | state_effects: new Generation; parent → SUCCESSOR_CREATED
- formula: NONE | units: NONE
- invariants: ordered conjunction of all 7 conditions; Evolution cannot be triggered by unverified price crossing | failure_behavior: INELIGIBLE_EVOLUTION_CANDIDATE if any condition fails | safety_impact: CRITICAL
- dependencies: STR-0026, STR-0027, STR-0028, STR-0029, STR-0030, STR-0031, STR-0032 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0026 — Condition 1: prior directional traversal established (≥1 level POSITION_VERIFIED in Generation)
- section: §4.1 Evolution trigger | lines: L191–L193 | type: GUARD | strength: MUST | tag: [UR][DEFINED]
- wording: "A prior directional traversal has been established … at least one level of one group has reached POSITION_VERIFIED (§6) within that Generation's lifecycle."
- inputs: POSITION_VERIFIED events | outputs: traversal-established flag | preconditions: ≥1 verified level | postconditions: traversal recorded | state_effects: traversal record
- formula: NONE | units: NONE
- invariants: traversal grounded on POSITION_VERIFIED | failure_behavior: no traversal → no return level | safety_impact: HIGH
- dependencies: STR-0129 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0027 — Condition 2: traversed/origin group is recorded
- section: §4.1 Evolution trigger | lines: L194 | type: STATE_TRANSITION | strength: MUST | tag: [UR][DEFINED]
- wording: "The traversed/origin group is recorded."
- inputs: traversal | outputs: recorded origin group | preconditions: traversal established | postconditions: origin group persisted | state_effects: origin-group field (feeds §4.5 Dominance)
- formula: NONE | units: NONE
- invariants: origin group persisted for dominance determination | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0026, STR-0055 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0028 — Condition 3: market reverses toward the opposite group
- section: §4.1 Evolution trigger | lines: L195 | type: GUARD | strength: MUST | tag: [UR][DEFINED]
- wording: "The market reverses toward the opposite group."
- inputs: market price direction | outputs: reversal detection | preconditions: traversal recorded | postconditions: reversal observed | state_effects: NONE
- formula: NONE | units: NONE
- invariants: NONE | failure_behavior: no reversal → no Evolution | safety_impact: MEDIUM
- dependencies: STR-0027 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0029 — Condition 4: reaches opposite group's established (dynamic, traversal-derived) return level
- section: §4.1 Evolution trigger | lines: L196–L202 | type: GUARD | strength: MUST | tag: [UR][DEFINED]
- wording: "The market reaches the opposite group's established return level — the highest level of the opposite group that reached POSITION_VERIFIED during the recorded prior traversal … The return level is dynamic and traversal-derived, not a configured value"
- inputs: recorded traversal; POSITION_VERIFIED levels of opposite group | outputs: return level | preconditions: opposite-group levels verified in prior traversal | postconditions: return level defined dynamically | state_effects: return-level record
- formula: return_level = highest opposite-group level reaching POSITION_VERIFIED in recorded prior traversal | units: NONE
- invariants: ReturnLevelBU/ReturnLevelSL are NOT configuration keys; dynamic/traversal-derived | failure_behavior: return level undefined if no verified traversal | safety_impact: HIGH
- dependencies: STR-0026, STR-0322 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0030 — Condition 5: return verified by strategy order POSITION_VERIFIED (hedge orders ineligible), held continuously through confirmation window
- section: §4.1 Evolution trigger | lines: L203–L208 | type: GUARD | strength: MUST | tag: [UR][DEFINED]
- wording: "verified by a strategy order at the return level reaching POSITION_VERIFIED … hedge orders are NOT eligible to satisfy this condition … holds continuously for the confirmation window (§4.2)."
- inputs: strategy-order fill; authoritative position delta; confirmation window | outputs: verified-return flag | preconditions: strategy (not hedge) order at return level | postconditions: condition holds through window | state_effects: verified-return latch
- formula: NONE | units: seconds (window, §4.2) | invariants: hedge orders not eligible; POSITION_VERIFIED required
- failure_behavior: de-verification resets window | safety_impact: CRITICAL
- dependencies: STR-0029, STR-0036, STR-0129 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0031 — Condition 6: exposure, reconciliation, risk, fillability, transition guards pass
- section: §4.1 Evolution trigger | lines: L209–L210 | type: GUARD | strength: MUST | tag: [UR][DEFINED]
- wording: "Exposure, reconciliation, risk, fillability, and transition guards pass (§11.1 ordering; the §8 gate list)."
- inputs: §11.1 ordering; §8 gate list | outputs: guard pass/fail | preconditions: candidate active | postconditions: all guards pass | state_effects: NONE
- formula: NONE | units: NONE
- invariants: no transition bypasses risk/exposure/fillability/reconciliation gates | failure_behavior: block if any guard fails | safety_impact: CRITICAL
- dependencies: STR-0163, STR-0199 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0032 — Condition 7: current Generation eligible under §4.4 (lock unset; GenerationID < limit)
- section: §4.1 Evolution trigger | lines: L211–L212 | type: GUARD | strength: MUST | tag: [UR][DEFINED]
- wording: "The current Generation is eligible to create a successor under §4.4 (successor lock not set; GenerationID < effective Generation limit)."
- inputs: successor-lock flag; GenerationID; effective limit | outputs: eligibility | preconditions: lock unset and GenerationID<limit | postconditions: eligible to create successor | state_effects: NONE
- formula: NONE | units: NONE
- invariants: ≤1 successor per Generation; no successor at GenerationID=99 | failure_behavior: INELIGIBLE_EVOLUTION_CANDIDATE (SUCCESSOR_LOCK_ACTIVE / GENERATION_ID_LIMIT) | safety_impact: HIGH
- dependencies: STR-0049, STR-0058 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0033 — Evolution trigger is NOT any single insufficient signal
- section: §4.1 Evolution trigger | lines: L214–L230 | type: GUARD | strength: MUST_NOT | tag: [UR][DD][DEFINED]
- wording: "The trigger is NOT (each is individually insufficient): terminal-level reach alone; level-number equality alone; requested order fill alone; raw price crossing alone; order acknowledgement alone; isolated fill message alone; unverified WebSocket evidence alone"
- inputs: candidate signals | outputs: rejection of insufficient triggers | preconditions: apparent trigger signal | postconditions: not treated as Evolution | state_effects: NONE
- formula: NONE | units: NONE
- invariants: also rejects legacy |B−S| rule, |BU−SL|==1 rule, superseded dual-group threshold rule | failure_behavior: not executed | safety_impact: HIGH
- dependencies: STR-0025 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0034 — Minimum penetration; missed-Cycle Evolution deferred (not cancelled), per-Cycle evaluated
- section: §4.1 Evolution trigger | lines: L226 | type: STATE_TRANSITION | strength: MUST | tag: [UR][DD][DEFINED]
- wording: "If no level of the opposite group reaches POSITION_VERIFIED in a Cycle … no new Generation is created in that Cycle; the Evolution opportunity is deferred to a later Cycle of the same Generation, not cancelled"
- inputs: per-Cycle traversal state | outputs: deferral | preconditions: no verified traversal in Cycle | postconditions: opportunity carried forward | state_effects: deferred-candidate carry-forward
- formula: NONE | units: NONE
- invariants: deferred-not-cancelled (D-01); intermediate penetration without verified return creates no Generation | failure_behavior: no Generation this Cycle | safety_impact: MEDIUM
- dependencies: STR-0029 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0035 — Fail-closed on unverified/skipped return; record INELIGIBLE_EVOLUTION_CANDIDATE, never resurrect/silently discard
- section: §4.1 Evolution trigger | lines: L228 | type: FAILURE_BEHAVIOR | strength: MUST | tag: [DD][UR][DEFINED]
- wording: "if the return level is skipped (§9.3) or only partially verified, no Evolution occurs. Record INELIGIBLE_EVOLUTION_CANDIDATE (reason RETURN_LEVEL_UNVERIFIED); the failed instance is never resurrected or retroactively completed"
- inputs: return-level verification state | outputs: INELIGIBLE_EVOLUTION_CANDIDATE record | preconditions: skipped/partial return | postconditions: no Evolution; failed instance not resurrected | state_effects: candidate record with reason code
- formula: NONE | units: NONE
- invariants: apparent trigger failing any condition recorded with reason, never silently discarded, never executed; skipped portion contributes zero exposure/PnL | failure_behavior: INELIGIBLE_EVOLUTION_CANDIDATE (RETURN_LEVEL_UNVERIFIED); fail-closed | safety_impact: CRITICAL
- dependencies: STR-0025, STR-0190 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §4.2 Evolution Confirmation Tolerance (L232–L249)

### STR-0036 — Candidate must hold continuously for EvolutionConfirmationSeconds (60s) before Evolution fires
- section: §4.2 Evolution Confirmation Tolerance | lines: L234–L236 | type: GUARD | strength: MUST | tag: [SD][DEFINED]
- wording: "The Evolution candidate (§4.1 conditions 1–4) must hold CONTINUOUSLY for EvolutionConfirmationSeconds (config; approved value 60s, §14 D-03) before Evolution fires."
- inputs: candidate state; EvolutionConfirmationSeconds=60 | outputs: fire/hold | preconditions: candidate formed | postconditions: fire only after continuous window | state_effects: confirmation timer
- formula: NONE | units: seconds (60) | invariants: continuity over window required
- failure_behavior: interruption prevents fire | safety_impact: HIGH
- dependencies: STR-0025, STR-0258 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0037 — Confirmation evaluated only over POSITION_VERIFIED evidence
- section: §4.2 Evolution Confirmation Tolerance | lines: L238–L239 | type: GUARD | strength: MUST | tag: [SD][DEFINED]
- wording: "Evaluated only over POSITION_VERIFIED evidence (inherits §6's verification requirement automatically — not a separately-tuned mechanism)."
- inputs: POSITION_VERIFIED evidence | outputs: window evaluation | preconditions: verified evidence | postconditions: evaluation on verified only | state_effects: NONE
- formula: NONE | units: NONE | invariants: inherits §6 verification; not separately tuned
- failure_behavior: unverified evidence ignored | safety_impact: HIGH
- dependencies: STR-0129 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0038 — Hysteresis: return-level boundary latched for the confirmation window
- section: §4.2 Evolution Confirmation Tolerance | lines: L241–L244 | type: GUARD | strength: MUST | tag: [SD][DEFINED]
- wording: "once the candidate forms, the return-level boundary is latched for the confirmation window"
- inputs: candidate formation | outputs: latched boundary | preconditions: candidate formed | postconditions: boundary latched | state_effects: latch
- formula: NONE | units: NONE | invariants: prevents flip-flop at boundary
- failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0036 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0039 — De-verification of the return condition resets the window
- section: §4.2 Evolution Confirmation Tolerance | lines: L243–L244 | type: STATE_TRANSITION | strength: MUST | tag: [SD][DEFINED]
- wording: "de-verification of the return condition resets the window (prevents flip-flop at the boundary)."
- inputs: de-verification event | outputs: window reset | preconditions: return condition de-verified | postconditions: confirmation window restarted | state_effects: timer reset
- formula: NONE | units: NONE | invariants: flip-flop prevention
- failure_behavior: window resets (no fire) | safety_impact: MEDIUM
- dependencies: STR-0036 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0040 — Only one Evolution transition in flight per Basket (state-transition locking)
- section: §4.2 Evolution Confirmation Tolerance | lines: L246–L247 | type: GUARD | strength: MUST | tag: [SD][DEFINED]
- wording: "Only one Evolution transition may be in flight per Basket at a time (state-transition locking)."
- inputs: in-flight Evolution state | outputs: lock | preconditions: an Evolution in flight | postconditions: no concurrent Evolution | state_effects: Basket-scoped Evolution lock
- formula: NONE | units: NONE | invariants: single-in-flight per Basket (also §4.7 P2)
- failure_behavior: concurrent attempt blocked | safety_impact: HIGH
- dependencies: STR-0066 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §4.3 Generation states (L250–L271)

### STR-0041 — Generation state machine + FROZEN overlay
- section: §4.3 Generation states | lines: L252–L259 | type: LIFECYCLE_STATE | strength: MUST | tag: [DD][UR][DEFINED]
- wording: "CREATED → ACTIVE → EVOLUTION_PENDING … → SUCCESSOR_CREATED … → DISABLED_AT_CYCLE_99 … → CLOSED_ONLY_AS_PART_OF_BASKET … FROZEN: overlay from Basket FREEZE (§13.3) on any non-terminal state."
- inputs: lifecycle events | outputs: Generation state | preconditions: Generation exists | postconditions: state ∈ defined set | state_effects: CREATED/ACTIVE/EVOLUTION_PENDING/SUCCESSOR_CREATED/DISABLED_AT_CYCLE_99/CLOSED_ONLY_AS_PART_OF_BASKET/FROZEN
- formula: NONE | units: NONE | invariants: defined state set only
- failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0006 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0042 — ACTIVE: exactly one per Basket (newest), full progression capability
- section: §4.3 Generation states | lines: L263 | type: LIFECYCLE_STATE | strength: MUST | tag: [DD][UR][DEFINED]
- wording: "ACTIVE: exactly one per Basket — the newest. Full progression capability: may open Levels, start Cycles, and (if eligible under §4.4) create its one successor."
- inputs: NONE | outputs: ACTIVE Generation | preconditions: newest Generation | postconditions: exactly one ACTIVE per Basket | state_effects: ACTIVE
- formula: NONE | units: NONE | invariants: exactly one ACTIVE (newest) per Basket
- failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0041 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0043 — EVOLUTION_PENDING transient; no new successor elsewhere while in flight
- section: §4.3 Generation states | lines: L264 | type: LIFECYCLE_STATE | strength: MUST | tag: [DD][UR][DEFINED]
- wording: "EVOLUTION_PENDING: transient; the §4.2 confirmation window is running. No new successor may be started elsewhere in the Basket while it is in flight."
- inputs: confirmation window | outputs: transient state | preconditions: window running | postconditions: no concurrent successor start | state_effects: EVOLUTION_PENDING
- formula: NONE | units: NONE | invariants: single Evolution in flight
- failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0040 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0044 — SUCCESSOR_CREATED: progression lock (own Cycles continue; no new successor/Evolution)
- section: §4.3 Generation states | lines: L265 | type: LIFECYCLE_STATE | strength: MUST | tag: [UR][DEFINED]
- wording: "SUCCESSOR_CREATED: progression lock. May continue its own Cycle progression … May not create another successor, may not start a new Evolution … Its positions remain in Basket accounting and Hedge controls"
- inputs: successor creation | outputs: locked-progression state | preconditions: created a successor | postconditions: own Cycles allowed; no new successor | state_effects: SUCCESSOR_CREATED
- formula: NONE | units: NONE | invariants: positions remain in Basket accounting and hedge controls
- failure_behavior: further successor blocked | safety_impact: HIGH
- dependencies: STR-0049, STR-0074 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0045 — DISABLED_AT_CYCLE_99: terminal progression state; retains protection/accounting; not a closure state
- section: §4.3 Generation states | lines: L266 | type: LIFECYCLE_STATE | strength: MUST | tag: [UR][DEFINED]
- wording: "DISABLED_AT_CYCLE_99: terminal progression state (§5.3). No new Cycles, no new Levels, no successor, ever. Remains eligible for: … It is a strategy-progression state, not a position-closure state"
- inputs: Cycle-limit reach | outputs: disabled state | preconditions: effective Cycle limit reached | postconditions: no progression; reconciliation/hedge/accounting retained | state_effects: DISABLED_AT_CYCLE_99
- formula: NONE | units: NONE | invariants: disabled ≠ closed; exposure fully live
- failure_behavior: progression blocked | safety_impact: HIGH
- dependencies: STR-0084 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0046 — CLOSED_ONLY_AS_PART_OF_BASKET: entered only via §13.4 closure, never individually
- section: §4.3 Generation states | lines: L267 | type: LIFECYCLE_STATE | strength: MUST | tag: [DD][UR][DEFINED]
- wording: "CLOSED_ONLY_AS_PART_OF_BASKET: entered only when the Basket closure sequence (§13.4) verifies closure. Never entered individually."
- inputs: §13.4 closure verification | outputs: closed state | preconditions: Basket closure verified | postconditions: Generation closed as part of Basket | state_effects: CLOSED_ONLY_AS_PART_OF_BASKET
- formula: NONE | units: NONE | invariants: never entered individually
- failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0243 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0047 — FROZEN is overlay only; never erases underlying lifecycle state
- section: §4.3 Generation states | lines: L268 | type: LIFECYCLE_STATE | strength: MUST | tag: [DD][DEFINED]
- wording: "FROZEN: overlay only; it never erases the underlying lifecycle state."
- inputs: Basket FREEZE | outputs: FROZEN overlay | preconditions: non-terminal state | postconditions: overlay applied; base state preserved | state_effects: FROZEN overlay
- formula: NONE | units: NONE | invariants: overlay preserves base state
- failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0239 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0048 — Terminology mapping: EVOLVED superseded; EVOLVED_PASSIVE deprecated; no dual-named persisted state
- section: §4.3 Generation states | lines: L270 | type: PERSISTENCE_RULE | strength: MUST | tag: [DD][DEFINED]
- wording: "v1.0's EVOLVED state is superseded … The Amendment's EVOLVED_PASSIVE label is deprecated as an alias … No state may carry two names in persisted data."
- inputs: legacy labels | outputs: canonical state names | preconditions: legacy occurrence | postconditions: mapped to SUCCESSOR_CREATED or DISABLED_AT_CYCLE_99 | state_effects: persisted state naming
- formula: NONE | units: NONE | invariants: no state carries two names in persisted data
- failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0044, STR-0045 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §4.4 One-Successor Constraint & Successor Lock (L272–L280)

### STR-0049 — A Generation may create a successor at most once in its eligible pre-limit lifecycle
- section: §4.4 One-Successor Constraint | lines: L274 | type: GUARD | strength: MUST | tag: [UR][DEFINED]
- wording: "A Generation may create a successor Generation at most once during its eligible pre-limit lifecycle"
- inputs: successor creation events | outputs: one-successor enforcement | preconditions: eligible Generation | postconditions: ≤1 successor | state_effects: successor lock
- formula: NONE | units: NONE | invariants: at most one successor per Generation
- failure_behavior: second attempt → INELIGIBLE_EVOLUTION_CANDIDATE | safety_impact: HIGH
- dependencies: STR-0013 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0050 — After G creates G+1, G enters SUCCESSOR_CREATED
- section: §4.4 One-Successor Constraint | lines: L275 | type: STATE_TRANSITION | strength: MUST | tag: [UR][DEFINED]
- wording: "After Generation G creates Generation G+1, G enters SUCCESSOR_CREATED (§4.3)"
- inputs: successor creation | outputs: state transition | preconditions: G created G+1 | postconditions: G in SUCCESSOR_CREATED | state_effects: G→SUCCESSOR_CREATED
- formula: NONE | units: NONE | invariants: NONE
- failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0044, STR-0049 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0051 — While SUCCESSOR_CREATED and below limit: continue Cycles; no second successor from any Cycle
- section: §4.4 One-Successor Constraint | lines: L276 | type: GUARD | strength: MUST | tag: [UR][DEFINED]
- wording: "While G is SUCCESSOR_CREATED and below its Cycle limit: it may continue its Cycle progression … it may not create another successor; no Cycle of G below its limit may create another successor"
- inputs: G state; Cycle events | outputs: allowed/blocked transitions | preconditions: G SUCCESSOR_CREATED, below limit | postconditions: Cycles allowed; successor blocked | state_effects: Cycle progression continues
- formula: NONE | units: NONE | invariants: no Cycle of G creates a second successor
- failure_behavior: successor attempt blocked | safety_impact: HIGH
- dependencies: STR-0050 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0052 — Normative example: G0 creating G1 at C0 cannot create G2 from C1..limit
- section: §4.4 One-Successor Constraint | lines: L277 | type: SCENARIO | strength: MUST | tag: [UR][DEFINED]
- wording: "if Generation 0 creates Generation 1 at Cycle 0, Generation 0 cannot create Generation 2 from Cycle 1 through its Cycle limit; its progression boundary is its Cycle limit, then disable (§5.3)."
- inputs: G0 successor state | outputs: enforcement | preconditions: G0 created G1 at C0 | postconditions: no G2 from G0 | state_effects: G0 progression bounded then disable
- formula: NONE | units: NONE | invariants: one-successor
- failure_behavior: G2 from G0 blocked | safety_impact: HIGH
- dependencies: STR-0051 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0053 — Lock is per Generation: G1 has independent eligibility to create G2 once
- section: §4.4 One-Successor Constraint | lines: L278 | type: GUARD | strength: MUST | tag: [UR][DEFINED]
- wording: "The lock is per Generation: Generation 1 has its own independent eligibility and may itself create Generation 2 once, subject to the same rules and the global GenerationID limit"
- inputs: G1 eligibility | outputs: independent lock | preconditions: G1 eligible | postconditions: G1 may create one successor | state_effects: per-Generation lock
- formula: NONE | units: NONE | invariants: locks are independent per Generation
- failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0049 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0054 — Apparent Evolution while lock active → INELIGIBLE_EVOLUTION_CANDIDATE (SUCCESSOR_LOCK_ACTIVE), never executed
- section: §4.4 One-Successor Constraint | lines: L279 | type: FAILURE_BEHAVIOR | strength: MUST | tag: [UR][DEFINED]
- wording: "An apparent Evolution while the lock is active is recorded as an INELIGIBLE_EVOLUTION_CANDIDATE (reason SUCCESSOR_LOCK_ACTIVE), never executed"
- inputs: apparent Evolution; active lock | outputs: candidate record | preconditions: lock active | postconditions: recorded, not executed | state_effects: INELIGIBLE_EVOLUTION_CANDIDATE
- formula: NONE | units: NONE | invariants: never silently executed
- failure_behavior: INELIGIBLE_EVOLUTION_CANDIDATE (SUCCESSOR_LOCK_ACTIVE) | safety_impact: HIGH
- dependencies: STR-0049 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §4.5 Post-Evolution Dominance (L281–L299)

### STR-0055 — Dominance = origin/traversed group of parent's recorded prior traversal
- section: §4.5 Post-Evolution Dominance | lines: L285–L293 | type: FORMULA | strength: MUST | tag: [DD][DEFINED]
- wording: "Dominance(successor) := the origin/traversed group of the parent Generation's recorded prior traversal is Dominant."
- inputs: parent's recorded traversal | outputs: dominant side | preconditions: Evolution firing | postconditions: dominant side set | state_effects: dominance field
- formula: Dominance := origin/traversed group of parent's recorded prior traversal | units: NONE
- invariants: single dominance source | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0027 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0056 — Dominant side fixed at Evolution time; never recomputed per Cycle
- section: §4.5 Post-Evolution Dominance | lines: L294–L295 | type: GUARD | strength: MUST | tag: [DD][DEFINED]
- wording: "The Dominant side is fixed at Evolution time (this §4.5) and never recomputed per Cycle."
- inputs: Evolution event | outputs: fixed dominance | preconditions: Evolution fired | postconditions: dominance immutable for Generation lifetime | state_effects: dominance latch
- formula: NONE | units: NONE | invariants: dominance persists Generation lifetime
- failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0055 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0057 — MaxReachedLevel-comparison superseded; no other dominance source
- section: §4.5 Post-Evolution Dominance | lines: L298 | type: GUARD | strength: MUST_NOT | tag: [DD][DEFINED]
- wording: "The v2.0 MaxReachedLevel-comparison working default (former option (c)) is superseded … No other dominance source may be used"
- inputs: NONE | outputs: NONE | preconditions: NONE | postconditions: only §4.5 rule used | state_effects: NONE
- formula: NONE | units: NONE | invariants: single dominance rule
- failure_behavior: NONE | safety_impact: LOW
- dependencies: STR-0055 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §4.6 Generation 99 (L300–L307)

### STR-0058 — G99 cannot create G100; successor attempt rejected (GENERATION_ID_LIMIT); never wraps to G0
- section: §4.6 Generation 99 | lines: L302 | type: FAILURE_BEHAVIOR | strength: MUST_NOT | tag: [UR][DD][DEFINED]
- wording: "it cannot create Generation 100 … The Basket MUST NOT silently wrap to Generation 0 or create an out-of-range successor … A successor attempt at GenerationID = 99 is rejected and recorded as INELIGIBLE_EVOLUTION_CANDIDATE (reason GENERATION_ID_LIMIT)"
- inputs: successor attempt at G99 | outputs: rejection record | preconditions: GenerationID=99 | postconditions: no G100; no wrap | state_effects: INELIGIBLE_EVOLUTION_CANDIDATE
- formula: NONE | units: NONE | invariants: no Generation 100; no wrap to G0
- failure_behavior: INELIGIBLE_EVOLUTION_CANDIDATE (GENERATION_ID_LIMIT) | safety_impact: HIGH
- dependencies: STR-0021, STR-0032 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0059 — G99 at Cycle limit → DISABLED_AT_CYCLE_99; Scenario 19 normative and reachable; G99-C99 deepest valid point
- section: §4.6 Generation 99 | lines: L302 | type: STATE_TRANSITION | strength: MUST | tag: [DD][DEFINED]
- wording: "If Generation 99 reaches its Cycle limit it becomes DISABLED_AT_CYCLE_99 … Scenario 19 is normative and reachable in normal configuration … G99–C99 is the deepest valid lifecycle point"
- inputs: G99 Cycle-limit reach | outputs: disabled state | preconditions: G99 at limit | postconditions: DISABLED_AT_CYCLE_99 | state_effects: G99 disabled
- formula: NONE | units: NONE | invariants: G99-C99 deepest valid point
- failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0084, STR-0127 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0060 — If effective Generation limit <99 (config), same semantics at that limit
- section: §4.6 Generation 99 | lines: L304 | type: GUARD | strength: MUST | tag: [DD][DEFINED]
- wording: "If the effective Generation limit is below 99 (config), the same semantics apply at that limit: the newest Generation cannot create a successor"
- inputs: effective Generation limit | outputs: enforcement at limit | preconditions: limit <99 | postconditions: no successor beyond limit | state_effects: limit enforcement
- formula: NONE | units: count | invariants: generalizes §4.6 without changing semantics
- failure_behavior: successor blocked at limit | safety_impact: MEDIUM
- dependencies: STR-0024 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0061 — One-successor rule spans full lifecycle; parent Cycle axis continues after successor
- section: §4.6 Generation 99 | lines: L306 | type: INVARIANT | strength: MUST | tag: [DD][DEFINED]
- wording: "each Generation has exactly one child across its entire 99-Cycle lifecycle … All Cycles of a Generation below its limit remain valid progression even after that Generation has created its one successor"
- inputs: Generation lifecycle | outputs: enforcement | preconditions: successor created | postconditions: parent Cycles continue; no second child | state_effects: Cycle progression + successor lock
- formula: NONE | units: NONE | invariants: exactly one child ever; Cycle axis independent of successor lock
- failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0049, STR-0051 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0062 — Max representable chain exactly 100 Generations (G0…G99); linear (not exponential) growth
- section: §4.6 Generation 99 | lines: L306 | type: INVARIANT | strength: MUST | tag: [DD][DEFINED]
- wording: "The maximum representable chain is exactly 100 Generations (G0…G99), each creating at most one successor — Generation growth is linear, not exponential"
- inputs: successor rule | outputs: bounded chain | preconditions: NONE | postconditions: ≤100 Generations | state_effects: NONE
- formula: NONE | units: count (100) | invariants: linear growth; PASSIVE-exposure concern structurally addressed
- failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0061 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §4.7 Deterministic precedence for simultaneous Generation/Cycle events (L308–L338)

### STR-0063 — Transitions evaluated in passes; total order; no event twice; unexecuted re-evaluated next pass
- section: §4.7 Deterministic precedence | lines: L310–L311 | type: PRECEDENCE_RULE | strength: MUST | tag: [DD][DEFINED]
- wording: "All state transitions are evaluated in passes. Within one pass, the following total order applies; no event may execute twice, and any event not executed in this pass is re-evaluated in the next"
- inputs: candidate transitions | outputs: ordered execution | preconditions: pass begins | postconditions: total-ordered execution | state_effects: pass engine
- formula: NONE | units: NONE | invariants: deterministic total order; idempotent per pass
- failure_behavior: unexecuted → next pass | safety_impact: HIGH
- dependencies: NONE | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0064 — P0: Position verification & reconciliation feeds everything
- section: §4.7 Deterministic precedence | lines: L313 | type: PRECEDENCE_RULE | strength: MUST | tag: [DD][DEFINED]
- wording: "P0  POSITION VERIFICATION & RECONCILIATION (feeds everything; §11.1)"
- inputs: authoritative state | outputs: verified state feeding all passes | preconditions: pass begins | postconditions: P0 first | state_effects: reconciliation
- formula: NONE | units: NONE | invariants: P0 precedes all | failure_behavior: NONE | safety_impact: CRITICAL
- dependencies: STR-0199 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0065 — P1: Risk/exposure protection & hedge recovery may block/divert every lower transition
- section: §4.7 Deterministic precedence | lines: L314–L315 | type: PRECEDENCE_RULE | strength: MUST | tag: [DD][DEFINED]
- wording: "P1  RISK / EXPOSURE PROTECTION & HEDGE RECOVERY (may block or divert every transition below; §11.1, §11.2)"
- inputs: exposure classification | outputs: block/divert | preconditions: after P0 | postconditions: risk enforced before progression | state_effects: hedge recovery
- formula: NONE | units: NONE | invariants: risk precedence over progression | failure_behavior: block/divert | safety_impact: CRITICAL
- dependencies: STR-0064, STR-0199, STR-0206 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0066 — P2: Locks — ≤1 Evolution in flight per Basket; ≤1 Cycle transition per Generation per pass
- section: §4.7 Deterministic precedence | lines: L316–L317 | type: PRECEDENCE_RULE | strength: MUST | tag: [DD][DEFINED]
- wording: "P2  LOCKS: at most one Evolution transition in flight per Basket (§4.2); at most one Cycle transition per Generation per pass."
- inputs: in-flight state | outputs: locks | preconditions: after P1 | postconditions: locks enforced | state_effects: transition locks
- formula: NONE | units: NONE | invariants: single Evolution per Basket; single Cycle transition per Generation per pass | failure_behavior: excess blocked | safety_impact: HIGH
- dependencies: STR-0040 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0067 — P3: Same-Generation conflict — DISABLE beats Evolution (reason CYCLE_LIMIT_REACHED)
- section: §4.7 Deterministic precedence | lines: L318–L324 | type: PRECEDENCE_RULE | strength: MUST | tag: [UR][DEFINED]
- wording: "if, for the same Generation G, both a Cycle-limit disable condition (§5.3) and an Evolution condition (§4.1) are verified in the same pass, the DISABLE executes and the Evolution candidate is recorded INELIGIBLE_EVOLUTION_CANDIDATE (reason CYCLE_LIMIT_REACHED)."
- inputs: concurrent disable+Evolution for G | outputs: disable executes | preconditions: both verified same pass | postconditions: DISABLE wins | state_effects: DISABLED_AT_CYCLE_99; ineligible candidate
- formula: NONE | units: NONE | invariants: successor eligibility ends at Cycle limit | failure_behavior: INELIGIBLE_EVOLUTION_CANDIDATE (CYCLE_LIMIT_REACHED) | safety_impact: HIGH
- dependencies: STR-0084, STR-0025 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0068 — P4: Across Generations — Evolution executes before Cycle transitions; lower GenerationID first
- section: §4.7 Deterministic precedence | lines: L325–L329 | type: PRECEDENCE_RULE | strength: MUST | tag: [DD][DEFINED]
- wording: "an Evolution transition executes BEFORE Cycle transitions … If two Evolutions were eligible in one pass … the lower GenerationID executes first."
- inputs: cross-Generation candidates | outputs: ordered execution | preconditions: after P3 | postconditions: Evolution before Cycle; lower ID first | state_effects: transition ordering
- formula: NONE | units: NONE | invariants: GENERATION EVOLUTION → CYCLE CREATION | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0063 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0069 — P5: Cycle transitions execute (standard §5.2 + disable §5.3, incl. parent continued progression)
- section: §4.7 Deterministic precedence | lines: L330–L332 | type: PRECEDENCE_RULE | strength: MUST | tag: [DD][DEFINED]
- wording: "P5  CYCLE TRANSITIONS execute (standard §5.2 and disable §5.3), including the parent Generation's continued Cycle progression after its own successor creation (§4.4 item 3)."
- inputs: Cycle transition candidates | outputs: executed transitions | preconditions: after P4 | postconditions: Cycle transitions complete | state_effects: Cycle transitions
- formula: NONE | units: NONE | invariants: parent progression continues post-successor | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0074, STR-0084, STR-0051 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0070 — P6: Level arming/order placement only after all transitions complete
- section: §4.7 Deterministic precedence | lines: L333–L334 | type: PRECEDENCE_RULE | strength: MUST | tag: [DD][DEFINED]
- wording: "P6  LEVEL ARMING / ORDER PLACEMENT proceeds only after all transitions in this pass are complete."
- inputs: pass completion | outputs: arming/placement | preconditions: all transitions complete | postconditions: arming proceeds | state_effects: order placement
- formula: NONE | units: NONE | invariants: arming after transitions | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0063, STR-0163 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §5.1 Terminal Event (L341–L355)

### STR-0071 — TerminalEvent definition (configured terminal level reaches POSITION_VERIFIED in Cycle C of Generation G)
- section: §5.1 Terminal Event | lines: L343–L347 | type: EVENT_SEMANTICS | strength: MUST | tag: [DD][UR][DEFINED]
- wording: "TerminalEvent(G, C, group) := the configured terminal level of the traversed group (the highest configured level, e.g. BU6/SL6 with GridLevels = 6) reaches POSITION_VERIFIED in Cycle C of Generation G."
- inputs: terminal level; POSITION_VERIFIED | outputs: TerminalEvent | preconditions: terminal level verified | postconditions: Cycle terminal event raised | state_effects: terminal event
- formula: TerminalEvent(G,C,group) := terminal-level POSITION_VERIFIED | units: NONE
- invariants: uses highest configured level | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0072, STR-0140 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0072 — POSITION_VERIFIED requires BOTH verified exchange fill AND authoritative position delta
- section: §5.1 Terminal Event | lines: L349–L353 | type: GUARD | strength: MUST | tag: [UR][DEFINED]
- wording: "POSITION_VERIFIED requires BOTH: verified exchange order fill AND corresponding authoritative position delta."
- inputs: exchange fill; authoritative position delta | outputs: POSITION_VERIFIED | preconditions: both present | postconditions: verified state | state_effects: POSITION_VERIFIED
- formula: POSITION_VERIFIED ⇔ verified fill ∧ authoritative position delta | units: NONE
- invariants: LEVEL FILLED ⇔ ORDER FILLED ∧ POSITION DELTA VERIFIED | failure_behavior: not verified if either missing | safety_impact: CRITICAL
- dependencies: STR-0129 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0073 — Price crossing/ack/isolated fill/requested qty are insufficient for POSITION_VERIFIED
- section: §5.1 Terminal Event | lines: L352–L353 | type: GUARD | strength: MUST_NOT | tag: [UR][DEFINED]
- wording: "A price crossing, order acknowledgement, isolated fill message, or requested order quantity is insufficient."
- inputs: partial signals | outputs: rejection | preconditions: only partial signal | postconditions: not verified | state_effects: NONE
- formula: NONE | units: NONE | invariants: no verification from partial signals
- failure_behavior: not verified | safety_impact: CRITICAL
- dependencies: STR-0072 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §5.2 Standard Cycle Transition (L356–L385)

### STR-0074 — Standard Cycle transition executes strictly in the 8-step order when C < effective limit
- section: §5.2 Standard Cycle Transition | lines: L358–L375 | type: STATE_TRANSITION | strength: MUST | tag: [DD][UR][DEFINED]
- wording: "When TerminalEvent(G, C, group) occurs and C < min(MaxCyclesPerGeneration, 99), the transition executes strictly in this order"
- inputs: TerminalEvent; C<limit | outputs: new Cycle | preconditions: terminal event; below limit | postconditions: ordered 8-step transition complete | state_effects: TERMINAL_PENDING→COMPLETED; new Cycle CREATED→ACTIVE
- formula: NONE | units: NONE | invariants: strict step ordering
- failure_behavior: BLOCKED at step 4 / step 7 on gate failure | safety_impact: HIGH
- dependencies: STR-0071, STR-0075, STR-0076, STR-0077, STR-0078, STR-0079, STR-0080 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0075 — Step 2: cancel all pending (not POSITION_VERIFIED) orders of the exhausted traversal
- section: §5.2 Standard Cycle Transition | lines: L362–L363 | type: STATE_TRANSITION | strength: MUST | tag: [DD][UR][DEFINED]
- wording: "Cancel all pending (not POSITION_VERIFIED) orders belonging to the exhausted traversal of Cycle C"
- inputs: pending orders | outputs: cancellations | preconditions: TERMINAL_PENDING | postconditions: exhausted-side pending cancelled | state_effects: order cancellation
- formula: NONE | units: NONE | invariants: only exhausted traversal (narrower than §5.3) | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0074 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0076 — Step 3: reconcile authoritative position and order state (clearinghouseState/webData2)
- section: §5.2 Standard Cycle Transition | lines: L364–L365 | type: RECOVERY_RULE | strength: MUST | tag: [DD][UR][DEFINED]
- wording: "Reconcile authoritative position and order state (clearinghouseState / webData2)"
- inputs: authoritative state | outputs: reconciled state | preconditions: after cancellations | postconditions: reconciled | state_effects: reconciliation
- formula: NONE | units: NONE | invariants: authoritative-only | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0200 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0077 — Step 4: non-overlap test (§5.6); on failure BLOCKED, TERMINAL_PENDING held, RECONCILIATION_REQUIRED
- section: §5.2 Standard Cycle Transition | lines: L366–L368 | type: FAILURE_BEHAVIOR | strength: MUST | tag: [DD][UR][DEFINED]
- wording: "Compute the ladder non-overlap test (§5.6); on failure the transition is BLOCKED: Cycle stays TERMINAL_PENDING, a RECONCILIATION_REQUIRED condition is raised (fail-closed)"
- inputs: §5.6 test | outputs: pass/BLOCKED | preconditions: reconciled | postconditions: proceed or BLOCKED | state_effects: RECONCILIATION_REQUIRED
- formula: NONE | units: NONE | invariants: fail-closed | failure_behavior: BLOCKED; RECONCILIATION_REQUIRED | safety_impact: HIGH
- dependencies: STR-0104 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0078 — Step 6: create Cycle G-(C+1) → CREATED → ACTIVE (same Generation)
- section: §5.2 Standard Cycle Transition | lines: L370–L371 | type: STATE_TRANSITION | strength: MUST | tag: [DD][UR][DEFINED]
- wording: "Create Cycle G-(C+1) → CREATED → ACTIVE (same Generation)"
- inputs: COMPLETED Cycle | outputs: new Cycle | preconditions: prior Cycle COMPLETED | postconditions: successor Cycle ACTIVE in same Generation | state_effects: new Cycle
- formula: NONE | units: NONE | invariants: same Generation | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0074 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0079 — Step 7: capture new execution-grounded reference (§5.4), subject to §5.4.1 tolerance
- section: §5.2 Standard Cycle Transition | lines: L372–L373 | type: STATE_TRANSITION | strength: MUST | tag: [DD][UR][DEFINED]
- wording: "Capture the new execution-grounded reference price (§5.4), subject to the §5.4.1 reference-price tolerance"
- inputs: §5.4 capture; §5.4.1 tolerance | outputs: new reference | preconditions: successor Cycle created | postconditions: reference captured within tolerance | state_effects: reference price
- formula: NONE | units: price | invariants: tolerance-gated | failure_behavior: BLOCKED if §5.4.1 exceeded | safety_impact: HIGH
- dependencies: STR-0091, STR-0096 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0080 — Step 8: issue fresh ladder for BOTH groups subject to strategy gates (§8, §10)
- section: §5.2 Standard Cycle Transition | lines: L374–L375 | type: STATE_TRANSITION | strength: MUST | tag: [DD][UR][DEFINED]
- wording: "Issue a fresh ladder for BOTH groups relative to the new reference, subject to all strategy gates (§8, §10)"
- inputs: new reference; §8/§10 gates | outputs: new ladder | preconditions: reference captured | postconditions: ladder issued through gates | state_effects: new ladder
- formula: NONE | units: NONE | invariants: passes §8/§10 gates | failure_behavior: gate failures per §8 | safety_impact: MEDIUM
- dependencies: STR-0163, STR-0193 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0081 — Cycle transition does NOT create a Generation, close positions, erase history, or remove exposure
- section: §5.2 Standard Cycle Transition | lines: L379–L383 | type: GUARD | strength: MUST_NOT | tag: [UR][DEFINED]
- wording: "does not create a new Generation by itself; does not close the completed Cycle's positions; does not erase the completed Cycle's history; does not remove completed Cycle exposure from Generation or Basket accounting"
- inputs: NONE | outputs: NONE | preconditions: Cycle transition | postconditions: Generation/positions/history/exposure preserved | state_effects: accounting preserved
- formula: NONE | units: NONE | invariants: completed-Cycle exposure retained | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0074 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0082 — Cycle transition prevents unintended overlap between old and new ladder (§5.6)
- section: §5.2 Standard Cycle Transition | lines: L383 | type: GUARD | strength: MUST | tag: [UR][DEFINED]
- wording: "prevents unintended overlap between the old and new ladder (§5.6)"
- inputs: §5.6 test | outputs: overlap prevention | preconditions: new ladder | postconditions: no overlap | state_effects: NONE
- formula: NONE | units: NONE | invariants: no unintended overlap | failure_behavior: BLOCKED on overlap | safety_impact: HIGH
- dependencies: STR-0104 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0083 — Cycle transition blocked/diverted to Hedge Recovery unless ExposureDelta within tolerance (ExposureTolerance dynamic default)
- section: §5.2 Standard Cycle Transition | lines: L384 | type: GUARD | strength: MUST | tag: [DYN][DEFINED]
- wording: "|ExposureDelta| ≤ ExposureTolerance AND no Hedge Recovery is in progress AND the Basket is not in ERROR/RECOVERY/FREEZE … ExposureTolerance is a base-asset-quantity bound … dynamic default (0.001 × StepBps / 10) × NotionalPerLevel / MarkPrice"
- inputs: ExposureDelta; ExposureTolerance; Basket state | outputs: proceed/block/divert | preconditions: transition candidate | postconditions: proceed only within tolerance | state_effects: gate
- formula: ExposureTolerance = (0.001 × StepBps / 10) × NotionalPerLevel / MarkPrice; NotionalPerLevel = MaxBasketNotional / GridLevels | units: base-asset quantity
- invariants: grid progression hard-gated on exposure within tolerance | failure_behavior: BLOCKED / diverted to Hedge Recovery | safety_impact: CRITICAL
- dynamic_note: must remain dynamic — never freeze to a constant (D-16; canonical PARAMETER: STR-0339)
- dependencies: STR-0339, STR-0199 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §5.3 Cycle-Limit Disable Transition (L386–L407)

### STR-0084 — Cycle-limit disable executes the 6-step sequence at TerminalEvent(G, 99/limit)
- section: §5.3 Cycle-Limit Disable Transition | lines: L388–L402 | type: STATE_TRANSITION | strength: MUST | tag: [UR][DEFINED]
- wording: "When TerminalEvent(G, 99, group) occurs (or TerminalEvent(G, limit, group) at a lower effective limit) … [6-step sequence]"
- inputs: TerminalEvent at limit | outputs: disable sequence | preconditions: effective Cycle limit reached | postconditions: Generation DISABLED_AT_CYCLE_99 | state_effects: G→DISABLED_AT_CYCLE_99
- formula: NONE | units: NONE | invariants: strict step order | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0071, STR-0085, STR-0086, STR-0087 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0085 — Disable step 2: cancel ALL pending Profit Layer progression orders of Generation G (both groups)
- section: §5.3 Cycle-Limit Disable Transition | lines: L394–L397 | type: STATE_TRANSITION | strength: MUST | tag: [UR][DEFINED]
- wording: "Cancel ALL pending Profit Layer progression orders associated with Generation G (both groups) — broader than §5.2's exhausted-side cancellation"
- inputs: pending progression orders | outputs: cancellations | preconditions: disable triggered | postconditions: all progression orders cancelled | state_effects: order cancellation
- formula: NONE | units: NONE | invariants: broader than §5.2 (both groups) | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0084 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0086 — Disable step 5: Generation G → DISABLED_AT_CYCLE_99
- section: §5.3 Cycle-Limit Disable Transition | lines: L399 | type: STATE_TRANSITION | strength: MUST | tag: [UR][DEFINED]
- wording: "Generation G → DISABLED_AT_CYCLE_99"
- inputs: disable sequence | outputs: state transition | preconditions: reconciled + COMPLETED | postconditions: G disabled | state_effects: DISABLED_AT_CYCLE_99
- formula: NONE | units: NONE | invariants: NONE | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0084, STR-0045 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0087 — Disable step 6: no Cycle 100; no successor ever by G; identities/history preserved
- section: §5.3 Cycle-Limit Disable Transition | lines: L400–L401 | type: GUARD | strength: MUST_NOT | tag: [UR][DEFINED]
- wording: "No Cycle 100 is created; no successor may ever be created by G; all identities and history are preserved"
- inputs: NONE | outputs: NONE | preconditions: G disabled | postconditions: no Cycle 100; no successor; history intact | state_effects: identity/history preservation
- formula: NONE | units: NONE | invariants: no Cycle 100; history immutable | failure_behavior: reject | safety_impact: HIGH
- dependencies: STR-0021, STR-0023 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0088 — Disabled Generation remains open for reconciliation/hedge/accounting/closure; not closed until §13.4
- section: §5.3 Cycle-Limit Disable Transition | lines: L404 | type: LIFECYCLE_STATE | strength: MUST | tag: [UR][DEFINED]
- wording: "The disabled Generation remains open for: position reconciliation, Hedge Recovery, exposure correction, mirroring … funding and fee accounting … and Basket-level closure … not considered closed until the Basket closure sequence (§13.4)"
- inputs: disabled Generation | outputs: retained eligibility | preconditions: disabled | postconditions: management/accounting retained | state_effects: retained obligations
- formula: NONE | units: NONE | invariants: disabled ≠ closed | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0086, STR-0243 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0089 — If no progression-capable Generation remains, Profit progression halts Basket-wide; hedge/reconciliation/accounting/closure continue
- section: §5.3 Cycle-Limit Disable Transition | lines: L406 | type: STATE_TRANSITION | strength: MUST | tag: [DD][DEFINED]
- wording: "If no progression-capable Generation remains in the Basket (all DISABLED_AT_CYCLE_99), Profit Layer progression halts Basket-wide; Hedge, reconciliation, accounting, and closure operations continue"
- inputs: Generation states | outputs: Basket-wide halt of progression | preconditions: all Generations disabled | postconditions: progression halted; management continues | state_effects: Basket progression halt
- formula: NONE | units: NONE | invariants: hedge/accounting/closure continue | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0086 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0090 — Reaching Cycle 99 does not close the Generation and does not close the Basket
- section: §5.3 Cycle-Limit Disable Transition | lines: L406 | type: GUARD | strength: MUST_NOT | tag: [UR][DEFINED]
- wording: "Reaching Cycle 99 does not close the Generation and does not close the Basket"
- inputs: NONE | outputs: NONE | preconditions: Cycle 99 reached | postconditions: no closure | state_effects: NONE
- formula: NONE | units: NONE | invariants: disable ≠ closure | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0088 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §5.4 Cycle Reference Price (L408–L427)

### STR-0091 — CycleReferenceDerivation config: four execution-grounded options (TERMINAL_EXECUTION default)
- section: §5.4 Cycle Reference Price | lines: L410–L424 | type: PARAMETER | strength: MUST | tag: [DD][DEFINED]
- wording: "CycleReferenceDerivation (config) := TERMINAL_EXECUTION (default) … TERMINAL_VWAP … TERMINAL_MID … TERMINAL_PLUS_STEP"
- inputs: config selection | outputs: reference derivation policy | preconditions: Cycle/Generation fire | postconditions: policy applied | state_effects: reference derivation
- formula: NONE | units: policy | invariants: TERMINAL_EXECUTION default; four options only
- failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0268 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0092 — All four derivations execution-grounded (never raw last-tick/trigger price)
- section: §5.4 Cycle Reference Price | lines: L426 | type: GUARD | strength: MUST | tag: [DD][DEFINED]
- wording: "All four remain execution-grounded (never a raw last-tick/trigger price)."
- inputs: derivation options | outputs: execution-grounded reference | preconditions: derivation | postconditions: never raw tick | state_effects: NONE
- formula: NONE | units: NONE | invariants: execution-grounded only | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0091 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0093 — Tick rounding applied at Level-price conversion, not capture; reference stored full precision
- section: §5.4 Cycle Reference Price | lines: L426 | type: GUARD | strength: MUST | tag: [DD][DEFINED]
- wording: "Tick-size rounding applies when converting to Level prices, not at capture time — the reference is stored at full precision."
- inputs: reference capture | outputs: full-precision reference | preconditions: capture | postconditions: rounding deferred to level conversion | state_effects: reference precision
- formula: NONE | units: price | invariants: full precision at capture (precision rule; cf. §6.3 STR-0135) | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0135 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0094 — Selected reference policy is configuration and MUST be explicit
- section: §5.4 Cycle Reference Price | lines: L426 | type: GUARD | strength: MUST | tag: [DD][DEFINED]
- wording: "The selected policy is configuration and MUST be explicit."
- inputs: config | outputs: explicit policy | preconditions: config load | postconditions: explicit policy set | state_effects: config
- formula: NONE | units: NONE | invariants: explicit config required | failure_behavior: fail-closed if unset | safety_impact: MEDIUM
- dependencies: STR-0091 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0095 — At fire, captured reference additionally gated by §5.4.1 tolerance
- section: §5.4 Cycle Reference Price | lines: L426 | type: GUARD | strength: MUST | tag: [DD][DEFINED]
- wording: "At the moment a new Cycle or Generation fires, the captured reference is additionally gated by the §5.4.1 reference-price tolerance."
- inputs: captured reference; §5.4.1 | outputs: gated reference | preconditions: fire | postconditions: reference within tolerance | state_effects: NONE
- formula: NONE | units: NONE | invariants: tolerance gate at fire | failure_behavior: BLOCKED if exceeded | safety_impact: HIGH
- dependencies: STR-0096 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §5.4.1 Reference-Price Tolerance at Cycle/Generation Fire (L428–L471)

### STR-0096 — [DYN] ReferencePriceToleranceBps := 0.33 × StepBps; captured reference must lie within tolerance
- section: §5.4.1 Reference-Price Tolerance | lines: L431–L438 | type: FORMULA | strength: MUST | tag: [DYN][DEFINED]
- wording: "ReferencePriceToleranceBps := 0.33 × StepBps … |captured_reference_price − nominal_reference_price| ≤ ReferencePriceToleranceBps / 10000 × nominal_reference_price"
- inputs: StepBps; captured & nominal reference | outputs: within/exceeds | preconditions: fire | postconditions: gate evaluated | state_effects: reference gate
- formula: ReferencePriceToleranceBps = 0.33 × StepBps; band = ±(tol/10000)×nominal | units: bps
- invariants: coefficient strictly <1.0 | failure_behavior: BLOCKED if exceeded | safety_impact: HIGH
- dynamic_note: must remain dynamic — never freeze to a constant (D-17; DYNAMIC-CALIBRATABLE; canonical PARAMETER: STR-0341)
- dependencies: STR-0261, STR-0341 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0097 — Within tolerance: fire normally, use captured reference as-is, log deviation
- section: §5.4.1 Reference-Price Tolerance | lines: L440–L443 | type: STATE_TRANSITION | strength: MUST | tag: [DYN][DEFINED]
- wording: "If the captured reference price is within this tolerance: the Cycle/Generation fires normally; the captured reference price is used as-is (§5.4); the event is logged with the deviation magnitude"
- inputs: within-tolerance reference | outputs: normal fire + log | preconditions: within band | postconditions: fires; deviation logged | state_effects: transition + audit log
- formula: NONE | units: bps | invariants: log deviation for audit | failure_behavior: NONE | safety_impact: MEDIUM
- dynamic_note: must remain dynamic — never freeze to a constant (D-17)
- dependencies: STR-0096 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0098 — Exceeds tolerance: BLOCKED fail-closed, no ladder issuance, RECONCILIATION_REQUIRED, no fallback, re-eval next pass
- section: §5.4.1 Reference-Price Tolerance | lines: L445–L452 | type: FAILURE_BEHAVIOR | strength: MUST | tag: [DYN][DEFINED]
- wording: "If the captured reference price exceeds this tolerance: the transition is BLOCKED (fail-closed) … a RECONCILIATION_REQUIRED condition is raised; no fallback reference price is auto-selected; the transition is re-evaluated on the next pass after reconciliation (§4.7 P0)."
- inputs: out-of-band reference | outputs: BLOCKED | preconditions: exceeds tolerance | postconditions: no capture/ladder; RECONCILIATION_REQUIRED | state_effects: block; reconciliation
- formula: NONE | units: NONE | invariants: no auto fallback reference | failure_behavior: BLOCKED; RECONCILIATION_REQUIRED; fail-closed | safety_impact: HIGH
- dynamic_note: must remain dynamic — never freeze to a constant (D-17)
- dependencies: STR-0096, STR-0064 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0099 — §5.6 non-overlap remains authoritative structural check; reference tolerance gates capture upstream; both must pass
- section: §5.4.1 Reference-Price Tolerance | lines: L454–L458 | type: GUARD | strength: MUST | tag: [DYN][DEFINED]
- wording: "the non-overlap test (§5.6) remains the authoritative structural check … it gates the reference capture itself, upstream of ladder construction. Both must pass for a transition to complete."
- inputs: §5.4.1 gate; §5.6 test | outputs: combined gating | preconditions: transition | postconditions: both pass | state_effects: NONE
- formula: NONE | units: NONE | invariants: reference tolerance ≠ replacement for §5.6 | failure_behavior: BLOCKED if either fails | safety_impact: HIGH
- dynamic_note: references the dynamic ReferencePriceToleranceBps (D-17) — that tolerance must remain dynamic; never freeze to a constant (canonical: STR-0341)
- dependencies: STR-0096, STR-0104 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0100 — 0.33 coefficient DYNAMIC-CALIBRATABLE, strictly <1.0 so reference cannot drift a full step
- section: §5.4.1 Reference-Price Tolerance | lines: L465–L467 | type: PARAMETER | strength: MUST | tag: [DYN][DEFINED]
- wording: "The 0.33 coefficient is DYNAMIC-CALIBRATABLE (proposal-only per §14 global rule). It is strictly smaller than 1.0 by construction, so a captured reference can never drift a full step and violate §5.6."
- inputs: coefficient 0.33 | outputs: bounded tolerance | preconditions: NONE | postconditions: tolerance <1 step | state_effects: NONE
- formula: coefficient = 0.33 (<1.0) | units: ratio
- invariants: strictly <1.0 by construction | failure_behavior: NONE | safety_impact: MEDIUM
- dynamic_note: must remain dynamic — never freeze to a constant (D-17; proposal-only per §14 global rule)
- dependencies: STR-0096, STR-0292 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §5.5 Generation vs. Cycle — formal distinction (L472–L487)

### STR-0101 — GENERATION question: verified path-dependent traversal-and-return → new epoch (old survives)
- section: §5.5 Generation vs. Cycle | lines: L474–L479 | type: EVENT_SEMANTICS | strength: MUST | tag: [DD][DEFINED]
- wording: "GENERATION asks: 'Has the market completed a verified path-dependent traversal-and-return, so that a strategic successor epoch should begin?' → path-dependent return (§4.1) → new epoch; old epoch survives"
- inputs: traversal-and-return | outputs: new epoch | preconditions: verified return | postconditions: successor epoch; old survives | state_effects: new Generation
- formula: NONE | units: NONE | invariants: old epoch survives (SUCCESSOR_CREATED then DISABLED_AT_CYCLE_99) | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0025 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0102 — CYCLE question: single-group terminal reach → new traversal, same epoch
- section: §5.5 Generation vs. Cycle | lines: L481–L483 | type: EVENT_SEMANTICS | strength: MUST | tag: [DD][DEFINED]
- wording: "CYCLE asks: 'Has the ladder in ONE direction been fully consumed, requiring a fresh anchor?' → single-group terminal reach (§5.1) → new traversal, SAME epoch."
- inputs: single-group terminal reach | outputs: new Cycle | preconditions: terminal event | postconditions: new traversal same epoch | state_effects: new Cycle
- formula: NONE | units: NONE | invariants: same Generation | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0071 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0103 — Cycle numbering restarts at 0 per Generation; Generation and Cycle counters are independent axes
- section: §5.5 Generation vs. Cycle | lines: L486 | type: IDENTITY_RULE | strength: MUST | tag: [UR][DEFINED]
- wording: "Cycle numbering restarts at 0 for every new Generation; Generation and Cycle counters are independent axes (§3)"
- inputs: NONE | outputs: counters | preconditions: new Generation | postconditions: CycleID resets to 0 | state_effects: counter reset
- formula: NONE | units: count | invariants: independent axes | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0016 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §5.6 Ladder Non-Overlap Test (L488–L512)

### STR-0104 — Non-overlap is a computable gate (no longer OQ-dependent)
- section: §5.6 Ladder Non-Overlap Test | lines: L490 | type: GUARD | strength: MUST | tag: [DD][DEFINED]
- wording: "The v1.0 invariant 'Cycle transition must not create unintended level overlap' is now a computable gate, no longer OQ-dependent"
- inputs: new ladder | outputs: pass/fail | preconditions: ladder issuance | postconditions: overlap computed | state_effects: gate
- formula: NONE (N1–N3) | units: NONE | invariants: computable, deterministic | failure_behavior: BLOCKED on fail | safety_impact: HIGH
- dependencies: STR-0105, STR-0106, STR-0107 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0105 — N1: new level prices strictly monotonic in level index in traversal direction
- section: §5.6 Ladder Non-Overlap Test | lines: L494–L495 | type: GUARD | strength: MUST | tag: [DD][DEFINED]
- wording: "Every new level price MUST be strictly monotonic in level index in the traversal direction (BU ascending, SL descending)."
- inputs: new level prices | outputs: monotonicity check | preconditions: ladder built | postconditions: strictly monotonic | state_effects: NONE
- formula: BU ascending, SL descending, strict | units: price | invariants: strict monotonicity | failure_behavior: BLOCKED | safety_impact: HIGH
- dependencies: STR-0104 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0106 — N2: new Level-1 strictly beyond old Cycle's terminal execution price (>0 ticks)
- section: §5.6 Ladder Non-Overlap Test | lines: L496–L500 | type: GUARD | strength: MUST | tag: [DD][DEFINED]
- wording: "The new Level-1 price MUST lie strictly beyond the old Cycle's terminal-level execution price by more than zero ticks … no new level price may lie within the closed interval spanned by the old Cycle's reference price and the old terminal execution price."
- inputs: new Level-1 price; old terminal exec price; old reference | outputs: check | preconditions: ladder built | postconditions: no overlap with old interval | state_effects: NONE
- formula: new_L1 strictly beyond old terminal exec by >0 ticks | units: price/ticks | invariants: no level within old [reference, terminal] interval | failure_behavior: BLOCKED | safety_impact: HIGH
- dependencies: STR-0104 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0107 — N3: no new level price equals a still-live same-group level price within same Generation
- section: §5.6 Ladder Non-Overlap Test | lines: L501–L502 | type: GUARD | strength: MUST_NOT | tag: [DD][DEFINED]
- wording: "No new level price may equal any still-live level price of the same group within the same Generation."
- inputs: new prices; still-live same-group prices | outputs: check | preconditions: ladder built | postconditions: no equal live price | state_effects: NONE
- formula: NONE | units: price | invariants: no price collision within group+Generation | failure_behavior: BLOCKED | safety_impact: HIGH
- dependencies: STR-0104 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0108 — On N1–N3 failure: BLOCKED fail-closed, RECONCILIATION_REQUIRED, no fallback; structural infeasibility is a config error at validation time
- section: §5.6 Ladder Non-Overlap Test | lines: L506–L510 | type: FAILURE_BEHAVIOR | strength: MUST | tag: [DD][DEFINED]
- wording: "On failure of N1–N3: the Cycle transition is BLOCKED (fail-closed, §5.2 step 4); RECONCILIATION_REQUIRED is raised; no fallback reference derivation is auto-selected. If the configured derivation structurally cannot satisfy N1–N3 … that is a configuration error surfaced at validation time"
- inputs: N1–N3 result | outputs: BLOCKED / config error | preconditions: failure | postconditions: no fallback; reconciliation | state_effects: RECONCILIATION_REQUIRED
- formula: NONE | units: NONE | invariants: no auto fallback derivation | failure_behavior: BLOCKED; RECONCILIATION_REQUIRED; config error at validation | safety_impact: HIGH
- dependencies: STR-0104, STR-0077 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §5.7 Normative Generation/Cycle scenarios (L513–L555) — Scenarios 01–20

> Each is a normative interpretation pin (`[UR][DEFINED]`). Fields compressed to: initial/sequence → expected outcome. All `SCENARIO`, strength MUST.

### STR-0109 — Scenario 01: no verified traversal → no Generation; continue G0-C0
- section: §5.7 Scenario 01 | lines: L516 | type: SCENARIO | strength: MUST | tag: [UR][DEFINED]
- wording: "No verified traversal → no Generation; continue G0-C0."
- inputs: no verified traversal | outputs: no Generation | preconditions: G0-C0 active | postconditions: continue G0-C0 | state_effects: none
- formula: NONE | units: NONE | invariants: no Generation without verified traversal | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0026 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0110 — Scenario 02: SL1→SL2 verified, no return → no Generation
- section: §5.7 Scenario 02 | lines: L517 | type: SCENARIO | strength: MUST | tag: [UR][DEFINED]
- wording: "SL1→SL2 verified, no return → no Generation."
- inputs: SL1,SL2 verified; no return | outputs: no Generation | preconditions: traversal only | postconditions: no Generation | state_effects: none
- formula: NONE | units: NONE | invariants: return required | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0029 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0111 — Scenario 03: SL2→BU1→BU2 verified, no terminal, no verified return → no Generation
- section: §5.7 Scenario 03 | lines: L518 | type: SCENARIO | strength: MUST | tag: [UR][DEFINED]
- wording: "SL2→BU1→BU2 verified, no terminal, no verified return → no Generation."
- inputs: partial cross-group traversal | outputs: no Generation | preconditions: no verified return | postconditions: no Generation | state_effects: none
- formula: NONE | units: NONE | invariants: penetration without return insufficient | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0034 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0112 — Scenario 04: SL2→BU1→BU2→ verified return to established SL2 → create G1-C0
- section: §5.7 Scenario 04 | lines: L519–L520 | type: SCENARIO | strength: MUST | tag: [UR][DEFINED]
- wording: "SL2→BU1→BU2→ verified return to established SL2 → create G1-C0 [DEFINED, D-01/D-02 approved]."
- inputs: traversal + verified return to established level | outputs: G1-C0 created | preconditions: §4.1 conditions met | postconditions: successor Generation | state_effects: new Generation
- formula: NONE | units: NONE | invariants: canonical Evolution trigger | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0025, STR-0029, STR-0030 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0113 — Scenario 05: raw price touch of return level → no Generation; reconcile
- section: §5.7 Scenario 05 | lines: L521 | type: SCENARIO | strength: MUST | tag: [UR][DEFINED]
- wording: "Raw price touch of the return level → no Generation; reconcile."
- inputs: raw price touch | outputs: no Generation; reconcile | preconditions: unverified touch | postconditions: reconcile | state_effects: reconciliation
- formula: NONE | units: NONE | invariants: raw crossing insufficient | failure_behavior: reconcile | safety_impact: HIGH
- dependencies: STR-0033, STR-0073 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0114 — Scenario 06: return order acknowledged, delta unverified → no Generation; RECONCILIATION_REQUIRED or wait POSITION_VERIFIED
- section: §5.7 Scenario 06 | lines: L522–L523 | type: SCENARIO | strength: MUST | tag: [UR][DEFINED]
- wording: "Return order acknowledged, delta unverified → no Generation; RECONCILIATION_REQUIRED or wait for POSITION_VERIFIED."
- inputs: ack without delta | outputs: no Generation | preconditions: delta unverified | postconditions: reconcile/wait | state_effects: RECONCILIATION_REQUIRED
- formula: NONE | units: NONE | invariants: ack insufficient | failure_behavior: RECONCILIATION_REQUIRED | safety_impact: HIGH
- dependencies: STR-0073 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0115 — Scenario 07: partial return verification → no Generation; mirror verified exposure, manage remainder
- section: §5.7 Scenario 07 | lines: L524–L525 | type: SCENARIO | strength: MUST | tag: [UR][DEFINED]
- wording: "Partial return verification → no Generation; mirror verified exposure, manage remainder."
- inputs: partial verification | outputs: no Generation; mirror + manage | preconditions: partial | postconditions: mirror verified exposure | state_effects: mirroring
- formula: NONE | units: NONE | invariants: partial return insufficient | failure_behavior: no Generation | safety_impact: HIGH
- dependencies: STR-0035, STR-0208 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0116 — Scenario 08: BU6 verified (terminal) → complete C0; create G0-C1; no new Generation
- section: §5.7 Scenario 08 | lines: L526 | type: SCENARIO | strength: MUST | tag: [UR][DEFINED]
- wording: "BU6 verified (terminal) → complete C0; create G0-C1. No new Generation."
- inputs: terminal BU6 verified | outputs: G0-C1 | preconditions: terminal event | postconditions: new Cycle same Generation | state_effects: Cycle transition
- formula: NONE | units: NONE | invariants: terminal reach → Cycle not Generation | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0074 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0117 — Scenario 09: BU6 terminal with pending orders → cancel relevant pending, reconcile, create G0-C1; no Generation change
- section: §5.7 Scenario 09 | lines: L527–L528 | type: SCENARIO | strength: MUST | tag: [UR][DEFINED]
- wording: "BU6 terminal with pending orders → cancel relevant pending orders, reconcile, create G0-C1. No Generation change."
- inputs: terminal + pending | outputs: G0-C1 | preconditions: terminal event | postconditions: cancel+reconcile+new Cycle | state_effects: cancellation, reconciliation, Cycle transition
- formula: NONE | units: NONE | invariants: cancel exhausted-side pending | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0075, STR-0076, STR-0078 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0118 — Scenario 10: BU6 terminal in C0, verified return in C1 → G1-C0; G0 passive/locked; separate events
- section: §5.7 Scenario 10 | lines: L529–L530 | type: SCENARIO | strength: MUST | tag: [UR][DEFINED]
- wording: "BU6 terminal in C0, verified return in C1 → G1-C0 created; G0 passive/locked. Cycle and Generation transitions remain separate events."
- inputs: terminal then verified return | outputs: G1-C0 | preconditions: separate events | postconditions: successor Generation; G0 locked | state_effects: Cycle + Generation transitions
- formula: NONE | units: NONE | invariants: Cycle and Generation are separate events | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0074, STR-0025 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0119 — Scenario 11: G0 creates G1 at C0 → G0 SUCCESSOR_CREATED; no G2 from C1..98
- section: §5.7 Scenario 11 | lines: L531 | type: SCENARIO | strength: MUST | tag: [UR][DEFINED]
- wording: "G0 creates G1 at C0 → G0 enters SUCCESSOR_CREATED; no G2 from C1..98."
- inputs: G0→G1 | outputs: lock | preconditions: successor created | postconditions: no G2 from G0 | state_effects: SUCCESSOR_CREATED
- formula: NONE | units: NONE | invariants: one successor | failure_behavior: successor blocked | safety_impact: HIGH
- dependencies: STR-0050, STR-0051 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0120 — Scenario 12: G0-C2 attempts another Evolution → rejected (SUCCESSOR_LOCK_ACTIVE); recorded ineligible
- section: §5.7 Scenario 12 | lines: L532–L533 | type: SCENARIO | strength: MUST | tag: [UR][DEFINED]
- wording: "G0-C2 attempts another Evolution → rejected (SUCCESSOR_LOCK_ACTIVE); apparent path recorded as ineligible candidate."
- inputs: Evolution attempt under lock | outputs: rejection | preconditions: lock active | postconditions: recorded ineligible | state_effects: INELIGIBLE_EVOLUTION_CANDIDATE
- formula: NONE | units: NONE | invariants: never silently executed | failure_behavior: INELIGIBLE_EVOLUTION_CANDIDATE (SUCCESSOR_LOCK_ACTIVE) | safety_impact: HIGH
- dependencies: STR-0054 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0121 — Scenario 13: G0-C50 after successor → valid terminal creates G0-C51; Generation creation prohibited
- section: §5.7 Scenario 13 | lines: L534–L535 | type: SCENARIO | strength: MUST | tag: [UR][DEFINED]
- wording: "G0-C50 after successor creation → valid terminal event creates G0-C51; Generation creation remains prohibited for G0."
- inputs: terminal in C50 | outputs: G0-C51 | preconditions: G0 SUCCESSOR_CREATED | postconditions: Cycle continues; no Generation | state_effects: Cycle transition
- formula: NONE | units: NONE | invariants: parent Cycle axis continues; no second successor | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0051, STR-0061 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0122 — Scenario 14: G0-C98 terminal verified → create G0-C99; Generation creation prohibited
- section: §5.7 Scenario 14 | lines: L536 | type: SCENARIO | strength: MUST | tag: [UR][DEFINED]
- wording: "G0-C98 terminal verified → create G0-C99; Generation creation prohibited."
- inputs: terminal C98 | outputs: G0-C99 | preconditions: below limit | postconditions: new Cycle | state_effects: Cycle transition
- formula: NONE | units: NONE | invariants: no Generation | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0074 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0123 — Scenario 15: G0-C99 terminal verified → G0 DISABLED_AT_CYCLE_99; no Cycle 100
- section: §5.7 Scenario 15 | lines: L537 | type: SCENARIO | strength: MUST | tag: [UR][DEFINED]
- wording: "G0-C99 terminal verified → G0 DISABLED_AT_CYCLE_99; no Cycle 100."
- inputs: terminal C99 | outputs: disabled | preconditions: at limit | postconditions: DISABLED_AT_CYCLE_99 | state_effects: disable
- formula: NONE | units: NONE | invariants: no Cycle 100 | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0084 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0124 — Scenario 16: disabled G0, BasketNetPnL below target → stays open, progression inactive; hedge/reconcile/manage only
- section: §5.7 Scenario 16 | lines: L538–L539 | type: SCENARIO | strength: MUST | tag: [UR][DEFINED]
- wording: "Disabled G0, BasketNetPnL below closure target → stays open, inactive for progression; hedge/reconciliation/management only."
- inputs: disabled; PnL<target | outputs: stays open | preconditions: below target | postconditions: management only | state_effects: none (management)
- formula: NONE | units: NONE | invariants: disabled ≠ closed | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0088, STR-0255 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0125 — Scenario 17: disabled G0, ExposureDelta breaches acute threshold → Hedge Recovery priority; Profit stays disabled
- section: §5.7 Scenario 17 | lines: L540–L541 | type: SCENARIO | strength: MUST | tag: [UR][DEFINED]
- wording: "Disabled G0, ExposureDelta breaches acute threshold → Hedge Recovery takes priority; bounded urgent correction; Profit Layer stays disabled."
- inputs: acute ExposureDelta | outputs: Hedge Recovery | preconditions: acute breach | postconditions: bounded correction | state_effects: hedge recovery
- formula: NONE | units: NONE | invariants: hedge priority; progression stays disabled | failure_behavior: Hedge Recovery | safety_impact: CRITICAL
- dependencies: STR-0206, STR-0088 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0126 — Scenario 18: G1 own eligible traversal+return → create G2-C0; G1 SUCCESSOR_CREATED; G0 lock does not block G1
- section: §5.7 Scenario 18 | lines: L542–L543 | type: SCENARIO | strength: MUST | tag: [UR][DEFINED]
- wording: "G1 performs its own eligible traversal+return → create G2-C0; G1 enters SUCCESSOR_CREATED. G0's lock does not block G1."
- inputs: G1 verified return | outputs: G2-C0 | preconditions: G1 eligible | postconditions: G2 created | state_effects: new Generation; G1 lock
- formula: NONE | units: NONE | invariants: locks independent per Generation | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0053 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0127 — Scenario 19: G99 otherwise-valid Evolution → rejected (GENERATION_ID_LIMIT); never wraps; progression continues per §4.6
- section: §5.7 Scenario 19 | lines: L544–L545 | type: SCENARIO | strength: MUST | tag: [UR][DEFINED]
- wording: "G99 otherwise-valid Evolution → rejected (GENERATION_ID_LIMIT); recorded; never wraps to G0; progression continues per §4.6."
- inputs: Evolution at G99 | outputs: rejection | preconditions: GenerationID=99 | postconditions: no G100; no wrap | state_effects: INELIGIBLE_EVOLUTION_CANDIDATE
- formula: NONE | units: NONE | invariants: no wrap to G0 | failure_behavior: INELIGIBLE_EVOLUTION_CANDIDATE (GENERATION_ID_LIMIT) | safety_impact: HIGH
- dependencies: STR-0058 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0128 — Scenario 20: G99-C99 terminal + BasketNetPnL reaches target → run §13.4; CLOSED only after net-profit AND residual-exposure pass
- section: §5.7 Scenario 20 | lines: L546–L552 | type: SCENARIO | strength: MUST | tag: [UR][DEFINED]
- wording: "G99-C99 terminal verified; BasketNetPnL reaches the approved closure target (D-06 formula) → run §13.4 closure sequence; Basket CLOSED only after both the net-profit condition and verified residual-exposure condition pass"
- inputs: G99-C99 terminal; PnL≥target | outputs: closure sequence | preconditions: both conditions | postconditions: CLOSED only after both pass | state_effects: Basket closure
- formula: NONE | units: NONE | invariants: closure requires both conditions | failure_behavior: not closed unless both pass | safety_impact: CRITICAL
- dependencies: STR-0243, STR-0244, STR-0248 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §6.1 State pipeline (L558–L571)

### STR-0129 — Execution state pipeline (INTENT_CREATED → … → POSITION_VERIFIED; plus CANCELLED/EMERGENCY/SKIPPED/ERROR; LOCKED→IDLE)
- section: §6.1 State pipeline | lines: L560–L568 | type: LIFECYCLE_STATE | strength: MUST | tag: [SD][HC][DEFINED]
- wording: "INTENT_CREATED → ORDER_SUBMITTED → ORDER_ACKNOWLEDGED → ORDER_ACTIVE → PARTIALLY_FILLED → FILLED → POSITION_VERIFIED ↘ CANCELLED → EMERGENCY … → SKIPPED … → ERROR … Protection-locked levels additionally start: LOCKED → IDLE"
- inputs: order events; authoritative reads | outputs: level/order state | preconditions: intent created | postconditions: state ∈ pipeline | state_effects: order/level state machine
- formula: NONE | units: NONE | invariants: POSITION_VERIFIED is terminal verified state
- failure_behavior: EMERGENCY / SKIPPED / ERROR / CANCELLED per branch | safety_impact: HIGH
- venue_evidence_status: VERIFIED (Phase 2/2b — orderUpdates + orderStatus + REST ack)
- venue_evidence_refs: [SRC-104, SRC-105, SRC-109]
- dependencies: STR-0131 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0130 — EMERGENCY (trigger-without-fill) and SKIPPED (tolerance/economics fail) are first-class states
- section: §6.1 State pipeline | lines: L565–L566 | type: EVENT_SEMANTICS | strength: MUST | tag: [SD][DEFINED]
- wording: "EMERGENCY (trigger-without-fill) → SKIPPED (tolerance/economics fail)"
- inputs: trigger without fill; tolerance/economics fail | outputs: EMERGENCY/SKIPPED | preconditions: pipeline active | postconditions: state set | state_effects: EMERGENCY, SKIPPED
- formula: NONE | units: NONE | invariants: SKIPPED terminal, contributes zero | failure_behavior: SKIPPED / EMERGENCY | safety_impact: HIGH
- dependencies: STR-0182, STR-0190 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0131 — Hard rule: LEVEL FILLED ⇔ ORDER FILLED ∧ POSITION DELTA VERIFIED
- section: §6.1 State pipeline | lines: L570 | type: INVARIANT | strength: MUST | tag: [SD][DEFINED]
- wording: "LEVEL FILLED ⇔ ORDER FILLED ∧ POSITION DELTA VERIFIED."
- inputs: order fill; position delta | outputs: FILLED status | preconditions: both present | postconditions: level FILLED only when both hold | state_effects: FILLED gating
- formula: LEVEL FILLED ⇔ ORDER FILLED ∧ POSITION DELTA VERIFIED | units: NONE | invariants: core system invariant
- failure_behavior: not FILLED if either missing | safety_impact: CRITICAL
- dependencies: STR-0004 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0132 — No FILLED from bare userFills/REST ack alone; authoritative position read must confirm delta
- section: §6.1 State pipeline | lines: L570 | type: GUARD | strength: MUST_NOT | tag: [SD][HC][DEFINED]
- wording: "No state reaches FILLED … from a bare userFills message or REST ack alone — a subsequent authoritative position-state read (clearinghouseState/webData2) must confirm the delta."
- inputs: userFills; REST ack; authoritative read | outputs: confirmed/unconfirmed | preconditions: fill signal | postconditions: FILLED only after authoritative confirm | state_effects: verification gate
- formula: NONE | units: NONE | invariants: authoritative read required | failure_behavior: not FILLED without authoritative confirm | safety_impact: CRITICAL
- venue_evidence_status: VERIFIED (Phase 2/2b — orderStatus + clearinghouseState authoritative; userFills alone insufficient. Authority source = clearinghouseState; webData2/3 nuance in CONFLICT-002/GATE-002, non-blocking)
- venue_evidence_refs: [SRC-105, SRC-107, SRC-109]
- dependencies: STR-0131, STR-0133 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §6.2 Hyperliquid mechanisms relied on (L572–L575)

### STR-0133 — Venue mechanisms relied on (cloid, REST ack, orderStatus, WS orderUpdates/userFills, REST userFills history ≤10,000, clearinghouseState/webData2, TIF Gtc/Ioc/Alo)
- section: §6.2 Hyperliquid mechanisms | lines: L574 | type: EVENT_SEMANTICS | strength: MUST | tag: [HC][DEFINED]
- wording: "cloid (128-bit client order ID, idempotent order identity) · REST POST /exchange ack (resting/filled/error) · orderStatus info endpoint · WS orderUpdates · WS userFills … REST userFills/userFillsByTime (durable history, ≤10,000 retained) · clearinghouseState/webData2 … TIF: Gtc/Ioc/Alo"
- inputs: venue APIs | outputs: relied-on mechanisms | preconditions: venue integration | postconditions: mechanisms available | state_effects: adapter dependencies
- formula: NONE | units: NONE (history retained ≤10,000) | invariants: cloid idempotent identity
- failure_behavior: NONE | safety_impact: HIGH
- venue_evidence_status: VERIFIED (Phase 2/2b — cloid 128-bit, ack resting/filled/error, orderStatus, WS orderUpdates, WS userFills snapshot-tagged, userFillsByTime ≤10000, TIF Alo/Gtc/Ioc all confirmed. Note: cloid duplicate-submission de-dup is NOT documented — deferred observation item; does not affect the enumerated mechanisms)
- venue_evidence_refs: [SRC-104, SRC-105, SRC-107, SRC-109, SRC-110]
- dependencies: NONE | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0134 — Trigger orders evaluated against oracle mark price, not last trade
- section: §6.2 Hyperliquid mechanisms | lines: L574 | type: EVENT_SEMANTICS | strength: MUST | tag: [HC][DEFINED]
- wording: "trigger orders evaluated against oracle mark price, not last trade."
- inputs: trigger orders; oracle mark price | outputs: trigger evaluation | preconditions: trigger order active | postconditions: evaluated vs oracle mark | state_effects: trigger semantics
- formula: NONE | units: price | invariants: oracle mark (not last trade) governs triggers
- failure_behavior: NONE | safety_impact: HIGH
- venue_evidence_status: VERIFIED (Phase 2b — robust-price-indices: mark price triggers TP/SL, not last trade; "oracle mark" maps to venue mark price which incorporates oracle+book+CEX. CONFLICT-003 RESOLVED)
- venue_evidence_refs: [SRC-112, SRC-117, SRC-118]
- dependencies: STR-0133 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §6.3 Precision (L576–L581)

### STR-0135 — Price precision: ≤5 significant figures AND ≤(MAX_DECIMALS−szDecimals) decimals, MAX_DECIMALS=6 for perps
- section: §6.3 Precision | lines: L578 | type: FORMULA | strength: MUST | tag: [HC][DEFINED]
- wording: "Prices: ≤5 significant figures and ≤ (MAX_DECIMALS − szDecimals) decimal places, MAX_DECIMALS = 6 for perps"
- inputs: price; szDecimals; MAX_DECIMALS=6 | outputs: normalized price | preconditions: order build | postconditions: price within precision | state_effects: price normalization
- formula: decimals ≤ (6 − szDecimals); sig figs ≤ 5 | units: sig figs / decimal places | invariants: precision compliance
- failure_behavior: fail-closed (normalize before signing; else exchange reject) | safety_impact: HIGH
- venue_evidence_status: VERIFIED (Phase 2 — tick-and-lot-size confirms ≤5 sig figs, ≤(6−szDecimals) decimals, MAX_DECIMALS=6 perps)
- venue_evidence_refs: [SRC-108]
- dependencies: STR-0138 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0136 — Integer prices always valid
- section: §6.3 Precision | lines: L578 | type: GUARD | strength: MUST | tag: [HC][DEFINED]
- wording: "integer prices always valid"
- inputs: integer price | outputs: valid price | preconditions: order build | postconditions: integer accepted | state_effects: NONE
- formula: NONE | units: price | invariants: integer prices exempt from decimal rule
- failure_behavior: NONE | safety_impact: MEDIUM
- venue_evidence_status: VERIFIED (Phase 2 — tick-and-lot-size: "Integer prices are always allowed")
- venue_evidence_refs: [SRC-108]
- dependencies: STR-0135 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0137 — Size precision: sizes rounded to the asset's szDecimals (from meta)
- section: §6.3 Precision | lines: L578 | type: FORMULA | strength: MUST | tag: [HC][DEFINED]
- wording: "Sizes: rounded to the asset's szDecimals (from meta)."
- inputs: size; szDecimals (from meta) | outputs: normalized size | preconditions: order build | postconditions: size at szDecimals | state_effects: size normalization
- formula: size rounded to szDecimals | units: base-asset size | invariants: precision compliance
- failure_behavior: fail-closed | safety_impact: HIGH
- venue_evidence_status: VERIFIED (Phase 2 — sizes rounded to szDecimals from meta.universe; BTC 5, ETH 4)
- venue_evidence_refs: [SRC-108, SRC-107]
- dependencies: STR-0138 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0138 — Normalization happens in the Execution Engine before every signed order (never exchange reject-and-retry)
- section: §6.3 Precision | lines: L578 | type: GUARD | strength: MUST | tag: [HC][DD][DEFINED]
- wording: "Normalization happens in the Execution Engine before every signed order — never left to the exchange to reject-and-retry (this is the single most common third-party-SDK bug class on this venue)."
- inputs: raw price/size | outputs: normalized order | preconditions: before signing | postconditions: normalized before submission | state_effects: pre-sign normalization
- formula: NONE | units: NONE | invariants: normalize before signing; price/size normalized before signing (§15)
- failure_behavior: fail-closed (do not rely on exchange rejection) | safety_impact: HIGH
- venue_evidence_status: VERIFIED (Phase 2/2b — tick-and-lot-size precision + signing: trailing zeros/precision must be handled client-side before signing; tickRejected exists)
- venue_evidence_refs: [SRC-108, SRC-119]
- dependencies: STR-0135, STR-0137 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §7.1 Distance model (L584–L650)

### STR-0139 — Distances in bps, converted to absolute price at order-build then tick-rounded; pips/absolute/percentage rejected
- section: §7.1 Distance model | lines: L586–L591 | type: FORMULA | strength: MUST | tag: [DD][DEFINED]
- wording: "Basis points (bps), not pips — converted to an absolute price at order-build time, then tick-rounded (§6.3). Rejected: absolute price distance … plain percentage"
- inputs: bps distance; mark price | outputs: absolute price | preconditions: order build | postconditions: tick-rounded absolute price | state_effects: price computation
- formula: absolute_price = f(bps, reference); then tick-round (§6.3) | units: bps
- invariants: bps convention; tick-round at build | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0135 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0140 — StepBps = 10 (approved default; calibratable)
- section: §7.1 Distance model | lines: L594–L598 | type: PARAMETER | strength: MUST | tag: [DD][DEFINED]
- wording: "StepBps = 10 (approved default; calibratable per §14 D-09 Group E, except as noted)"
- inputs: config | outputs: StepBps | preconditions: NONE | postconditions: StepBps set | state_effects: geometry anchor
- formula: NONE | units: bps (10) | invariants: base anchor for bps-derived defaults
- failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: NONE | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0141 — GridLevels = 6 (approved; NOT calibratable, hard-excluded from optimizer)
- section: §7.1 Distance model | lines: L595–L598 | type: PARAMETER | strength: MUST | tag: [DD][DEFINED]
- wording: "GridLevels = 6 (approved; NOT calibratable — hard-excluded from the optimizer allowlist per §14 D-09 Group E)"
- inputs: config | outputs: GridLevels | preconditions: NONE | postconditions: N=6 | state_effects: ladder size
- formula: NONE | units: count (6; arch max 12) | invariants: NOT calibratable
- failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: NONE | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0142 — FirstLevelDistanceBps = 2 × StepBps = 20 (approved default)
- section: §7.1 Distance model | lines: L597 | type: PARAMETER | strength: MUST | tag: [DD][DEFINED]
- wording: "FirstLevelDistanceBps = 2 × StepBps = 20 (approved default)"
- inputs: StepBps | outputs: FirstLevelDistanceBps | preconditions: StepBps set | postconditions: FLD=2×StepBps | state_effects: L1 distance
- formula: FirstLevelDistanceBps = 2 × StepBps | units: bps (20 at default)
- invariants: composes from StepBps | failure_behavior: NONE | safety_impact: LOW
- dependencies: STR-0140 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0143 — Level-1 distance rule (G0 & every continuation Cycle): both groups' L1 at FirstLevelDistanceBps; Levels 2..N at StepBps
- section: §7.1 Distance model | lines: L602–L610 | type: FORMULA | strength: MUST | tag: [SD][DEFINED]
- wording: "For every Cycle of Generation 0, and for every continuation Cycle … Level 1 of BOTH groups is placed FirstLevelDistanceBps from that Cycle's reference price … Levels 2..N use normal StepBps spacing from the preceding level of the same group."
- inputs: reference; FirstLevelDistanceBps; StepBps | outputs: level prices | preconditions: G0 or continuation Cycle | postconditions: L1 at FLD; L2..N at StepBps | state_effects: ladder geometry
- formula: L1 = reference ± FirstLevelDistanceBps; Lk = L(k-1) ± StepBps | units: bps
- invariants: symmetric L1 for both groups in G0/continuation | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0142, STR-0010 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0144 — Successor Generation asymmetric posture persists for Generation lifetime; dominant fixed at Evolution time
- section: §7.1 Distance model | lines: L611–L614 | type: FORMULA | strength: MUST | tag: [SD][DEFINED]
- wording: "Successor Generation (post-Evolution) Cycle 0 AND every subsequent Cycle … the asymmetric posture persists for the Generation's lifetime, with the dominant side fixed at Evolution time (§4.5) and never recomputed per Cycle"
- inputs: dominance (§4.5) | outputs: asymmetric geometry | preconditions: successor Generation | postconditions: asymmetry all Cycles | state_effects: geometry
- formula: NONE | units: NONE | invariants: dominant fixed at Evolution time | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0056 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0145 — Successor dominant side Level-1 = Gen2DistanceMultiplier × StepBps from reference; subsequent +StepBps
- section: §7.1 Distance model | lines: L615–L631 | type: FORMULA | strength: MUST | tag: [SD][DD][DEFINED]
- wording: "Dominant side: BU1 = Gen2DistanceMultiplier × StepBps from reference; BU2 = BU1 + StepBps; BU3+ = previous level + StepBps"
- inputs: reference; Gen2DistanceMultiplier; StepBps | outputs: dominant level prices | preconditions: successor Generation | postconditions: dominant ladder | state_effects: geometry
- formula: L1_dom = Gen2DistanceMultiplier × StepBps; Lk = L(k-1) + StepBps | units: bps
- invariants: composes from anchors | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0149 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0146 — Successor weak side Level-1 = WeakSideFirstLevelMultiplier × StepBps; LOCKED until weak Level-2 fills (POSITION_VERIFIED), re-applied per Cycle
- section: §7.1 Distance model | lines: L617–L634 | type: GUARD | strength: MUST | tag: [SD][DD][DEFINED]
- wording: "Weak side's Level 1: LOCKED until weak side's Level 2 fills (POSITION_VERIFIED) — re-applied per Cycle ladder … SL1 = WeakSideFirstLevelMultiplier × StepBps from reference — LOCKED until SL2 fills"
- inputs: WeakSideFirstLevelMultiplier; StepBps; weak L2 fill | outputs: weak L1 (locked) | preconditions: successor Generation | postconditions: L1 locked until L2 POSITION_VERIFIED | state_effects: LOCKED state
- formula: L1_weak = WeakSideFirstLevelMultiplier × StepBps; LOCKED until L2 verified | units: bps
- invariants: unlock only on weak L2 POSITION_VERIFIED | failure_behavior: stays LOCKED | safety_impact: MEDIUM
- dependencies: STR-0149, STR-0072 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0147 — Successor weak side Level-2 READY (unlock trigger); all other levels normal StepBps
- section: §7.1 Distance model | lines: L618–L636 | type: STATE_TRANSITION | strength: MUST | tag: [SD][DD][DEFINED]
- wording: "Weak side's Level 2: READY (unlock trigger) … SL2 = SL1 + StepBps — READY (unlock trigger); SL3+ = previous level + StepBps"
- inputs: weak L2 | outputs: unlock trigger | preconditions: successor Generation | postconditions: L2 ready; unlocks L1 on fill | state_effects: READY / unlock
- formula: L2_weak = L1_weak + StepBps; Lk = L(k-1) + StepBps | units: bps
- invariants: L2 is the unlock trigger | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0146 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0148 — Dominant-side volume (all levels) = Gen2SizeMultiplier × (MaxBasketNotional/GridLevels); weak side unchanged
- section: §7.1 Distance model | lines: L628–L637 | type: FORMULA | strength: MUST | tag: [DD][DEFINED]
- wording: "Volume of ALL dominant-side levels = Gen2SizeMultiplier × (MaxBasketNotional / GridLevels) … Weak side … Volume = MaxBasketNotional / GridLevels (unchanged vs. base levels)"
- inputs: Gen2SizeMultiplier; MaxBasketNotional; GridLevels | outputs: level volumes | preconditions: successor Generation | postconditions: dominant scaled; weak unchanged | state_effects: sizing
- formula: dom_vol = Gen2SizeMultiplier × (MaxBasketNotional/GridLevels); weak_vol = MaxBasketNotional/GridLevels | units: USD notional
- invariants: bounded by MaxLevelNotionalDominant / MaxLevelNotional | failure_behavior: reject on cap breach | safety_impact: HIGH
- dependencies: STR-0150, STR-0156 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0149 — Gen2DistanceMultiplier (default 2, range 1.1–2.0) and WeakSideFirstLevelMultiplier (default 2) are single-purpose distance scalers
- section: §7.1 Distance model | lines: L639–L646 | type: PARAMETER | strength: MUST | tag: [DD][DEFINED]
- wording: "Gen2DistanceMultiplier (approved default 2, approved range 1.1–2.0) — scales ONLY the dominant side's Level-1 distance; WeakSideFirstLevelMultiplier (approved default 2) — scales ONLY the weak side's Level-1 distance"
- inputs: config | outputs: distance multipliers | preconditions: NONE | postconditions: each scales only its distance | state_effects: geometry params
- formula: NONE | units: ratio (2; range 1.1–2.0) | invariants: single-purpose, decoupled from sizing
- failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0140 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0150 — Gen2SizeMultiplier (default 1.5) scales ONLY USD notional of Gen2+ levels; split from distance multipliers
- section: §7.1 Distance model | lines: L639–L648 | type: PARAMETER | strength: MUST | tag: [DD][DEFINED]
- wording: "Gen2LotMultiplier is split into two independent, single-purpose parameters … Gen2SizeMultiplier (approved default 1.5) — scales ONLY the USD notional of Generation-2+ Levels"
- inputs: config | outputs: size multiplier | preconditions: NONE | postconditions: scales only notional | state_effects: sizing param
- formula: NONE | units: ratio (1.5) | invariants: decouples spacing from size (corrects GridEA overload)
- failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: NONE | impl: NOT_STARTED | verif: NOT_STARTED

---

## §7.2 Protection Level Locking → Fillability-Gated Unlock (L651–L654)

### STR-0151 — Unlock condition unchanged: next level fills → protection level unlocks
- section: §7.2 Protection Level Locking | lines: L653 | type: STATE_TRANSITION | strength: MUST | tag: [SD][DEFINED]
- wording: "Unlock condition unchanged from GridEA (next level fills → protection level unlocks)."
- inputs: next-level fill | outputs: unlock | preconditions: locked level | postconditions: level unlocked (eligible to arm) | state_effects: LOCKED→eligible
- formula: NONE | units: NONE | invariants: unlock on next-level fill | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0146 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0152 — Unlocking only makes level eligible to arm; arming still passes full §8 gate list before any live order
- section: §7.2 Protection Level Locking | lines: L653–L654 | type: GUARD | strength: MUST | tag: [SD][DEFINED]
- wording: "Unlocking makes the level eligible to arm, but arming still passes through the full Pending Order Architecture gate list (§8) — including the Fillability Analyzer and Cost Analyzer — before any live order is placed."
- inputs: unlocked level; §8 gates | outputs: arm/deny | preconditions: level unlocked | postconditions: order only after all gates | state_effects: gating
- formula: NONE | units: NONE | invariants: unlock ≠ bypass gates | failure_behavior: stays IDLE/PRECHECK on gate fail | safety_impact: HIGH
- dependencies: STR-0163 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §7.3 Position sizing (L655–L699)

### STR-0153 — USD-notional-per-level, converted to base-asset at order-build via live mark, rounded szDecimals; fixed-qty/fixed-margin rejected
- section: §7.3 Position sizing | lines: L657–L662 | type: FORMULA | strength: MUST | tag: [DD][DEFINED]
- wording: "USD-notional-per-level, converted to base-asset size at order-build time using live mark price, rounded to szDecimals. Rejected: fixed base-asset quantity … fixed margin-at-config-time"
- inputs: USD notional; live mark; szDecimals | outputs: base-asset size | preconditions: order build | postconditions: size computed & rounded | state_effects: sizing
- formula: size = USD_notional / mark_price, rounded to szDecimals | units: base-asset size
- invariants: notional-based sizing | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0137 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0154 — Exposure caps are hard USD-notional caps: reject rather than silently clip
- section: §7.3 Position sizing | lines: L664 | type: GUARD | strength: MUST | tag: [DD][DEFINED]
- wording: "Exposure caps (USD notional, hard — reject rather than silently clip)"
- inputs: order notional; caps | outputs: accept/reject | preconditions: order build | postconditions: reject if over cap | state_effects: cap enforcement
- formula: NONE | units: USD notional | invariants: hard caps; no silent clipping
- failure_behavior: reject over-cap orders | safety_impact: CRITICAL
- dependencies: STR-0155, STR-0156, STR-0157, STR-0158, STR-0159 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0155 — MaxLevelNotional = MaxBasketNotional / GridLevels
- section: §7.3 Position sizing | lines: L665 | type: FORMULA | strength: MUST | tag: [DD][DEFINED]
- wording: "MaxLevelNotional = MaxBasketNotional / GridLevels"
- inputs: MaxBasketNotional; GridLevels | outputs: MaxLevelNotional | preconditions: caps computed | postconditions: per-level cap | state_effects: cap
- formula: MaxLevelNotional = MaxBasketNotional / GridLevels | units: USD notional
- invariants: binds every non-dominant level | failure_behavior: reject over-cap | safety_impact: HIGH
- dependencies: STR-0158, STR-0141 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0156 — MaxLevelNotionalDominant = Gen2SizeMultiplier × (MaxBasketNotional / GridLevels)
- section: §7.3 Position sizing | lines: L666–L667 | type: FORMULA | strength: MUST | tag: [DD][DEFINED]
- wording: "MaxLevelNotionalDominant = Gen2SizeMultiplier × (MaxBasketNotional / GridLevels)"
- inputs: Gen2SizeMultiplier; MaxBasketNotional; GridLevels | outputs: dominant cap | preconditions: caps computed | postconditions: dominant-level cap | state_effects: cap
- formula: MaxLevelNotionalDominant = Gen2SizeMultiplier × (MaxBasketNotional / GridLevels) | units: USD notional
- invariants: binds dominant-side levels | failure_behavior: reject over-cap | safety_impact: HIGH
- dependencies: STR-0150, STR-0158 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0157 — MaxCycleNotional = MaxBasketNotional / MaxActiveCycles
- section: §7.3 Position sizing | lines: L668 | type: FORMULA | strength: MUST | tag: [DD][DEFINED]
- wording: "MaxCycleNotional = MaxBasketNotional / MaxActiveCycles"
- inputs: MaxBasketNotional; MaxActiveCycles | outputs: per-Cycle cap | preconditions: caps computed | postconditions: Cycle cap | state_effects: cap
- formula: MaxCycleNotional = MaxBasketNotional / MaxActiveCycles | units: USD notional
- invariants: NONE | failure_behavior: reject over-cap | safety_impact: HIGH
- dependencies: STR-0161 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0158 — MaxGenerationNotional = MaxBasketNotional / MaxActiveGenerations
- section: §7.3 Position sizing | lines: L669 | type: FORMULA | strength: MUST | tag: [DD][DEFINED]
- wording: "MaxGenerationNotional = MaxBasketNotional / MaxActiveGenerations"
- inputs: MaxBasketNotional; MaxActiveGenerations | outputs: per-Generation cap | preconditions: caps computed | postconditions: Generation cap | state_effects: cap
- formula: MaxGenerationNotional = MaxBasketNotional / MaxActiveGenerations | units: USD notional
- invariants: NONE | failure_behavior: reject over-cap | safety_impact: HIGH
- dependencies: STR-0160 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0159 — MaxBasketNotional = sum across ALL Generations (ACTIVE + PASSIVE); PASSIVE exposure fully live (formula §12.1)
- section: §7.3 Position sizing | lines: L670–L674 | type: FORMULA | strength: MUST | tag: [DD][DEFINED]
- wording: "MaxBasketNotional (sum across ALL Generations, ACTIVE + PASSIVE — the number that matters most, since PASSIVE exposure is fully live; approved formula and input definitions: §12.1, D-13)"
- inputs: all Generations' exposure | outputs: basket cap | preconditions: caps computed | postconditions: basket-wide cap | state_effects: cap
- formula: see §12.1 (STR-0227) | units: USD notional
- invariants: PASSIVE exposure fully live and counted | failure_behavior: reject over-cap | safety_impact: CRITICAL
- dependencies: STR-0227 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0160 — MaxActiveGenerations := count of all Generations not yet CLOSED_ONLY_AS_PART_OF_BASKET (incl. DISABLED_AT_CYCLE_99) (D-14)
- section: §7.3 Position sizing | lines: L676–L679 | type: FORMULA | strength: MUST | tag: [DD][DEFINED]
- wording: "MaxActiveGenerations := the count of all Generations in the Basket not yet CLOSED_ONLY_AS_PART_OF_BASKET — including DISABLED_AT_CYCLE_99 Generations (their exposure is fully live, §5.3)."
- inputs: Generation states | outputs: divisor count | preconditions: caps computed | postconditions: conservative divisor | state_effects: cap divisor
- formula: count(Generations not CLOSED_ONLY_AS_PART_OF_BASKET) | units: count
- invariants: conservative (includes disabled) | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0158 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0161 — MaxActiveCycles := count of all Cycles of counted Generations not yet closed (incl. COMPLETED) (D-14)
- section: §7.3 Position sizing | lines: L680–L683 | type: FORMULA | strength: MUST | tag: [DD][DEFINED]
- wording: "MaxActiveCycles := the count of all Cycles of the counted Generations not yet closed as part of the Basket — including COMPLETED Cycles (their exposure is retained, §5.2)."
- inputs: Cycle states | outputs: divisor count | preconditions: caps computed | postconditions: conservative divisor | state_effects: cap divisor
- formula: count(Cycles not closed, incl COMPLETED) | units: count
- invariants: conservative (includes COMPLETED) | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0157 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0162 — D-12 resolution: dominant-side successor volume governed by MaxLevelNotionalDominant; others by MaxLevelNotional; over-cap rejected
- section: §7.3 Position sizing | lines: L685–L695 | type: GUARD | strength: MUST | tag: [DD][DEFINED]
- wording: "§7.1's dominant-side successor volume (Gen2SizeMultiplier × MaxLevelNotional) is a legitimate level size governed by its own derived cap MaxLevelNotionalDominant; MaxLevelNotional binds every other level. A dominant-side successor level above MaxLevelNotionalDominant is rejected like any other cap breach."
- inputs: dominant volume; caps | outputs: accept/reject | preconditions: order build | postconditions: correct cap applied | state_effects: cap enforcement
- formula: dominant bound = MaxLevelNotionalDominant; others = MaxLevelNotional | units: USD notional
- invariants: resolves dominant-volume vs level-cap conflict (R-01) | failure_behavior: reject over-cap | safety_impact: HIGH
- dependencies: STR-0155, STR-0156, STR-0148 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §8 Pending Order & Fillability Architecture (L700–L764)

### STR-0163 — Pre-arm within PendingArmDistance as resting Alo/Gtc; ALL gates must pass; any gate failure → IDLE/PRECHECK (logged, not error); arming depends on ArmPolicy
- section: §8 Pending Order & Fillability | lines: L702–L710, L757 | type: GUARD | strength: MUST | tag: [DD][DEFINED]
- wording: "Levels within PendingArmDistance (approved default 5 × StepBps = 50 bps …) of mark price pre-arm as resting Alo/Gtc limit orders. Before arming, ALL gates must pass. … Any gate failure → Level stays IDLE/PRECHECK, logged, not an error state."
- inputs: mark price; PendingArmDistance; §8 gate results; ArmPolicy | outputs: pre-arm / arm / IDLE | preconditions: level near mark | postconditions: order only if all gates pass and ArmPolicy allows | state_effects: PRECHECK/IDLE/AWAITING_ARM/armed
- formula: PendingArmDistance = 5 × StepBps = 50 bps (default) | units: bps
- invariants: gate failure is IDLE/PRECHECK, not ERROR; all gates mandatory | failure_behavior: IDLE/PRECHECK (logged) | safety_impact: HIGH
- dependencies: STR-0164, STR-0173, STR-0269 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0164 — ArmPolicy AUTO: level arms automatically the moment all §8 gates pass (no human approval)
- section: §8 Pending Order & Fillability | lines: L710–L713 | type: STATE_TRANSITION | strength: MAY | tag: [DD][DEFINED]
- wording: "AUTO — no human approval: a Level arms automatically the moment all §8 gates pass."
- inputs: gate pass; ArmPolicy=AUTO | outputs: armed level | preconditions: all gates pass | postconditions: level armed | state_effects: arm
- formula: NONE | units: NONE | invariants: still requires all §8 gates | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0163 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0165 — ArmPolicy SEMI: AWAITING_ARM until explicit operator approval; timeout → cancel to IDLE/PRECHECK; timeout NEVER auto-executes
- section: §8 Pending Order & Fillability | lines: L714–L718 | type: STATE_TRANSITION | strength: MUST | tag: [DD][DEFINED]
- wording: "SEMI — the Level enters AWAITING_ARM after all §8 gates pass; it arms only on explicit operator approval; if ArmRequestTimeoutSeconds elapses → cancel, return to IDLE/PRECHECK (logged). Timeout NEVER auto-executes."
- inputs: gate pass; operator approval; ArmRequestTimeoutSeconds | outputs: armed / cancelled | preconditions: all gates pass | postconditions: arm only on approval | state_effects: AWAITING_ARM → armed/IDLE
- formula: NONE | units: seconds | invariants: timeout never auto-executes (fail-closed) | failure_behavior: timeout → IDLE/PRECHECK | safety_impact: HIGH
- dependencies: STR-0167 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0166 — ArmPolicy WEBHOOK: external service approves within timeout; timeout/error → fail-closed; never auto-approval; operator identity = service identity, recorded
- section: §8 Pending Order & Fillability | lines: L719–L723 | type: STATE_TRANSITION | strength: MUST | tag: [DD][DEFINED]
- wording: "WEBHOOK — an external approving service must approve within ArmRequestTimeoutSeconds; timeout or error → fail-closed (IDLE/PRECHECK). A webhook failure NEVER converts to auto-approval. Operator identity = service identity, recorded per request."
- inputs: webhook approval; timeout | outputs: armed / fail-closed | preconditions: all gates pass | postconditions: arm only on service approval | state_effects: AWAITING_ARM → armed/IDLE
- formula: NONE | units: seconds | invariants: failure never converts to auto-approval; identity recorded | failure_behavior: timeout/error → fail-closed IDLE/PRECHECK | safety_impact: HIGH
- dependencies: STR-0167 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0167 — ArmPolicy defaults (Testnet=AUTO, Live=SEMI); ArmRequestTimeoutSeconds=30 (required for SEMI/WEBHOOK)
- section: §8 Pending Order & Fillability | lines: L724–L726 | type: PARAMETER | strength: MUST | tag: [DD][DEFINED]
- wording: "Approved defaults (§14 D-10): Testnet = AUTO (fast testing); Live = SEMI (human confirmation). ArmRequestTimeoutSeconds = 30 (required configuration for SEMI/WEBHOOK)."
- inputs: environment | outputs: ArmPolicy; timeout | preconditions: config | postconditions: defaults set | state_effects: policy config
- formula: NONE | units: seconds (30) | invariants: Live default SEMI (human confirmation)
- failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0274, STR-0275 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0168 — Arm-gate invariant 1: arm gate NEVER applies to EXPOSURE_CORRECTION_INTENT (hedge/survival never gated on human/service latency)
- section: §8 Pending Order & Fillability | lines: L730 | type: INVARIANT | strength: MUST_NOT | tag: [UR][DEFINED]
- wording: "The arm gate NEVER applies to EXPOSURE_CORRECTION_INTENT — hedge/survival paths are never gated on human or service latency (§11.2 acute branch, §13.3)."
- inputs: intent tag | outputs: gate applicability | preconditions: EXPOSURE_CORRECTION_INTENT | postconditions: arm gate skipped for it | state_effects: NONE
- formula: NONE | units: NONE | invariants: hedge/survival never gated on latency | failure_behavior: NONE | safety_impact: CRITICAL
- dependencies: STR-0206, STR-0240 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0169 — Arm-gate invariant 2: arm gate NEVER overrides FREEZE (FREEZE blocks ENTRY_INTENT regardless of approval)
- section: §8 Pending Order & Fillability | lines: L731 | type: INVARIANT | strength: MUST_NOT | tag: [UR][DEFINED]
- wording: "The arm gate NEVER overrides FREEZE — Freeze blocks ENTRY_INTENT regardless of approval state (§13.3)."
- inputs: FREEZE state; approval | outputs: block | preconditions: FROZEN | postconditions: ENTRY_INTENT blocked | state_effects: NONE
- formula: NONE | units: NONE | invariants: approval cannot bypass FREEZE | failure_behavior: block ENTRY_INTENT | safety_impact: CRITICAL
- dependencies: STR-0239 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0170 — Arm-gate invariant 3: human/delegate approval is additional gate only — can restrict, never bypass any §8 gate or §10 floor
- section: §8 Pending Order & Fillability | lines: L732 | type: INVARIANT | strength: MUST_NOT | tag: [UR][DEFINED]
- wording: "Human/delegate approval is an additional gate — it can only further restrict arming, never bypass any §8 gate or §10 economics floor."
- inputs: approval | outputs: gate composition | preconditions: approval present | postconditions: approval only restricts | state_effects: NONE
- formula: NONE | units: NONE | invariants: approval never bypasses gates/economics | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0163, STR-0181 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0171 — Arm-gate invariant 4: every arm request/approval/denial/expiry persisted with identity + timestamp
- section: §8 Pending Order & Fillability | lines: L733 | type: PERSISTENCE_RULE | strength: MUST | tag: [UR][DEFINED]
- wording: "Every arm request, approval, denial, and expiry is persisted with identity and timestamp — §15 invariant 19 (reconstructability) extends to the arm workflow."
- inputs: arm workflow events | outputs: persisted records | preconditions: arm workflow | postconditions: identity+timestamp persisted | state_effects: audit log
- formula: NONE | units: NONE | invariants: reconstructability extends to arm workflow | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0334 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0172 — Arm-gate invariant 5: ArmRequestTimeoutSeconds required; UNSET keeps all arming BLOCKED (fail-closed)
- section: §8 Pending Order & Fillability | lines: L734 | type: FAILURE_BEHAVIOR | strength: MUST | tag: [UR][DEFINED]
- wording: "ArmRequestTimeoutSeconds is a required configuration value — UNSET keeps all arming BLOCKED (fail-closed)."
- inputs: ArmRequestTimeoutSeconds | outputs: arming enabled/BLOCKED | preconditions: config check | postconditions: BLOCKED if UNSET | state_effects: fail-closed
- formula: NONE | units: seconds | invariants: no invented default | failure_behavior: UNSET → BLOCKED (fail-closed) | safety_impact: HIGH
- dependencies: STR-0167 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0173 — Gate 1: order-book depth at target ≥ MinDepthMultiple × order size
- section: §8 Pending Order & Fillability | lines: L737–L738 | type: GUARD | strength: MUST | tag: [DD][DEFINED]
- wording: "Order-book depth at target price ≥ MinDepthMultiple (approved default 10 …) × order size"
- inputs: book depth; MinDepthMultiple=10; order size | outputs: pass/fail | preconditions: arming | postconditions: depth sufficient | state_effects: gate
- formula: depth ≥ MinDepthMultiple × order_size | units: ratio (×10)
- invariants: NONE | failure_behavior: IDLE/PRECHECK | safety_impact: HIGH
- dependencies: STR-0270 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0174 — Gate 2: distance-to-market within DistanceBand [StepBps/2, 10 × StepBps] = [5,100] bps
- section: §8 Pending Order & Fillability | lines: L739–L741 | type: GUARD | strength: MUST | tag: [DD][DEFINED]
- wording: "Distance-to-market within the approved sane band: DistanceBand = [StepBps/2, 10 × StepBps] (approved default [5, 100] bps …)"
- inputs: distance-to-market; DistanceBand | outputs: pass/fail | preconditions: arming | postconditions: within band | state_effects: gate
- formula: DistanceBand = [StepBps/2, 10 × StepBps] | units: bps
- invariants: NONE | failure_behavior: IDLE/PRECHECK | safety_impact: MEDIUM
- dependencies: STR-0271 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0175 — Gates 3 & 4: order size ≥ asset minimum [HC]; margin available ≥ required initial margin + MarginSafetyBuffer
- section: §8 Pending Order & Fillability | lines: L742–L745 | type: GUARD | strength: MUST | tag: [HC][DD][DEFINED]
- wording: "Order size ≥ asset minimum … Margin available ≥ required initial margin + MarginSafetyBuffer (approved default 0.20 × required initial margin …)"
- inputs: order size; asset min; margin; MarginSafetyBuffer | outputs: pass/fail | preconditions: arming | postconditions: size/margin ok | state_effects: gate
- formula: margin_avail ≥ required_initial_margin × (1 + 0.20) | units: base-asset size; USD margin
- invariants: NONE | failure_behavior: IDLE/PRECHECK | safety_impact: HIGH
- venue_evidence_status: VERIFIED (Phase 2 — $10 minimum order value (minTradeNtlRejected); margin = size×mark/leverage; max order-value tiers)
- venue_evidence_refs: [SRC-104, SRC-105, SRC-115, SRC-116]
- dependencies: STR-0272 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0176 — Gates 5 & 6: exposure caps (§7.3) not exceeded; open-order count has headroom below per-account cap (~1000 [HC]), preserving hedge headroom
- section: §8 Pending Order & Fillability | lines: L746–L749 | type: GUARD | strength: MUST | tag: [HC][DD][DEFINED]
- wording: "Exposure caps (§7.3) not exceeded … Open-order count has headroom below Hyperliquid's per-account cap (default ~1000; … so exposure caps must preserve headroom specifically for hedge orders)"
- inputs: exposure caps; open-order count; per-account cap | outputs: pass/fail | preconditions: arming | postconditions: caps + headroom ok | state_effects: gate
- formula: NONE | units: USD notional; order count (~1000) | invariants: preserve headroom for hedge orders
- failure_behavior: IDLE/PRECHECK | safety_impact: HIGH
- venue_evidence_status: VERIFIED (Phase 2 — rate-limits: default 1000 open orders/user (up to 5000 by volume); reduce-only/trigger rejected at ≥1000)
- venue_evidence_refs: [SRC-111]
- dependencies: STR-0154 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0177 — Gates 7 & 8: price/size normalized (§6.3)
- section: §8 Pending Order & Fillability | lines: L750 | type: GUARD | strength: MUST | tag: [DD][HC][DEFINED]
- wording: "7–8. Price/size normalized (§6.3)"
- inputs: price; size | outputs: normalized order | preconditions: arming | postconditions: normalized before signing | state_effects: gate
- formula: NONE | units: NONE | invariants: normalize before signing | failure_behavior: IDLE/PRECHECK | safety_impact: HIGH
- venue_evidence_status: VERIFIED (Phase 2 — price/size normalization per tick-and-lot-size; cf. STR-0135/0137/0138)
- venue_evidence_refs: [SRC-108]
- dependencies: STR-0138 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0178 — Gate 9: Market/Basket not in FREEZE/ERROR/RECOVERY
- section: §8 Pending Order & Fillability | lines: L751 | type: GUARD | strength: MUST | tag: [DD][DEFINED]
- wording: "Market/Basket not in FREEZE/ERROR/RECOVERY"
- inputs: Basket state | outputs: pass/fail | preconditions: arming ENTRY_INTENT | postconditions: not in blocked state | state_effects: gate
- formula: NONE | units: NONE | invariants: ENTRY_INTENT blocked in FREEZE/ERROR/RECOVERY | failure_behavior: IDLE/PRECHECK | safety_impact: HIGH
- dependencies: STR-0239 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0179 — Gate 10: Cost Analyzer — NetExpectedEdge > NetExpectedEdgeFloor (default StepBps/10 = 1)
- section: §8 Pending Order & Fillability | lines: L752–L754 | type: ECONOMIC_RULE | strength: MUST | tag: [DD][DEFINED]
- wording: "Cost Analyzer: NetExpectedEdge > NetExpectedEdgeFloor (approved default StepBps/10 = 1 when StepBps = 10 …) (see §10)"
- inputs: NetExpectedEdge; NetExpectedEdgeFloor | outputs: pass/fail | preconditions: arming | postconditions: economics clear floor | state_effects: gate
- formula: NetExpectedEdge > NetExpectedEdgeFloor (= StepBps/10) | units: bps
- invariants: economic floor enforced | failure_behavior: IDLE/PRECHECK (Skip §9.3) | safety_impact: HIGH
- dependencies: STR-0193, STR-0273 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0180 — Generation-state arming rule: DISABLED_AT_CYCLE_99 can never arm ENTRY_INTENT; EXPOSURE_CORRECTION_INTENT exempt from gate-9 FREEZE & progression prohibition but passes all other gates
- section: §8 Pending Order & Fillability | lines: L758–L759 | type: GUARD | strength: MUST | tag: [UR][DD][DEFINED]
- wording: "Levels of a DISABLED_AT_CYCLE_99 Generation can never arm ENTRY_INTENT orders. EXPOSURE_CORRECTION_INTENT orders (§13.3) are exempt from gate 9's FREEZE block and from this progression prohibition, but pass every other gate"
- inputs: Generation state; intent tag | outputs: arm/deny | preconditions: DISABLED generation | postconditions: no ENTRY_INTENT; correction allowed via other gates | state_effects: gating
- formula: NONE | units: NONE | invariants: correction exempt only from gate-9 + progression prohibition | failure_behavior: ENTRY_INTENT blocked | safety_impact: CRITICAL
- dependencies: STR-0045, STR-0168 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0181 — Fillability Analyzer: walks L2 book, computes VWAP slippage; explicitly a snapshot estimate (defense-in-depth, not a guarantee)
- section: §8 Pending Order & Fillability | lines: L761 | type: GUARD | strength: MUST | tag: [DD][DEFINED]
- wording: "Fillability Analyzer: walks live L2 book … computes VWAP-execution-price slippage … explicitly a snapshot estimate, not a guarantee — defense-in-depth via (1) gating arming, (2) Ioc pricing …, (3) POSITION_VERIFIED reconciliation …, (4) Level Skip …"
- inputs: live L2 book; order size | outputs: VWAP slippage estimate | preconditions: arming/emergency | postconditions: slippage estimated | state_effects: fillability estimate
- formula: VWAP over book from best outward | units: bps | invariants: snapshot estimate, not guarantee; backstopped by POSITION_VERIFIED + Skip
- failure_behavior: unfillable → Skip fallback | safety_impact: HIGH
- dependencies: STR-0072, STR-0190 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §9.1 Emergency Execution (L767–L788)

### STR-0182 — Emergency Execution triggered when a pending trigger fires but doesn't fill within EmergencyBoundedWaitSeconds=30; replaces unbounded market catch-up
- section: §9.1 Emergency Execution | lines: L769 | type: STATE_TRANSITION | strength: MUST | tag: [SD][DD][DEFINED]
- wording: "Replaces GridEA's unbounded Market-Order catch-up. Triggered when a pending order's trigger fires but doesn't fill within the bounded wait EmergencyBoundedWaitSeconds = 30 s"
- inputs: trigger fire; bounded wait=30s | outputs: emergency path | preconditions: trigger fired, no fill in wait | postconditions: emergency evaluation | state_effects: EMERGENCY
- formula: NONE | units: seconds (30) | invariants: bounded, never unbounded market order
- failure_behavior: proceed to band eval or SKIP | safety_impact: HIGH
- dependencies: STR-0277 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0183 — [DYN] EmergencyTolerance := 0.005 × (10000 / Leverage_effective) bps (auto-tightens at higher leverage)
- section: §9.1 Emergency Execution | lines: L772–L776 | type: PARAMETER | strength: MUST | tag: [DYN][DEFINED]
- wording: "tolerance := EmergencyTolerance = 0.005 × (10000 / Leverage_effective) bps [DYNAMIC — CALIBRATION PENDING]"
- inputs: Leverage_effective | outputs: EmergencyTolerance | preconditions: emergency eval | postconditions: tolerance computed | state_effects: tolerance
- formula: EmergencyTolerance = 0.005 × (10000 / Leverage_effective) bps | units: bps
- invariants: auto-tightens at higher leverage | failure_behavior: NONE | safety_impact: HIGH
- dynamic_note: must remain dynamic — never freeze to a constant (D-16; canonical PARAMETER: STR-0338)
- dependencies: STR-0338, STR-0219 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0184 — Breach of the wait bound alerted via the three-layer breach response
- section: §9.1 Emergency Execution | lines: L777–L779 | type: FAILURE_BEHAVIOR | strength: MUST | tag: [SD][DEFINED]
- wording: "Breach of the wait bound is alerted as part of the standard three-layer breach response (Alert → Soft Protective Action → Operator Decision, §12.1)."
- inputs: wait-bound breach | outputs: alert | preconditions: breach | postconditions: three-layer response | state_effects: alert
- formula: NONE | units: NONE | invariants: three-layer response | failure_behavior: Alert→Soft→Operator | safety_impact: MEDIUM
- dependencies: STR-0216 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0185 — Emergency band [TargetPrice×(1−tol), ×(1+tol)]; if fillable within band AND NetExpectedEdge clears floor → submit Ioc at band edge (never unbounded market)
- section: §9.1 Emergency Execution | lines: L780–L784 | type: STATE_TRANSITION | strength: MUST | tag: [SD][DD][DEFINED]
- wording: "band := [TargetPrice × (1−tolerance), TargetPrice × (1+tolerance)] IF Fillable(size, side, tolerance) AND best executable price within band AND NetExpectedEdge (§10) clears the configured floor: submit Ioc at the tolerance-band edge (never unbounded market order)"
- inputs: TargetPrice; tolerance; fillability; NetExpectedEdge | outputs: Ioc order | preconditions: fillable & economic within band | postconditions: bounded Ioc | state_effects: order submission
- formula: band = [TargetPrice×(1−tol), TargetPrice×(1+tol)] | units: price | invariants: never unbounded market order
- failure_behavior: else → LEVEL_SKIPPED | safety_impact: CRITICAL
- dependencies: STR-0183, STR-0193, STR-0181 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0186 — Else (not fillable/economic within band) → LEVEL_SKIPPED
- section: §9.1 Emergency Execution | lines: L784 | type: FAILURE_BEHAVIOR | strength: MUST | tag: [SD][DD][DEFINED]
- wording: "ELSE: → LEVEL_SKIPPED"
- inputs: band eval fail | outputs: LEVEL_SKIPPED | preconditions: not fillable/economic | postconditions: level skipped | state_effects: LEVEL_SKIPPED
- formula: NONE | units: NONE | invariants: Skip over unsafe/uneconomic fill | failure_behavior: LEVEL_SKIPPED | safety_impact: HIGH
- dependencies: STR-0190 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0187 — Hard invariant: never chase price beyond tolerance; never accept a fillable-but-uneconomic fill
- section: §9.1 Emergency Execution | lines: L787 | type: INVARIANT | strength: MUST_NOT | tag: [SD][DD][DEFINED]
- wording: "Hard invariant: never chase price beyond tolerance, and never accept a fillable-but-uneconomic fill."
- inputs: tolerance; economics | outputs: bounded behavior | preconditions: emergency | postconditions: no chase beyond tol; no uneconomic fill | state_effects: NONE
- formula: NONE | units: NONE | invariants: emergency execution cannot exceed EmergencyTolerance | failure_behavior: SKIP | safety_impact: CRITICAL
- dependencies: STR-0183, STR-0198 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §9.2 Maker→Taker re-evaluation (L789–L801)

### STR-0188 — At timeout: genuine four-way re-evaluation, NOT an automatic maker-to-taker escalation
- section: §9.2 Maker→Taker re-evaluation | lines: L791 | type: GUARD | strength: MUST | tag: [UR][DEFINED]
- wording: "the system performs a genuine four-way re-evaluation, not an automatic maker-to-taker escalation"
- inputs: timeout | outputs: re-evaluation | preconditions: maker timeout | postconditions: four-way decision | state_effects: decision
- formula: NONE | units: NONE | invariants: taker never occurs solely because maker timed out | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0189 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0189 — Four-way branches: WAIT / Ioc / REPRICE / SKIP with defined justification for each
- section: §9.2 Maker→Taker re-evaluation | lines: L793–L800 | type: STATE_TRANSITION | strength: MUST | tag: [UR][DEFINED]
- wording: "WAIT — maker path's NetExpectedEdge still positive … Ioc — taker path justified AND within tolerance band; REPRICE — … a repriced Alo order … would be — cancel and re-arm …; SKIP — none justified"
- inputs: NetExpectedEdge per path; tolerance band | outputs: WAIT/Ioc/REPRICE/SKIP | preconditions: timeout re-eval | postconditions: one branch chosen | state_effects: order action
- formula: NONE | units: NONE | invariants: each branch requires its own justification | failure_behavior: SKIP if none justified | safety_impact: HIGH
- dependencies: STR-0193 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §9.3 Level Skip Model (L802–L806)

### STR-0190 — LEVEL_SKIPPED is a first-class terminal state: per-level (never blocks subsequent levels), no automatic retry within the same Cycle
- section: §9.3 Level Skip Model | lines: L804 | type: LIFECYCLE_STATE | strength: MUST | tag: [SD][DD][DEFINED]
- wording: "LEVEL_SKIPPED is a first-class terminal state, not an error: per-level (never blocks or holds subsequent levels), no automatic retry within the same Cycle"
- inputs: skip decision | outputs: LEVEL_SKIPPED | preconditions: skip triggered | postconditions: terminal per-level state | state_effects: LEVEL_SKIPPED
- formula: NONE | units: NONE | invariants: never blocks subsequent levels; no auto-retry in Cycle | failure_behavior: terminal (not error) | safety_impact: MEDIUM
- dependencies: NONE | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0191 — A skipped level contributes zero exposure and zero PnL
- section: §9.3 Level Skip Model | lines: L804 | type: INVARIANT | strength: MUST | tag: [SD][DD][DEFINED]
- wording: "contributes zero exposure and zero PnL"
- inputs: skipped level | outputs: zero contribution | preconditions: LEVEL_SKIPPED | postconditions: 0 exposure, 0 PnL | state_effects: accounting
- formula: exposure=0; PnL=0 | units: NONE | invariants: zero contribution | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0190 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0192 — Skipped instance never resurrected/retroactively filled; may recur naturally in a future Cycle/Generation at a new reference
- section: §9.3 Level Skip Model | lines: L804 | type: GUARD | strength: MUST_NOT | tag: [SD][DD][DEFINED]
- wording: "may recur naturally in a future Cycle/Generation at a new reference price but the specific skipped instance is never resurrected or retroactively filled."
- inputs: skipped instance | outputs: no resurrection | preconditions: LEVEL_SKIPPED | postconditions: instance not revived | state_effects: NONE
- formula: NONE | units: NONE | invariants: specific instance never resurrected | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0190 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §10 Execution Economics (L808–L836)

### STR-0193 — NetExpectedEdge formula (GrossGridEdge − Fee − EstimatedSlippage − FundingCostEstimate − OtherExecutionCosts)
- section: §10 Execution Economics | lines: L811–L819 | type: FORMULA | strength: MUST | tag: [UR][DEFINED]
- wording: "NetExpectedEdge(path) := GrossGridEdge(level, bps) − Fee(path) − EstimatedSlippage(path) − FundingCostEstimate(holding_period) − OtherExecutionCosts(path)"
- inputs: gross edge; fee; slippage; funding; other costs | outputs: NetExpectedEdge | preconditions: path eval | postconditions: net edge computed | state_effects: economics
- formula: NetExpectedEdge = GrossGridEdge − Fee − EstimatedSlippage − FundingCostEstimate − OtherExecutionCosts | units: bps
- invariants: net (not gross) governs arming | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0194, STR-0181 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0194 — Fees pulled live from userFees [HC], NEVER hardcoded (Tier-0 base ≈ taker 0.045%, maker 0.015%)
- section: §10 Execution Economics | lines: L813–L816 | type: ECONOMIC_RULE | strength: MUST | tag: [HC][DEFINED]
- wording: "Fee(path) [HC] pulled live from userFees — Tier-0 base ≈ taker 0.045%, maker 0.015%, but NEVER hardcoded; moves with volume tier/staking/promotions"
- inputs: userFees (live) | outputs: fee | preconditions: economics eval | postconditions: live fee used | state_effects: fee input
- formula: NONE | units: % (taker ≈0.045%, maker ≈0.015% base) | invariants: never hardcoded; live per tier
- failure_behavior: NONE | safety_impact: HIGH
- venue_evidence_status: VERIFIED (Phase 2 — fees: perps Tier-0 base taker 0.045% / maker 0.015%; tiered by 14d volume + staking; pull live, never hardcode)
- venue_evidence_refs: [SRC-114]
- dependencies: STR-0193 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0195 — Normal Level arming prefers MAKER (Alo) — lower fee; Alo reject-instead-of-cross can never accidentally take
- section: §10 Execution Economics | lines: L822–L824 | type: ECONOMIC_RULE | strength: SHOULD | tag: [UR][DEFINED]
- wording: "Normal Level arming → prefer MAKER (Alo) — lower fee, and Alo's reject-instead-of-cross semantics mean it can never accidentally take"
- inputs: path options | outputs: maker preference | preconditions: normal arming | postconditions: prefer Alo | state_effects: path selection
- formula: NONE | units: NONE | invariants: Alo cannot accidentally take | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0193 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0196 — Emergency/Hedge only → TAKER (Ioc) — fill certainty is the point
- section: §10 Execution Economics | lines: L825–L826 | type: ECONOMIC_RULE | strength: MUST | tag: [UR][DEFINED]
- wording: "Emergency Execution/Hedge only → TAKER (Ioc) — fill certainty is the point"
- inputs: emergency/hedge context | outputs: taker path | preconditions: emergency/hedge | postconditions: Ioc used | state_effects: path selection
- formula: NONE | units: NONE | invariants: taker restricted to emergency/hedge | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0185, STR-0206 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0197 — floor := NetExpectedEdgeFloor; NetExpectedEdge ≤ floor (either path) → do not arm / do not attempt (Skip applies)
- section: §10 Execution Economics | lines: L827–L831 | type: GUARD | strength: MUST | tag: [UR][DEFINED]
- wording: "floor := NetExpectedEdgeFloor … NetExpectedEdge ≤ floor (either path) → do not arm / do not attempt (§9.3 Skip applies)"
- inputs: NetExpectedEdge; floor | outputs: arm/skip | preconditions: eval | postconditions: no arm if ≤ floor | state_effects: gating
- formula: NetExpectedEdge ≤ NetExpectedEdgeFloor → do not arm | units: bps
- invariants: economic floor enforced both paths | failure_behavior: Skip (§9.3) | safety_impact: HIGH
- dependencies: STR-0179, STR-0273 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0198 — A fillable-but-uneconomic Level is skipped: capital preservation governs over fill-chasing
- section: §10 Execution Economics | lines: L833 | type: INVARIANT | strength: MUST | tag: [UR][DEFINED]
- wording: "A Level that is fillable but not economically justified is skipped for the same reason an unfillable one is — capital preservation governs over fill-chasing."
- inputs: fillable-but-uneconomic level | outputs: skip | preconditions: uneconomic | postconditions: skipped | state_effects: LEVEL_SKIPPED
- formula: NONE | units: NONE | invariants: skipped level preferable to unsafe/irrational execution | failure_behavior: LEVEL_SKIPPED | safety_impact: HIGH
- dependencies: STR-0190 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §11.1 Expected vs. Actual Exposure (L839–L865)

### STR-0199 — ExpectedExposure := Σ VERIFIED filled quantity (not requested_qty) over {PARTIALLY_FILLED, FILLED, POSITION_VERIFIED}
- section: §11.1 Expected vs. Actual Exposure | lines: L842–L843 | type: FORMULA | strength: MUST | tag: [SD][DD][DEFINED]
- wording: "ExpectedExposure(Basket) := Σ over Levels in {PARTIALLY_FILLED, FILLED, POSITION_VERIFIED} of their VERIFIED filled quantity (not requested_qty)"
- inputs: verified filled quantities | outputs: ExpectedExposure | preconditions: level states | postconditions: expected exposure computed | state_effects: exposure model
- formula: ExpectedExposure = Σ verified_filled_qty over {PARTIALLY_FILLED,FILLED,POSITION_VERIFIED} | units: base-asset quantity
- invariants: uses verified filled qty, never requested_qty | failure_behavior: NONE | safety_impact: CRITICAL
- dependencies: STR-0131 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0200 — ActualExposure := net position from clearinghouseState/webData2 ONLY (never local bookkeeping)
- section: §11.1 Expected vs. Actual Exposure | lines: L844–L845 | type: FORMULA | strength: MUST | tag: [SD][HC][DEFINED]
- wording: "ActualExposure(Basket) := net position size from clearinghouseState/webData2 ONLY — never derived from local order bookkeeping"
- inputs: clearinghouseState/webData2 | outputs: ActualExposure | preconditions: authoritative read | postconditions: actual exposure from venue only | state_effects: exposure model
- formula: ActualExposure = net position from clearinghouseState/webData2 | units: base-asset quantity
- invariants: Actual Exposure only from authoritative exchange state | failure_behavior: NONE | safety_impact: CRITICAL
- venue_evidence_status: VERIFIED (Phase 2 — clearinghouseState.assetPositions[].position.szi = signed net position; authoritative. webData2/3 nuance → CONFLICT-002/GATE-002, non-blocking)
- venue_evidence_refs: [SRC-107, SRC-109]
- authoritative_source: clearinghouseState only
- owner_decision: DECISION-002
- dependencies: STR-0133 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0201 — ExposureDelta := ExpectedExposure − ActualExposure
- section: §11.1 Expected vs. Actual Exposure | lines: L846 | type: FORMULA | strength: MUST | tag: [SD][DD][DEFINED]
- wording: "ExposureDelta := ExpectedExposure − ActualExposure"
- inputs: ExpectedExposure; ActualExposure | outputs: ExposureDelta | preconditions: both computed | postconditions: delta computed | state_effects: exposure model
- formula: ExposureDelta = ExpectedExposure − ActualExposure | units: base-asset quantity
- invariants: Expected never treated as Actual | failure_behavior: NONE | safety_impact: CRITICAL
- dependencies: STR-0199, STR-0200 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0202 — Classification of a nonzero ExposureDelta (normal / transient / escalate)
- section: §11.1 Expected vs. Actual Exposure | lines: L849 | type: GUARD | strength: MUST | tag: [SD][DD][DEFINED]
- wording: "Classification of a nonzero delta (normal/transient/escalate) and priority ordering"
- inputs: ExposureDelta | outputs: classification | preconditions: nonzero delta | postconditions: classified | state_effects: classification
- formula: NONE | units: base-asset quantity | invariants: deterministic classification | failure_behavior: escalate on acute | safety_impact: HIGH
- dependencies: STR-0201 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0203 — Priority ordering: POSITION VERIFICATION → RISK/EXPOSURE PROTECTION → HEDGE RECOVERY → CYCLE-LIMIT DISABLE → GRID EXECUTION → GENERATION EVOLUTION → CYCLE CREATION
- section: §11.1 Expected vs. Actual Exposure | lines: L851–L862 | type: PRECEDENCE_RULE | strength: MUST | tag: [SD][DD][DEFINED]
- wording: "POSITION VERIFICATION … → RISK / EXPOSURE PROTECTION … → HEDGE RECOVERY … → CYCLE-LIMIT DISABLE TRANSITION (§5.3) → GRID EXECUTION → GENERATION EVOLUTION (§4.1) → CYCLE CREATION (§5.2)"
- inputs: candidate actions | outputs: ordered priority | preconditions: pass | postconditions: total deterministic order | state_effects: precedence
- formula: NONE | units: NONE | invariants: total, deterministic, consistent with §4.7 | failure_behavior: NONE | safety_impact: CRITICAL
- dependencies: STR-0063 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0204 — HEDGE RECOVERY permitted even under FREEZE (tagged EXPOSURE_CORRECTION_INTENT, distinct from ENTRY_INTENT)
- section: §11.1 Expected vs. Actual Exposure | lines: L856–L858 | type: GUARD | strength: MUST | tag: [SD][DD][DEFINED]
- wording: "HEDGE RECOVERY (permitted even under FREEZE — tagged EXPOSURE_CORRECTION_INTENT, distinct from ENTRY_INTENT)"
- inputs: FREEZE state; hedge recovery | outputs: permitted correction | preconditions: FROZEN | postconditions: correction allowed | state_effects: EXPOSURE_CORRECTION_INTENT
- formula: NONE | units: NONE | invariants: correction distinct from ENTRY_INTENT | failure_behavior: NONE | safety_impact: CRITICAL
- dependencies: STR-0240 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0205 — Grid progression is hard-gated on exposure within tolerance — not a soft preference
- section: §11.1 Expected vs. Actual Exposure | lines: L864 | type: INVARIANT | strength: MUST | tag: [SD][DD][DEFINED]
- wording: "Grid progression is hard-gated on exposure being within tolerance — not a soft preference."
- inputs: ExposureDelta; tolerance | outputs: gate | preconditions: progression candidate | postconditions: blocked unless within tolerance | state_effects: gating
- formula: NONE | units: base-asset quantity | invariants: grid progression blocked while ExposureDelta exceeds tolerance unless Hedge Recovery is active transition | failure_behavior: BLOCKED | safety_impact: CRITICAL
- dependencies: STR-0083, STR-0203 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §11.2 Hedge cost-awareness (L866–L876)

### STR-0206 — ACUTE risk (approaching maintenance margin, or beyond MaxExposureImbalance) → hedge immediately via Ioc regardless of cost (unconditional)
- section: §11.2 Hedge cost-awareness | lines: L869–L872 | type: GUARD | strength: MUST | tag: [UR][DEFINED]
- wording: "IF risk of leaving ExposureDelta unresolved is ACUTE (approaching maintenance margin, or beyond MaxExposureImbalance §12.1): hedge immediately via Ioc regardless of cost — unconditional"
- inputs: risk state; MaxExposureImbalance | outputs: immediate Ioc hedge | preconditions: acute risk | postconditions: unconditional hedge | state_effects: hedge recovery
- formula: NONE | units: base-asset quantity | invariants: acute branch unconditional | failure_behavior: immediate Ioc | safety_impact: CRITICAL
- dependencies: STR-0223 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0207 — ELSE (non-acute) → evaluate via §10 NetExpectedEdge; prefer maker-side correction
- section: §11.2 Hedge cost-awareness | lines: L873–L875 | type: ECONOMIC_RULE | strength: SHOULD | tag: [UR][DEFINED]
- wording: "ELSE: evaluate via §10's NetExpectedEdge model; prefer a maker-side correction when risk isn't acute enough to justify the taker spread"
- inputs: NetExpectedEdge | outputs: maker-side correction | preconditions: non-acute risk | postconditions: economic correction | state_effects: hedge path
- formula: NONE | units: NONE | invariants: cost-aware when non-acute | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0193, STR-0206 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §11.3 Mirroring (L877–L892)

### STR-0208 — Mirroring re-scoped as one input into Hedge Layer; Basket-scoped; driven by verified cumulative fill (recomputes on every incremental partial fill)
- section: §11.3 Mirroring | lines: L879 | type: EVENT_SEMANTICS | strength: MUST | tag: [SD][DEFINED]
- wording: "Re-scoped as one input into the Hedge Layer (§11.1), Basket-scoped (not Generation-scoped), driven by verified cumulative fill (recomputes on every incremental partial fill, not just 0%/100%)"
- inputs: verified cumulative fill | outputs: mirror recomputation | preconditions: fill events | postconditions: mirror recomputed | state_effects: mirroring input
- formula: NONE | units: NONE | invariants: Basket-scoped; verified-fill driven | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0199 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0209 — Mirror Event → recompute opposite leg's trigger/target price (symmetric formula)
- section: §11.3 Mirroring | lines: L882–L884 | type: FORMULA | strength: MUST | tag: [SD][DEFINED]
- wording: "Mirror Event (opposite hedge leg fired) → recompute opposite leg's trigger/target price (symmetric formula)"
- inputs: mirror event | outputs: recomputed trigger/target | preconditions: opposite leg fired | postconditions: symmetric price computed | state_effects: mirror target
- formula: symmetric trigger/target recomputation | units: price | invariants: symmetric | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0208 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0210 — Mirror produces a Mirror INTENT (updated target), not an immediate order; re-enters §8 + §10 gates; never bypasses them
- section: §11.3 Mirroring | lines: L884–L889 | type: GUARD | strength: MUST | tag: [SD][DEFINED]
- wording: "produces a Mirror INTENT (updated target price), not an immediate order → the updated level re-enters the NORMAL Pending Order Architecture (§8) and Cost Analyzer (§10) gates before any order is placed — Mirroring never bypasses precheck/liquidity/precision/exposure/economics/reconciliation"
- inputs: mirror intent | outputs: gated order | preconditions: mirror recomputed | postconditions: passes §8/§10 before order | state_effects: gating
- formula: NONE | units: NONE | invariants: Mirror Intent always passes normal execution validation | failure_behavior: gate failures per §8 | safety_impact: HIGH
- dependencies: STR-0163, STR-0193 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0211 — Mirroring eligibility: ACTIVE, SUCCESSOR_CREATED, DISABLED_AT_CYCLE_99; never creates ENTRY_INTENT
- section: §11.3 Mirroring | lines: L891 | type: GUARD | strength: MUST | tag: [UR][DD][DEFINED]
- wording: "Mirroring for protection remains available for ACTIVE, SUCCESSOR_CREATED, and DISABLED_AT_CYCLE_99 Generations; it never creates ENTRY_INTENT orders."
- inputs: Generation state | outputs: mirroring eligibility | preconditions: protection need | postconditions: mirroring allowed for stated states | state_effects: NONE
- formula: NONE | units: NONE | invariants: never creates ENTRY_INTENT | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0208 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §11.4 Partial fill ↔ hedge interaction (L893–L898)

### STR-0212 — While PARTIALLY_FILLED: exposure contribution = verified filled quantity; Mirroring recomputes on every incremental fill
- section: §11.4 Partial fill ↔ hedge interaction | lines: L895 | type: FORMULA | strength: MUST | tag: [DD][DEFINED]
- wording: "While a Level sits PARTIALLY_FILLED: exposure contribution = verified filled quantity so far; Mirroring recomputes on every incremental fill"
- inputs: partial fills | outputs: exposure contribution | preconditions: PARTIALLY_FILLED | postconditions: contribution = verified filled | state_effects: exposure
- formula: contribution = verified_filled_qty_so_far | units: base-asset quantity
- invariants: verified filled only | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0199, STR-0208 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0213 — Unfilled remainder is NOT independently hedged while working within its normal timeout (not-yet-exposure)
- section: §11.4 Partial fill ↔ hedge interaction | lines: L895 | type: GUARD | strength: MUST_NOT | tag: [DD][DEFINED]
- wording: "the unfilled remainder is not independently hedged while still actively working within its normal timeout (not-yet-exposure)"
- inputs: unfilled remainder | outputs: no independent hedge | preconditions: within normal timeout | postconditions: remainder not hedged | state_effects: NONE
- formula: NONE | units: base-asset quantity | invariants: not-yet-exposure not hedged | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0212 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0214 — Only once remainder times out into Emergency Execution is it subject to tolerance/economics/Skip; skipped residual permanently zero, no hedge needed
- section: §11.4 Partial fill ↔ hedge interaction | lines: L895 | type: STATE_TRANSITION | strength: MUST | tag: [DD][DEFINED]
- wording: "only once the remainder times out into Emergency Execution (§9.1) does it become subject to tolerance/economics/Skip — a skipped residual permanently contributes zero, requiring no hedge for exposure that was never taken."
- inputs: remainder timeout | outputs: emergency handling / skip | preconditions: timeout | postconditions: tolerance/economics/Skip applied | state_effects: EMERGENCY/SKIP
- formula: NONE | units: base-asset quantity | invariants: skipped residual = zero exposure, no hedge | failure_behavior: LEVEL_SKIPPED possible | safety_impact: HIGH
- dependencies: STR-0182, STR-0191 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §12.1 Range Survivability (L901–L978)

> Note: STR-* order here groups the §12.1 material by role; `source_lines` remains authoritative per entry. MaxExposureImbalance and ExposureTolerance dynamic defaults are canonically defined in §16 (STR-0329..0331) and cross-referenced.

### STR-0215 — A ranging market must degrade gracefully (no state corruption, no catastrophic drawdown); continuously monitored Basket-scoped bounds
- section: §12.1 Range Survivability | lines: L903 | type: INVARIANT | strength: MUST | tag: [UR][DEFINED]
- wording: "A ranging market must degrade gracefully, not corrupt state or produce catastrophic drawdown. Continuously monitored, Basket-scoped bounds with approved values and formulas"
- inputs: market conditions | outputs: monitored bounds | preconditions: active Basket | postconditions: graceful degradation | state_effects: monitoring
- formula: NONE | units: NONE | invariants: range oscillation must not corrupt the state machine | failure_behavior: bound breach → three-layer response | safety_impact: CRITICAL
- dependencies: STR-0216 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0216 — Three-layer breach-response pattern (Alert → Soft Protective Action → Operator Decision); no auto-terminate on Group B breach; calibration changes proposal-only
- section: §12.1 Range Survivability | lines: L905 | type: FAILURE_BEHAVIOR | strength: MUST | tag: [UR][DEFINED]
- wording: "breach of any bound follows the three-layer response — (1) Alert … (2) Soft Protective Action … (3) Operator Decision (the system never auto-terminates on a Group B breach …). Calibration-proposed changes to these bounds are proposal-only"
- inputs: bound breach | outputs: three-layer response | preconditions: breach | postconditions: alert+soft action+operator | state_effects: response
- formula: NONE | units: NONE | invariants: never auto-terminate on Group B; proposals never auto-applied | failure_behavior: Alert→Soft→Operator | safety_impact: HIGH
- dependencies: STR-0215 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0217 — MaxRangeInducedDD = 100% of Basket equity (total basket loss); FIXED, not calibratable
- section: §12.1 Range Survivability | lines: L908–L912 | type: PARAMETER | strength: MUST | tag: [UR][DEFINED]
- wording: "MaxRangeInducedDD … APPROVED value: 100% of Basket equity, i.e. total basket loss — the bound is reached only when the Basket's equity is fully consumed."
- inputs: range-churn DD | outputs: bound | preconditions: monitoring | postconditions: bound tracked separately from directional DD | state_effects: risk bound
- formula: MaxRangeInducedDD = 100% of Basket equity | units: % of equity
- invariants: tracked separately from directional-move DD | failure_behavior: three-layer response | safety_impact: HIGH
- dependencies: STR-0216 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0218 — MaxExecutionCost = 30% of BasketNetPnL when >0; 100 bps of MaxBasketNotional when ≤0 (two-regime); FIXED
- section: §12.1 Range Survivability | lines: L921–L926 | type: PARAMETER | strength: MUST | tag: [UR][DEFINED]
- wording: "MaxExecutionCost — cumulative fees+slippage bound. APPROVED dynamic rule: 30% of BasketNetPnL when BasketNetPnL > 0; 100 bps of MaxBasketNotional when BasketNetPnL ≤ 0"
- inputs: BasketNetPnL; MaxBasketNotional | outputs: cost bound | preconditions: monitoring | postconditions: two-regime bound | state_effects: risk bound
- formula: PnL>0: 0.30×BasketNetPnL; PnL≤0: 100 bps × MaxBasketNotional | units: USD (fraction / bps)
- invariants: two-regime resolves denominator question | failure_behavior: three-layer response | safety_impact: HIGH
- dependencies: STR-0234, STR-0227 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0219 — Leverage_effective = min(Leverage_user, MaxLeverage_asset) (D-13)
- section: §12.1 Range Survivability | lines: L947 | type: FORMULA | strength: MUST | tag: [UR][DEFINED]
- wording: "Leverage_effective = min(Leverage_user, MaxLeverage_asset)"
- inputs: Leverage_user; MaxLeverage_asset | outputs: Leverage_effective | preconditions: config | postconditions: effective leverage | state_effects: leverage input
- formula: Leverage_effective = min(Leverage_user, MaxLeverage_asset) | units: ratio
- invariants: feeds EmergencyTolerance, MaxExposureImbalance, margin math | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0222 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0220 — MaxFailedLevelRate = 5%, window = ALL Levels of the ACTIVE Basket; sustained breach → Market Selection re-eval; FIXED
- section: §12.1 Range Survivability | lines: L927–L931 | type: PARAMETER | strength: MUST | tag: [UR][DEFINED]
- wording: "MaxFailedLevelRate — fraction of Levels reaching SKIPPED. APPROVED value: 5%. APPROVED window: ALL Levels of the ACTIVE Basket … Sustained breach → Market Selection re-evaluation at next Basket INITIALIZING."
- inputs: SKIPPED level count; all Levels | outputs: rate bound | preconditions: monitoring | postconditions: bound tracked | state_effects: risk bound
- formula: MaxFailedLevelRate = SKIPPED/total ≤ 5% | units: % of Levels
- invariants: window = all Levels of ACTIVE Basket (not rolling) | failure_behavior: sustained breach → Market Selection re-eval | safety_impact: MEDIUM
- dependencies: STR-0190 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0221 — MaxHedgeCost = 2% of MaxBasketNotional; FIXED
- section: §12.1 Range Survivability | lines: L932–L936 | type: PARAMETER | strength: MUST | tag: [UR][DEFINED]
- wording: "MaxHedgeCost — cumulative Emergency Hedge cost. APPROVED default: 2% of MaxBasketNotional."
- inputs: cumulative hedge cost; MaxBasketNotional | outputs: hedge-cost bound | preconditions: monitoring | postconditions: bound tracked | state_effects: risk bound
- formula: MaxHedgeCost = 2% × MaxBasketNotional | units: % of USD notional
- invariants: high value signals mistuned tolerance for regime | failure_behavior: three-layer response | safety_impact: MEDIUM
- dependencies: STR-0227 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0222 — Leverage_user = 3 (fixed owner choice, D-13)
- section: §12.1 Range Survivability | lines: L948 | type: PARAMETER | strength: MUST | tag: [UR][DEFINED]
- wording: "Leverage_user = 3  (fixed owner choice, D-13)"
- inputs: owner choice | outputs: Leverage_user | preconditions: config | postconditions: =3 | state_effects: leverage input
- formula: NONE | units: ratio (3) | invariants: fixed owner choice | failure_behavior: NONE | safety_impact: HIGH
- dependencies: NONE | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0223 — [DYN] MaxExposureImbalance := (0.25 × 0.5 / Leverage_effective) × NotionalPerLevel / MarkPrice — |ExposureDelta| bound forcing unconditional Hedge Recovery
- section: §12.1 Range Survivability | lines: L913–L920 | type: PARAMETER | strength: MUST | tag: [DYN][DEFINED]
- wording: "MaxExposureImbalance — |ExposureDelta| bound forcing unconditional Hedge Recovery (§11.2's acute branch). Base-asset quantity. DYNAMIC default (D-16): (0.25 × 0.5 / Leverage_effective) × NotionalPerLevel / MarkPrice"
- inputs: Leverage_effective; NotionalPerLevel; MarkPrice | outputs: MaxExposureImbalance | preconditions: monitoring | postconditions: acute-hedge threshold | state_effects: risk bound
- formula: MaxExposureImbalance = (0.25 × 0.5 / Leverage_effective) × (MaxBasketNotional/GridLevels) / MarkPrice | units: base-asset quantity
- invariants: auto-tightens at higher leverage; drives §11.2 acute branch | failure_behavior: breach → unconditional Hedge Recovery | safety_impact: CRITICAL
- dynamic_note: must remain dynamic — never freeze to a constant (D-16; canonical PARAMETER: STR-0340)
- dependencies: STR-0219, STR-0227, STR-0141, STR-0340, STR-0206 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0224 — CapitalBase = account equity incl. unrealized PnL (clearinghouseState accountValue) (D-13)
- section: §12.1 Range Survivability | lines: L949–L950 | type: FORMULA | strength: MUST | tag: [UR][HC][DEFINED]
- wording: "CapitalBase = account equity including unrealized PnL, read from clearinghouseState accountValue at computation time (D-13)"
- inputs: clearinghouseState accountValue | outputs: CapitalBase | preconditions: computation time | postconditions: CapitalBase read | state_effects: capital input
- formula: CapitalBase = accountValue (incl unrealized PnL) | units: USD
- invariants: read from authoritative venue state | failure_behavior: NONE | safety_impact: HIGH
- venue_evidence_status: VERIFIED (Phase 2 — marginSummary.accountValue = equity incl. unrealized PnL; unrealized pnl counts toward cross account value/margin)
- venue_evidence_refs: [SRC-107, SRC-115]
- authoritative_source: clearinghouseState only
- owner_decision: DECISION-002
- dependencies: STR-0200 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0225 — MaxSafeNotional_margin = CapitalBase × Leverage_effective / 2 (D-13)
- section: §12.1 Range Survivability | lines: L951–L956 | type: FORMULA | strength: MUST | tag: [UR][DEFINED]
- wording: "MaxSafeNotional_margin = CapitalBase × Leverage_effective / 2 (D-13; the divisor 2 keeps the margin-account liquidation distance at ≈ half the 3×-leverage distance)"
- inputs: CapitalBase; Leverage_effective | outputs: MaxSafeNotional_margin | preconditions: computation | postconditions: safe notional | state_effects: cap input
- formula: MaxSafeNotional_margin = CapitalBase × Leverage_effective / 2 | units: USD notional
- invariants: divisor 2 preserves liquidation distance | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0224, STR-0219 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0226 — HedgeReserveRatio = 0.10; k_liquidity = 0.10 (approved, D-09 Group B)
- section: §12.1 Range Survivability | lines: L957–L958 | type: PARAMETER | strength: MUST | tag: [UR][DEFINED]
- wording: "HedgeReserveRatio = 0.10 (approved, D-09 Group B) … k_liquidity = 0.10 (approved, D-09 Group B)"
- inputs: config | outputs: ratios | preconditions: config | postconditions: set | state_effects: formula inputs
- formula: NONE | units: ratio (0.10 each) | invariants: NONE | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: NONE | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0227 — MaxBasketNotional = min(Leverage_effective×CapitalBase×(1−HedgeReserveRatio), MaxSafeNotional_margin, k_liquidity×MarketDepth)
- section: §12.1 Range Survivability | lines: L937–L944 | type: FORMULA | strength: MUST | tag: [UR][DEFINED]
- wording: "MaxBasketNotional := min( Leverage_effective × CapitalBase × (1 − HedgeReserveRatio), MaxSafeNotional_margin, k_liquidity × MarketDepth )"
- inputs: Leverage_effective; CapitalBase; HedgeReserveRatio; MaxSafeNotional_margin; k_liquidity; MarketDepth | outputs: MaxBasketNotional | preconditions: inputs defined | postconditions: primary mechanical control computed | state_effects: master cap
- formula: MaxBasketNotional = min(Leverage_effective×CapitalBase×(1−HedgeReserveRatio), MaxSafeNotional_margin, k_liquidity×MarketDepth) | units: USD notional
- invariants: primary control against range-induced state corruption | failure_behavior: NONE | safety_impact: CRITICAL
- dependencies: STR-0219, STR-0224, STR-0225, STR-0226, STR-0228 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0228 — MarketDepth = Σ USD bid+ask book depth within ±(10 × StepBps) of mid (D-13)
- section: §12.1 Range Survivability | lines: L959–L962 | type: FORMULA | strength: MUST | tag: [UR][HC][DEFINED]
- wording: "MarketDepth = sum of USD bid+ask book depth within ±(10 × StepBps) of mid at computation time (D-13; matches the DistanceBand upper bound, §8)"
- inputs: L2 book; StepBps; mid | outputs: MarketDepth | preconditions: computation | postconditions: depth measured | state_effects: formula input
- formula: MarketDepth = Σ(bid+ask depth) within ±(10×StepBps) of mid | units: USD
- invariants: matches DistanceBand upper bound | failure_behavior: NONE | safety_impact: MEDIUM
- venue_evidence_status: PARTIALLY_VERIFIED (Phase 2 — l2Book provides per-level px/sz but is bounded to ≤20 levels/side (5 fast/20 slow on WS); the ±10×StepBps window may exceed 20 levels for tight grids. Design nuance for Phase 3; no conflict record)
- venue_evidence_refs: [SRC-105, SRC-109]
- dependencies: STR-0140 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0229 — MaxBasketNotional computed ONCE (proposed → owner-confirmed → binding); formula NOT re-executed while running (§14 global rule)
- section: §12.1 Range Survivability | lines: L964–L966 | type: GUARD | strength: MUST | tag: [UR][DEFINED]
- wording: "Computed ONCE to produce the proposed value; the confirmed value is binding and the formula is NOT re-executed while the system runs (§14 global rule)."
- inputs: proposed value; owner confirmation | outputs: binding value | preconditions: first computation | postconditions: value binding | state_effects: config freeze
- formula: NONE | units: USD notional | invariants: formula never re-executed at runtime | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0227, STR-0257 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0230 — Explicit goal: bounds guarantee a range cannot force an unrecoverable state (not profitability)
- section: §12.1 Range Survivability | lines: L977 | type: INVARIANT | strength: MUST | tag: [UR][DEFINED]
- wording: "these bounds do not guarantee profitability in a range — they guarantee a range cannot force an unrecoverable state."
- inputs: bounds | outputs: safety guarantee | preconditions: monitoring | postconditions: no unrecoverable state | state_effects: NONE
- formula: NONE | units: NONE | invariants: survivability ≠ profitability | failure_behavior: NONE | safety_impact: CRITICAL
- dependencies: STR-0215 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §12.2 Two-Layer framing (restated) (L979–L986)

### STR-0231 — Hedge Layer seeks symmetry with override authority; Profit Layer may be asymmetric, bounded, never overrides; §11.1 ordering is the formal boundary
- section: §12.2 Two-Layer framing | lines: L981 | type: INVARIANT | strength: MUST | tag: [UR][DD][DEFINED]
- wording: "Hedge Layer seeks symmetry, has override authority; Profit Layer may be asymmetric, is bounded by Hedge Layer's exposure caps and never overrides them. §11.1's priority ordering is the formal boundary between the two."
- inputs: layer roles | outputs: boundary | preconditions: NONE | postconditions: layer boundary enforced | state_effects: NONE
- formula: NONE | units: NONE | invariants: hedge symmetry and profit asymmetry are separate; asymmetry only inside DD envelope | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0203 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0232 — Risk precedence over the closure target: acute risk → Hedge/Freeze/Recovery/emergency closure take precedence over waiting for profit
- section: §12.2 Two-Layer framing | lines: L983 | type: PRECEDENCE_RULE | strength: MUST | tag: [UR][DEFINED]
- wording: "if risk becomes acute before the Basket net-profit closure target is reached, Hedge Layer authority, Freeze, Recovery, and emergency closure rules take precedence over waiting for profit."
- inputs: acute risk; closure target | outputs: precedence | preconditions: acute risk pre-target | postconditions: risk actions precede | state_effects: precedence
- formula: NONE | units: NONE | invariants: risk precedence over profit target | failure_behavior: NONE | safety_impact: CRITICAL
- dependencies: STR-0206, STR-0244 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0233 — The net-profit target is not permission to tolerate unrecoverable exposure
- section: §12.2 Two-Layer framing | lines: L983 | type: INVARIANT | strength: MUST_NOT | tag: [UR][DEFINED]
- wording: "The net-profit target is not permission to tolerate unrecoverable exposure"
- inputs: NONE | outputs: NONE | preconditions: NONE | postconditions: no tolerance of unrecoverable exposure | state_effects: NONE
- formula: NONE | units: NONE | invariants: profit never justifies unrecoverable exposure | failure_behavior: NONE | safety_impact: CRITICAL
- dependencies: STR-0232 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §13.1 PnL (L989–L997)

### STR-0234 — BasketNetPnL = BasketRealizedPnL + BasketUnrealizedPnL − BasketFees + BasketFunding
- section: §13.1 PnL | lines: L992–L993 | type: FORMULA | strength: MUST | tag: [SD][DEFINED]
- wording: "BasketNetPnL = BasketRealizedPnL + BasketUnrealizedPnL − BasketFees + BasketFunding"
- inputs: realized/unrealized PnL; fees; funding | outputs: BasketNetPnL | preconditions: accounting | postconditions: net PnL computed | state_effects: PnL accounting
- formula: BasketNetPnL = BasketRealizedPnL + BasketUnrealizedPnL − BasketFees + BasketFunding | units: USD
- invariants: funding included (sign per formula) | failure_behavior: NONE | safety_impact: HIGH
- dependencies: NONE | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0235 — NET (never gross) controls every lifecycle decision (restart target, freeze trigger, closure target)
- section: §13.1 PnL | lines: L996 | type: INVARIANT | strength: MUST | tag: [SD][DEFINED]
- wording: "NET, never gross, controls every lifecycle decision (restart target, freeze trigger, closure target §13.4)."
- inputs: BasketNetPnL | outputs: lifecycle decisions | preconditions: decision point | postconditions: net governs | state_effects: lifecycle control
- formula: NONE | units: USD | invariants: Basket economic decisions use NET PnL | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0234 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0236 — Gross PnL retained only as observability metric; funding not negligible
- section: §13.1 PnL | lines: L996 | type: ECONOMIC_RULE | strength: MUST | tag: [SD][DEFINED]
- wording: "Gross retained only as an observability metric — funding is not the negligible background cost MT5 swap was in GridEA's model."
- inputs: gross PnL; funding | outputs: observability | preconditions: accounting | postconditions: gross observational only | state_effects: metrics
- formula: NONE | units: USD | invariants: funding is material | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0234 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §13.2 States (L998–L1006)

### STR-0237 — Basket state machine: INITIALIZING → ACTIVE → FREEZE_REQUESTED → FREEZING → FROZEN → RESTARTING → (new Basket) → INITIALIZING
- section: §13.2 States | lines: L1000–L1005 | type: LIFECYCLE_STATE | strength: MUST | tag: [SD][DEFINED]
- wording: "INITIALIZING → ACTIVE → FREEZE_REQUESTED → FREEZING → FROZEN → RESTARTING → (new Basket) → INITIALIZING"
- inputs: lifecycle events | outputs: Basket state | preconditions: Basket exists | postconditions: state ∈ set | state_effects: Basket state machine
- formula: NONE | units: NONE | invariants: defined state set | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0005 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0238 — Basket ERROR ⇄ RECOVERY and CLOSED branches
- section: §13.2 States | lines: L1004 | type: LIFECYCLE_STATE | strength: MUST | tag: [SD][DEFINED]
- wording: "ERROR ⇄ RECOVERY … CLOSED"
- inputs: error/recovery/closure events | outputs: ERROR/RECOVERY/CLOSED | preconditions: from ACTIVE/FROZEN | postconditions: branch state set | state_effects: Basket state machine
- formula: NONE | units: NONE | invariants: ERROR⇄RECOVERY bidirectional; CLOSED terminal | failure_behavior: ERROR/RECOVERY | safety_impact: HIGH
- dependencies: STR-0237 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §13.3 Freeze (L1007–L1010)

### STR-0239 — During FROZEN: no new Levels/Cycles/Generations; FREEZE blocks only ENTRY_INTENT
- section: §13.3 Freeze | lines: L1009 | type: GUARD | strength: MUST | tag: [SD][DD][DEFINED]
- wording: "During FROZEN: no new Levels/Cycles/Generations. Every order is tagged ENTRY_INTENT or EXPOSURE_CORRECTION_INTENT at creation; FREEZE blocks only the former."
- inputs: FROZEN state; order tag | outputs: block ENTRY_INTENT | preconditions: FROZEN | postconditions: no new Levels/Cycles/Generations; ENTRY_INTENT blocked | state_effects: freeze gating
- formula: NONE | units: NONE | invariants: FREEZE blocks ENTRY_INTENT only | failure_behavior: block ENTRY_INTENT | safety_impact: CRITICAL
- dependencies: STR-0240 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0240 — Every order tagged ENTRY_INTENT or EXPOSURE_CORRECTION_INTENT at creation
- section: §13.3 Freeze | lines: L1009 | type: GUARD | strength: MUST | tag: [DD][DEFINED]
- wording: "Every order is tagged ENTRY_INTENT or EXPOSURE_CORRECTION_INTENT at creation"
- inputs: order creation | outputs: intent tag | preconditions: order created | postconditions: intent tag set | state_effects: order metadata
- formula: NONE | units: NONE | invariants: mandatory intent tagging | failure_behavior: NONE | safety_impact: HIGH
- dependencies: NONE | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0241 — An opposite-direction hedge is EXPOSURE_CORRECTION_INTENT even without reduceOnly=true
- section: §13.3 Freeze | lines: L1009 | type: GUARD | strength: MUST | tag: [DD][DEFINED]
- wording: "An opposite-direction hedge is EXPOSURE_CORRECTION_INTENT even without reduceOnly=true"
- inputs: hedge order | outputs: intent classification | preconditions: opposite-direction hedge | postconditions: tagged EXPOSURE_CORRECTION_INTENT | state_effects: classification
- formula: NONE | units: NONE | invariants: classification not by reduce-only flag alone | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0240, STR-0242 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0242 — Intent classified by projected ExposureDelta before/after, not by the exchange's reduce-only flag alone
- section: §13.3 Freeze | lines: L1009 | type: GUARD | strength: MUST | tag: [DD][DEFINED]
- wording: "classified by projected ExposureDelta before/after, not by the exchange's reduce-only flag alone."
- inputs: projected ExposureDelta before/after | outputs: intent classification | preconditions: order eval | postconditions: correct classification | state_effects: classification
- formula: NONE | units: base-asset quantity | invariants: projected-delta classification | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0201 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §13.4 Closure (L1011–L1084)

### STR-0243 — Profit-target closure requires BOTH preconditions (net-profit AND residual-exposure)
- section: §13.4 Closure | lines: L1013 | type: GUARD | strength: MUST | tag: [UR][DEFINED]
- wording: "Closure preconditions (both required for a profit-target closure)"
- inputs: (a) net-profit; (b) residual exposure | outputs: closure eligibility | preconditions: both conditions | postconditions: eligible only if both pass | state_effects: closure gate
- formula: NONE | units: NONE | invariants: both required | failure_behavior: not closed unless both pass | safety_impact: CRITICAL
- dependencies: STR-0244, STR-0247 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0244 — Precondition (a): BasketNetPnL ≥ BasketNetProfitClosureTarget
- section: §13.4 Closure | lines: L1016 | type: GUARD | strength: MUST | tag: [UR][DEFINED]
- wording: "BasketNetPnL ≥ BasketNetProfitClosureTarget."
- inputs: BasketNetPnL; target | outputs: pass/fail | preconditions: closure eval | postconditions: net-profit condition | state_effects: closure gate
- formula: BasketNetPnL ≥ BasketNetProfitClosureTarget | units: USD
- invariants: NET PnL only | failure_behavior: not closed if unmet | safety_impact: CRITICAL
- dependencies: STR-0234, STR-0245 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0245 — BasketNetProfitClosureTarget = 3 × (TotalSystemCosts + StepBps_as_USD); StepBps_as_USD = StepBps × MaxBasketNotional / 10000 (D-06)
- section: §13.4 Closure | lines: L1019–L1021 | type: FORMULA | strength: MUST | tag: [UR][DEFINED]
- wording: "BasketNetProfitClosureTarget = 3 × (TotalSystemCosts + StepBps_as_USD); StepBps_as_USD = StepBps × MaxBasketNotional / 10000"
- inputs: TotalSystemCosts; StepBps; MaxBasketNotional | outputs: target | preconditions: first eligibility | postconditions: target computed | state_effects: closure target
- formula: target = 3 × (TotalSystemCosts + StepBps × MaxBasketNotional / 10000) | units: USD
- invariants: derived, computed once | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0246, STR-0140, STR-0227 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0246 — TotalSystemCosts = all execution costs (fees/slippage/hedge/funding/closing/other) accumulated lifetime-to-date (D-15); computed once, owner-confirmed, binding
- section: §13.4 Closure | lines: L1022–L1029 | type: FORMULA | strength: MUST | tag: [UR][DEFINED]
- wording: "TotalSystemCosts includes maker+taker fees, slippage, hedge cost, funding, closing costs, and all other execution costs, accumulated over the Basket's LIFETIME-TO-DATE … used ONCE … the confirmed value is binding and the formula is NOT re-executed"
- inputs: cost components (lifetime-to-date) | outputs: TotalSystemCosts | preconditions: evaluation instant | postconditions: cost accumulated | state_effects: cost accounting
- formula: TotalSystemCosts = Σ(fees, slippage, hedge, funding, closing, other) lifetime-to-date | units: USD
- invariants: lifetime-to-date window (D-15); computed once then binding | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0257 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0247 — Precondition (b): residual ActualExposure ≤ ResidualExposureToleranceAtClosure
- section: §13.4 Closure | lines: L1034 | type: GUARD | strength: MUST | tag: [UR][DEFINED]
- wording: "residual ActualExposure ≤ ResidualExposureToleranceAtClosure."
- inputs: residual ActualExposure; tolerance | outputs: pass/fail | preconditions: closure eval | postconditions: residual-exposure condition | state_effects: closure gate
- formula: residual ActualExposure ≤ ResidualExposureToleranceAtClosure | units: base-asset quantity
- invariants: verified residual exposure required | failure_behavior: not closed if unmet | safety_impact: CRITICAL
- dependencies: STR-0200, STR-0248 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0248 — ResidualExposureToleranceAtClosure := round_to_min_tradable_size(f), f = (StepBps × MaxBasketNotional / 10000) / GridLevels (D-07(F))
- section: §13.4 Closure | lines: L1037–L1046 | type: FORMULA | strength: MUST | tag: [UR][DEFINED]
- wording: "ResidualExposureToleranceAtClosure := round_to_min_tradable_size( f(StepBps, MaxBasketNotional) ) … f := (StepBps × MaxBasketNotional / 10000) / GridLevels"
- inputs: StepBps; MaxBasketNotional; GridLevels; szDecimals | outputs: tolerance | preconditions: closure eval | postconditions: derived tolerance | state_effects: closure tolerance
- formula: f = (StepBps × MaxBasketNotional / 10000) / GridLevels; tol = round_to_min_tradable_size(f) | units: USD notional → base-asset size (szDecimals)
- invariants: derived; resolved to szDecimals grid | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0140, STR-0227, STR-0141, STR-0137 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0249 — Closure sequence is a verified state machine (never equivalent to "close order submitted") — ordered steps
- section: §13.4 Closure | lines: L1053–L1063 | type: STATE_TRANSITION | strength: MUST | tag: [SD][UR][DEFINED]
- wording: "stop new Profit Layer progression → cancel resting progression orders → reconcile authoritative state → protect or correct acute exposure … → close positions … → reconcile fills and actual position state → verify residual exposure within tolerance … → verify BasketNetPnL has reached the closure target … → mark Basket CLOSED only after ALL required conditions pass"
- inputs: closure trigger | outputs: ordered closure | preconditions: closure initiated | postconditions: verified sequence complete | state_effects: Basket closure
- formula: NONE | units: NONE | invariants: verified state machine, not "order submitted" | failure_behavior: block until conditions pass | safety_impact: CRITICAL
- dependencies: STR-0243, STR-0255 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0250 — Gross PnL MUST NOT substitute for the configured net-profit target
- section: §13.4 Closure | lines: L1065 | type: GUARD | strength: MUST_NOT | tag: [UR][DEFINED]
- wording: "Gross PnL MUST NOT substitute for the configured net-profit target"
- inputs: gross PnL | outputs: rejection of substitution | preconditions: closure eval | postconditions: net target used | state_effects: NONE
- formula: NONE | units: USD | invariants: net (not gross) target | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0244 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0251 — Indefinite management: if target unmet and no acute risk, Basket (incl. DISABLED Generations) stays open indefinitely; MUST NOT resume forbidden Profit progression
- section: §13.4 Closure | lines: L1067 | type: GUARD | strength: MUST | tag: [UR][DEFINED]
- wording: "if the net-profit target has not been reached and no acute risk exists, the Basket — including any DISABLED_AT_CYCLE_99 Generations — remains open for management indefinitely. It MUST NOT resume forbidden Profit Layer progression merely because the Basket remains open."
- inputs: target unmet; no acute risk | outputs: stay open | preconditions: unmet target, no acute risk | postconditions: open, no forbidden progression | state_effects: management state
- formula: NONE | units: NONE | invariants: open ≠ resume progression | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0088 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0252 — Hedge Recovery and exposure-correction remain permitted when required for survivability during indefinite management
- section: §13.4 Closure | lines: L1067 | type: GUARD | strength: MUST | tag: [UR][DEFINED]
- wording: "Hedge Recovery and exposure-correction actions remain permitted when required for survivability."
- inputs: survivability need | outputs: permitted corrections | preconditions: indefinite management | postconditions: corrections allowed | state_effects: hedge recovery
- formula: NONE | units: NONE | invariants: correction always available for survivability | failure_behavior: NONE | safety_impact: CRITICAL
- dependencies: STR-0206, STR-0251 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0253 — BasketCloseMode config: IMMEDIATE_IOC / TWAP / HYBRID (default)
- section: §13.4 Closure | lines: L1069–L1079 | type: PARAMETER | strength: MUST | tag: [DD][DEFINED]
- wording: "BasketCloseMode (config): IMMEDIATE_IOC … TWAP … HYBRID (default) — per-leg classification by size vs. book depth"
- inputs: config | outputs: close mode | preconditions: closure | postconditions: mode selected | state_effects: closure policy
- formula: NONE | units: policy | invariants: HYBRID default | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0291 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0254 — TWAP via Hyperliquid native TWAP [HC] (≥30s intervals, ≤3% per-suborder slippage); remaining quantity tracked explicitly, never assumed closed on submission
- section: §13.4 Closure | lines: L1073–L1078 | type: STATE_TRANSITION | strength: MUST | tag: [HC][DD][DEFINED]
- wording: "TWAP — legs above a threshold via Hyperliquid's native TWAP (parent order sliced ≥30s intervals, ≤3% per-suborder slippage); TWAP parent → child fills → actual position → remaining quantity is tracked explicitly, never assumed closed on submission"
- inputs: TWAP parent; child fills; actual position | outputs: tracked remaining qty | preconditions: TWAP close | postconditions: remaining tracked | state_effects: closure tracking
- formula: NONE | units: seconds (≥30); % (≤3%) | invariants: never assumed closed on submission
- failure_behavior: NONE | safety_impact: HIGH
- venue_evidence_status: VERIFIED (Phase 2 — order-types: native TWAP, suborders ≥30s, ≤3% per-suborder slippage, catch-up ≤3× normal suborder)
- venue_evidence_refs: [SRC-112, SRC-104]
- dependencies: STR-0253 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0255 — Every closing leg passes Fillability Analyzer gating AND POSITION_VERIFIED before being counted closed
- section: §13.4 Closure | lines: L1081 | type: GUARD | strength: MUST | tag: [DD][DEFINED]
- wording: "Every leg, regardless of mode, passes Fillability Analyzer gating and POSITION_VERIFIED confirmation before being counted closed."
- inputs: closing legs | outputs: verified-closed legs | preconditions: closing | postconditions: counted closed only after verification | state_effects: closure verification
- formula: NONE | units: NONE | invariants: POSITION_VERIFIED before counted closed | failure_behavior: not counted closed until verified | safety_impact: CRITICAL
- dependencies: STR-0181, STR-0072 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0256 — Basket marked CLOSED only after ALL required conditions pass
- section: §13.4 Closure | lines: L1062 | type: STATE_TRANSITION | strength: MUST | tag: [UR][DEFINED]
- wording: "mark Basket CLOSED only after ALL required conditions pass"
- inputs: closure conditions | outputs: CLOSED | preconditions: all conditions pass | postconditions: Basket CLOSED | state_effects: CLOSED
- formula: NONE | units: NONE | invariants: CLOSED requires verified residual exposure AND net-profit precondition | failure_behavior: not CLOSED until all pass | safety_impact: CRITICAL
- dependencies: STR-0243, STR-0249 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §14 Parameter Reference (L1085–L1183)

> Each row of the §14 tables is registered here as a PARAMETER requirement with its binding value/formula, unit, defining §-reference, and `calibration_status` verbatim. Where a parameter's behavior is defined elsewhere, `dependencies` cross-references the behavioral STR. `impl`/`verif` = NOT_STARTED throughout.

### STR-0257 — §14 GLOBAL RULE: all values/formulas are proposal-only; formula used ONCE; confirmed value binding; formula NOT re-executed while running
- section: §14 Parameter Reference (global rule) | lines: L1089 | type: GUARD | strength: MUST | tag: [UR][DEFINED]
- wording: "All values and formulas … are for proposal to the Strategy Owner only. Formulas are used once … Once confirmed, the value is binding … the formula is not re-executed. Formulas never change values automatically."
- inputs: formula; owner confirmation | outputs: binding value | preconditions: proposal | postconditions: value binding until owner change/shutdown | state_effects: config governance
- formula: NONE | units: NONE | invariants: numeric values never invented by implementation; formulas never auto-change values | failure_behavior: NONE | safety_impact: CRITICAL
- dependencies: NONE | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0258 — EvolutionConfirmationSeconds = 60 s (§4.2, D-03) — CALIBRATABLE
- section: §14 Parameter Reference | lines: L1118 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "EvolutionConfirmationSeconds | 60 | s | §4.2 (D-03) | CALIBRATABLE"
- inputs: config | outputs: value | preconditions: NONE | postconditions: bound value | state_effects: register | formula: NONE | units: s (60)
- invariants: calibration_status = CALIBRATABLE | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0036 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0259 — MaxGenerations = 99 (§3, D-08) — FIXED
- section: §14 Parameter Reference | lines: L1119 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "MaxGenerations | 99 | count | §3 (D-08) | FIXED"
- inputs: config | outputs: value | preconditions: NONE | postconditions: bound | state_effects: register | formula: NONE | units: count (99)
- invariants: calibration_status = FIXED | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0024 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0260 — MaxCyclesPerGeneration = 99 (§3, D-08) — FIXED
- section: §14 Parameter Reference | lines: L1120 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "MaxCyclesPerGeneration | 99 | count | §3 (D-08) | FIXED"
- inputs: config | outputs: value | preconditions: NONE | postconditions: bound | state_effects: register | formula: NONE | units: count (99)
- invariants: calibration_status = FIXED | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0024 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0261 — StepBps = 10 bps (§7.1, D-09 C) — CALIBRATABLE
- section: §14 Parameter Reference | lines: L1126 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "StepBps | 10 | bps | §7.1 (D-09 C) | CALIBRATABLE"
- inputs: config | outputs: value | preconditions: NONE | postconditions: bound | state_effects: register | formula: NONE | units: bps (10)
- invariants: calibration_status = CALIBRATABLE; base anchor | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0140 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0262 — GridLevels = 6 (§7.1, D-09 C) — FIXED (NOT calibratable)
- section: §14 Parameter Reference | lines: L1127 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "GridLevels | 6 | count | §7.1 (D-09 C) | FIXED — NOT calibratable"
- inputs: config | outputs: value | preconditions: NONE | postconditions: bound | state_effects: register | formula: NONE | units: count (6)
- invariants: calibration_status = FIXED — NOT calibratable | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0141 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0263 — FirstLevelDistanceBps = 2 × StepBps = 20 bps (§7.1, D-09 C) — CALIBRATABLE (formula-fixed default)
- section: §14 Parameter Reference | lines: L1128 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "FirstLevelDistanceBps | 2 × StepBps = 20 | bps | §7.1 (D-09 C) | CALIBRATABLE (formula-fixed default)"
- inputs: StepBps | outputs: value | preconditions: StepBps set | postconditions: bound | state_effects: register | formula: 2 × StepBps | units: bps (20)
- invariants: calibration_status = CALIBRATABLE (formula-fixed default) | failure_behavior: NONE | safety_impact: LOW
- dependencies: STR-0142 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0264 — ReferencePriceToleranceBps = 0.33 × StepBps (§5.4.1, D-17) — [DYNAMIC-CALIBRATABLE]
- section: §14 Parameter Reference | lines: L1129 | type: PARAMETER | strength: MUST | tag: [DYN][DEFINED]
- wording: "ReferencePriceToleranceBps | 0.33 × StepBps — e.g. StepBps = 10 → 3.3 bps; 5 → 1.65; 20 → 6.6 | bps | §5.4.1 (D-17) | [DYNAMIC-CALIBRATABLE]"
- inputs: StepBps | outputs: tolerance | preconditions: NONE | postconditions: bound formula | state_effects: register | formula: 0.33 × StepBps | units: bps
- invariants: calibration_status = [DYNAMIC-CALIBRATABLE] | failure_behavior: NONE | safety_impact: HIGH
- dynamic_note: must remain dynamic — never freeze to a constant (D-17; canonical §16: STR-0341)
- dependencies: STR-0096, STR-0341 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0265 — Gen2DistanceMultiplier = 2 (range 1.1–2.0) (§7.1, D-09 C) — CALIBRATABLE
- section: §14 Parameter Reference | lines: L1130 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "Gen2DistanceMultiplier | 2 (range 1.1–2.0) | ratio | §7.1 (D-09 C) | CALIBRATABLE"
- inputs: config | outputs: value | preconditions: NONE | postconditions: bound | state_effects: register | formula: NONE | units: ratio (2; 1.1–2.0)
- invariants: calibration_status = CALIBRATABLE | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0149 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0266 — WeakSideFirstLevelMultiplier = 2 (§7.1, D-09 C) — CALIBRATABLE
- section: §14 Parameter Reference | lines: L1131 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "WeakSideFirstLevelMultiplier | 2 | ratio | §7.1 (D-09 C) | CALIBRATABLE"
- inputs: config | outputs: value | preconditions: NONE | postconditions: bound | state_effects: register | formula: NONE | units: ratio (2)
- invariants: calibration_status = CALIBRATABLE | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0149 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0267 — Gen2SizeMultiplier = 1.5 (§7.1, D-09 C) — CALIBRATABLE
- section: §14 Parameter Reference | lines: L1132 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "Gen2SizeMultiplier | 1.5 | ratio | §7.1 (D-09 C) | CALIBRATABLE"
- inputs: config | outputs: value | preconditions: NONE | postconditions: bound | state_effects: register | formula: NONE | units: ratio (1.5)
- invariants: calibration_status = CALIBRATABLE | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0150 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0268 — CycleReferenceDerivation = TERMINAL_EXECUTION (default of §5.4 four) (§5.4) — FIXED
- section: §14 Parameter Reference | lines: L1133 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "CycleReferenceDerivation | TERMINAL_EXECUTION (default of the four §5.4 options) | policy | §5.4 | FIXED"
- inputs: config | outputs: policy | preconditions: NONE | postconditions: bound | state_effects: register | formula: NONE | units: policy
- invariants: calibration_status = FIXED | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0091 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0269 — PendingArmDistance = 5 × StepBps = 50 bps (§8, D-09 D) — CALIBRATABLE
- section: §14 Parameter Reference | lines: L1139 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "PendingArmDistance | 5 × StepBps = 50 | bps | §8 (D-09 D) | CALIBRATABLE"
- inputs: StepBps | outputs: value | preconditions: NONE | postconditions: bound | state_effects: register | formula: 5 × StepBps | units: bps (50)
- invariants: calibration_status = CALIBRATABLE | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0163 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0270 — MinDepthMultiple = 10 (§8, D-09 D) — CALIBRATABLE
- section: §14 Parameter Reference | lines: L1140 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "MinDepthMultiple | 10 | ratio | §8 (D-09 D) | CALIBRATABLE"
- inputs: config | outputs: value | preconditions: NONE | postconditions: bound | state_effects: register | formula: NONE | units: ratio (10)
- invariants: calibration_status = CALIBRATABLE | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0173 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0271 — DistanceBand = [StepBps/2, 10 × StepBps] = [5,100] bps (§8, D-09 D) — CALIBRATABLE
- section: §14 Parameter Reference | lines: L1141 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "DistanceBand | [StepBps/2, 10 × StepBps] = [5, 100] | bps | §8 (D-09 D) | CALIBRATABLE"
- inputs: StepBps | outputs: band | preconditions: NONE | postconditions: bound | state_effects: register | formula: [StepBps/2, 10 × StepBps] | units: bps ([5,100])
- invariants: calibration_status = CALIBRATABLE | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0174 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0272 — MarginSafetyBuffer = 0.20 × required initial margin (§8, D-09 D) — CALIBRATABLE
- section: §14 Parameter Reference | lines: L1142 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "MarginSafetyBuffer | 0.20 × required initial margin | fraction | §8 (D-09 D) | CALIBRATABLE"
- inputs: required initial margin | outputs: buffer | preconditions: NONE | postconditions: bound | state_effects: register | formula: 0.20 × required initial margin | units: fraction
- invariants: calibration_status = CALIBRATABLE | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0175 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0273 — NetExpectedEdgeFloor = StepBps/10 = 1 bps (§8/§10, D-09 D) — CALIBRATABLE
- section: §14 Parameter Reference | lines: L1143 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "NetExpectedEdgeFloor | StepBps / 10 = 1 | bps | §8/§10 (D-09 D) | CALIBRATABLE"
- inputs: StepBps | outputs: floor | preconditions: NONE | postconditions: bound | state_effects: register | formula: StepBps / 10 | units: bps (1)
- invariants: calibration_status = CALIBRATABLE | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0179, STR-0197 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0274 — ArmPolicy = {AUTO, SEMI, WEBHOOK}; default Testnet=AUTO, Live=SEMI (§8, D-10) — FIXED
- section: §14 Parameter Reference | lines: L1144 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "ArmPolicy | {AUTO, SEMI, WEBHOOK}; default Testnet = AUTO, Live = SEMI | policy | §8 (D-10) | FIXED"
- inputs: environment | outputs: policy | preconditions: NONE | postconditions: bound | state_effects: register | formula: NONE | units: policy
- invariants: calibration_status = FIXED | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0167 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0275 — ArmRequestTimeoutSeconds = 30 s (§8, D-10) — FIXED (required for SEMI/WEBHOOK)
- section: §14 Parameter Reference | lines: L1145 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "ArmRequestTimeoutSeconds | 30 | s | §8 (D-10) | FIXED (required for SEMI/WEBHOOK)"
- inputs: config | outputs: timeout | preconditions: NONE | postconditions: bound | state_effects: register | formula: NONE | units: s (30)
- invariants: calibration_status = FIXED; required for SEMI/WEBHOOK | failure_behavior: UNSET → arming BLOCKED | safety_impact: HIGH
- dependencies: STR-0167, STR-0172 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0276 — EmergencyTolerance = 0.005 × (10000/Leverage_effective) bps (§9.1, D-09 A → D-16) — [DYNAMIC — CALIBRATION PENDING]
- section: §14 Parameter Reference | lines: L1151 | type: PARAMETER | strength: MUST | tag: [DYN][DEFINED]
- wording: "EmergencyTolerance | 0.005 × (10000 / Leverage_effective) — e.g. 2→25, 3→17, 5→10 | bps | §9.1 (D-09 A → D-16) | [DYNAMIC — CALIBRATION PENDING]"
- inputs: Leverage_effective | outputs: tolerance | preconditions: NONE | postconditions: bound formula | state_effects: register | formula: 0.005 × (10000 / Leverage_effective) | units: bps
- invariants: calibration_status = [DYNAMIC — CALIBRATION PENDING] | failure_behavior: NONE | safety_impact: HIGH
- dynamic_note: must remain dynamic — never freeze to a constant (D-16; canonical §16: STR-0338)
- dependencies: STR-0183, STR-0338 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0277 — EmergencyBoundedWaitSeconds = 30 s (§9.1, D-09 A) — FIXED
- section: §14 Parameter Reference | lines: L1152 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "EmergencyBoundedWaitSeconds | 30 | s | §9.1 (D-09 A) | FIXED"
- inputs: config | outputs: wait | preconditions: NONE | postconditions: bound | state_effects: register | formula: NONE | units: s (30)
- invariants: calibration_status = FIXED | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0182 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0278 — ExposureTolerance = (0.001 × StepBps/10) × NotionalPerLevel/MarkPrice (§5.2/§11.1, D-09 A → D-16) — [DYNAMIC — CALIBRATION PENDING]
- section: §14 Parameter Reference | lines: L1158 | type: PARAMETER | strength: MUST | tag: [DYN][DEFINED]
- wording: "ExposureTolerance | (0.001 × StepBps / 10) × NotionalPerLevel / MarkPrice … e.g. 0.00005 BTC at defaults | base-asset quantity | §5.2/§11.1 (D-09 A → D-16) | [DYNAMIC — CALIBRATION PENDING]"
- inputs: StepBps; MaxBasketNotional; GridLevels; MarkPrice | outputs: tolerance | preconditions: NONE | postconditions: bound formula | state_effects: register | formula: (0.001 × StepBps / 10) × (MaxBasketNotional/GridLevels) / MarkPrice | units: base-asset quantity
- invariants: calibration_status = [DYNAMIC — CALIBRATION PENDING] | failure_behavior: NONE | safety_impact: CRITICAL
- dynamic_note: must remain dynamic — never freeze to a constant (D-16; canonical §16: STR-0339)
- dependencies: STR-0083, STR-0339 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0279 — MaxExposureImbalance = (0.25 × 0.5/Leverage_effective) × NotionalPerLevel/MarkPrice (§11.2/§12.1, D-09 A → D-16) — [DYNAMIC — CALIBRATION PENDING]
- section: §14 Parameter Reference | lines: L1159 | type: PARAMETER | strength: MUST | tag: [DYN][DEFINED]
- wording: "MaxExposureImbalance | (0.25 × 0.5 / Leverage_effective) × NotionalPerLevel / MarkPrice … e.g. 0.00208 BTC at defaults (3×) | base-asset quantity | §11.2/§12.1 (D-09 A → D-16) | [DYNAMIC — CALIBRATION PENDING]"
- inputs: Leverage_effective; MaxBasketNotional; GridLevels; MarkPrice | outputs: bound | preconditions: NONE | postconditions: bound formula | state_effects: register | formula: (0.25 × 0.5 / Leverage_effective) × (MaxBasketNotional/GridLevels) / MarkPrice | units: base-asset quantity
- invariants: calibration_status = [DYNAMIC — CALIBRATION PENDING] | failure_behavior: NONE | safety_impact: CRITICAL
- dynamic_note: must remain dynamic — never freeze to a constant (D-16; canonical §16: STR-0340)
- dependencies: STR-0223, STR-0340 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0280 — MaxRangeInducedDD = 100% of Basket equity (§12.1, D-09 B) — FIXED (NOT calibratable)
- section: §14 Parameter Reference | lines: L1160 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "MaxRangeInducedDD | 100% of Basket equity (total basket loss) | % of equity | §12.1 (D-09 B) | FIXED — NOT calibratable"
- inputs: NONE | outputs: bound | preconditions: NONE | postconditions: bound | state_effects: register | formula: NONE | units: % equity (100%)
- invariants: calibration_status = FIXED — NOT calibratable | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0217 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0281 — MaxExecutionCost = 30% of BasketNetPnL (>0) / 100 bps of MaxBasketNotional (≤0) (§12.1, D-09 B) — FIXED
- section: §14 Parameter Reference | lines: L1161 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "MaxExecutionCost | 30% of BasketNetPnL when BasketNetPnL > 0; 100 bps of MaxBasketNotional when BasketNetPnL ≤ 0 | two-regime (fraction / bps) | §12.1 (D-09 B) | FIXED — NOT calibratable"
- inputs: BasketNetPnL; MaxBasketNotional | outputs: bound | preconditions: NONE | postconditions: bound | state_effects: register | formula: two-regime | units: fraction / bps
- invariants: calibration_status = FIXED — NOT calibratable | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0218 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0282 — MaxFailedLevelRate = 5% (window = ALL Levels of ACTIVE Basket) (§12.1, D-09 B) — FIXED
- section: §14 Parameter Reference | lines: L1162 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "MaxFailedLevelRate | 5%, window = ALL Levels of the ACTIVE Basket | % of Levels | §12.1 (D-09 B) | FIXED — NOT calibratable"
- inputs: NONE | outputs: bound | preconditions: NONE | postconditions: bound | state_effects: register | formula: NONE | units: % of Levels (5%)
- invariants: calibration_status = FIXED — NOT calibratable | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0220 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0283 — MaxHedgeCost = 2% of MaxBasketNotional (§12.1, D-09 B) — FIXED
- section: §14 Parameter Reference | lines: L1163 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "MaxHedgeCost | 2% of MaxBasketNotional | % of USD notional | §12.1 (D-09 B) | FIXED — NOT calibratable"
- inputs: MaxBasketNotional | outputs: bound | preconditions: NONE | postconditions: bound | state_effects: register | formula: 2% × MaxBasketNotional | units: % of USD notional
- invariants: calibration_status = FIXED — NOT calibratable | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0221 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0284 — MaxBasketNotional = min(3-term formula); inputs per D-13 (§12.1, D-09 B + D-13) — DERIVED (computed once, then binding)
- section: §14 Parameter Reference | lines: L1164 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "MaxBasketNotional | min(Leverage_effective × CapitalBase × (1 − HedgeReserveRatio), MaxSafeNotional_margin, k_liquidity × MarketDepth); inputs defined at the formula (D-13) … | USD notional | §12.1 (D-09 B + D-13) | DERIVED — computed once, then binding"
- inputs: D-13 inputs | outputs: cap | preconditions: inputs defined | postconditions: bound once | state_effects: register | formula: min(...) | units: USD notional
- invariants: calibration_status = DERIVED — computed once then binding | failure_behavior: NONE | safety_impact: CRITICAL
- dependencies: STR-0227, STR-0229 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0285 — MaxLevelNotional = MaxBasketNotional / GridLevels (§7.3) — DERIVED
- section: §14 Parameter Reference | lines: L1165 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "MaxLevelNotional | MaxBasketNotional / GridLevels | USD notional | §7.3 | DERIVED"
- inputs: MaxBasketNotional; GridLevels | outputs: cap | preconditions: NONE | postconditions: bound | state_effects: register | formula: MaxBasketNotional / GridLevels | units: USD notional
- invariants: calibration_status = DERIVED | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0155 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0286 — MaxLevelNotionalDominant = Gen2SizeMultiplier × (MaxBasketNotional/GridLevels) (§7.3, D-12) — DERIVED
- section: §14 Parameter Reference | lines: L1166 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "MaxLevelNotionalDominant | Gen2SizeMultiplier × (MaxBasketNotional / GridLevels) | USD notional | §7.3 (D-12) | DERIVED"
- inputs: Gen2SizeMultiplier; MaxBasketNotional; GridLevels | outputs: cap | preconditions: NONE | postconditions: bound | state_effects: register | formula: Gen2SizeMultiplier × (MaxBasketNotional / GridLevels) | units: USD notional
- invariants: calibration_status = DERIVED | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0156 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0287 — MaxCycleNotional = MaxBasketNotional / MaxActiveCycles (§7.3, D-14) — DERIVED
- section: §14 Parameter Reference | lines: L1167 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "MaxCycleNotional | MaxBasketNotional / MaxActiveCycles; MaxActiveCycles = count of all Cycles … incl. COMPLETED (D-14) | USD notional | §7.3 (D-14) | DERIVED"
- inputs: MaxBasketNotional; MaxActiveCycles | outputs: cap | preconditions: NONE | postconditions: bound | state_effects: register | formula: MaxBasketNotional / MaxActiveCycles | units: USD notional
- invariants: calibration_status = DERIVED | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0157, STR-0161 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0288 — MaxGenerationNotional = MaxBasketNotional / MaxActiveGenerations (§7.3, D-14) — DERIVED
- section: §14 Parameter Reference | lines: L1168 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "MaxGenerationNotional | MaxBasketNotional / MaxActiveGenerations; MaxActiveGenerations = count of all Generations … incl. DISABLED_AT_CYCLE_99 (D-14) | USD notional | §7.3 (D-14) | DERIVED"
- inputs: MaxBasketNotional; MaxActiveGenerations | outputs: cap | preconditions: NONE | postconditions: bound | state_effects: register | formula: MaxBasketNotional / MaxActiveGenerations | units: USD notional
- invariants: calibration_status = DERIVED | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0158, STR-0160 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0289 — BasketNetProfitClosureTarget = 3 × (TotalSystemCosts + StepBps_as_USD) (§13.4, D-06) — DERIVED (computed once, owner-confirmed, binding)
- section: §14 Parameter Reference | lines: L1174 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "BasketNetProfitClosureTarget | 3 × (TotalSystemCosts + StepBps_as_USD); StepBps_as_USD = StepBps × MaxBasketNotional / 10000; TotalSystemCosts = approved cost set … lifetime-to-date (D-15) | USD | §13.4 (D-06) | DERIVED — computed once … then binding"
- inputs: TotalSystemCosts; StepBps; MaxBasketNotional | outputs: target | preconditions: first eligibility | postconditions: bound once | state_effects: register | formula: 3 × (TotalSystemCosts + StepBps × MaxBasketNotional / 10000) | units: USD
- invariants: calibration_status = DERIVED — computed once, owner-confirmed, binding | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0245 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0290 — ResidualExposureToleranceAtClosure = round_to_min_tradable_size(f), f = (StepBps × MaxBasketNotional/10000)/GridLevels (§13.4, D-07(F)) — DERIVED
- section: §14 Parameter Reference | lines: L1175 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "ResidualExposureToleranceAtClosure | round_to_min_tradable_size(f), f = (StepBps × MaxBasketNotional / 10000) / GridLevels (D-07(F)) | USD notional → resolved to base-asset size (szDecimals, §6.3) | §13.4 (D-07) | DERIVED"
- inputs: StepBps; MaxBasketNotional; GridLevels; szDecimals | outputs: tolerance | preconditions: NONE | postconditions: bound | state_effects: register | formula: round_to_min_tradable_size((StepBps × MaxBasketNotional / 10000) / GridLevels) | units: USD → base-asset size
- invariants: calibration_status = DERIVED | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0248 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0291 — BasketCloseMode = HYBRID (default of three §13.4 options) (§13.4) — FIXED
- section: §14 Parameter Reference | lines: L1176 | type: PARAMETER | strength: MUST | tag: [DEFINED]
- wording: "BasketCloseMode | HYBRID (default of the three §13.4 options) | policy | §13.4 | FIXED"
- inputs: config | outputs: policy | preconditions: NONE | postconditions: bound | state_effects: register | formula: NONE | units: policy
- invariants: calibration_status = FIXED | failure_behavior: NONE | safety_impact: MEDIUM
- dependencies: STR-0253 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0292 — Calibration allowlist (D-09 Group E): Groups A/C(except GridLevels)/D calibratable; Group B not; four dynamic defaults (D-16 ×3, D-17) are priority calibration targets
- section: §14 Parameter Reference | lines: L1178–L1180 | type: GUARD | strength: MUST | tag: [DEFINED]
- wording: "Group A rows — all CALIBRATABLE. Group C rows — all CALIBRATABLE except GridLevels. Group D rows — all CALIBRATABLE. Group B rows — NOT calibratable (proposal-only). The four dynamic defaults … are calibratable and are the priority calibration targets."
- inputs: parameter groups | outputs: allowlist | preconditions: NONE | postconditions: calibratability defined | state_effects: calibration policy
- formula: NONE | units: NONE | invariants: Group B not calibratable; GridLevels excluded | failure_behavior: NONE | safety_impact: HIGH
- dependencies: STR-0257 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §15 State Machine Invariants (L1184–L1214)

> Base invariants `[DD]` (L1188) captured individually as STR-0293..STR-0315; amendment invariants 1–20 `[UR][DD]` (L1192–L1211) as STR-0316..STR-0335. All INVARIANT, strength MUST/MUST_NOT, impl/verif NOT_STARTED. `source_lines` = L1188 for all base clauses (single prose line), L1192–L1211 for amendment items.

### STR-0293 — Level FILLED ⇔ Order Fill ∧ Position Delta Verified
- section: §15 (base) | lines: L1188 | type: INVARIANT | strength: MUST | tag: [DD][DEFINED]
- wording: "Level FILLED ⇔ Order Fill ∧ Position Delta Verified" | safety_impact: CRITICAL
- formula: LEVEL FILLED ⇔ ORDER FILLED ∧ POSITION DELTA VERIFIED | units: NONE | inputs: order fill; position delta | outputs: FILLED | preconditions: both | postconditions: FILLED only if both | state_effects: FILLED gating | invariants: core | failure_behavior: not FILLED otherwise | dependencies: STR-0131 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0294 — Actual Exposure only from authoritative exchange state
- section: §15 (base) | lines: L1188 | type: INVARIANT | strength: MUST | tag: [DD][DEFINED]
- wording: "Actual Exposure only from authoritative exchange state" | safety_impact: CRITICAL
- formula: NONE | units: base-asset quantity | inputs: authoritative state | outputs: ActualExposure | preconditions: authoritative read | postconditions: actual from venue only | state_effects: exposure | invariants: no local bookkeeping | failure_behavior: NONE | dependencies: STR-0200 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0295 — Expected Exposure never treated as Actual
- section: §15 (base) | lines: L1188 | type: INVARIANT | strength: MUST_NOT | tag: [DD][DEFINED]
- wording: "Expected Exposure never treated as Actual" | safety_impact: CRITICAL
- formula: NONE | units: base-asset quantity | inputs: ExpectedExposure | outputs: NONE | preconditions: NONE | postconditions: expected ≠ actual | state_effects: exposure | invariants: separation | failure_behavior: NONE | dependencies: STR-0199, STR-0200 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0296 — Grid progression blocked while ExposureDelta exceeds tolerance, unless Hedge Recovery is the active transition
- section: §15 (base) | lines: L1188 | type: INVARIANT | strength: MUST | tag: [DD][DEFINED]
- wording: "Grid progression blocked while ExposureDelta exceeds tolerance, unless Hedge Recovery is the active transition" | safety_impact: CRITICAL
- formula: NONE | units: base-asset quantity | inputs: ExposureDelta; tolerance | outputs: block | preconditions: progression | postconditions: blocked unless hedge recovery | state_effects: gating | invariants: hard gate | failure_behavior: BLOCKED | dependencies: STR-0205 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0297 — Emergency execution cannot exceed EmergencyTolerance
- section: §15 (base) | lines: L1188 | type: INVARIANT | strength: MUST_NOT | tag: [DD][DEFINED]
- wording: "Emergency execution cannot exceed EmergencyTolerance" | safety_impact: CRITICAL
- formula: NONE | units: bps | inputs: EmergencyTolerance | outputs: bounded execution | preconditions: emergency | postconditions: never exceeds tol | state_effects: bound | invariants: bounded | failure_behavior: SKIP | dependencies: STR-0187 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0298 — Every order has a persistent unique cloid, persisted BEFORE network submission
- section: §15 (base) | lines: L1188 | type: INVARIANT | strength: MUST | tag: [DD][DEFINED]
- wording: "Every order has a persistent unique client identifier (cloid), persisted BEFORE network submission" | safety_impact: CRITICAL
- formula: NONE | units: NONE | inputs: cloid | outputs: persisted id | preconditions: before submission | postconditions: cloid persisted first | state_effects: idempotency | invariants: persist-before-submit | failure_behavior: NONE | dependencies: STR-0133 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0299 — Price/size normalized before signing
- section: §15 (base) | lines: L1188 | type: INVARIANT | strength: MUST | tag: [DD][DEFINED]
- wording: "Price/size normalized before signing" | safety_impact: HIGH
- formula: NONE | units: NONE | inputs: price; size | outputs: normalized order | preconditions: before signing | postconditions: normalized | state_effects: normalization | invariants: normalize-before-sign | failure_behavior: NONE | dependencies: STR-0138 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0300 — Maker/Taker decisions account for actual execution economics (§10)
- section: §15 (base) | lines: L1188 | type: INVARIANT | strength: MUST | tag: [DD][DEFINED]
- wording: "Maker/Taker decisions account for actual execution economics (§10)" | safety_impact: HIGH
- formula: NONE | units: NONE | inputs: NetExpectedEdge | outputs: path decision | preconditions: path choice | postconditions: economics-aware | state_effects: path | invariants: economics-based | failure_behavior: NONE | dependencies: STR-0193 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0301 — Taker execution never occurs solely because a maker order timed out (§9.2)
- section: §15 (base) | lines: L1188 | type: INVARIANT | strength: MUST_NOT | tag: [DD][DEFINED]
- wording: "Taker execution never occurs solely because a maker order timed out (§9.2)" | safety_impact: HIGH
- formula: NONE | units: NONE | inputs: timeout | outputs: no auto-taker | preconditions: maker timeout | postconditions: taker only if justified | state_effects: path | invariants: no auto-escalation | failure_behavior: four-way re-eval | dependencies: STR-0188 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0302 — Mirror Intent always passes normal execution validation (§11.3)
- section: §15 (base) | lines: L1188 | type: INVARIANT | strength: MUST | tag: [DD][DEFINED]
- wording: "Mirror Intent always passes normal execution validation (§11.3)" | safety_impact: HIGH
- formula: NONE | units: NONE | inputs: mirror intent | outputs: gated order | preconditions: mirror | postconditions: passes §8/§10 | state_effects: gating | invariants: no bypass | failure_behavior: gate fail → IDLE | dependencies: STR-0210 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0303 — Basket CLOSED requires verified residual exposure within tolerance AND the net-profit closure precondition where applicable (§13.4)
- section: §15 (base) | lines: L1188 | type: INVARIANT | strength: MUST | tag: [DD][DEFINED]
- wording: "Basket CLOSED requires verified residual exposure within tolerance AND the net-profit closure precondition where applicable (§13.4)" | safety_impact: CRITICAL
- formula: NONE | units: NONE | inputs: residual exposure; net PnL | outputs: closed | preconditions: both conditions | postconditions: CLOSED only if both | state_effects: closure | invariants: both required | failure_behavior: not closed | dependencies: STR-0243 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0304 — Evolution cannot be triggered by an unverified price crossing
- section: §15 (base) | lines: L1188 | type: INVARIANT | strength: MUST_NOT | tag: [DD][DEFINED]
- wording: "Evolution cannot be triggered by an unverified price crossing" | safety_impact: CRITICAL
- formula: NONE | units: NONE | inputs: price crossing | outputs: no Evolution | preconditions: unverified crossing | postconditions: no Evolution | state_effects: NONE | invariants: verified-only | failure_behavior: NONE | dependencies: STR-0033 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0305 — Cycle transition must not create unintended level overlap (computable test §5.6)
- section: §15 (base) | lines: L1188 | type: INVARIANT | strength: MUST_NOT | tag: [DD][DEFINED]
- wording: "Cycle transition must not create unintended level overlap (computable test: §5.6)" | safety_impact: HIGH
- formula: NONE | units: NONE | inputs: §5.6 test | outputs: no overlap | preconditions: transition | postconditions: no overlap | state_effects: gating | invariants: computable | failure_behavior: BLOCKED | dependencies: STR-0104 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0306 — GenerationID/CycleID are independent internal fields, never encoded together
- section: §15 (base) | lines: L1188 | type: INVARIANT | strength: MUST_NOT | tag: [DD][DEFINED]
- wording: "GenerationID/CycleID are independent internal fields, never encoded together" | safety_impact: MEDIUM
- formula: NONE | units: NONE | inputs: IDs | outputs: independent fields | preconditions: NONE | postconditions: never co-encoded | state_effects: identity | invariants: independence | failure_behavior: NONE | dependencies: STR-0016 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0307 — Range oscillation must not inherently corrupt the state machine
- section: §15 (base) | lines: L1188 | type: INVARIANT | strength: MUST_NOT | tag: [DD][DEFINED]
- wording: "Range oscillation must not inherently corrupt the state machine" | safety_impact: CRITICAL
- formula: NONE | units: NONE | inputs: range oscillation | outputs: stable state machine | preconditions: ranging | postconditions: no corruption | state_effects: NONE | invariants: robustness | failure_behavior: three-layer response | dependencies: STR-0215 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0308 — Hedge symmetry and profit asymmetry are separate concepts
- section: §15 (base) | lines: L1188 | type: INVARIANT | strength: MUST | tag: [DD][DEFINED]
- wording: "Hedge symmetry and profit asymmetry are separate concepts" | safety_impact: HIGH
- formula: NONE | units: NONE | inputs: layers | outputs: separation | preconditions: NONE | postconditions: separate concepts | state_effects: NONE | invariants: separation | failure_behavior: NONE | dependencies: STR-0231 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0309 — Profit asymmetry permitted only inside the Basket risk/DD envelope
- section: §15 (base) | lines: L1188 | type: INVARIANT | strength: MUST | tag: [DD][DEFINED]
- wording: "Profit asymmetry permitted only inside the Basket risk/DD envelope" | safety_impact: HIGH
- formula: NONE | units: NONE | inputs: risk envelope | outputs: bounded asymmetry | preconditions: NONE | postconditions: within envelope | state_effects: NONE | invariants: bounded | failure_behavior: NONE | dependencies: STR-0231 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0310 — Basket economic decisions use NET PnL
- section: §15 (base) | lines: L1188 | type: INVARIANT | strength: MUST | tag: [DD][DEFINED]
- wording: "Basket economic decisions use NET PnL" | safety_impact: HIGH
- formula: NONE | units: USD | inputs: BasketNetPnL | outputs: decisions | preconditions: decision | postconditions: net used | state_effects: lifecycle | invariants: net-only | failure_behavior: NONE | dependencies: STR-0235 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0311 — A skipped level is preferable to an unsafe or economically irrational execution
- section: §15 (base) | lines: L1188 | type: INVARIANT | strength: SHOULD | tag: [DD][DEFINED]
- wording: "A skipped level is preferable to an unsafe or economically irrational execution" | safety_impact: HIGH
- formula: NONE | units: NONE | inputs: unsafe/uneconomic option | outputs: skip preference | preconditions: choice | postconditions: prefer skip | state_effects: SKIP | invariants: capital preservation | failure_behavior: LEVEL_SKIPPED | dependencies: STR-0198 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0312 — A slower verified transition is preferable to a fast unverified one
- section: §15 (base) | lines: L1188 | type: INVARIANT | strength: SHOULD | tag: [DD][DEFINED]
- wording: "A slower verified transition is preferable to a fast unverified one" | safety_impact: HIGH
- formula: NONE | units: NONE | inputs: verified vs fast | outputs: prefer verified | preconditions: choice | postconditions: verified preferred | state_effects: NONE | invariants: verification-first | failure_behavior: NONE | dependencies: STR-0072 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0313 — Human-readable identity remains deterministic (G{..}-C{..}-{Dir}{..} format)
- section: §15 (base) | lines: L1188 | type: INVARIANT | strength: MUST | tag: [DD][DEFINED]
- wording: "Human-readable identity remains deterministic (G{GenerationID:02d}-C{CycleID:02d}-{Direction}{LevelID:02d})" | safety_impact: MEDIUM
- formula: G{GenerationID:02d}-C{CycleID:02d}-{Direction}{LevelID:02d} | units: NONE | inputs: identity fields | outputs: display | preconditions: NONE | postconditions: deterministic string | state_effects: display | invariants: deterministic | failure_behavior: NONE | dependencies: STR-0020 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0314 — No state transition depends solely on intended orders
- section: §15 (base) | lines: L1188 | type: INVARIANT | strength: MUST_NOT | tag: [DD][DEFINED]
- wording: "No state transition depends solely on intended orders" | safety_impact: CRITICAL
- formula: NONE | units: NONE | inputs: intended orders | outputs: no transition | preconditions: intent only | postconditions: no transition from intent alone | state_effects: NONE | invariants: verified-only transitions | failure_behavior: NONE | dependencies: STR-0004 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0315 — Every state transition is reconstructable from persisted state and authoritative exchange events
- section: §15 (base) | lines: L1188 | type: INVARIANT | strength: MUST | tag: [DD][DEFINED]
- wording: "Every state transition is reconstructable from persisted state and authoritative exchange events" | safety_impact: CRITICAL
- formula: NONE | units: NONE | inputs: persisted state; exchange events | outputs: reconstructable transition | preconditions: NONE | postconditions: reconstructable | state_effects: persistence | invariants: reconstructability | failure_behavior: NONE | dependencies: STR-0171 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0316 — Amendment invariant 1: CycleID always in 0..99 (and below effective limit)
- section: §15 (amendment 1) | lines: L1192 | type: INVARIANT | strength: MUST | tag: [UR][DD][DEFINED]
- wording: "CycleID is always in 0..99 (and always below the effective limit)." | safety_impact: HIGH
- formula: 0 ≤ CycleID ≤ 99 | units: count | inputs: CycleID | outputs: range | preconditions: NONE | postconditions: in range | state_effects: identity | invariants: bounded | failure_behavior: reject | dependencies: STR-0018 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0317 — Amendment invariant 2: GenerationID always in 0..99 (and below effective limit)
- section: §15 (amendment 2) | lines: L1193 | type: INVARIANT | strength: MUST | tag: [UR][DD][DEFINED]
- wording: "GenerationID is always in 0..99 (and always below the effective limit)." | safety_impact: HIGH
- formula: 0 ≤ GenerationID ≤ 99 | units: count | inputs: GenerationID | outputs: range | preconditions: NONE | postconditions: in range | state_effects: identity | invariants: bounded | failure_behavior: reject | dependencies: STR-0017 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0318 — Amendment invariant 3: No Cycle 100 may ever be created
- section: §15 (amendment 3) | lines: L1194 | type: INVARIANT | strength: MUST_NOT | tag: [UR][DD][DEFINED]
- wording: "No Cycle 100 may ever be created." | safety_impact: HIGH
- formula: NONE | units: count | inputs: create request | outputs: reject | preconditions: CycleID=100 | postconditions: rejected | state_effects: NONE | invariants: no Cycle 100 | failure_behavior: reject | dependencies: STR-0021 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0319 — Amendment invariant 4: No Generation 100 may ever be created
- section: §15 (amendment 4) | lines: L1195 | type: INVARIANT | strength: MUST_NOT | tag: [UR][DD][DEFINED]
- wording: "No Generation 100 may ever be created." | safety_impact: HIGH
- formula: NONE | units: count | inputs: create request | outputs: reject | preconditions: GenerationID=100 | postconditions: rejected | state_effects: NONE | invariants: no Generation 100 | failure_behavior: reject (GENERATION_ID_LIMIT) | dependencies: STR-0021, STR-0058 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0320 — Amendment invariant 5: Terminal-level reach creates a new Cycle in the same Generation when CycleID < effective limit
- section: §15 (amendment 5) | lines: L1196 | type: INVARIANT | strength: MUST | tag: [UR][DD][DEFINED]
- wording: "Terminal-level reach creates a new Cycle in the same Generation when CycleID < the effective limit." | safety_impact: MEDIUM
- formula: NONE | units: NONE | inputs: terminal reach | outputs: new Cycle | preconditions: CycleID<limit | postconditions: new Cycle same Generation | state_effects: Cycle transition | invariants: same Generation | failure_behavior: NONE | dependencies: STR-0074 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0321 — Amendment invariant 6: Terminal-level reach alone does not create a new Generation
- section: §15 (amendment 6) | lines: L1197 | type: INVARIANT | strength: MUST_NOT | tag: [UR][DD][DEFINED]
- wording: "Terminal-level reach alone does not create a new Generation." | safety_impact: HIGH
- formula: NONE | units: NONE | inputs: terminal reach | outputs: no Generation | preconditions: terminal only | postconditions: no Generation | state_effects: NONE | invariants: terminal≠Evolution | failure_behavior: NONE | dependencies: STR-0033 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0322 — Amendment invariant 7: A path-dependent verified return may create a successor Generation only when eligible
- section: §15 (amendment 7) | lines: L1198 | type: INVARIANT | strength: MUST | tag: [UR][DD][DEFINED]
- wording: "A path-dependent verified return may create a successor Generation only when the Generation is eligible." | safety_impact: HIGH
- formula: NONE | units: NONE | inputs: verified return; eligibility | outputs: successor | preconditions: eligible | postconditions: successor created | state_effects: new Generation | invariants: verified+eligible | failure_behavior: INELIGIBLE_EVOLUTION_CANDIDATE | dependencies: STR-0025, STR-0032 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0323 — Amendment invariant 8: Each Generation may create at most one successor; lock permanent (spans full lifecycle, D-08)
- section: §15 (amendment 8) | lines: L1199 | type: INVARIANT | strength: MUST | tag: [UR][DD][DEFINED]
- wording: "Each Generation may create at most one successor before its Cycle-limit boundary … the successor lock is permanent for that Generation" | safety_impact: HIGH
- formula: NONE | units: NONE | inputs: successor events | outputs: one-successor | preconditions: NONE | postconditions: ≤1 successor ever | state_effects: successor lock | invariants: permanent lock | failure_behavior: block second | dependencies: STR-0049, STR-0061 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0324 — Amendment invariant 9: After creating a successor, later Cycles below the limit cannot create another successor
- section: §15 (amendment 9) | lines: L1200 | type: INVARIANT | strength: MUST_NOT | tag: [UR][DD][DEFINED]
- wording: "After a Generation creates a successor, later Cycles below the Cycle limit cannot create another successor from that Generation." | safety_impact: HIGH
- formula: NONE | units: NONE | inputs: later Cycles | outputs: no successor | preconditions: lock active | postconditions: no second successor | state_effects: lock | invariants: lock persists across Cycles | failure_behavior: block | dependencies: STR-0051 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0325 — Amendment invariant 10: Reaching the Cycle limit disables the Generation's further Profit Layer progression
- section: §15 (amendment 10) | lines: L1201 | type: INVARIANT | strength: MUST | tag: [UR][DD][DEFINED]
- wording: "Reaching the Cycle limit disables the Generation's further Profit Layer progression." | safety_impact: HIGH
- formula: NONE | units: NONE | inputs: Cycle-limit reach | outputs: disable | preconditions: at limit | postconditions: progression disabled | state_effects: DISABLED_AT_CYCLE_99 | invariants: disable at limit | failure_behavior: NONE | dependencies: STR-0084 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0326 — Amendment invariant 11: DISABLED_AT_CYCLE_99 does not mean the Generation's positions are closed
- section: §15 (amendment 11) | lines: L1202 | type: INVARIANT | strength: MUST | tag: [UR][DD][DEFINED]
- wording: "DISABLED_AT_CYCLE_99 does not mean the Generation's positions are closed." | safety_impact: HIGH
- formula: NONE | units: NONE | inputs: disabled state | outputs: not-closed | preconditions: disabled | postconditions: positions live | state_effects: NONE | invariants: disabled≠closed | failure_behavior: NONE | dependencies: STR-0045 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0327 — Amendment invariant 12: A disabled Generation remains in Basket exposure/PnL/funding/fee/hedge/reconciliation accounting
- section: §15 (amendment 12) | lines: L1203 | type: INVARIANT | strength: MUST | tag: [UR][DD][DEFINED]
- wording: "A disabled Generation remains in Basket exposure, PnL, funding, fee, hedge, and reconciliation accounting." | safety_impact: HIGH
- formula: NONE | units: NONE | inputs: disabled Generation | outputs: retained accounting | preconditions: disabled | postconditions: full accounting retained | state_effects: accounting | invariants: exposure fully live | failure_behavior: NONE | dependencies: STR-0088 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0328 — Amendment invariant 13: Basket closure requires the approved net-profit target and the verified residual exposure condition
- section: §15 (amendment 13) | lines: L1204 | type: INVARIANT | strength: MUST | tag: [UR][DD][DEFINED]
- wording: "Basket closure requires the approved net-profit target and the verified residual exposure condition." | safety_impact: CRITICAL
- formula: NONE | units: NONE | inputs: net-profit; residual exposure | outputs: closure gate | preconditions: closure | postconditions: both required | state_effects: closure | invariants: both required | failure_behavior: not closed | dependencies: STR-0243 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0329 — Amendment invariant 14: Acute Hedge Recovery may override waiting for the net-profit target
- section: §15 (amendment 14) | lines: L1205 | type: INVARIANT | strength: MUST | tag: [UR][DD][DEFINED]
- wording: "Acute Hedge Recovery may override waiting for the net-profit target." | safety_impact: CRITICAL
- formula: NONE | units: NONE | inputs: acute risk | outputs: override | preconditions: acute | postconditions: hedge precedence | state_effects: hedge recovery | invariants: risk precedence | failure_behavior: NONE | dependencies: STR-0232 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0330 — Amendment invariant 15: A raw price crossing/ack/isolated fill cannot trigger Cycle completion or Generation creation
- section: §15 (amendment 15) | lines: L1206 | type: INVARIANT | strength: MUST_NOT | tag: [UR][DD][DEFINED]
- wording: "A raw price crossing, order acknowledgement, or isolated fill message cannot trigger Cycle completion or Generation creation." | safety_impact: CRITICAL
- formula: NONE | units: NONE | inputs: raw signals | outputs: no transition | preconditions: unverified | postconditions: no Cycle/Generation | state_effects: NONE | invariants: verified-only | failure_behavior: NONE | dependencies: STR-0073, STR-0304 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0331 — Amendment invariant 16: GenerationID and CycleID remain independent fields
- section: §15 (amendment 16) | lines: L1207 | type: INVARIANT | strength: MUST | tag: [UR][DD][DEFINED]
- wording: "GenerationID and CycleID remain independent fields." | safety_impact: MEDIUM
- formula: NONE | units: NONE | inputs: IDs | outputs: independence | preconditions: NONE | postconditions: independent | state_effects: identity | invariants: independence | failure_behavior: NONE | dependencies: STR-0306 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0332 — Amendment invariant 17: Historical Cycles and Generations are never deleted, overwritten, or recycled
- section: §15 (amendment 17) | lines: L1208 | type: INVARIANT | strength: MUST_NOT | tag: [UR][DD][DEFINED]
- wording: "Historical Cycles and Generations are never deleted, overwritten, or recycled." | safety_impact: HIGH
- formula: NONE | units: NONE | inputs: historical objects | outputs: immutability | preconditions: exists | postconditions: preserved | state_effects: history | invariants: immutable history | failure_behavior: reject mutation | dependencies: STR-0023 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0333 — Amendment invariant 18: An apparent Evolution after the one-successor lock is recorded as ineligible, not silently executed
- section: §15 (amendment 18) | lines: L1209 | type: INVARIANT | strength: MUST | tag: [UR][DD][DEFINED]
- wording: "An apparent Evolution after the one-successor lock is recorded as an ineligible Evolution candidate, not silently executed." | safety_impact: HIGH
- formula: NONE | units: NONE | inputs: apparent Evolution; lock | outputs: ineligible record | preconditions: lock active | postconditions: recorded, not executed | state_effects: INELIGIBLE_EVOLUTION_CANDIDATE | invariants: never silent | failure_behavior: INELIGIBLE_EVOLUTION_CANDIDATE | dependencies: STR-0054 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0334 — Amendment invariant 19: Every Generation/Cycle transition is reconstructable from persisted events and authoritative exchange observations
- section: §15 (amendment 19) | lines: L1210 | type: INVARIANT | strength: MUST | tag: [UR][DD][DEFINED]
- wording: "Every Generation/Cycle transition is reconstructable from persisted events and authoritative exchange observations." | safety_impact: CRITICAL
- formula: NONE | units: NONE | inputs: persisted events; exchange observations | outputs: reconstructable | preconditions: NONE | postconditions: reconstructable | state_effects: persistence | invariants: reconstructability (extends to arm workflow) | failure_behavior: NONE | dependencies: STR-0315, STR-0171 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0335 — Amendment invariant 20: No transition may bypass normal risk, exposure, fillability, economics, precision, and reconciliation gates
- section: §15 (amendment 20) | lines: L1211 | type: INVARIANT | strength: MUST_NOT | tag: [UR][DD][DEFINED]
- wording: "No transition may bypass normal risk, exposure, fillability, economics, precision, and reconciliation gates." | safety_impact: CRITICAL
- formula: NONE | units: NONE | inputs: transition | outputs: gated transition | preconditions: any transition | postconditions: all gates applied | state_effects: gating | invariants: no gate bypass | failure_behavior: BLOCKED | dependencies: STR-0163, STR-0203 | impl: NOT_STARTED | verif: NOT_STARTED

---

## §16 Dynamic Defaults Pending Calibration (L1215–L1369)

### STR-0336 — §16 handling of the four dynamic defaults (tagged at every use; each read logged; runs distinguishable in audit; owner-overridable; supersede prior [TEMP] defaults)
- section: §16 Dynamic Defaults | lines: L1219–L1225 | type: GUARD | strength: MUST | tag: [DYN][DEFINED]
- wording: "Each is tagged [DYNAMIC — CALIBRATION PENDING] (D-16) or [DYNAMIC-CALIBRATABLE] (D-17) at every point of use … overridable by the Strategy Owner at any time … every read of a dynamic default is logged with its tag, and a run using dynamic defaults is distinguishable in the audit trail from a run using calibrated, owner-confirmed values."
- inputs: dynamic default reads | outputs: tagged/logged usage | preconditions: default used | postconditions: logged + distinguishable | state_effects: audit
- formula: NONE | units: NONE | invariants: never frozen; owner override needs no recalibration; supersede prior [TEMP] | failure_behavior: NONE | safety_impact: HIGH
- dynamic_note: must remain dynamic — never freeze to a constant (D-16/D-17)
- dependencies: STR-0257 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0337 — [HC] Hyperliquid contract mechanics used by the derivations (maintenance=½ initial at max lev; hourly funding 1/8; BTC/ETH max lev 40×; mark price for margin/liquidation)
- section: §16 Dynamic Defaults | lines: L1227–L1238 | type: EVENT_SEMANTICS | strength: MUST | tag: [HC][DEFINED]
- wording: "Maintenance margin = half of initial margin at max leverage. Funding is paid hourly, at 1/8 of the 8-hour funding rate. BTC/ETH max leverage = 40x → initial margin fraction 2.5%, maintenance margin fraction 1.25% … Mark price is used for margin accounting and liquidation triggers."
- inputs: venue margin/funding mechanics | outputs: derivation inputs | preconditions: derivations | postconditions: mechanics relied on | state_effects: derivation basis
- formula: maintenance = ½ × initial (at max lev); funding hourly = (1/8) × 8h rate | units: % / ratio
- invariants: derivations grounded in venue mechanics | failure_behavior: NONE | safety_impact: HIGH
- venue_evidence_status: RESOLVED_VIA_OWNER_DECISION (Phase 3; was CONFLICTED Phase 2/2b. VERIFIED mechanics: maintenance=½ initial at max leverage, funding hourly at 1/8 of 8h rate, mark price for margin/liquidation. The "BTC/ETH max leverage = 40x" figure is ILLUSTRATIVE per DECISION-001; runtime reads meta.maxLeverage live and Leverage_effective=min(3, meta.maxLeverage)=3, so formulas unaffected)
- owner_decision: DECISION-001
- venue_evidence_refs: [SRC-113, SRC-115, SRC-116, SRC-117, SRC-118]
- dependencies: NONE | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0338 — [DYN] CANONICAL EmergencyTolerance := 0.005 × (10000 / Leverage_effective) bps (D-16) — must remain dynamic
- section: §16 Dynamic Defaults | lines: L1240–L1264 | type: PARAMETER | strength: MUST | tag: [DYN][DEFINED]
- wording: "EmergencyTolerance := 0.005 × (10000 / Leverage_effective) bps … Derivation: 0.5% of the initial-margin distance … Supersedes the 50 bps [TEMPORARY — CALIBRATION PENDING] default (D-16). Must be calibrated."
- inputs: Leverage_effective | outputs: EmergencyTolerance | preconditions: emergency eval | postconditions: dynamic tolerance | state_effects: tolerance
- formula: EmergencyTolerance = 0.005 × (10000 / Leverage_effective) bps | units: bps (e.g. 2→25, 3→16.7, 5→10)
- invariants: auto-tightens at higher leverage; supersedes 50 bps [TEMP] | failure_behavior: NONE | safety_impact: HIGH
- dynamic_note: must remain dynamic — never freeze to a constant (D-16); must be calibrated
- dependencies: STR-0219, STR-0276, STR-0183, STR-0337 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0339 — [DYN] CANONICAL ExposureTolerance := (0.001 × StepBps/10) × NotionalPerLevel/MarkPrice (D-16) — must remain dynamic
- section: §16 Dynamic Defaults | lines: L1266–L1294 | type: PARAMETER | strength: MUST | tag: [DYN][DEFINED]
- wording: "ExposureTolerance := (0.001 × StepBps / 10) × NotionalPerLevel / MarkPrice where NotionalPerLevel := MaxBasketNotional / GridLevels … Supersedes the (0.1 × level) [TEMPORARY — CALIBRATION PENDING] default (D-16). Must be calibrated."
- inputs: StepBps; MaxBasketNotional; GridLevels; MarkPrice | outputs: ExposureTolerance | preconditions: progression gate eval | postconditions: dynamic tolerance | state_effects: tolerance
- formula: ExposureTolerance = (0.001 × StepBps / 10) × (MaxBasketNotional/GridLevels) / MarkPrice | units: base-asset quantity (e.g. 0.00005 BTC at defaults)
- invariants: ExposureTolerance < MaxExposureImbalance < one level (consistency note); supersedes (0.1×level) [TEMP] | failure_behavior: NONE | safety_impact: CRITICAL
- dynamic_note: must remain dynamic — never freeze to a constant (D-16); must be calibrated
- dependencies: STR-0140, STR-0227, STR-0141, STR-0278, STR-0083, STR-0342 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0340 — [DYN] CANONICAL MaxExposureImbalance := (0.25 × 0.5/Leverage_effective) × NotionalPerLevel/MarkPrice (D-16) — must remain dynamic
- section: §16 Dynamic Defaults | lines: L1296–L1325 | type: PARAMETER | strength: MUST | tag: [DYN][DEFINED]
- wording: "MaxExposureImbalance := (0.25 × 0.5 / Leverage_effective) × NotionalPerLevel / MarkPrice … 0.5 / Leverage_effective = MaintenanceMarginFraction … Supersedes the (1.0 × level) [TEMPORARY — CALIBRATION PENDING] default (D-16). Must be calibrated."
- inputs: Leverage_effective; MaxBasketNotional; GridLevels; MarkPrice | outputs: MaxExposureImbalance | preconditions: acute-hedge eval | postconditions: dynamic bound | state_effects: risk bound
- formula: MaxExposureImbalance = (0.25 × 0.5 / Leverage_effective) × (MaxBasketNotional/GridLevels) / MarkPrice | units: base-asset quantity (e.g. 0.00208 BTC at 3×)
- invariants: auto-tightens at higher leverage; drives §11.2 acute branch; supersedes (1.0×level) [TEMP] | failure_behavior: breach → unconditional Hedge Recovery | safety_impact: CRITICAL
- dynamic_note: must remain dynamic — never freeze to a constant (D-16); must be calibrated
- dependencies: STR-0219, STR-0227, STR-0141, STR-0279, STR-0223, STR-0337, STR-0342 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0341 — [DYN] CANONICAL ReferencePriceToleranceBps := 0.33 × StepBps (D-17, DYNAMIC-CALIBRATABLE) — must remain dynamic
- section: §16 Dynamic Defaults | lines: L1327 | type: PARAMETER | strength: MUST | tag: [DYN][DEFINED]
- wording: "§5.4.1 ReferencePriceToleranceBps = 0.33 × StepBps — the reference-price tolerance at Cycle/Generation fire, tagged [DYNAMIC-CALIBRATABLE] (proposal-only per the §14 global rule)."
- inputs: StepBps | outputs: ReferencePriceToleranceBps | preconditions: Cycle/Generation fire | postconditions: dynamic tolerance | state_effects: reference gate
- formula: ReferencePriceToleranceBps = 0.33 × StepBps | units: bps
- invariants: coefficient strictly <1.0; gates capture upstream of §5.6 (which stays authoritative) | failure_behavior: BLOCKED above tolerance (§5.4.1) | safety_impact: HIGH
- dynamic_note: must remain dynamic — never freeze to a constant (D-17); proposal-only per §14 global rule
- dependencies: STR-0096, STR-0264, STR-0261 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0342 — Consistency note: mutual ordering ExposureTolerance < MaxExposureImbalance < NotionalPerLevel/MarkPrice; if it fails at any input set, reported — coefficients never adjusted silently
- section: §16 Dynamic Defaults | lines: L1329 | type: INVARIANT | strength: MUST | tag: [DYN][DEFINED]
- wording: "Mutual ordering (must hold at every input set): ExposureTolerance < MaxExposureImbalance < NotionalPerLevel / MarkPrice — guard < acute trigger < one full level … if it ever fails at a candidate input set, the failure is reported — coefficients are never adjusted silently."
- inputs: three dynamic defaults; input sets | outputs: ordering check | preconditions: any input set | postconditions: ordering holds or reported | state_effects: consistency
- formula: ExposureTolerance < MaxExposureImbalance < NotionalPerLevel/MarkPrice | units: base-asset quantity
- invariants: ordering must hold; failure reported, never silently patched | failure_behavior: report on failure | safety_impact: HIGH
- dynamic_note: must remain dynamic — never freeze to a constant (verified in CALIBRATION-REPORT.md per spec)
- dependencies: STR-0338, STR-0339, STR-0340, STR-0341 | impl: NOT_STARTED | verif: NOT_STARTED

### STR-0343 — Implementation MUST NOT invent a value for anything not in §14
- section: §16 Dynamic Defaults | lines: L1364 | type: GUARD | strength: MUST_NOT | tag: [UR][DEFINED]
- wording: "The implementation must not invent a value for anything not in §14"
- inputs: parameter set | outputs: no invented values | preconditions: NONE | postconditions: only §14 values used | state_effects: config governance
- formula: NONE | units: NONE | invariants: no invented values; fail-closed on missing required value | failure_behavior: fail-closed | safety_impact: CRITICAL
- dependencies: STR-0257 | impl: NOT_STARTED | verif: NOT_STARTED

---

## STEP 5 — Self-consistency checks (reported, not silently repaired)

- **Total requirements:** 343 (STR-0001 … STR-0343), contiguous, no gaps.
- **Duplicate requirement_id:** 0 (verified: 343 headers, 343 unique ids).
- **Dangling dependency references:** 0 — every `STR-xxxx` cited in a `dependencies:` field resolves to an existing header (verified after the forward-reference repair pass; 20 forward-references were corrected to final IDs).
- **Per-type counts (sum = 343):** GUARD 76 · INVARIANT 62 · PARAMETER 55 · FORMULA 33 · STATE_TRANSITION 28 · SCENARIO 21 · LIFECYCLE_STATE 17 · EVENT_SEMANTICS 11 · PRECEDENCE_RULE 10 · IDENTITY_RULE 10 · FAILURE_BEHAVIOR 10 · ECONOMIC_RULE 6 · PERSISTENCE_RULE 3 · RECOVERY_RULE 1.
- **Normative strength counts:** MUST 302 · MUST_NOT 36 · SHOULD 4 · MAY 1.
- **`[HC]` requirements:** 17 blocks, all carry `venue_evidence_status: UNVERIFIED` (Phase 2 will verify). List: STR-0132, STR-0133, STR-0134, STR-0135, STR-0136, STR-0137, STR-0138, STR-0175, STR-0176, STR-0177, STR-0194, STR-0200, STR-0224, STR-0228, STR-0254, STR-0337 — plus STR-0129 (`[SD][HC]`). (Count reflects blocks whose tag contains `[HC]`.)
- **`[DYN]` requirements retain their formula (never a constant):** the four canonical dynamic-default PARAMETERS keep their full formulas — STR-0338 (EmergencyTolerance), STR-0339 (ExposureTolerance), STR-0340 (MaxExposureImbalance), STR-0341 (ReferencePriceToleranceBps) — and their §14-register (STR-0264, STR-0276, STR-0278, STR-0279) and behavioral (STR-0083, STR-0096, STR-0100) mirrors. Every `[DYN]` block carries a `dynamic_note: must remain dynamic — never freeze to a constant`. No dynamic default was reduced to a constant.
- **`fail-closed` coverage:** `Strategy.md` contains 12 occurrences of "fail-closed" (L16, 28, 31, 63, 368, 446, 506, 719, 734, 1339, 1361 — L1339/L1361/L28 are change-log/closed-ledger, L63 is the tag legend, all non-normative). Every **normative** fail-closed phrase maps to a requirement whose `failure_behavior` is fail-closed/BLOCKED: §4.1 D-04 → STR-0035; §5.2 step 4 (L368) → STR-0077; §5.4.1 (L446, L31) → STR-0098; §5.6 (L506) → STR-0108; §8 WEBHOOK (L719) → STR-0166; §8 arm-invariant 5 (L734) → STR-0172. Additionally, 52 requirement blocks carry a fail-closed/BLOCKED/RECONCILIATION_REQUIRED/LEVEL_SKIPPED/INELIGIBLE `failure_behavior` value, so fail-closed semantics are represented well beyond the 10 dedicated FAILURE_BEHAVIOR-typed entries.
- **Ambiguous normative_strength:** none left implicit. See OPEN / interpretation notes below for every strength that was inferred from non-RFC-2119 wording ("prefer", "preferable", "may").

### OPEN items and interpretation notes (surfaced, NOT silently resolved)

- **OPEN-01 (non-blocking interpretation tension) — CycleReferenceDerivation default vs. "MUST be explicit":** §5.4 gives `TERMINAL_EXECUTION` as the default of four options (STR-0091, STR-0268) yet also states "The selected policy is configuration and MUST be explicit" (STR-0094). Both are captured verbatim; the tension (is a default permitted, or must the operator set it explicitly?) is **not resolved here**. It aligns with §16/STR-0343 ("must not invent a value"); a later phase/Owner should decide whether the default is usable or explicit config is mandatory (fail-closed). No guess made.
- **Strength inferred from wording (not a semantic guess):** SHOULD assigned where `Strategy.md` says "prefer"/"preferable" — STR-0195 ("prefer MAKER"), STR-0207 ("prefer a maker-side correction"), STR-0311 ("preferable"), STR-0312 ("preferable"). MAY assigned to STR-0164 (AUTO "arms automatically" — permissive mode). All other rules are MUST/MUST_NOT. These are the only 5 non-MUST strengths; each is a direct reading of the source verb, recorded here for transparency.
- **Taxonomy note (not a semantic issue):** STR-0093 (§5.4 tick-rounding at conversion, full-precision reference) is a precision rule; since `PRECISION_RULE` is not in the allowed `requirement_type` set, it is typed `GUARD` with the precision nature noted in its `invariants` field. Same family as §6.3 (STR-0135–STR-0138).
- **Blocking semantic ambiguities:** **none.** Per `Strategy.md` §16 closed ledger, all owner decisions D-01…D-17 are resolved and no `[OQ]` remains open; the four calibration-pending values are specified dynamic mechanisms (not open questions) and are preserved as such.

### Notes on consolidation (where multiple source clauses share one ID, by the atomicity rule)

- STR-0175 = §8 gates 3 & 4 (order-size-min + margin+buffer — two per-order feasibility prechecks).
- STR-0176 = §8 gates 5 & 6 (exposure caps + open-order headroom — two capacity prechecks).
- STR-0177 = §8 gates 7 & 8 ("Price/size normalized" — a single atomic normalization rule).
These are the only intra-section gate consolidations; every other §8 gate and rule has its own ID. Dynamic-default parameters intentionally appear in both their behavioral section, their §14 register row, and their §16 canonical entry (per Phase-1 special extraction duties c & d), cross-linked via `dependencies`/`dynamic_note`.

*End of STRATEGY_CONTRACT.md (Phase 1). Authority remains `Strategy.md`; this contract is derived and non-authoritative.*
