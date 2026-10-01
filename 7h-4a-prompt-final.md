# Phase 7h-4a — FINAL PROMPT (§12.1 Bounds + Three-Layer Breach + ST-17/20/21/22)

**Base:** `origin/main @ 7489848` (`7489848414dac3df5d63f987fcd59120ce031aac`, 7h-3 merged).
**Branch:** create `claude/7h-4a-risk-bounds` on `7489848`. Commit on that branch ONLY.
**Scope:** §12.1 range-survivability bounds + three-layer breach ladder + ST-17/ST-20/ST-21/ST-22
typing + State slots. **Later:** 7h-4b = §10 economics + §5.2 step-8 issuance + P6-real +
ST-05↔ST-04 coupling (separate prompt, separate base — NOT this run).

**INTEGRITY CHECK (do this FIRST, before any other work):** confirm this file contains Parts
A–H plus Appendix P1–P12 and ends with the exact line
`END OF 7h-4a PROMPT — REPORT SHA + TRUE COUNTS + COINED/SEAM INVENTORIES`.
If any Part/Appendix is missing or the closing line differs → **STOP** (report the missing
piece; do not execute).

**Execution rule (standing):** every repo-answerable question is PINNED below with a citation.
Zero pre-listed STOPs (Part F). Only the global abort rule stops the run. This Part D is
authoritative for 7h-4a (self-contained restatement — do NOT go read prior phase prompt files).

---

## Part A — Scope and non-goals

### A1. Build

- **B1 — §12.1 bound-value functions (pure).** Five functions, one per monitored bound. Inputs
  are parameters (no ST reads inside the functions); the caller composes.
  - `compute_max_range_induced_dd_pct()` → `100` (FIXED; STR-0217/STR-0280).
  - `compute_max_execution_cost_pnl_regime(basket_net_pnl, max_basket_notional)` → two-regime
    (STR-0218/STR-0281).
  - `compute_max_failed_level_rate()` → `5` (FIXED; STR-0220/STR-0282) + the PINNED failed-level
    counting rule (comment-level; the runtime computes the rate).
  - `compute_max_hedge_cost(max_basket_notional)` → 2% of MBN (STR-0221/STR-0283).
  - `compute_max_exposure_imbalance_qty(leverage_effective, notional_per_level_usd, mark_price)`
    → DYNAMIC formula (STR-0223/STR-0279/STR-0340; §16 D-16). ADDED by pre-flight: the draft
    omitted it, but it is a continuously-monitored §12.1 runtime bound with a pinned formula,
    and its consumer slot (`P1ExposureMarkers.max_exposure_imbalance`, 7g-3b) already exists.
- **B2 — Three-layer breach ladder (per §12.1 + STR-0216).** Pure
  `apply_breach_response(current_value, bound_value, prior_layer)` → `(next_layer, code|None)`
  over the 8-cell table (Part B). Breach inputs are per-bound current-vs-bound comparisons;
  the caller drives evaluations. No side effects; the runtime maps layers to actions.
