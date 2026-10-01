# AsterGrid (formerly hypergrid)

Deterministic, AI-independent runtime for an Aster perpetual asymmetric
hedge-grid strategy. The codebase was imported **verbatim** from the hypergrid
project on 2026-10-01 (Phase M — full history preserved; see
`research/migration/MIGRATION.md`). The Aster venue delta (hedge-mode startup
gate, two-sided exposure, V3 API surface) is specified in
`docs/contract/CONTRACT_DELTA_ASTER.md` and lands in phases P2/P3
(`docs/ROADMAP.md`).

## Authority & design (do not duplicate here)

- **Strategy authority:** `Strategy.md` (immutable; v2.3-final). Never modified.
- **Program governance:** `prompt.md` (Master Control Prompt v3.0).
- **Architecture:** `research/architecture/ARCHITECTURE_DECISION.md` — **CAND-B**,
  event-sourced single process; the append-only event log is the source of truth;
  the core is pure and side-effect-free; adapters are the only side-effect edge;
  signing is an isolated security boundary.
- **Decisions:** `research/decisions/DECISION_REGISTER.md` (DECISION-001..023).
- **Verification strategy:** `research/validation/VALIDATION_PLAN.md`.
- **Event model / interfaces:** `research/implementation/EVENT_MODEL.md`,
  `INTERFACE_MAP.md`, `CAP0024_DESIGN.md`.

## Package layout (`src/astergrid/`)

- `core/` — **pure domain** (stdlib-only; never imports `logging`; single-threaded;
  no `float` in the decision/money path). Phase 7b landed the deterministic
  foundation: `core/events/` (ten event kinds + envelope + sha256 hash chain +
  canonical order + watermark), `core/event_log/` (append-only port +
  in-memory/SQLite logs; the log alone allocates `log_sequence` from 0), and
  `core/serialization/` (canonical JSON frozen for OCaml interop). Phase 7c added
  `core/state.py` (frozen `State`, one placeholder per ST-01..ST-23) and
  `core/fold.py` (a pure, metadata-only `fold(envelopes) -> State`). Phase 7d added
  `core/pass_engine.py` (`run_pass`, the P0–P6 stages — P2/P3/P4 real, the rest
  stubs) and `core/transitions/` (§4.7 locks + precedence + reason codes). Phase 7e
  added the §4 Evolution transition + permanent successor lock (`generation.py`,
  executed inside P4; typed ST-02/14/15/16 in `generation_state.py`). Phase 7f
  made P5 real: the §5 Cycle transition (`cycle.py`) with execution-grounded
  reference capture (§5.4/§5.4.1) and the §5.6 non-overlap test; typed ST-03/ST-10
  in `cycle_state.py`. Phase 7g-1 added the §7.1 grid geometry (`geometry.py`) and
  §7.2 protection locking (`protection_lock.py`) as pure functions, plus minimal
  ST-04 typing (`level_state.py`) — no `run_pass` wiring. Phase 7g-2 added §7.3
  position sizing + hard caps + D-14 counting helpers (`sizing.py`) as pure
  functions, plus `LevelState.size_notional_usd`. Phase 7g-3a added the §11.1
  exposure derivatives + acute predicate + classification (`exposure.py`) and typed
  ST-07/08/09 (`exposure_state.py`). Phase 7g-3b made **P1 real** (`hedge.py`): the
  Fix-1 exposure gate (STR-0345/0346), §11.2 hedge urgency + HedgeIntent, §11.3
  mirror eligibility (price formula is a documented stop-item), §11.4 remainder
  tri-state; typed ST-19/ST-23 and wrote the first ST-07/08/09 values. Phase 7h-1
  made **P0 real** (`observation.py`): it records observed §6.1 lifecycle + VERIFIED
  `filled_quantity` into ST-04, populates ST-19, and projects `p1_exposure_markers`
  for the untouched P1 — closing the 7g-3b seam (markers-fed, envelopes unread,
  write-only); the §6.1 hard rule and the §7.2/§6.1 lock coherence are enforced at
  construction. The remaining §8 arming, §9/§10, and real P6 are later phases.
  Guards: `tests/test_core_*`.
- `adapters/` — side-effect boundary (venue I/O, persistence, signing) — Phase 7b+.
- `runtime/` — the process shell: logging, wiring, asyncio. `logging_setup.py`
  provides the JSON formatter + context + redaction.
- `operator/` — gated operator surface (arm approval, kill-switch) — Phase 7b+.
- `config/` — Pydantic v2 models derived from `Strategy.md` §14 (`schema.py`).

## Runtime / stack (DECISION-022 / DECISION-023)

Python (int/`Decimal` in the decision path; `mypy --strict`; core single-threaded).
Event store = SQLite behind a port (no Redis/Kafka — prohibited by CAND-B).
Config = Pydantic v2 + TOML. UI (later) = FastAPI + Jinja/HTMX. CAP-0024
reference model = OCaml (DECISION-021, separate offline codebase — no shared code).

## Dev

```bash
pip install -e ".[dev]"
pytest -q
mypy --strict src/astergrid
ruff check src tests
```
