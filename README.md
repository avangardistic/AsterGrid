# hypergrid

Deterministic, AI-independent runtime for a Hyperliquid perpetual asymmetric
hedge-grid strategy. This is the **Phase 7a scaffolding** — an empty skeleton;
it contains **no trading/domain logic** yet.

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

## Package layout (`src/hypergrid/`)

- `core/` — **pure domain** (Phase 7b+). Stdlib-only; **must never import
  `logging`**; single-threaded; no `float` in the decision/money path
  (`int`/`decimal.Decimal` only). Enforced by `tests/test_core_no_logging.py`.
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
mypy --strict src/hypergrid
ruff check src tests
```