- **B3 — ST-17/ST-20/ST-21/ST-22 rows (frozen dataclasses + validators + canonical).**
  - ST-17 `AccountEquityState`: `capital_base_usd`, `source`, `read_at_ts`.
  - ST-20 `RiskBoundTrackerState`: 4 lifetime-to-date tracked quantities + `bound_layers`
    (per-bound ladder states as `BoundLayerState` rows).
  - ST-21 `BasketNetPnLState`: `realized_usd`, `unrealized_usd`, `fees_usd`, `funding_usd`,
    `net_usd` + the STR-0234 invariant.
  - ST-22 `FreezeErrorRecoveryOverlayState`: `operational_state` (REUSE 7h-2's enum),
    `since_ts`, `last_reason_code`.
- **B4 — State slots wiring.** RETYPE the 4 placeholders IN PLACE (exact names pinned in Part B;
  no renames, no new fields, field count stays 23); extend `_TYPED_ST_FIELD_NAMES`; add 4
  serialization blocks; refresh 2 comments (exact replacement text pinned).

### A2. Non-goals (seams — each with its home)

- **§10 economics:** no fee math, no Cost Analyzer, no floor. → **7h-4b.**
- **§5.2 step-8:** ladder issuance untouched. → **7h-4b.**
- **P6:** stays `STUBBED`. This phase does NOT touch `pass_engine.py`. → **7h-4b.**
- **ST-05↔ST-04 coupling:** not designed. → **7h-4b.**
- **MaxBasketNotional FORMULA (STR-0284):** NOT built. MBN arrives as a parameter everywhere.
  The formula is DERIVED-computed-once-then-binding with operator confirmation (§12.1 + §14
  global rule) — a startup/operator-path concern. → **post-7h.**
- **Failed-rate COUNTING:** the counting rule is PINNED (failed := ST-04 `LEVEL_SKIPPED`; window
  := ALL ACTIVE-basket levels; STR-0220 + STR-0190), but the rate itself is computed by the
  caller/runtime from pipeline rows. → **runtime/post-7h.**
- **Sustained-breach → Market Selection re-evaluation** (STR-0220): consequence beyond the
  ladder. → **post-7h.**
- **Soft-action CONTENT** (which intervention: Hedge Recovery vs order-cancellation vs arming
  suspension): runtime policy. 7h-4a provides the LAYER + code; the runtime chooses the action.
  → **runtime/post-7h.**
- **OPERATOR_DECISION mechanics** (how a human is reached/told): operator-path. → **post-7h.**
- **Alert event-log wiring:** the persisted alert record IS `BoundLayerState`
  (`bound_id` = identity, `updated_at_ts` = timestamp, carried on ST-20). Any additional alert
  EVENT in the log is runtime-side. → **runtime/post-7h.**
- **ST-22 writers** (P1/CAP-0023 per the ST-22 cell's trigger): 7h-4a types the row only; no
  pass writes it. → **post-7h.**
- **STR-0342 consistency ordering** (ExposureTolerance < MaxExposureImbalance < level): needs
  all three tolerance formulas + a reporter; 7h-4a builds ONE. → **later (calibration-time).**
- **ST-18/ST-19/ST-23 shapes:** untouched (ST-19/ST-23 already typed; ST-18 stays placeholder).
- **`prompt.md`:** conflicted (`<<<<<<< HEAD` L1, re-verified at `7489848`), non-authoritative,
  do not read.
- **Venue adapter / signing / UI:** none.

---

## Part B — Behavior specification

### B1 — Bound-value functions (`risk_bounds.py`)

All Decimal-only (literals as `Decimal("...")`, never float). `isinstance(x, Decimal)` guards;
non-Decimal → `ValueError`. Ambient default context; NEVER mutate (`getcontext()`/`setcontext()`
writes forbidden — Part C2). Every literal carries its cite (D3).

**B1.1 — `compute_max_range_induced_dd_pct() -> Decimal`.** Returns `Decimal("100")`.
FIXED, % of Basket equity. Note (comment): a bound on basket-equity consumption — reached only
at total basket loss (§12.1). Cite: §12.1; STR-0217; STR-0280.

**B1.2 — `compute_max_execution_cost_pnl_regime(*, basket_net_pnl: Decimal,
max_basket_notional: Decimal) -> Decimal`.**
- `basket_net_pnl > 0` → `Decimal("0.30") * basket_net_pnl` (30%; cite STR-0281).
- `basket_net_pnl <= 0` → `max_basket_notional * Decimal("100") / Decimal("10000")`
  (100 bps; cite STR-0281). Boundary `== 0` takes the MBN regime (the Strategy's `≤ 0`).
Validation: `max_basket_notional > 0` (else `ValueError`); `basket_net_pnl` any Decimal.
Cite: §12.1 (two-regime form); STR-0218; STR-0281.

**B1.3 — `compute_max_failed_level_rate() -> Decimal`.** Returns `Decimal("5")`.
FIXED, % of Levels. PINNED counting rule (module comment + `RiskBoundTrackerState` field
comment; the runtime implements it): a FAILED level := an ST-04 row at `LEVEL_SKIPPED`
(the §9.3 per-level terminal — covers BOTH skip paths, since the ST-05 leg differs by path
and cannot be the counter); window := ALL Levels of the ACTIVE Basket (not rolling).
Cite: §12.1; STR-0220 (formula `SKIPPED/total ≤ 5%`); STR-0190 (§9.3); STR-0282.

**B1.4 — `compute_max_hedge_cost(*, max_basket_notional: Decimal) -> Decimal`.**
Returns `max_basket_notional * Decimal("2") / Decimal("100")` (2%; cite STR-0283).
Validation: `max_basket_notional > 0`. Cite: §12.1; STR-0221; STR-0283.

**B1.5 — `compute_max_exposure_imbalance_qty(*, leverage_effective: Decimal,
notional_per_level_usd: Decimal, mark_price: Decimal) -> Decimal`.**
DYNAMIC formula — a FORMULA, never a constant (7h-3 tolerance precedent; STR-0340
`dynamic_note`). Pinned evaluation order (bitwise determinism; comment each step):
```python
mmf = Decimal("0.5") / leverage_effective  # MaintenanceMarginFraction (STR-0340)
return (Decimal("0.25") * mmf * notional_per_level_usd) / mark_price
```
No quantization (no rounding pinned — return the exact ambient-context result).
Validation: all three `> 0` (else `ValueError`). Units: base-asset quantity.
Cite: §12.1; §16 D-16 (STR-0329..0331); STR-0223; STR-0279; STR-0340. Worked vector
STR-0279: defaults at 3× ≈ `0.00208` BTC (E2 pins it at 5dp).

### B2 — Breach ladder (`risk_bounds.py`)

**Vocabulary (pinned):**
- `BreachLayer` (StrEnum, `_NameValueStrEnum` leaf pattern): `NONE` (COINED — the no-breach
  state), `ALERT` (VERBATIM §12.1/STR-0216 "Alert"), `SOFT_PROTECTIVE_ACTION` (VERBATIM
  "Soft Protective Action"), `OPERATOR_DECISION` (VERBATIM "Operator Decision").
- `RiskReasonCode` (StrEnum, module-local — `reason_codes.py` is FROZEN with no reusable
  code; ArmBlockCode precedent): `RISK_BOUND_ALERT`, `RISK_BOUND_SOFT_ACTION`,
  `RISK_BOUND_OPERATOR_REQUIRED` — all COINED ← §12.1 breach-response paragraph.
- Bound ids: VALIDATED `str` (lifecycle-string precedent — mixed case forbids enum),
  exactly the 5 verbatim §12.1 names: `MaxRangeInducedDD`, `MaxExposureImbalance`,
  `MaxExecutionCost`, `MaxFailedLevelRate`, `MaxHedgeCost`. (MaxBasketNotional is NOT a
  monitored bound — computed-once per the §14 global rule — so it has no ladder.)

**`apply_breach_response(*, current_value: Decimal, bound_value: Decimal,
prior_layer: BreachLayer) -> tuple[BreachLayer, RiskReasonCode | None]`.**
`breached := current_value > bound_value` (STRICT — `==` is compliant, pinned by STR-0220's
`SKIPPED/total ≤ 5%`; all five are MAX bounds). Total 8-cell table:
- not breached, ANY prior → `(NONE, None)` (cleared).
- breached, `NONE` → `(ALERT, RISK_BOUND_ALERT)`.
- breached, `ALERT` → `(SOFT_PROTECTIVE_ACTION, RISK_BOUND_SOFT_ACTION)`.
- breached, `SOFT_PROTECTIVE_ACTION` → `(OPERATOR_DECISION, RISK_BOUND_OPERATOR_REQUIRED)`.
- breached, `OPERATOR_DECISION` → `(OPERATOR_DECISION, None)` (sticky; no new code).
Validation: Decimals; `bound_value > 0`; `current_value >= 0` (all five monitored
quantities are non-negative by construction); `prior_layer` must be a `BreachLayer`
(else `ValueError`). No auto-terminate: every cell RETURNS (STR-0216).
Cite: §12.1 breach-response paragraph; STR-0215/STR-0216. The persistence-ladder dynamics
(one step per breached evaluation) are COINED-but-anchored: the Strategy pins the 3 layers
and their order but no transition triggers (STR-0216 `formula: NONE`).

### B3 — Row types (`risk_state.py`)

Leaf module: stdlib (`dataclasses`, `decimal`, `enum`, `re`) + same-package `arm_state`
(`OperationalState`) and `risk_bounds` (`BreachLayer`) ONLY. Frozen, slots, self-validating,
`to_canonical_obj` (enums as `.value`, Decimals native, tuples as lists, omit-None R-JSON-6).
Timestamps: module-local `_ISO_UTC_MICROS` regex + `_validate_iso_ts` helper — copy the
arm_state pattern (no `datetime`, no frozen/private import):
`^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$`.

**B3.1 — `AccountEquityState` (ST-17).**
- `capital_base_usd: Decimal` (`> 0`).
- `source: str` — MUST equal `"clearinghouseState"` (validated `__post_init__` equality).
  This is the ST-08 precedent (`ActualExposureState.source`; DECISION-002 names the
  AUTHORITY endpoint, not a JSON path). Comment cites the exact field
  `marginSummary.accountValue` (DECISION-002 evidence SRC-107) + STR-0224 + ST-17 cell.
- `read_at_ts: str` (ISO-8601-Z micros, module-local validator).
Cite: STR-0224; DECISION-002; STATE_OWNERSHIP ST-17 (owner CAP-0002; point-in-time).

**B3.2 — `RiskBoundTrackerState` + `BoundLayerState` (ST-20).**
- `cumulative_execution_cost_usd: Decimal` (≥ 0; lifetime-to-date, D-15).
- `cumulative_hedge_cost_usd: Decimal` (≥ 0; lifetime-to-date).
- `failed_level_rate_pct: Decimal` (∈ [0, 100]; counting rule per B1.3 — runtime-fed).
- `range_induced_dd_pct: Decimal` (∈ [0, 100]).
- `bound_layers: tuple[BoundLayerState, ...]` — sorted by `bound_id`, no dups (row-level
  `__post_init__`); empty tuple allowed (nothing evaluated yet).
- `BoundLayerState`: `bound_id: str` (∈ the 5 verbatim names), `layer: BreachLayer`
  (`isinstance`-validated), `updated_at_ts: str` (ISO validator). THIS is the persisted
  alert record: `bound_id` = identity, `updated_at_ts` = timestamp (§12.1 "persisted,
  with identity and timestamp"; the runtime supplies `updated_at_ts` at evaluation).
- NOTE (field comment): the |ExposureDelta| CURRENT value lives in ST-09 (already typed);
  ST-20 carries only that bound's LADDER state, not a duplicate quantity.
Cite: §12.1; STR-0218/0220/0221 (bounds); STATE_OWNERSHIP ST-20 (owner CAP-0017;
lifetime-to-date D-15; recovery = reconstruct from event log).

**B3.3 — `BasketNetPnLState` (ST-21).**
- `realized_usd`, `unrealized_usd`, `fees_usd`, `funding_usd`, `net_usd` (all Decimal, any
  sign — rebates/negative funding exist).
- Invariant (`__post_init__`, exact): `net_usd == realized_usd + unrealized_usd - fees_usd
  + funding_usd`. Comment: NET (never gross) governs every lifecycle decision (STR-0235).
Cite: §13.1; STR-0234 (verbatim formula); STR-0235; STATE_OWNERSHIP ST-21 (owner CAP-0018).

**B3.4 — `FreezeErrorRecoveryOverlayState` (ST-22).**
- `operational_state: OperationalState` — REUSE `arm_state.OperationalState` (9 members
  VERBATIM §13.2; do NOT redefine). `isinstance`-validated.
- `since_ts: str` (ISO-8601-Z micros).
- `last_reason_code: str | None` — when present, a NON-EMPTY `str` (type-checked only).
  Content is NOT validated against any closed set: the overlay cause vocabulary is OPEN
  (runtime/post-7h writers across subsystems); the row CARRIES provenance, it does not gate.
  (Distinguished from `ArmRequestState.block_code`, which is a closed enum because ST-12 is
  a closed 5-state machine.)
Cite: §13.2 (states); §13.3 (freeze); STR-0238/STR-0239; STATE_OWNERSHIP ST-22 (owner
CAP-0023; overlay never erases underlying state, STR-0047).

### B4 — State wiring (`state.py`)

RETYPE in place (D6 — wiring types, not adds; the 23 `st*` field count MUST NOT change):
- `st17_account_equity_capital_base: AccountEquityState | None = None  # ST-17 (7h-4a)`
- `st20_risk_bound_trackers: RiskBoundTrackerState | None = None  # ST-20 (7h-4a)`
- `st21_basket_pnl_accounting_net: BasketNetPnLState | None = None  # ST-21 (7h-4a)`
- `st22_freeze_error_recovery_overlay: FreezeErrorRecoveryOverlayState | None = None  # ST-22 (7h-4a)`
(Field names are the ACTUAL placeholder spellings at `7489848` — no renames.)
- Add the 4 names to `_TYPED_ST_FIELD_NAMES`.
- Add 4 singleton serialization blocks (st07-pattern: `if self.stXX is not None:` →
  `to_canonical_obj()`), inserted directly after the `st16_evolution_candidate_windows`
  block, before `effective_generation_limit`.
- Add the import after the `order_state` import (ruff-isort order):
  `from hypergrid.core.transitions.risk_state import (AccountEquityState, BasketNetPnLState,
  FreezeErrorRecoveryOverlayState, RiskBoundTrackerState)`.
- Comment refresh 1 (module docstring forward note) — replace
  `ST-17 → 7h (venue reads / MaxBasketNotional; 7g-3b reads no CapitalBase);\nST-18 → 7h;
  ST-01, ST-06, ST-20..ST-22 stay ... placeholders until\ntheir rule lands.` with
  `ST-17/20/21/22 → 7h-4a (risk_state.py rows; venue reads still runtime-fed,
  MaxBasketNotional formula post-7h);\nST-18 → 7h; ST-01, ST-06 stay ... placeholders
  until\ntheir rule lands.` (keep the surrounding note text intact).
- Comment refresh 2 (above the domain fields) — replace
  `Typed so far: ... ST-05/12 (7h-2).` + `ST-01/06/11/13/17/18/20/21/22 remain placeholders`
  with `Typed so far: ... ST-05/12 (7h-2), ST-17/20/21/22 (7h-4a).` +
  `ST-01/06/11/13/18 remain placeholders`.
- NO new `_validate_*` (singletons; `bound_layers` ordering is row-level, enforced in
  `RiskBoundTrackerState.__post_init__`).

---

## Part C — Code placement and conventions

### C1 — Module names

- `src/hypergrid/core/transitions/risk_bounds.py` (B1 + B2 + `BreachLayer` + `RiskReasonCode`).
- `src/hypergrid/core/transitions/risk_state.py` (B3: 5 dataclasses).
- `src/hypergrid/core/state.py` (B4 — the ONLY existing source file edited).
- `src/hypergrid/core/transitions/__init__.py` (re-exports + `__all__`, ruff-isort order):
  `BreachLayer`, `RiskReasonCode`, the 6 B1/B2 functions, `AccountEquityState`,
  `RiskBoundTrackerState`, `BoundLayerState`, `BasketNetPnLState`,
  `FreezeErrorRecoveryOverlayState`.
- **New tests:** `tests/test_risk_bounds.py`, `tests/test_breach_response.py`,
  `tests/test_risk_state.py`. NO other test file is created or touched.
- Research docs-only: `research/architecture/STATE_OWNERSHIP.md` — append
  `; row typed 7h-4a (risk_state.py)` to each ST-17/20/21/22 cell's `notes:` ONLY.

### C2 — Purity, layering, time

`core/` imports: stdlib (`dataclasses`, `decimal`, `enum`, `re`) + same-package leaves ONLY
(enforced by `tests/test_core_no_forbidden_imports.py`, which bans `logging`, `time`,
`datetime`, `random`, `os`, `pydantic`, `httpx`, `websockets`, `eth_account`, `numpy`,
`pandas`, `requests`, `aiohttp`, `asyncio`). No `float` (literal, call, annotation, or
subscript — same test). No `hashlib` outside `envelope.py`. No decimal-context mutation.
New modules MUST NOT import `core.state`, `core.pass_engine`, `core.fold`, or `config/*`.

### C3 — Additive edits + UNTOUCHED

- `state.py`: 4 retypes + frozenset + 4 serialization blocks + import + 2 comment refreshes
  (Part B4 — nothing else in the file).
- `transitions/__init__.py`: re-exports + `__all__` only.
- **UNTOUCHED (empty diff required):** every other file under `src/` (including
  `pass_engine.py`, `cycle.py`, `arm_state.py`, `order_state.py`, `reason_codes.py`,
  all `core/events/*`, all of `config/`), every existing file under `tests/`,
  `Strategy.md`, `research/strategy/STRATEGY_CONTRACT.md`, `research/decisions/*`,
  `prompt.md`, `pyproject.toml`.

### C4 — Enum and literal rules

- `_NameValueStrEnum` (auto() == name): define the module-local copy in `risk_bounds.py`
  (leaf pattern — 5 precedents: arm/order/hedge/emergency/execution_cancel).
- `BreachLayer`: NONE coined; ALERT/SOFT_PROTECTIVE_ACTION/OPERATOR_DECISION VERBATIM
  (§12.1 + STR-0216; mechanical SNAKE transform of "Alert" / "Soft Protective Action" /
  "Operator Decision" — pin the mapping in a comment).
- `RiskReasonCode`: all 3 COINED ← §12.1 breach-response paragraph (ArmBlockCode precedent).
- Bound ids: validated `str` against the 5 verbatim §12.1 names (NOT an enum; lifecycle
  precedent). The frozenset stays module-private (`_BOUND_IDS`); tests exercise it via
  validation errors.
- Every numeric literal in B1 carries an inline cite (D3 — no bare `0.30`/`100`/`2`/`0.25`).

---

## Part D — Standing engineering rules (authoritative for 7h-4a)

- **D1 Determinism & purity:** `core/` is pure, clock-free, I/O-free. Timestamps and venue
  quantities ARRIVE as parameters (validated, never generated). No banned imports, no float,
  no context mutation (Part C2).
- **D2 Fail-closed:** invalid input → `ValueError` (never a silent default, never a
  None-coercion). Unknown tokens → `ValueError`. Where an exact `int` is required, reject
  `bool` (`type(x) is int`).
- **D3 Cite-or-coin:** every bound, comparator, threshold literal, and vocabulary item carries
  a Strategy `§`/STR citation or an explicit `COINED ← anchor` comment. No bare magic.
- **D4 Additive-only edits:** existing files gain retypes/extends/appends ONLY (Part B4/C3).
  Never reshape an existing field, function, or test; never rename.
- **D5 No new STUBs:** every function built is real, total on validated inputs, and E-tested.
  No `TODO`/`FIXME`/`NotImplementedError`/placebo branches. (Typing a row ≠ a stub.)
- **D6 State wiring types (not adds):** the 23 `st*` field count is preserved; serialization
  via `to_canonical_obj()` + R-JSON-6 omit-None; `canonical_dumps`-clean at every depth.
- **D7 Test discipline:** new behavior in NEW test files only; existing tests untouched unless
  pre-authorized in Part E (none are — E1); E-matrices pin every boundary; no `skip`/`xfail`;
  report TRUE counts (collected, not claimed).
- **D8 Reconciliation-allowed:** when this prompt's own signature sketch is incomplete relative
  to its prose + test matrix, you MAY accept the minimal additive input/output field to satisfy
  prose + tests, provided ALL hold: (a) flagged in the report as `reconciliation (not a STOP)`;
  (b) documented in the module; (c) validated; (d) Strategy-§/STR-cited; (e) strictly minimal —
  no behavior beyond satisfying this prompt's own prose + matrix; (f) touches no frozen or
  Part-C3-untouched file; (g) adds no scope (no new module/test beyond the pinned set to
  support it); (h) pre-flight's aim remains zero such cases. Any reconciliation failing
  (e)–(h) is a **global STOP**.

---

## Part E — Tests

### E1 — Suite, types, hygiene

- Full suite green: 453 at base + all new tests (report the TRUE total).
- NO existing-test edits (none pre-authorized). In particular these two MUST pass UNMODIFIED
  (they are the D6 tripwires — field count stays 23):
  `tests/test_state.py::test_state_has_23_domain_placeholders`,
  `tests/test_order_lifecycle.py::test_domain_placeholder_count_preserved`.
- `mypy --strict`: the phase must introduce ZERO new errors. Method (version-robust): run
  `mypy --strict src tests` on the BASE tree and on the phase tree with the SAME tool; the
  error-set delta must be EMPTY (pre-existing baseline errors, if any under your mypy version,
  are out of scope — do not fix, do not touch those files).
- `ruff check`: all passed. `ruff format --check`: every NEW/EDITED file clean (pre-existing
  unformatted files are out of scope — do not touch).
- No new dependencies. `git status` shows ONLY the pinned file set (Part G).

### E2 — Behavior matrices (new test files)

- **`test_risk_bounds.py`:** exact-value vectors — DD `== 100`; exec PnL>0 (`1000 → 300`),
  PnL `== 0` → MBN regime, PnL `< 0` → MBN regime (`MBN 30000 → 300`); failed `== 5`;
  hedge `MBN 30000 → 600`; imbalance terminating vector
  (`lev 2, NPL 5000, PX 100000 → 0.003125` EXACT) + the STR-0279 defaults vector
  (`lev 3, NPL 5000, PX 100000`, quantized to 5dp `== 0.00208`); validation errors
  (non-Decimal; `MBN ≤ 0`; `lev/NPL/PX ≤ 0`).
- **`test_breach_response.py`:** all 8 table cells (parametrized); boundary `current == bound`
  → NOT breached (clears to `(NONE, None)` from every prior); the 3 escalation codes; sticky
  carries `None`; clear carries `None`; validation (non-Decimal; `bound ≤ 0`; `current < 0`;
  non-`BreachLayer` prior); no-auto-terminate (all 8 cells return — never raise).
- **`test_risk_state.py`:** all 5 dataclasses frozen; ST-17 source accepts `"clearinghouseState"`
  and REJECTS everything else (including `"clearinghouseState.accountValue"` and
  `"clearinghouseState accountValue"` — regression pins for the verbatim trap); ST-17
  `capital ≤ 0` rejected; timestamp validator (one good + three bad); ST-21 invariant (one
  valid + two violated: wrong net, non-Decimal); ST-20 ranges + `bound_layers` sorted/no-dup
  + bad `bound_id` + bad layer type + empty-tuple-OK; ST-22 accepts all 9 `OperationalState`
  members + `last_reason_code` str-or-None (+ non-empty rule, non-str rejected);
  `to_canonical_obj` + `canonical_dumps` round-trips incl. a fully-populated State with all
  4 slots; 4 slots default `None`; the 4 names ∈ `_TYPED_ST_FIELD_NAMES` (import from
  `hypergrid.core.state` — private-import-in-tests precedent).

### E3 — Pipeline, slots, persistence

- End-to-end: build an ST-21 row → read its `net_usd` → compute the B1.2 bound → build an
  ST-20 row → `apply_breach_response` → attach the resulting `BoundLayerState` → serialize
  the State → `canonical_dumps` clean.
- Unchanged-surface check: empty diffs for `pass_engine.py`, `cycle.py`, `arm_state.py`,
  `reason_codes.py`, `core/events/*`, `config/*`, all pre-existing tests.

---

## Part F — STOPs

**Zero pre-listed.** The draft's narrow STOPs were resolved by pre-flight against `7489848`:
(S-1 placeholder names → the 4 ACTUAL spellings are pinned in Part B4 — retype in place, no
rename); (S-2 fourth layer → evaporated — §12.1 + STR-0216 pin exactly 3 layers). The draft's
B1.5 soft-bands were incoherent (the SOFT band was unreachable for `multiplier ≥ 1`) and are
REPLACED by the Part B2 ladder — do not resurrect them.
**Global abort rule:** any E1 breakage, any need to edit a frozen/Part-C3-untouched file or
any existing test, any reconciliation failing D8 (e)–(h), or any genuinely unresolvable
question → STOP with the failing artifact + citations + the exact function-level question.

---

## Part G — Deliverables

1. `src/hypergrid/core/transitions/risk_bounds.py`, `src/hypergrid/core/transitions/risk_state.py`.
2. Additive edits: `src/hypergrid/core/state.py` (Part B4), `transitions/__init__.py`,
   `research/architecture/STATE_OWNERSHIP.md` (4 notes-cells only).
3. Tests: `tests/test_risk_bounds.py`, `tests/test_breach_response.py`, `tests/test_risk_state.py`.
4. Report: base SHA + branch SHA; TRUE test counts (base/new/total); mypy BASE-vs-phase
   error-set evidence; ruff evidence; coined-vocab inventory (each with anchor); seam
   confirmations (each A2 item + where it went); pre-authorized edits (none — confirm);
   reconciliation flags (if any, per D8); the E3 e2e result.

## Part H — Acceptance checklist

- [ ] E1 all green (453 + new, TRUE total reported; the two 23-count tests pass UNMODIFIED).
- [ ] E2/E3 matrices pass per the pinned vectors/tables.
- [ ] D3 holds (every literal/vocab cited or coined-anchored).
- [ ] D8 obeyed if used (a)–(h), else confirm "no reconciliation".
- [ ] Part C3 untouched list verified empty-diff (report the command + output).
- [ ] Report carries SHA + true counts + coined/seam inventories.

---

## Appendix — Pinned readings

- **P1** §12.1 breach paragraph (VERBATIM core): "(1) Alert (persisted, with identity and
  timestamp), (2) Soft Protective Action (the least-aggressive intervention that addresses the
  breach …), (3) Operator Decision (the system never auto-terminates on a Group B breach;
  escalation beyond the soft action is a human decision)".
- **P2** §12.1 bound wordings: DD "100% of Basket equity, i.e. total basket loss"; imbalance
  "(0.25 × 0.5 / Leverage_effective) × NotionalPerLevel / MarkPrice" + "forcing unconditional
  Hedge Recovery (§11.2's acute branch)"; exec "30% of BasketNetPnL when BasketNetPnL > 0; 100
  bps of MaxBasketNotional when BasketNetPnL ≤ 0 (the two-regime form resolves the
  previously-open denominator question)"; failed "fraction of Levels reaching SKIPPED …
  5% … ALL Levels of the ACTIVE Basket (not a rolling time window) … Sustained breach →
  Market Selection re-evaluation at next Basket INITIALIZING"; hedge "2% of
  MaxBasketNotional"; MBN "Computed ONCE … the confirmed value is binding and the formula is
  NOT re-executed while the system runs (§14 global rule)".
- **P3** Contract rows: STR-0215/STR-0216 (ladder; `formula: NONE` — triggers coined); STR-0217
  (DD); STR-0218/STR-0281 (exec); STR-0220/STR-0282 (failed; formula `SKIPPED/total ≤ 5%`;
  deps STR-0190); STR-0221/STR-0283 (hedge); STR-0223/STR-0279/STR-0340 (imbalance; e.g.
  `0.00208` BTC at 3×; `dynamic_note: must remain dynamic`); STR-0284 (MBN DERIVED-once);
  STR-0224 (CapitalBase; wording uses the SPACE form — the validated literal follows the
  ST-08 endpoint precedent instead, Part B3.1); STR-0234/STR-0235 (NET formula + NET-governs);
  STR-0238/STR-0239 (ERROR⇄RECOVERY/CLOSED; FROZEN); STR-0342 (ordering — seamed, Part A2).
- **P4** ST cells (STATE_OWNERSHIP.md): ST-17 owner CAP-0002, point-in-time, NEVER webData2/3;
  ST-20 owner CAP-0017, lifetime-to-date (D-15), reconstruct-from-log; ST-21 owner CAP-0018,
  recomputed checkpoints; ST-22 owner CAP-0023, STR-0047 (overlay never erases).
- **P5** `state.py @7489848`: placeholders L143/L146–L148 (exact spellings in Part B4);
  `_TYPED_ST_FIELD_NAMES` L462 (14 members); serialization = explicit per-field blocks
  (st07-pattern); forward-note docstring + `Typed so far` comment (replacement text in B4).
- **P6** Precedents: ST-08 `source == "clearinghouseState"` (exposure_state.py); 7h-2 D6
  typing-preserves-23 (test_order_lifecycle.py D6 comment); module-local code enums
  (ArmBlockCode 16 members); `_NameValueStrEnum` leaf copies; arm_state ISO-ts validator
  (regex pinned in Part B3); `P1ExposureMarkers.max_exposure_imbalance` (consumer slot exists
  — wiring is runtime-side); 7h-3 DYNAMIC-formula pattern (formula + provenance + ambient
  context; applied to B1.5).
- **P7** Vocab pins: `BreachLayer` 4 (1 coined + 3 verbatim); `RiskReasonCode` 3 (all coined);
  bound ids 5 verbatim strs (NOT MBN); `NONE` = no-breach state (not a Strategy layer).
- **P8** Untouched enforcement: Part C3 list (incl. `config/`, `arm_state.py`, all existing
  tests). E3 re-verifies.
- **P9** Carried rulings: 7h-3 `tolerance_leverage_in` reconciliation (D8's live precedent);
  LEVEL_SKIPPED = the §9.3 per-level terminal (B1.3's counter).
- **P10** Verified counts: 382 STR rows (`^### STR-` in STRATEGY_CONTRACT.md), 23 DECISIONs
  (`^## DECISION-` in DECISION_REGISTER.md). No OWNER_GATE count is asserted (unverified —
  do not assert one).
- **P11** `prompt.md` conflicted (`<<<<<<< HEAD` L1 @7489848) — non-authoritative, do not read.
  Strategy SHA (drift check): `085044e72efa75e7` (first 16 hex of sha256 @7489848).
- **P12** If this prompt's sketch and its prose/matrix ever disagree, prose + matrix win; bridge
  the gap ONLY via D8 (flagged, minimal, cited) — never by silent reinterpretation.

END OF 7h-4a PROMPT — REPORT SHA + TRUE COUNTS + COINED/SEAM INVENTORIES