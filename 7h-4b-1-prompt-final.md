# Phase 7h-4b-1 — FINAL PROMPT (§10 Economics + §5.2 Step-8 Ladder Issuance)

**Base:** `origin/main @ 0d6748f` (`0d6748fb9899addbf32c10a4bc496ad3cbeddaaf`, 7h-4a merged).
**Branch:** create `claude/7h-4b-1-economics` on `0d6748f`. Commit on that branch ONLY.
**Scope:** §10 economics pure functions + §5.2 step-8 one-direction ladder issuance (pure).
**Later:** 7h-4b-2 = P6-real + `run_pass` 3-tuple + ST-05↔ST-04 coupling + PassReport extension
(separate prompt, separate base — NOT this run). This phase touches NO pass-engine code,
NO State slots, NO existing tests.

**INTEGRITY CHECK (do this FIRST, before any other work):** confirm this file contains Parts
A–H plus Appendix P1–P12 and ends with the exact line
`END OF 7h-4b-1 PROMPT — REPORT SHA + TRUE COUNTS + COINED/SEAM INVENTORIES`.
If any Part/Appendix is missing or the closing line differs → **STOP** (report the missing
piece; do not execute).

**Execution rule (standing):** every repo-answerable question is PINNED below with a citation.
Zero pre-listed STOPs (Part F). Only the global abort rule stops the run. This Part D is
authoritative for 7h-4b-1 (self-contained restatement — do NOT go read prior phase prompt files).

---

## Part A — Scope and non-goals

### A1. Build

- **B1 — §10 economics (pure functions, bps in/bps out unless noted).**
  - `compute_gross_grid_edge(*, step_bps)` → `step_bps` (DECISION-017; STR-0349).
  - `compute_net_expected_edge(*, gross_edge_bps, fee_bps, slippage_bps, funding_bps,
    other_bps)` → 5-term subtraction (STR-0193).
  - `classify_path_economics(*, net_expected_edge_bps, floor_bps, is_emergency_or_hedge)`
    → `PathEconomicsVerdict` 3-way (STR-0195/0196/0197).
  - `check_arming_validity(*, gge_bps, fee_maker_bps, funding_est_bps, floor_bps)` → `bool`
    (STR-0350; DECISION-017).
- **B2 — §5.2 step-8 one-direction ladder issuance (pure).**
  `issue_fresh_ladder(...)` → `tuple[LevelState, ...]` for ONE direction. Gated on the §10
  bool param; composes 7g-1 `compute_ladder_geometry` + `is_protection_locked_initial` +
  `LevelState` construction. The caller (7h-4b-2 P6) composes BU + SL.

### A2. Non-goals (seams — each with its home)

- **P6-real / `run_pass` 3-tuple / emission-vs-append:** → **7h-4b-2.** This phase does NOT
  touch `pass_engine.py` (P6 stays `STUBBED`).
- **ST-05↔ST-04 coupling:** → **7h-4b-2.**
- **PassReport extension / `SubDecisionRecord`:** → **7h-4b-2.**
- **The §8 half of step-8's "all strategy gates (§8, §10)":** satisfied COMPOSITIONALLY by
  7h-4b-2's P6 (per-row `evaluate_arm_gates` on issued rows). B2 takes only the §10 bool.
  This split is FORCED: §8 gates need runtime book data no pure function can read.
  → **7h-4b-2.**
- **BU+SL composition + atomicity:** B2 is one direction per call; two-call composition and
  the fail-closed signal on partial issuance are P6's. → **7h-4b-2.**
- **§5.2 transition guards** (exposure-tolerance, FREEZE/ERROR/RECOVERY, step-4 non-overlap):
  evaluated by the transition driver (P5 markers + P6 composition), not by B2. → **7h-4b-2.**
- **Fee/funding VALUES** (userFees live reads, Tier-0 basis): arrive as parameters
  (STR-0194 NEVER-hardcoded). → **runtime/post-7h.**
- **`check_arming_validity` wiring:** its verdict consumer is config resolution (ST-11,
  still a placeholder; STR-0350 "rejected at calibration/config resolution"). 7h-4b-1 builds
  the pure check only. → **config-domain/post-7h.**
