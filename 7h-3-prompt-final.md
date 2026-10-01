# 7h-3 — §9 Submission + Remainder + Emergency/Skip + §5.2 Step-2 Cancel Selector

**Base:** `origin/main` @ `a8c2d00` (7h-2 merged). **Scope:** §9 submission mechanics + §11.4
remainder quantities + §9.1/§9.2 emergency-execution decisions + §9.3 `LEVEL_SKIPPED` placement +
§5.2 step-2 cancel selection + the `ORDER_SUBMITTED`-entry trigger (via B1). **Later (out of
scope):** 7h-4 = §10 economics + §12.1 bounds (incl. the three-layer breach response) +
ST-17/ST-20/ST-21/ST-22 + §5.2 step-8 ladder issuance + P6 (7h-4 writes P6); venue adapter +
UNKNOWN_SUBMISSION recovery + pre-side-effect reconciliation post-7h TBD.

**Execution rule (standing, now 2-for-1 validated):** every question answerable from the repo is
PINNED below with a citation — do not re-argue pinned readings. There are **zero pre-listed
STOPs** (Part F). The only stop condition is the global abort rule (Part F).

**Rescope notice (pre-flight ruling, do not re-argue):** the approved-split label "3-attempt
rule" is VOID — no attempt-counting rule, numeric bound, or attempt vocabulary exists anywhere
in the Strategy, the contract, or the decisions (verified by exhaustive grep; §9.3 even states
"no automatic retry within the same Cycle"). Likely etymology: §12.1's *three-layer* breach
response (Alert → Soft → Operator), which §9.1 cites for wait-bound breaches and which belongs
to 7h-4. B3 below therefore implements what §9 ACTUALLY contains (emergency band/edge decision +
four-way re-evaluation + skip legs), not attempt counting.

---

## Part A — Scope and non-goals

**A1. Build (this phase):**

- B1 — `submit_order` (submission mechanics: `CommandEvent` build + log append + receipt +
  `ORDER_SUBMITTED` row advance). No venue call.
- B2 — `track_remainder` (§11.4 remainder quantities). Pure.
- B3 — §9 emergency: `compute_emergency_tolerance_bps` (D-16 formula) + `evaluate_emergency`
  (§9.1 IF/ELSE unified with the §9.2 four-way) + `can_level_skip` (§9.3 terminality gate). Pure.
- B4 — `select_exhausted_candidates` (§5.2 step-2 cancel SELECTOR). Pure. Plus the `LEVEL_SKIPPED`
  14th lifecycle member in both ST-04 leaves (B4.6).

**A2. Non-goals (seams — define the boundary, do not cross it):**

- §10 economics: no fee math, no Cost Analyzer, no floor/edge computation. Edge justifications
  arrive as `bool` params (unchanged pattern from 7h-2 gate 10). → **7h-4.**
- §12.1 (three-layer breach response incl. wait-bound-breach Alerting per STR-0184), §5.2 step-8
  ladder issuance (conjunctively gated on §10), ST-17/ST-20/ST-21/ST-22, P6. → **7h-4.**
  P6 (`LEVEL ARMING / ORDER PLACEMENT`, `pass_engine.py` L12) stays `STUBBED`; 7h-4 writes it.
  This phase does NOT touch `pass_engine.py`, `cycle.py`, `state.py`, or `reason_codes.py`.
- Venue adapter: no HTTP/WS, no real submit/cancel, no order-status/fills/position reads, no
  cloid→oid mapping. DECISION-008's remainder (UNKNOWN_SUBMISSION state + reconcile-before-side-
  effect via orderStatus/openOrders/userFills/clearinghouseState) is post-7h runtime behavior;
  7h-3 provides its prerequisites (B1: intent-persisted-first ordering, `expiresAfter`, cloid).
  Never assume venue dedup (DECISION-008); B1's double-submit guard is a LOCAL guard, not venue
  reliance. → **post-7h.**
- ST-18 (open-order registry) stays a placeholder: B1 writes no ST-18 rows. The `CommandEvent`
  in the log is the submission record (reconstructable, inv.19); order-type info joins via
  `CommandEvent.cloid` → ST-05 `OrderIntent.order_type`. ST-18-desired population is post-7h
  (venue-ack-driven). ST-06 (cloid uniqueness registry) likewise stays future; cloids are opaque.