- **α·S/2 adverse-selection form:** PROPOSAL_ONLY (STR-0351 MUST_NOT) — do NOT implement.
- **Tick normalization** (§6.3 order-build time): B2 rows carry full-precision geometry prices;
  normalization happens downstream (7g-1 NO-ROUNDING note). → **existing seam, untouched.**
- **ST-18, venue adapter, signing/UI:** none. **`prompt.md`:** conflicted (`<<<<<<< HEAD` L1,
  re-verified at `0d6748f`), non-authoritative, do not read.

---

## Part B — Behavior specification

### B1 — §10 economics (`economics.py`)

Stdlib only (`decimal`, `enum`). All money/edge quantities are `Decimal` BIPS. Literals as
`Decimal("...")`, never float. `isinstance(x, Decimal)` guards; non-Decimal → `ValueError`.
Ambient default context; NEVER mutate (Part C2). Every literal cited (D3).

**B1.1 — `compute_gross_grid_edge(*, step_bps: Decimal) -> Decimal`.** Returns `step_bps`.
Validation: `step_bps > 0`. This is the DECISION-017 closed form (constant, deterministic);
the α·S/2 form MUST NOT be used (STR-0351). Cite: DECISION-017; STR-0349.

**B1.2 — `compute_net_expected_edge(*, gross_edge_bps: Decimal, fee_bps: Decimal,
slippage_bps: Decimal, funding_bps: Decimal, other_bps: Decimal) -> Decimal`.**
Returns `gross - fee - slippage - funding - other` (exact; all five terms are Strategy
vocabulary — `OtherExecutionCosts(path)` is §10/STR-0193's fifth term, not an invention).
Validation: all Decimal; `gross_edge_bps > 0` (GGE is StepBps>0 by construction — anything
else is caller bug); fee/slippage/funding/other ANY sign (rebates, negative funding, price
improvement exist). Cite: §10; STR-0193 (units: bps).

**B1.3 — `classify_path_economics(*, net_expected_edge_bps: Decimal, floor_bps: Decimal,
is_emergency_or_hedge: bool) -> PathEconomicsVerdict`.**
`PathEconomicsVerdict` (StrEnum, `_NameValueStrEnum` leaf pattern) — all COINED-but-anchored:
`BELOW_FLOOR` (← STR-0197 "→ do not arm"), `MAKER_PREFERRED` (← STR-0195 "prefer MAKER" —
SHOULD, hence *preferred*), `TAKER_REQUIRED` (← STR-0196 "→ TAKER" — MUST, hence *required*).
Order (total; the enum is COMPLETE — 0196 forbids normal-path taker, so no fourth member):
- `net_expected_edge_bps <= floor_bps` → `BELOW_FLOOR` (boundary `==` is BELOW — STR-0197's
  `≤`, "either path" — emergency too; failure behavior = §9.3 Skip).
- elif `is_emergency_or_hedge is True` → `TAKER_REQUIRED`.
- else → `MAKER_PREFERRED`.
Validation: Decimals; `floor_bps >= 0` (zero floor allowed; negative is nonsense);
`type(is_emergency_or_hedge) is bool` (truthy non-bools raise — D2). The floor arrives as a
PARAM (STR-0273 CALIBRATABLE — never hardcoded, never computed as StepBps/10 here).
Cite: §10 path selection + floor; STR-0195/0196/0197; STR-0273.

**B1.4 — `check_arming_validity(*, gge_bps: Decimal, fee_maker_bps: Decimal,
funding_est_bps: Decimal, floor_bps: Decimal) -> bool`.**
Returns `gge_bps - 2 * fee_maker_bps - funding_est_bps > floor_bps` (STRICT `>` — boundary
`==` is INVALID). "At Tier-0 fees" is the fee BASIS (comment; values arrive as params per
STR-0194). Validation: all Decimal; `gge_bps > 0`; `floor_bps >= 0`; fee/funding any sign.
Cite: DECISION-017; STR-0350 (worked vector `10 − 2·1.5 − 0 = 7 > 1 ✓` — E2 pins it).

### B2 — Step-8 issuance (`ladder_issuance.py`)

Leaf module: stdlib (`decimal`) + same-package `geometry.compute_ladder_geometry`,
`protection_lock.is_protection_locked_initial`, `level_state.LevelState` ONLY.

**`issue_fresh_ladder(*, reference_price: Decimal, direction: str, grid_levels: int,
step_bps: Decimal, first_level_distance_bps: Decimal, is_dominant: bool,
gen2_distance_multiplier: Decimal, weak_side_first_level_multiplier: Decimal,
size_notional_usd: Decimal, edge_clears_floor: bool, current_generation_id: int,
current_cycle_id: int) -> tuple[LevelState, ...]`.**
(12 params — `is_successor` is DERIVED, see below — not taken.)

- **Derive (R2):** `is_successor := current_generation_id > 0` (per-Generation constant,
  "never per-Cycle" — geometry docstring R2). Derived once, passed to BOTH geometry and the
  lock fn. A param here would invite R2 violations.
- **Validate FIRST (fail-closed — garbage raises even when blocked):**
  `type(edge_clears_floor) is bool`, `type(is_dominant) is bool` (both coerce silently in
  boolean context otherwise); `type(grid_levels) is int`, `type(current_generation_id) is
  int`, `type(current_cycle_id) is int` (bool-hole: `True` passes `1..12`/`0..99` range
  checks — 7h-3 `track_remainder` precedent); `size_notional_usd` Decimal `> 0`. Numerics
  (`reference_price`, `step_bps`, `first_level_distance_bps`, multipliers) and `direction`
  are validated by `compute_ladder_geometry` itself (do NOT duplicate); gen/cyc/grid RANGES
  by geometry (`1..12`) and the `LevelState` ctor (`0..99`) — B2 adds only the exact-type
  checks those layers lack. Anything invalid → `ValueError`.
- **Gate:** if `edge_clears_floor is False` → return `()` (blocked; no rows). This is the
  §10 half of step-8's gates (the caller computes the bool from B1.3 — `verdict !=
  BELOW_FLOOR`); the §8 half is P6-compositional (Part A2).
- **Issue:** `prices = compute_ladder_geometry(...)` (9 geometry params); for each price in
  traversal order with `level_id = 1..N`: `LevelState(current_generation_id,
  current_cycle_id, direction, level_id, price, is_protection_locked_initial(
  is_successor=derived, is_dominant=is_dominant, level_id=level_id),
  size_notional_usd=size_notional_usd)`; `filled_quantity=None`, `lifecycle=None`
  (pre-observation rows — the R10c coherence check is SKIPPED for `None` by ctor design).
- `current_generation_id`/`current_cycle_id` are the ids the ladder is issued FOR
  (post-transition G-(C+1); step 6 creates it, step 8 fills it) — pin in a comment.
- `grid_levels == 0` → `ValueError` (inherited from geometry's `1..12` — there is NO
  vacuous-empty path; the ONLY empty-tuple path is `edge_clears_floor is False`).
Cite: §5.2 step 8 ("Issue a fresh ladder for BOTH groups …, subject to all strategy gates
(§8, §10)"); STR-0080; §7.1 R1/R2 (chained prices; successor rule); STR-0146 (L1 lock).

---

## Part C — Code placement and conventions

### C1 — Module names

- `src/hypergrid/core/transitions/economics.py` (B1 + `PathEconomicsVerdict`).
- `src/hypergrid/core/transitions/ladder_issuance.py` (B2).
- `src/hypergrid/core/transitions/__init__.py` — re-exports + `__all__` ONLY (ruff-isort
  order): `compute_gross_grid_edge`, `compute_net_expected_edge`, `classify_path_economics`,
  `check_arming_validity`, `PathEconomicsVerdict`, `issue_fresh_ladder`.
- **New tests:** `tests/test_economics.py`, `tests/test_ladder_issuance.py`. NO other test
  file is created or touched.
- Research docs: NO `STATE_OWNERSHIP.md` change (no ST slot is typed or reshaped — rows go
  into the EXISTING ST-04 slot at caller side in 7h-4b-2).

### C2 — Purity, layering, time

`core/` imports: stdlib (`decimal`, `enum`) + same-package leaves ONLY (enforced by
`tests/test_core_no_forbidden_imports.py`: bans `logging`, `time`, `datetime`, `random`,
`os`, `pydantic`, `httpx`, `websockets`, `eth_account`, `numpy`, `pandas`, `requests`,
`aiohttp`, `asyncio`). No `float` (literal, call, annotation, subscript). No `hashlib`
outside `envelope.py`. No decimal-context mutation. New modules MUST NOT import `core.state`,
`core.pass_engine`, `core.fold`, or `config/*`. `ladder_issuance.py` MUST NOT import
`core.state` (rows are RETURNED, not stored — storing is the caller's job).

### C3 — Additive edits + UNTOUCHED

- `transitions/__init__.py`: re-exports + `__all__` only.
- **UNTOUCHED (empty diff required):** every other file under `src/` (including `state.py`,
  `pass_engine.py`, `geometry.py`, `protection_lock.py`, `level_state.py`, `reason_codes.py`,
  all `core/events/*`, all of `config/`), every existing file under `tests/`,
  `Strategy.md`, `research/strategy/STRATEGY_CONTRACT.md`, `research/decisions/*`,
  `research/architecture/STATE_OWNERSHIP.md`, `prompt.md`, `pyproject.toml`.

### C4 — Enum and literal rules

- `_NameValueStrEnum` (auto() == name): module-local copy in `economics.py` (leaf pattern).
- `PathEconomicsVerdict`: all 3 COINED-but-anchored (anchors pinned in Part B1.3).
- Every numeric literal carries an inline cite (D3). No fee constants anywhere (STR-0194
  NEVER-hardcoded — not even Tier-0 base values in comments as defaults; cite-only).

---

## Part D — Standing engineering rules (authoritative for 7h-4b-1)

- **D1 Determinism & purity:** `core/` is pure, clock-free, I/O-free. Venue quantities ARRIVE
  as parameters (validated, never generated). No banned imports, no float, no context
  mutation (Part C2).
- **D2 Fail-closed:** invalid input → `ValueError` (never a silent default, never a
  None-coercion). Unknown tokens → `ValueError`. Exact `int` required ⟹ reject `bool`
  (`type(x) is int`); exact `bool` required ⟹ reject non-bool (`type(x) is bool`).
- **D3 Cite-or-coin:** every bound, comparator, threshold literal, and vocabulary item carries
  a Strategy `§`/STR/DECISION citation or an explicit `COINED ← anchor` comment. No bare magic.
- **D4 Additive-only edits:** `__init__.py` gains re-exports ONLY (Part C1/C3). Never reshape
  an existing function or test; never rename.
- **D5 No new STUBs:** every function built is real, total on validated inputs, and E-tested.
  No `TODO`/`FIXME`/`NotImplementedError`/placebo branches.
- **D6 State untouched:** no slot is added, retyped, or reshaped; the 23 `st*` field count is
  preserved trivially (no `state.py` edit at all).
- **D7 Test discipline:** new behavior in NEW test files only; existing tests untouched (none
  pre-authorized — E1); E-matrices pin every boundary; no `skip`/`xfail`; report TRUE counts.
- **D8 Reconciliation-allowed:** when this prompt's own signature sketch is incomplete relative
  to its prose + test matrix, you MAY accept the minimal additive input/output field to satisfy
  prose + tests, provided ALL hold: (a) flagged in the report as `reconciliation (not a STOP)`;
  (b) documented in the module; (c) validated; (d) Strategy-§/STR/DECISION-cited; (e) strictly
  minimal — no behavior beyond satisfying this prompt's own prose + matrix; (f) touches no
  frozen or Part-C3-untouched file; (g) adds no scope (no new module/test beyond the pinned
  set to support it); (h) pre-flight's aim remains zero such cases. Any reconciliation failing
  (e)–(h) is a **global STOP**.

---

## Part E — Tests

### E1 — Suite, types, hygiene

- Full suite green: 478 at base + all new tests (report the TRUE total).
- NO existing-test edits (none pre-authorized).
- `mypy --strict`: the phase must introduce ZERO new errors. Method (version-robust): run
  `mypy --strict src tests` on the BASE tree and on the phase tree with the SAME tool; the
  error-set delta must be EMPTY (pre-existing baseline errors, if any under your mypy version,
  are out of scope — do not fix, do not touch those files).
- `ruff check`: all passed. `ruff format --check`: every NEW/EDITED file clean (pre-existing
  unformatted files are out of scope — do not touch).
- No new dependencies. `git status` shows ONLY the pinned file set (Part G).

### E2 — Behavior matrices (new test files)

- **`test_economics.py`:** B1.1 passthrough (`10 → 10`; rejects `0`/negative/non-Decimal —
  the exact-passthrough behaviorally pins "no α·S/2"); B1.2 exact
  (`10 − 1.5 − 0.5 − 0.25 − 0.25 = 7.5`; rejects non-Decimal, `gross ≤ 0`); B1.3
  (`(5,1,False) → MAKER_PREFERRED`; `(5,1,True) → TAKER_REQUIRED`; `(1,1,False) → BELOW_FLOOR`
  boundary; `(0.5,1,True) → BELOW_FLOOR` emergency-but-uneconomic; negative net → BELOW;
  rejects `floor < 0`, non-Decimal, non-bool flag); B1.4 STR-0350 vector
  (`(10,1.5,0,1) → True`) + boundary (`(4,1.5,0,1) → False`, `4−3=1 ≯ 1`) + rejects
  (`gge ≤ 0`, `floor < 0`, non-Decimal).
- **`test_ladder_issuance.py`:** blocked (`edge False` + otherwise-valid → `()`); validates
  first (garbage + `False` STILL raises — one case each for bad flag type, bad direction,
  `grid_levels 0`); issued G0 (N rows; `level_id 1..N`; prices `== compute_ladder_geometry`
  same-inputs output; R1 exact vector `ref 100000, step 10, first 20 → p1 == 100200,
  p2 == 100300.2`; all unlocked; size set; `lifecycle/filled None`); issued G1+ weak
  (`gen 1, non-dominant` → L1 locked, rest unlocked — proves `is_successor` derivation;
  dominant G1+ → all unlocked); BU ascending / SL descending monotonicity; int-exactness
  (`True` as `grid_levels`/gen/cyc raises); `grid_levels 13` raises.

### E3 — Pipeline + persistence

- End-to-end (no State involved — pure composition): `compute_gross_grid_edge(10)` →
  `compute_net_expected_edge(...)` → `classify_path_economics(net, floor=1, False)` →
  `edge_clears_floor := (verdict != BELOW_FLOOR)` → `issue_fresh_ladder(...)` → N rows →
  every row's `to_canonical_obj()` passes `canonical_dumps`.
- Unchanged-surface check: empty diffs for `state.py`, `pass_engine.py`, `geometry.py`,
  `protection_lock.py`, `level_state.py`, `reason_codes.py`, `core/events/*`, `config/*`,
  all pre-existing tests.

---

## Part F — STOPs

**Zero pre-listed.** Pre-flight resolved every repo-answerable gap against `0d6748f` (R2
derivation, lifecycle-None per the R10c ctor comment, `1..12` inheritance, `==`/`>` boundary
pins from STR-0197/STR-0350, the §8-half compositional split).
**Global abort rule:** any E1 breakage, any need to edit a frozen/Part-C3-untouched file or
any existing test, any reconciliation failing D8 (e)–(h), or any genuinely unresolvable
question → STOP with the failing artifact + citations + the exact function-level question.

---

## Part G — Deliverables

1. `src/hypergrid/core/transitions/economics.py`,
   `src/hypergrid/core/transitions/ladder_issuance.py`.
2. Additive edit: `transitions/__init__.py` (re-exports ONLY — nothing else in the repo).
3. Tests: `tests/test_economics.py`, `tests/test_ladder_issuance.py`.
4. Report: base SHA + branch SHA; TRUE test counts (base/new/total); mypy BASE-vs-phase
   error-set evidence; ruff evidence; coined-vocab inventory (each with anchor); seam
   confirmations (each A2 item + where it went); pre-authorized edits (none — confirm);
   reconciliation flags (if any, per D8); the E3 e2e result.

## Part H — Acceptance checklist

- [ ] E1 all green (478 + new, TRUE total reported).
- [ ] E2/E3 matrices pass per the pinned vectors/tables.
- [ ] D3 holds (every literal/vocab cited or coined-anchored; no fee constants anywhere).
- [ ] D8 obeyed if used (a)–(h), else confirm "no reconciliation".
- [ ] Part C3 untouched list verified empty-diff (report the command + output).
- [ ] Report carries SHA + true counts (base/new/total); mypy BASE-vs-phase
   error-set evidence; ruff evidence; coined-vocab inventory (each with anchor); seam
   confirmations (each A2 item + where it went); pre-authorized edits (none — confirm);
   reconciliation flags (if any, per D8); the E3 e2e result.

## Part H — Acceptance checklist

- [ ] E1 all green (478 + new, TRUE total reported).
- [ ] E2/E3 matrices pass per the pinned vectors/tables.
- [ ] D3 holds (every literal/vocab cited or coined-anchored; no fee constants anywhere).
- [ ] D8 obeyed if used (a)–(h), else confirm "no reconciliation".
- [ ] Part C3 untouched list verified empty-diff (report the command + output).
- [ ] Report carries SHA + true counts + coined/seam inventories.

---

## Appendix — Pinned readings

- **P1** §10 body (L808–L835): 5-term formula (Fee live `[HC]`; Slippage = Fillability
  Analyzer §8; Funding(holding_period); OtherExecutionCosts); path selection (Normal→MAKER
  Alo / Emergency-Hedge→TAKER Ioc); floor default StepBps/10; `≤ floor (either path) →
  do not arm / do not attempt (§9.3 Skip applies)`; fillable-but-uneconomic skipped.
- **P2** STR-0193 (formula, units bps) / STR-0194 (fees live, NEVER hardcoded) / STR-0195
  (SHOULD prefer maker) / STR-0196 (MUST taker-only-emergency; deps STR-0185/STR-0206) /
  STR-0197 (`≤ floor → do not arm`, both paths; failure = §9.3 Skip) / STR-0198
  (LEVEL_SKIPPED on uneconomic; deps STR-0190).
- **P3** DECISION-017 (Option A Owner 2026-09-22: `GGE := StepBps`; validity `GGE −
  2·fee_maker − funding_est > floor` at Tier-0; α·S/2 future-proposal-only) + STR-0349
  (closed form, bps) / STR-0350 (strict `>`; config-resolution consumer; worked `7 > 1 ✓`)
  / STR-0351 (α·S/2 MUST_NOT) / STR-0273 (floor StepBps/10 CALIBRATABLE → param, never
  computed here).
- **P4** §5.2 step 8 VERBATIM: "Issue a fresh ladder for BOTH groups relative to the new
  reference, subject to all strategy gates (§8, §10)" + STR-0080. One direction per B2 call
  (caller composes); §8-half compositional (Part A2 — forced by runtime-data need).
- **P5** 7g-1 geometry: `compute_ladder_geometry` 9-param keyword-only signature; chained
  R1 (`p1 = 100200, p2 = 100300.2` EXACT); R2 successor = per-Generation (`gen > 0`),
  "never per-Cycle"; `grid_levels ∈ 1..12` (ValueError outside); prices-only, full
  precision, NO rounding, NO sizing. `is_protection_locked_initial(*, is_successor,
  is_dominant, level_id)` (locked ⟺ succ ∧ ¬dom ∧ L1; STR-0146).
- **P6** `LevelState` ctor: 6 required positional + `size_notional_usd`/`filled_quantity`/
  `lifecycle` None-defaults; ranges `0..99`/`1..12`; R10c coherence SKIPPED when
  `lifecycle is None` (pre-observation rows anticipated by design).
- **P7** Precedents: 7h-3 `track_remainder` exact-int guards (bool-hole); arm/order/hedge/
  emergency/execution_cancel/risk_bounds `_NameValueStrEnum` leaf copies; E1 mypy
  base-vs-phase delta method; `STATE_OWNERSHIP.md` untouched (no ST change this phase).
- **P8** Untouched enforcement: Part C3 list (incl. `state.py`, all 7g-1 modules, all
  existing tests). E3 re-verifies.
- **P9** Carried rulings: 7h-3 `tolerance_leverage_in` reconciliation (D8's live precedent);
  7h-4a `BoundLayerState`-as-alert-record; LEVEL_SKIPPED = §9.3 terminal (B1.3's
  failure behavior lands there via caller/P6 — NOT built here).
- **P10** Verified counts: 382 STR rows, 23 DECISIONs (files untouched since verification —
  carried). No OWNER_GATE count is asserted (unverified — do not assert one).
- **P11** `prompt.md` conflicted (`<<<<<<< HEAD` L1 @0d6748f) — non-authoritative, do not read.
  Strategy SHA (drift check): `085044e72efa75e7` (first 16 hex of sha256 @0d6748f).
- **P12** If this prompt's sketch and its prose/matrix ever disagree, prose + matrix win;
  bridge the gap ONLY via D8 (flagged, minimal, cited) — never by silent reinterpretation.

END OF 7h-4b-1 PROMPT — REPORT SHA + TRUE COUNTS + COINED/SEAM INVENTORIES