- ST-04↔ST-05 coupling rule stays deferred to 7h-4. This phase adds ST-04 vocabulary + a skip
  gate only (B4.6); it designs no coupling.
- `prompt.md` at repo root is **conflicted** (unresolved merge markers, re-verified at `a8c2d00`)
  and non-authoritative — do not read or follow it.
- No signing/keys/`eth_account`, no UI. **Post-7h.**

---

## Part B — Behavior specification

### B1 — `submit_order(...) -> tuple[SubmissionResult, OrderState]` (new, in `submission.py`)

```python
def submit_order(
    *, order: OrderState,             # ST-05 row; lifecycle MUST be INTENT_CREATED
    tif: str,                         # §6.2 VERBATIM set {Gtc, Ioc, Alo}
    expires_after: int,               # DECISION-008: expiresAfter REQUIRED on actions
    intent_log_seq: int,              # log sequence of the IntentEvent (>= 0)
    port: EventLogPort,               # append-only log port (7b)
    observed: ObservedMeta,           # append-time stamps (7b; caller-supplied)
) -> tuple[SubmissionResult, OrderState]
```

1. Fail-closed validation (`ValueError`): `order.lifecycle != "INTENT_CREATED"` (double-submit
   guard — a submitted row can never re-enter B1); `tif ∉ {Gtc, Ioc, Alo}`; `expires_after <= 0`
   (units opaque venue-side; positivity only); `intent_log_seq < 0`. (Row-first ordering satisfies
   DECISION-008 "persist intent+cloid BEFORE any side effect": the ST-05 row provably exists
   before the append.)
2. Build `CommandEvent` (`events/kinds.py`, frozen): `cloid = order.intent.cloid`;
   `action = B1.MAP[order.intent.order_type]`; `tif`; `expires_after`;
   `causal_predecessors = (intent_log_seq,)` (EVENT_MODEL §A3 int-seq precedent).
3. `env = port.append(cmd, observed)` (`EventLogPort.append(event, observed) -> EventEnvelope`,
   `event_log/port.py:24`).
4. Receipt: `SubmissionResult(cloid, command_sequence = env.log_sequence: int,
   content_hash = env.content_hash: str, submitted_at_ts = observed.local_receive_ts)`
   (`EventEnvelope.log_sequence` R-SEQ-1 first-0 / `content_hash` sha256, `envelope.py:60/67`;
   `ObservedMeta.local_receive_ts: str`, `envelope.py:40`). Frozen/slots + `to_canonical_obj()`.
5. Trigger wire (the 7h-2-deferred `ORDER_SUBMITTED` entry): assert
   `is_legal_order_transition("INTENT_CREATED", "ORDER_SUBMITTED")` (table-honoring; raises if the
   table ever drifts), then return `dataclasses.replace(order, lifecycle="ORDER_SUBMITTED")`
   (re-validated by `OrderState.__post_init__`). Caller persists the row.
6. No `TimerEvent` input (timers are runtime-side; 7h-3 uses none). No ST-18 write (A2 seam).
   Appends EXACTLY once per call (E2 pins log-length +1 and the hash chain links).

**B1.MAP — `OrderType` → `CommandEvent.action` (PINNED; frozen vocab `{submit, cancel, modify,
twap}` forces it — extension is out of scope, not a STOP):** `LIMIT → "submit"`, `MARKET →
"submit"`, `STOP → "submit"`, `TAKE_PROFIT → "submit"`, `TWAP → "twap"`. COINED refinement:
"action = what the exchange is asked to do; order type is a parameter of that request" (trigger/
TIF/price params are post-7h venue-adapter concerns; type info joins via cloid → ST-05).

### B2 — `track_remainder(...) -> RemainderState` (new, in `remainder.py`)

```python
def track_remainder(
    *, requested_size: Decimal, verified_filled_size: Decimal,
    level_identity: tuple[int, int, str, int],  # (gen, cycle, direction, level)
    reference_price: Decimal,                   # caller-supplied (ST-04 LevelState.
) -> RemainderState                             # target_price is the caller's source)
```

- `level_identity` order `(gen, cycle, direction, level)` per the ST-04 key precedent
  (`state.py` ST-04 ordering key); `direction ∈ {"BU","SL"}` (§3 VERBATIM) else `ValueError`.
- Validation (`ValueError`): all three quantities `Decimal` instances; `requested_size > 0`;
  `0 <= verified_filled_size <= requested_size`; `reference_price > 0`. No ST-04 read (param
  keeps the ST-04↔ST-05 decoupling; no coupling designed — A2).
- `RemainderState`: `level_identity`, `requested_size`, `verified_filled_size`,
  `remaining_size = requested − verified` (exact), `remaining_notional_usd = remaining ×
  reference_price` (exact), `is_fully_filled = (remaining == 0)` + `to_canonical_obj()`.
- Cites: §11.4 L893 (`PARTIALLY_FILLED` contribution = verified-so-far; remainder "not
  independently hedged... (not-yet-exposure)"; remainder "times out into Emergency Execution
  (§9.1)"; "a skipped residual permanently contributes zero"). GUARD: STR-0199
  (`ExpectedExposure := Σ VERIFIED... not requested_qty`) governs the §11.1 exposure derivation
  ONLY — remainder arithmetic (which never treats requested AS filled) is outside its scope.
- Complementarity (no duplication, verified): `exposure.py` computes no remainder/notional;
  7g-3b's `classify_remainder_hedge_status(within_timeout: bool, skipped: bool)` classifies
  hedge status from runtime-evaluated bools. B2 computes quantities; no import either way.

### B3 — §9 emergency (new, in `emergency.py`)

Constants: `EMERGENCY_BOUNDED_WAIT_S = 30` (STR-0277, §9.1 D-09 Group A FIXED — the bound the
runtime's timer enforces; 7h-3 takes the breach as input). Tolerance is a FORMULA, never a
constant (STR-0276 `dynamic_note`, D-16):

```python
def compute_emergency_tolerance_bps(leverage_effective: Decimal) -> Decimal
```

- `50 / leverage_effective`, quantized to whole bps `ROUND_HALF_UP`. `leverage_effective <= 0`
  (or non-Decimal) → `ValueError`. Division uses the ambient default context (never mutated —
  no `getcontext()` writes anywhere); result quantized (whole-bps/10000 always terminates, so
  downstream band math is exact).
- The `3 → 17` vector (Strategy §9.1 + STR-0276 wording: `2→25, 3→17, 5→10`) PINS the rounding
  mode (16.67 → 17). E-tests pin all three vectors (+ `1→50`, `10→5`).
- L1368 "must log their use" vs no-logging-in-core: the tolerance travels WITH provenance —
  `EmergencyEvaluation` carries `tolerance_bps + tolerance_leverage_in + tolerance_formula
  ("STR-0276/D-16")`; the runtime logs from the record. (Same pattern as inv.4 identity.)

```python
def evaluate_emergency(
    *, wait_bound_breached: bool, direction: str,          # BU/SL (edge selection)
    target_price: Decimal, tolerance_bps: Decimal,         # band inputs (exact)
    fillable: bool,                      # Fillability Analyzer verdict (venue-side)
    best_exec_price: Decimal,            # venue quote; in-band check done HERE (pure)
    maker_edge_ok: bool, taker_edge_ok: bool,              # §10-side justifications
    reprice_would_justify: bool,         # §10-side/venue-side hypothetical
    remaining_size: Decimal,             # B2 output (caller-composed), > 0
    order_cloid: str, order_lifecycle_now: str,            # SKIP-leg fail-closed inputs
    level_identity: tuple[int,int,str,int], level_lifecycle_now: str,
) -> EmergencyEvaluation
```

- `wait_bound_breached is False` → `ValueError` (not an emergency; the runtime's 30s timer owns
  the bound). Band: `[target×(1−tol), target×(1+tol)]`, `tol = tolerance_bps/10000` (STR-0185).
  `in_band = (lo <= best_exec_price <= hi)` (inclusive; E2 pins endpoints).
- Priority (PINNED — list order + least-aggressive-first + STR-0188/0301 "never solely because
  of timeout"): `maker_edge_ok → WAIT_EXTEND`; elif `(taker_edge_ok AND fillable AND in_band)
  → IOC_AT_BAND_EDGE`; elif `reprice_would_justify → REPRICE_ALO`; else `→ LEVEL_SKIP`.
  Overlaps resolve by this order (E2 pins maker+taker→WAIT, taker+reprice→IOC).
- STR-0187 invariant BY CONSTRUCTION: IOC requires `taker_edge_ok` even when fillable (never
  fillable-but-uneconomic — E2 pins fillable+in-band+edge-fail → not IOC); `ioc_limit_price`
  IS the band edge (never beyond tolerance): `BU → hi`, `SL → lo` (side-selected edge;
  STR-0185 "at the tolerance-band edge"). `ioc_size = remaining_size`.
- Legs: `WAIT_EXTEND` = verdict only (breach Alerting is STR-0184 → §12.1 → 7h-4 seam).
  `IOC_AT_BAND_EDGE` / `REPRICE_ALO` = `cancel_original = True` (pending maker leg replaced;
  B1 executes: cancel-cmd + — for IOC — submit-cmd for the new Ioc row built via 7h-2's inlet
  with `tif="Ioc"`; the repriced-Alo construction needs the live book → post-7h, new row via
  B1 then). `LEVEL_SKIP` legs (data; applied runtime/7h-4-side):
  `EMERGENCY → SKIPPED`-candidate if `order_lifecycle_now == "EMERGENCY"`;
  `PARTIALLY_FILLED → CANCELLED`-candidate (remainder abandoned, verified fills stand — §11.4
  "skipped residual contributes zero") if `PARTIALLY_FILLED`; `ACTIVE` (or anything else) →
  `ValueError` (timeout detector must flag EMERGENCY first — explicit two-step, no silent
  chaining). Level leg: `level_lifecycle_now → LEVEL_SKIPPED`-candidate iff
  `can_level_skip(level_lifecycle_now)` else `ValueError`.
- `EmergencyVerdict {WAIT_EXTEND, IOC_AT_BAND_EDGE, REPRICE_ALO, LEVEL_SKIP}` (coined-but-
  anchored: §9.2 WAIT/Ioc/REPRICE/SKIP + §9.1 Ioc/LEVEL_SKIPPED). `EmergencyEvaluation` carries
  `order_cloid, level_identity, verdict, band_lo, band_hi, ioc_limit_price|None,
  ioc_size|None, tolerance_bps + provenance, cancel_original, skip legs` + `to_canonical_obj()`.

```python
def can_level_skip(from_lifecycle: str) -> bool   # in level_state.py (ST-04 home)
```

- `True` for `{ORDER_ACTIVE, EMERGENCY, PARTIALLY_FILLED}` (working states with a live order/
  remainder: §9.1 trigger case + §11.4 remainder-timeout case); `False` for the other 11
  (incl. `LEVEL_SKIPPED` itself — terminal, "never resurrected" §9.3); unknown → `ValueError`.
  Minimal skip-gate by design — NOT a general ST-04 table (7h-1 owns existing flows; no
  contradiction risk; a full table is a later-phase decision).

### B4 — §5.2 step-2 cancel selector (new, in `execution_cancel.py`) + `LEVEL_SKIPPED` member

```python
def select_exhausted_candidates(
    order_rows: tuple[OrderState, ...], gen_id: int, cycle_id: int, direction: str,
) -> tuple[CancelCandidate, ...]
```

- Selects rows with `intent.target_{generation,cycle}_id == (gen_id, cycle_id)` and
  `target_direction == direction`, AND `lifecycle ∈ {ORDER_SUBMITTED, ORDER_ACKNOWLEDGED,
  ORDER_ACTIVE, PARTIALLY_FILLED, EMERGENCY}` — the RESTING set (orders with live venue
  quantity). Output sorted by cloid (canonical, input-order-proof); empty→empty.
- PINNED purposive reading of L362-363 ("Cancel all pending (not POSITION_VERIFIED) orders..."),
  proved per excluded state (a venue cancel is void-or-reject for each — sending known-void
  cancels violates the §6.3 reject-philosophy; safety is preserved because provably nothing
  rests): `INTENT_CREATED` never sent (own log proves it); `FILLED` fully filled (nothing
  rests; authoritative per STR-0131/0132); `CANCELLED/SKIPPED/ERROR/POSITION_VERIFIED` terminal.
- `CancelCandidate(cloid, reason_code)`; `CancelReasonCode{EXHAUSTED_TRAVERSAL_CANCEL}` (coined ←
  L362-363; module-local — `reason_codes.py` is FROZEN, 15 members, no extension; no reusable
  cancel code exists there — verified). Frozen/slots + `to_canonical_obj()`.
- Seam: runtime/7h-4 sets P5's S2 marker (`exhausted_side_pending_cancelled`, `cycle.py:200`)
  from selector output + venue cancel-acks; the `→CANCELLED` transitions are venue-ack-triggered
  (post-7h). 7h-3 touches neither `cycle.py` nor `pass_engine.py` (P5 is marker-gated by 7f
  design; P6 stays `STUBBED` for 7h-4).

**B4.6 — `LEVEL_SKIPPED` 14th member (additive edits, C3):** add `"LEVEL_SKIPPED"` to BOTH
`_LIFECYCLES` frozensets (`level_state.py:38` + `observation_state.py:41` — the symmetric "both
leaves" design: ST-04 row vocab and P0 observed vocab stay identical) + update the
`level_state.py:36-37` comment (`13 §6.1 strings` → `13 §6.1 + LEVEL_SKIPPED (§9.3 STR-0190/0191:
first-class per-level terminal; zero exposure/PnL; never resurrected)`) + `can_level_skip`
(B3) in `level_state.py`. No other lifecycle semantics change (R10c untouched).

---

## Part C — Code placement and conventions

### C1 — True facts (all 10 former UNVERIFIED items resolved by pre-flight; no Part 0)

- `evaluate_wait` returns `tuple[ArmOutcome, ArmBlockCode | None]` (`arm.py`, 7h-2 as specced).
- `state.py` validates via `__post_init__` → `_validate_order_arm_invariants` (7h-2; untouched
  by 7h-3 — no new slots, no `state.py` change at all).
- `ArmRequestState` fields EXACTLY: `cloid, request_seq, status, timestamp, block_code=None,
  operator_identity=None` — no `request_id`, no `requested_at_ts`, no `level_identity`.
- `OrderState` fields EXACTLY: `intent: OrderIntent + lifecycle: str` (+ `cloid` property) —
  no outcome fields.
- `transitions/__init__.py` exports all names 7h-3 needs (`evaluate_wait`,
  `is_legal_order_transition`, `ArmBlockCode`, `OrderState`, `IntentTag`, ... — 7h-2 diff).
- `ArmBlockCode` EXACTLY 16: `GATE_1_DEPTH, GATE_2_DISTANCE, GATE_3_SIZE, GATE_4_MARGIN,
  GATE_5_EXPOSURE_CAPS, GATE_6_OPEN_ORDER_COUNT, GATE_7_PRICE_NORMALIZED,
  GATE_8_SIZE_NORMALIZED, GATE_9_MARKET_STATE, GATE_10_EDGE,
  DISABLED_GENERATION_BLOCKS_ENTRY, POLICY_ABSENT, ARM_TIMEOUT, ARM_DENIED, ARM_SUPERSEDED,
  ARM_WEBHOOK_ERROR` (neither guessed alternative).
- `DISTANCE_BAND = (5, 100)`, `tuple[int, int]` (`arm.py`).
- `is_legal_order_transition` = `_LEGAL_ORDER_EDGES` frozenset + function (`order_state.py`).
- Test files landed EXACTLY: `tests/test_arm_gates.py`, `tests/test_arm_state.py`,
  `tests/test_order_lifecycle.py` (28/17/10).
- `prompt.md` conflicted: RE-VERIFIED at `a8c2d00` (do-not-read stands).
- **New modules (exact names):** `src/hypergrid/core/transitions/submission.py` (B1),
  `remainder.py` (B2), `emergency.py` (B3), `execution_cancel.py` (B4). Re-export through
  `core/transitions/__init__.py` (existing precedent). `IntentTag` stays imported from
  `hedge_state` (never redefined). `EventLogPort` from `core/event_log/port.py`;
  `EventEnvelope/ObservedMeta` from `core/events/envelope.py` (read-only use of frozen types).

### C2 — Purity, layering, time

Unchanged from 7h-2 (no `logging/time/datetime/random/os/asyncio`/network/numeric imports in
`core/` — AST-enforced; no `float` — quantities `Decimal`, seconds/counts `int`; no logging;
no `getcontext()` mutation — division uses the ambient default context, results quantized).
Timestamps enter as ISO-8601-Z microsecond strings (via `ObservedMeta`; module-local validators
mirroring `_req_ts`, never importing the private helper). `to_canonical_obj()` per new row/
result type; `canonical_dumps` raises on `None`/`float`.

### C3 — Additive edits (exact; nothing else)

- `level_state.py`: +`"LEVEL_SKIPPED"` in `_LIFECYCLES` (L38-54) + comment refresh (L36-37) +
  `can_level_skip` (B3). Nothing else in the file.
- `observation_state.py`: +`"LEVEL_SKIPPED"` in `_LIFECYCLES` (L41+) only.
- `transitions/__init__.py`: re-exports + `__all__` (existing sort convention).
- Research docs-only (zero test impact): `STATE_OWNERSHIP.md` ST-04 notes cell +=
  `LEVEL_SKIPPED (§9.3)` (keeps the lifecycle-vocab note true).
- UNTOUCHED (E3 asserts empty diffs): `pass_engine.py`, `cycle.py`, `state.py`,
  `reason_codes.py` (15 members, frozen), all of `core/events/*`, all existing tests except the
  ONE pre-authorized edit (E1).

### C4 — Enum and dataclass rules

Same as 7h-2 §C4 (frozen/slots + `§/STR/DECISION` field comments; `StrEnum` + `auto()` co-located;
every member `VERBATIM …` or `COINED …` — no bare members; `_NameValueStrEnum`-style local base
where needed, never importing privates). New: `SubmissionResult`, `RemainderState`,
`EmergencyVerdict` (4), `EmergencyEvaluation`, `CancelCandidate`, `CancelReasonCode` (1).
Do NOT extend frozen enums (`ArmPolicy/ArmOutcome/OperatorDecision/OperationalState/ArmBlockCode`,
`IntentTag`, `CommandEvent.action`, TIF set).

---

## Part D — Standing engineering rules

**D1–D7 unchanged from 7h-2** (frozen read-only; structural absolute; cite-or-coin; determinism
by construction — literal inputs, no RNG/clock/order-dependence, canonical order DECISION-007;
no new STUBs — B4.2-selector/B1-advance are real logic, not placeholders; additive-only;
true counts). No D8 (nothing is UNVERIFIED). No Part 0 (deleted — all 10 resolved in C1).

---

## Part E — Tests (new files: `tests/test_submission.py`, `tests/test_remainder.py`, `tests/test_emergency.py`, `tests/test_execution_cancel.py`, `tests/test_level_skip.py`)

### E1 — Suite, types, hygiene (must all hold)

Full suite green (415 at base + new files); `mypy --strict` clean; `ruff check` + `ruff format
--check` clean; no new dependencies; no edits to any existing test or frozen/untouched module
except the ONE pre-authorized edit: **`tests/test_p0_lifecycle.py` 13-set → 14-set** (both
leaves' vocab lists + `LEVEL_SKIPPED`, comment refreshes `13 §6.1 strings` →
`13 §6.1 + LEVEL_SKIPPED (§9.3)`; 4th instance of the stage-realization-breaks-pinned-vocab-test
pattern — pre-authorized here, flagged in the report). `test_pass_engine_order.py` stays green
UNCHANGED (P6 remains `STUBBED`). Any other violation → global STOP (Part F).

### E2 — Behavior matrices

- **Submission (`test_submission.py`, real in-memory log from `core/event_log/memory.py` — no
  fake port):** all 5 `OrderType → action` mappings; exactly-once append (log length +1, chain
  links, `command_sequence` 0-based); receipt fields (`content_hash` non-empty sha256,
  `submitted_at_ts` echoes `local_receive_ts`); predecessors `== (intent_log_seq,)`; row advanced
  to `ORDER_SUBMITTED` + edge table-legal; double-submit (advanced row re-entered) → `ValueError`;
  bad tif / `expires_after <= 0` / non-`INTENT_CREATED` / negative seq → `ValueError`.
- **Remainder (`test_remainder.py`):** full-fill → `remaining == 0`, `is_fully_filled`; partial →
  exact `Decimal` difference + notional; `verified == 0` → `remaining == requested`; validation
  errors (negative, `verified > requested`, non-Decimal, bad direction, tuple-order respected).
- **Emergency (`test_emergency.py`):** tolerance vectors `1→50 / 2→25 / 3→17 / 5→10 / 10→5` +
  invalid leverage → `ValueError`; `breached=False` → `ValueError`; band formula exact + endpoint
  inclusivity; each verdict reachable (WAIT/IOC/REPRICE/SKIP); overlaps (maker+taker→WAIT,
  taker+reprice→IOC); IOC price == side edge (`BU→hi`, `SL→lo`); fillable+in-band+edge-fail →
  never IOC (STR-0187); SKIP legs (`EMERGENCY→SKIPPED`-candidate, `PARTIALLY_FILLED→CANCELLED`-
  candidate, `ACTIVE→ValueError`, level-leg honoring `can_level_skip`); provenance carried
  (tolerance + leverage + formula id).
- **Cancel (`test_execution_cancel.py`):** all 5 resting lifecycles selected; all 6 non-resting
  (`INTENT_CREATED/FILLED/CANCELLED/SKIPPED/ERROR/POSITION_VERIFIED`) excluded; traversal filter
  (wrong gen/cycle/direction excluded); output sorted by cloid; code on every candidate;
  empty→empty.

### E3 — Lifecycle, slots, persistence

- `LEVEL_SKIPPED`: accepted by BOTH leaves; terminal (no outgoing over all 14 — incl. no
  self-edge); `can_level_skip` (3 `True` / 11 `False` / unknown `ValueError`); both-leaves
  symmetry (same 14, same bogus rejection); R10c coherence untouched.
- End-to-end: synthetic intent → `construct_order_intent` → `classify_intent` → `submit_order` →
  log carries the `CommandEvent` + row at `ORDER_SUBMITTED`; cancel-selector over slot-shaped
  rows; emergency `LEVEL_SKIP` → candidates; `to_canonical_obj` + `canonical_dumps` round-trips
  for all new types; `transitions/__init__.py` exports import.
- Unchanged-surface check: empty diffs for `pass_engine.py`, `cycle.py`, `state.py`,
  `reason_codes.py`, `core/events/*` (7h-3 adds modules + 3 additive edits only).
- Inv.4/`P12`-style fields where applicable (identity + microsecond-Z ts on records that
  persist decisions); malformed timestamps rejected by module-local validators.

---

## Part F — STOPs: none pre-listed

Pre-flight resolved every ambiguity AND the four draft STOPs: (S-1) no attempt rule exists —
rescoped to §9 emergency (this prompt), nothing to STOP; (S-2) frozen vocab forces B1.MAP —
struck, not a phase decision; (S-3) B4.5 deleted with the no-P6 ruling — moot; (S-4) all 10
UNVERIFIED pinned in C1 — evaporated. The 12 hardest resolutions: (1) "3-attempt" void
(three-layer → 7h-4); (2) §5.2 = 8 steps, step 6 ≠ ladder issuance (that's step 8 → 7h-4);
(3) P6 stays `STUBBED` (7h-4 writes); P5 untouched (marker-gated by 7f design); (4) B4.2 as pure
selector (draft's no-op body would violate D5); (5) resting-set reading of L362-363 with
per-state proof; (6) `LEVEL_SKIPPED` 14th member, both leaves; (7) `can_level_skip` minimal gate
(no full ST-04 table); (8) PARTIAL-skip → `CANCELLED`-candidate, fills stand (§11.4); (9) B1
takes the ST-05 row + `expires_after` required (DECISION-008 Option B); (10) tolerance formula
+ `ROUND_HALF_UP` pinned by the `3→17` vector; (11) WAIT>IOC>REPRICE>SKIP priority;
(12) ST-05 `PARTIAL→ERROR` stays omitted (§9 doesn't need it — recorded 7h-2 decision stands).
**Global abort rule:** any E1 breakage, any need to edit a frozen/untouched module or an existing
test (outside the ONE pre-authorized edit), or any genuinely unresolvable question → STOP with
the failing artifact + citations + the exact function-level question. Do not work around.

---

## Part G — Deliverables

1. `src/hypergrid/core/transitions/submission.py`, `remainder.py`, `emergency.py`,
   `execution_cancel.py` (Part B/C).
2. Additive edits: `level_state.py` (member + comment + `can_level_skip`), `observation_state.py`
   (member), `transitions/__init__.py` (re-exports), `STATE_OWNERSHIP.md` ST-04 notes cell (C3).
3. `tests/test_submission.py`, `tests/test_remainder.py`, `tests/test_emergency.py`,
   `tests/test_execution_cancel.py`, `tests/test_level_skip.py` (Part E) + the ONE pre-authorized
   `test_p0_lifecycle.py` update (flagged).
4. Report: new-test count + suite total (true split, D7), mypy/ruff evidence, coined-vocab
   inventory, seam confirmations (7h-4/post-7h), the pre-authorized edit flagged.

## Part H — Acceptance checklist

- [ ] E1 all green (suite + mypy + ruff + structural), ONLY the pre-authorized test edit.
- [ ] E2/E3 matrices pass per the boundary tables (no weakened assertions).
- [ ] Cite-or-coin holds for every new member/field/comparator (D3).
- [ ] No STOP fired, or any fired STOP documented with citations (Part F).
- [ ] Report carries true counts (D7) and the coined/seam inventories (Part G.4).

---

## Appendix — Pinned readings index (corrected P1–P12)

- **P1** §9.1 L767-787 + STR-0182/0183/0184/0185/0186/0187 (trigger 30s; tolerance formula;
  three-layer alert → 7h-4; band + IF→Ioc-at-edge; ELSE→skip; hard invariant). No attempt rule.
- **P2** §9.2 L789-800 + STR-0188/0189/0301 (genuine four-way; WAIT/Ioc/REPRICE/SKIP
  justifications; taker-never-solely-from-timeout) → B3 priority + edge requirements.
- **P3** §9.3 L802-804 + STR-0190/0191 (first-class per-level terminal; zero/PnL; never
  resurrected; no same-Cycle retry) → B4.6 member + terminality.
- **P4** STR-0276 (D-16 formula + never-freeze note + `2→25/3→17/5→10` vectors) + STR-0277
  (30s D-09 Group A FIXED) + L1368 log-use rule (provenance-carried, runtime-logged).
- **P5** §5.2 step 2 L362-363 + STR-0075 (cancel selector; resting-set reading) + STR-0074
  (8-step order) + STR-0080 (step 8 → 7h-4) + P5 marker architecture (`cycle.py:191-245`:
  S2/S3/S8 gates exist; 7h-3 neither duplicates nor touches them).
- **P6** §11.4 L893 + `classify_remainder_hedge_status` (complementary, no overlap) + STR-0199
  guard (exposure-derivation scope only) → B2.
- **P7** DECISION-008 Option B (UNKNOWN_SUBMISSION recovery: intent-first, `expiresAfter`, no
  venue-dedup assumption; reconcile-before-side-effect + UNKNOWN state → post-7h) → B1 shape.
- **P8** Frozen facts: `CommandEvent` (`kinds.py`: cloid/action/tif/`expires_after`/`causal_
  predecessors`, action ∈ `{submit, cancel, modify, twap}`, tif str); `TimerEvent` unused by
  7h-3; `EventLogPort.append → EventEnvelope` (`port.py:24`); envelope `log_sequence`/
  `content_hash` (`envelope.py:60/67`); `ObservedMeta` (`envelope.py:38-40`); TIF
  `{Gtc,Ioc,Alo}` (§6.2); `reason_codes.py` 15 members, frozen.
- **P9** 7h-2 outputs reused (C1: exact shapes — `OrderState`, `IntentTag`, `evaluate_wait`,
  `ArmBlockCode`-16, `DISTANCE_BAND`, table+validator, test names) + 7h-2 acceptance rulings
  (`decision_by` accepted; supersede no-overwrite; ST-12 str; `PARTIAL→ERROR` stays omitted).
- **P10** P6 stays `STUBBED` (`pass_engine.py:12`, `test_pass_engine_order.py:24,54-55` green
  unchanged); 7h-4 writes P6 (coupling + §10-gated orchestration + step 8).
- **P11** ST-18 untouched (placeholder; desired-half post-7h) + ST-06 untouched + `STATE_OWNERSHIP.md`
  ST-04 notes-cell refresh (docs-only) + no new slots (no `state.py` change).
- **P12** Counts: **382** STR rows, **23** DECISIONs, **15** OWNER_GATEs (`GATE-001..013, 019,
  020`). `prompt.md` conflicted (re-verified `a8c2d00`): unreadable, non-authoritative.
  
  
  - `50 / leverage_effective`, quantized to whole bps `ROUND_HALF_UP`. `leverage_effective <= 0`
  (or non-Decimal) → `ValueError`. Division uses the ambient default context (never mutated —
  no `getcontext()` writes anywhere); result quantized (whole-bps/10000 always terminates, so
  downstream band math is exact).