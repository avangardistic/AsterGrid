# Owner input — 2026-10-01 (archived verbatim)

> **STATUS: ARCHIVE. The "Migration Prompt" below is SUPERSEDED. Do NOT execute it.**
> It predates the Owner's G-1/G-4/OPEN-2/OPEN-3 answers and contains defects found in pre-flight
> (V1 endpoints + HMAC + `X-MBX-APIKEY` which are obsolete under G-4=V3; `BOTH` on the order path;
> `read_user_fills → FillEvent`; `map_account_equity → AccountEquityState` without relaxing the `source` check;
> hypergrid→astergrid blind text replace; assumption that AsterGrid is empty; 7h-5a before the engine delta).
> The current plan is `docs/ROADMAP.md`; the migration executor prompt is `docs/prompts/PROMPT_MIGRATION_FREEBUFF.md`.
> Kept so no Owner text is lost.

---

## Owner answers (start of message)

- **G-4:** V3
- **OPEN-2:** روی هر طرف (per side)
- **OPEN-3:** margin mode cross, Multi-Assets mode

Owner requests in that message:
1. Save the whole text into a file and upload it to the repo.
2. "این رو هم میخوام توسط یک ایجنت دیگه اجرا کنم" — the migration prompt below (to be run by another agent).
3. Append the "Multi-Agent Ground / git check / optional tooling" addendum (Parts 9–12) to the migration prompt.
4. "فقط الان یک نقشه راه بنویس" (only write a roadmap now).
5. Write a prompt for a CLI AI agent (freebuff) for the migration.
6. Write a work-summary for DeepSeek, to open a new chat/session there.

---

## A. Migration Prompt: hypergrid → AsterGrid (fresh repo + 7h-5a-ASTER) — SUPERSEDED

**Purpose of this prompt:** one-shot instruction to a CLI AI agent. It will (1) migrate the codebase from `avangardistic/hypergrid` to the fresh empty repo `avangardistic/AsterGrid`, (2) strip Hyperliquid-specific artifacts, (3) execute the corrected **7h-5a-ASTER** phase (venue adapter only — no engine change; the ST-08 semantic stays out of this phase per the pre-flight verdict).

**Read this entire prompt before acting. Do not start any step until the previous step's exit criteria pass. Do not modify `Strategy.md`.**

---

### Part 0 — Non-negotiable rules carried from the hypergrid program

These are the operating rules the hypergrid program ran under. They are binding for AsterGrid.

1. **`Strategy.md` is immutable.** Never modify, rewrite, or normalize it.
2. **`prompt.md`** is the workflow protocol; it governs phases, gating, source governance, and artifact discipline. Read it fully once, refer to it as needed.
3. **No `float` in `core/`.** Money → `Decimal`; counts/seconds → `int`. `float` is forbidden except as the second argument of `isinstance(...)`.
4. **No `logging` in `core/`.** Logging belongs in `runtime/` and `adapters/`.
5. **`log_sequence` and `monotonic_counter` are allocated by the log only.** Callers supply all clock-derived values via `ObservedMeta`.
6. **Canonical JSON:** `sort_keys=True`; `Decimal` serialized as `{"__decimal__": "<string>"}`; `None` and `float` are rejected at any depth.
7. **Fail-closed on ambiguity.** Never guess, never silently continue, never invent defaults.
8. **Cite-or-coin discipline.** Every new enum member, field, or comparator carries a `VERBATIM` or `COINED` marker with an anchor (`file:line` or contract line).
9. **Counts are verified by grep, not memory.** Never assert a count without its grep command.
10. **Artifacts over conversation.** Durable files in `research/`, not chat context, are the source of truth.

---

### Part 1 — Base repository state (source)

**Source repo:** `github.com/avangardistic/hypergrid` (private).
**Source branch:** `main`.
**Source HEAD (at the time of this prompt):** `46b42b0` — **verify by `git log --oneline -1 origin/main` and quote the actual hash before continuing. If different, note it and proceed; the code tree is expected to be identical to `6a854c5` (docs-only change).**

**Baseline (record for the new repo's provenance):**

- `Strategy.md`: SHA-256 `085044e72efa75e7dd7e812588d8247c8e60152eecb233bd6969f6545a825e18`, 92,686 bytes, 1,368 lines (1-based).
- `prompt.md`: SHA-256 as recorded in the source repo's `research/sources/SOURCE_MANIFEST.md`.
- Test suite: **544 passing** at the source base.
- Code phases: **0 → 7h-4b-2** complete (Phase 7h-5a for Hyperliquid was drafted and **abandoned** — venue is wrong).
- Full phase history with commit hashes is listed in §5.

---

### Part 2 — Migration to AsterGrid

#### Step 2.1 — Clone the source repo

```powershell
cd C:\Users\Avangard\Desktop
git clone https://github.com/avangardistic/hypergrid.git AsterGrid
cd AsterGrid
```

**Exit criterion:** clone succeeds; `git log --oneline -1` shows the source `main` HEAD.

#### Step 2.2 — Verify source tree and record provenance

Before any modification:

1. `git log --oneline -10` — quote the actual hashes.
2. `Get-FileHash Strategy.md -Algorithm SHA256` — quote. **Must match** `085044e72efa75e7dd7e812588d8247c8e60152eecb233bd6969f6545a825e18`.
3. `python -m pytest -q` — quote the actual pass count. **Expect 544.**
4. `python -m mypy --strict src tests` — quote the error count. **Expect 119 / 132 files** (base errors live in `tests/`; `src` is clean).
5. `python -m ruff check src tests` — quote. **Expect "All checks passed!".**

**Write these values to `research/migration/SOURCE_PROVENANCE.md`** with timestamps. This file is the new repo's audit anchor.

**Exit criterion:** all five checks reproduce the expected values, or the divergence is documented and explained.

#### Step 2.3 — Point at the new remote

```powershell
git remote remove origin
git remote add origin https://github.com/avangardistic/AsterGrid.git
git remote -v
```

**Exit criterion:** `origin` points at `AsterGrid`.

#### Step 2.4 — Do NOT rewrite git history

The Hyperliquid phase history is the **reference** for what was built and why. Do not squash, rebase, or delete any commits. The migration is **additive** on a new branch.

```powershell
git checkout -b aster-migration
```

**Exit criterion:** on branch `aster-migration`.

---

### Part 3 — What to strip, keep, and re-home

#### Step 3.1 — Keep (venue-agnostic; ~80% of the code)

Everything in `src/hypergrid/core/` **except** the venues-specific adapter subpackage (see 3.2). This includes:

- `core/events/` — event model, append-only log, canonical JSON, envelope, identity, watermark
- `core/state.py` — State with all typed slots (ST-01..ST-22)
- `core/fold.py` — pure fold
- `core/pass_engine.py` — P0..P6
- `core/transitions/` — all transition modules:
  - `generation.py`, `generation_state.py`
  - `cycle.py`, `cycle_state.py`
  - `geometry.py`, `protection_lock.py`
  - `sizing.py`
  - `exposure.py`, `exposure_state.py`
  - `hedge.py`, `hedge_state.py`
  - `locks.py`, `markers.py`, `precedence.py`
  - `reason_codes.py`
  - `order_state.py`
  - `arm.py`, `arm_state.py`
  - `submission.py`, `execution_cancel.py`
  - `emergency.py`, `remainder.py`
  - `observation.py`, `observation_state.py`
  - `market_observation_state.py`
  - `risk_bounds.py`, `risk_state.py`
  - `economics.py`, `ladder_issuance.py`
  - `p6_stage.py`, `p6_state.py`
  - `pipeline_coupling.py`, `pass_report_ext.py`
  - `level_state.py`
  - `__init__.py`
- `core/serialization/`
- `core/event_log/`
- All tests except those that are Hyperliquid-endpoint-specific (there should be none — the tests use MockVenue-style markers, not real venue calls).

#### Step 3.2 — Strip (Hyperliquid-specific; empty or replace)

In the source repo, look for these and **remove or empty**:

- `src/hypergrid/adapters/` — was empty (`__all__ = []`) in the source; leave empty in the new repo unless 7h-5a-ASTER repopulates it.
- `src/hypergrid/operator/` — if it references Hyperliquid concepts, empty it; the operator surface is post-7h.
- Any `research/sources/hyperliquid/` content — **do not delete; move to `research/sources/_legacy_hyperliquid/`** for archival. The new repo's authoritative venue sources go into `research/sources/aster/`.
- Any Hyperliquid-specific references in `runtime/` — if there are none (they were not built yet), no action.
- `research/decisions/OWNER_GATE_*.md` that are venue-specific — move to `research/decisions/_legacy/` unless they're venue-agnostic (most are not venue-specific; they're strategy-semantic).

#### Step 3.3 — Rename the Python package

The package is `hypergrid`. Rename it to `astergrid`.

```powershell
# Rename the directory
Rename-Item -Path src\hypergrid -NewName astergrid
```

Then update all imports:

```powershell
# Update every "from hypergrid." and "import hypergrid" in src/ and tests/
Get-ChildItem -Path src, tests -Recurse -Filter *.py |
  ForEach-Object {
    (Get-Content $_.FullName) -replace 'hypergrid', 'astergrid' |
      Set-Content $_.FullName
  }
```

Then update `pyproject.toml`:

- Package name → `astergrid`
- Package discovery path if it references `hypergrid`
- Any other reference to `hypergrid`

Then update any test that references the package name.

**Do NOT touch the SHA-256 of `Strategy.md`** (it doesn't contain the package name, but verify after — `Get-FileHash Strategy.md`).

**Exit criterion:** `python -m pytest -q` still passes with the expected count (the rename is content-only; behavior identical).

#### Step 3.4 — Create the migration artifact

Create `research/migration/MIGRATION.md` recording:

- Source: `github.com/avangardistic/hypergrid` at commit `<quote>`.
- Target: `github.com/avangardistic/AsterGrid`.
- Reason: Hyperliquid is one-way only; the strategy requires hedge mode (three anchors: §2 BU/SL both live; §11.3 mirroring; §11.1 ExposureDelta per-side).
- Decision: migrate to **ASTER DEX** (hedge-mode-first; API-settable dual-side; perp model ≈ HL; HMAC signing).
- Rename: package `hypergrid` → `astergrid`; repo `hypergrid` → `AsterGrid`.
- Full phase history table (see §5).
- What stays venue-agnostic (~80%): Basket/Generation/Cycle/Level, Evolution, cycle lifecycle, geometry, sizing, economics, risk bounds, P0–P6, determinism, event log, tests.
- What changes for ASTER: `STR-0200`, `DECISION-002`, `§6.2`, `§6.3`, `STR-0224`, `§10`, `§13.4`, plus a new startup assertion (`assert_hedge_mode`).
- Non-goals of this migration: strategy semantics unchanged (except the ST-08 two-sided interpretation, which is a **separate Owner Gate** — see §4 below).

---

### Part 4 — Owner Gate G-1 (do NOT skip)

Before any ASTER-specific code, the Owner must answer **G-1**. This is a **semantic** decision about ST-08 (`ActualExposureState`).

#### 4.1 The finding (from the pre-flight verdict)

Under Hyperliquid's one-way model, `ActualExposureState.value` was the signed net position. Under ASTER's hedge model, LONG and SHORT can coexist — the net alone hides both legs. The strategy's `ExposureDelta` (§11.1) is defined **per side**; the one-sided form cannot represent `actual_long ≠ 0` and `actual_short ≠ 0` simultaneously.

**However**, the pre-flight found that a two-sided ST-08 has a **cascade** into three coupled components:

- `P1ExposureMarkers.net_position: Decimal` (`hedge_state.py`)
- `compute_actual_exposure(*, net_position) -> Decimal` (`exposure.py` — an identity on the net)
- `build_exposure_singletons(...)` (`hedge.py`) → `ActualExposureState(actual, "clearinghouseState")` and `ExposureDeltaState(actual_value=actual)`

Making ST-08 two-sided **requires** touching all four, plus the `source` field's hard-reject of `"clearinghouseState"`-only in both `AccountEquityState` and `ActualExposureState`. That is a **much bigger change** than a phase-scoped edit.

#### 4.2 The gate (three options)

Draft `research/decisions/OWNER_GATE_ASTER_001.md` (Persian, self-contained, with the format used in the source repo's `OWNER_GATE_*.md` files), asking the Owner to choose:

- **G-1 = A-full:** two-sided ST-08 as a **complete per-side pipeline** — `P1ExposureMarkers` per-side, `compute_actual_exposure` per-side, `build_exposure_singletons` per-side, `ExposureDeltaState` per-side, plus relaxed `source` validation on `AccountEquityState` and `ActualExposureState`. Cascade surface: `exposure_state.py`, `exposure.py`, `hedge.py`, `hedge_state.py`, plus ~10 test files. **Delivers the actual per-side progression gate.**
- **G-1 = A-lite:** ST-08 stores two-sided values now, but the `P1ExposureMarkers`/`compute`/`build` path keeps folding to net. **Does NOT deliver the per-side gate; it just records both sides.** Cheaper, but semantically incomplete for §11.1.
- **G-1 = B:** ST-08 stays `value: Decimal` (net); the `source` string records that the fold was done (`"asterdex:... (folded to net)"`). **Defers per-side entirely** — a separate Owner Gate is required before §11.1 can gate per-side.

**Recommendation (do NOT present as binding):** **A-full**, because §11.1 is per-side by construction; the net was only faithful under one-way. But the cost is real (the 4-file cascade + 10 test files), so this is genuinely the Owner's call.

**Exit criterion:** the gate file exists; the phase does **not** proceed to ASTER-specific code until the Owner answers.

---

### Part 5 — Phase history (for the migration record)

Copy this table verbatim into `research/migration/MIGRATION.md`:

| Phase | Commit | Deliverable |
|---|---|---|
| 0–6c | various | design + research (no runtime code) |
| 7a | `2e886f0` | scaffolding (pyproject, config, logging) |
| 7b | `0219b26` | event model + append-only log + canonical JSON |
| 7c | `048548f` | state + pure fold |
| 7d | `d51fb21` | P0–P6 skeleton + P2/P3/P4 (locks + precedence) |
| 7e | `141f4e1` | §4 Evolution trigger + ST-15 successor lock |
| 7f | `c2ad43f` | §5 Cycle lifecycle + reference capture + non-overlap |
| 7g-1 | `6ee967d` | §7.1 geometry + §7.2 protection locking + ST-04 |
| 7g-2 | `c916a71` | §7.3 sizing + caps + D-14 helpers |
| 7g-3a | (merged) | §11.1 exposure derivatives + ST-07/08/09 |
| 7g-3b | (merged) | §11.2/§11.3 hedge + mirroring + ST-17/19 |
| 7h-1 | (merged) | P0 real + P1 real + ST-04 completion |
| 7h-2 | `a8c2d00` | §8 arming gates + ST-05 + ST-12 |
| 7h-3 | `7489848` | §9 submission + remainder + emergency + skip + cancel selector |
| 7h-4a | `0d6748f` | §12.1 bounds + three-layer breach + ST-17/20/21/22 |
| 7h-4b-1 | `e36ff02` | §10 economics + §5.2 step-8 ladder issuance |
| cleanup ruff | `43e3170` | ruff-format on 9 pre-existing files |
| 7h-4b-2 | `6a854c5` | P6-real + coupling + 3-tuple + PassReport sub-decisions |
| **7h-5a-HL** | **abandoned** | Hyperliquid venue port — venue is one-way only |
| **7h-5a-ASTER** | **this phase** | ASTER venue port (see §6) |

---

### Part 6 — Phase 7h-5a-ASTER (venue adapter only)

**Scope (post-pre-flight verdict):** the `VenuePort` interface + deterministic `MockVenue` + hedge-mode startup assertion + command sink. **No engine change. No ST-08 semantic change. No `exposure.py`/`hedge.py`/`hedge_state.py`/`exposure_state.py` edit.**

The two-sided `ActualExposureState` (ST-08) is deferred to the phase after the Owner answers G-1.

#### 6.1 Base facts (verified from official ASTER docs)

- **Base URL:** `https://fapi.asterdex.com`
- **Hedge mode endpoints:**
  - `GET /fapi/v1/positionSide/dual` (weight 30) → `{"dualSidePosition": true|false}`
  - `POST /fapi/v1/positionSide/dual` (weight 1), body `{"dualSidePosition": "true"}` → **affects every symbol**
- **Positions:** `GET /fapi/v2/positionRisk` (weight 5) — per-symbol, per-`positionSide` rows.
- **Account:** `GET /fapi/v4/account` — equity, positions, margin summary.
- **Orders:** `POST /fapi/v1/order` — **`positionSide` is required** in hedge mode (`{BOTH, LONG, SHORT}`). `side ∈ {BUY, SELL}`.
- **TIF:** `{GTC, IOC, FOK, GTX}` (GTX = post-only).
- **Signing:** HMAC-SHA256.
- **Auth header:** the exact header name is **UNCONFIRMED** — do not assume `X-MBX-APIKEY` (Binance-ism). Verify at pre-flight or 5b.
- **Wire field naming:** ASTER uses camelCase on the wire (`positionAmt`, `unRealizedProfit`). Do **not** claim snake_case as "VERBATIM field names".

#### 6.2 Deliverables

**New files (all in `src/astergrid/adapters/`):**

- `venue_port.py` — the `VenuePort` Protocol (sync, consistent with `EventLogPort`), `PositionSide` StrEnum (`{BOTH, LONG, SHORT}`), `DualSidePosition`, `PositionRow`, `CommandReceipt`, `VenueReadError`, `VenueSubmitError`, `HedgeModeError`. Read methods: `read_dual_side_position`, `read_meta`, `read_position_risk`, `read_account_equity`, `read_mark_price`, `read_user_fills`, `read_order_status`. Submit methods: `submit_order`, `cancel_order`, `modify_order` — **all take `observed: ObservedMeta` and (for submits) `position_side: PositionSide` and `symbol: str`**.
- `mock_venue.py` — deterministic `MockVenue` driven by `MockVenueScript`; missing read key → `VenueReadError`; unscripted submit → `MockSubmitNotScriptedError`. No clock, no random, no `hashlib`.
- `hedge_mode_assert.py` — `assert_hedge_mode(*, port, read_at_ts) -> HedgeModeVerdict`. **Read-only in 5a**; the write (`POST .../dual`) is 5b's, gated by Owner. Returns a verdict; does not raise.
- `command_sink.py` — `SinkReceipt`, `consume_commands(*, commands: tuple[tuple[CommandEvent, PositionSide | None], ...], observed: ObservedMeta) -> tuple[SinkReceipt, ...]`. Deterministic from `ObservedMeta`.
- `venue_mapping.py` — **minimal mapping only for targets that exist and are unchanged**: `map_account_equity` → `AccountEquityState` (ST-17), `map_mark_price_to_market_observation` → `MarketObservationState` (ST-19). **No `ActualExposureState` mapping in this phase** — that is deferred to the post-G-1 phase. **No `MarketDepth` mapping** (deferred with named target: ASTER `GET /fapi/v1/depth`).

**Pre-authorized edit:**
- `src/astergrid/adapters/__init__.py` — populate `__all__` and module-level imports (isort order) for the public surface.

**No other edit.** No `state.py`, no `pass_engine.py`, no `exposure*.py`, no `hedge*.py`, no `risk_state.py`, no `core/events/*`, no `reason_codes.py`, no `markers.py`, no `pyproject.toml`.

**New tests:** `tests/test_venue_port_aster.py`, `tests/test_mock_venue_aster.py`, `tests/test_command_sink_aster.py`, `tests/test_hedge_mode_assert.py`, `tests/test_venue_mapping_aster.py`.

#### 6.3 Rules for this phase

- Every source-string literal (`"asterdex:/fapi/v1/positionSide/dual"`, etc.) is **COINED** — quote the actual endpoint path verbatim from the ASTER docs.
- `PositionSide` values are **VERBATIM** from ASTER's positionSide enum.
- Submit methods require `observed: ObservedMeta` (7h-3 precedent) — **do not omit**.
- `read_user_fills` returns a tuple of the frozen `FillEvent` (from `core/events/kinds.py`) with **exact-match** `client_order_id` semantics — **no prefix joins**.
- `read_user_fills` takes no `since_log_seq` param (the source repo dropped it in a prior pre-flight).
- `CommandReceipt.accepted_at_ts` is caller-supplied via `ObservedMeta` — no clock sampling.
- `PositionRow.position_side` is `{LONG, SHORT}` only on the position path; **`BOTH` appears only on the order path** (as required by ASTER's order endpoint).
- `MarketObservationState` has **only `mark_price`** — no `read_at_ts` field. Do not pass one.
- D16 structural test: no network-module imports (`httpx`, `websockets`, `requests`, `aiohttp`, `socket`) anywhere in `adapters/` in 5a.

#### 6.4 Non-goals (explicit)

- No real ASTER client (REST/WS) — that is 5b.
- No HMAC signing — 5b.
- No rate-limit governor — 5b.
- No `PassRunner` loop — 5c.
- No `ActualExposureState` two-sided change — post-G-1.
- No other `State` slot edit.
- No modification of `Strategy.md`.
- No `prompt.md` reference (it is Hyperliquid-era workflow; the source repo retains it as history, but the AsterGrid workflow is governed by this migration + the present prompt).

#### 6.5 STOPs (narrow, function-level only)

- **S-0** — G-1 not yet answered: this phase proceeds only with the adapter-only scope above; if the Owner later requests A-full before this phase starts, re-scope.
- **S-1** — `adapters/__init__.py` state differs from `__init__`-only with `__all__ = []`.
- **S-2** — any ASTER endpoint cited in §6.1 is absent or its shape differs.
- **S-3** — any existing test file is broken by the rename (there should be none; the rename is content-only).
- **S-4** — any need to edit a file outside the Part 6.2 pre-authorized list.
- **Global abort rule:** any E1 breakage (suite, mypy, ruff, structural tests), any need to edit a frozen/untouched module outside the pre-authorized list, or any genuinely unresolvable question → STOP with the failing artifact + citations + the exact function-level question.

#### 6.6 Report (per the source repo's `Part G.3` template)

Deliver a report containing:

- True test counts: new per-file + suite total.
- mypy delta vs base (both directions) — grep-based, not asserted from memory.
- ruff check + format evidence.
- D16 structural test result.
- Coined-vocab inventory with anchors.
- STOPs (or none).
- Pre-authorized edits, file-by-file.
- Typed-home inventory: which ST-* each mapping targets + `file:line`.
- The verbatim ASTER endpoint quotes for `positionSide/dual` (GET + POST), `positionRisk`, `order`, and account.

---

### Part 7 — Commit and branch strategy

- **Single commit** on `aster-migration` for the package rename + migration artifact (Steps 3.3 + 3.4).
- **Single commit** for 7h-5a-ASTER on a new branch `claude/7h-5a-aster-venue-port` off `aster-migration`.
- **Do NOT push** without explicit Owner instruction.
- **Do NOT merge** to `main` without Owner cross-check.

---

### Part 8 — Final checklist before you start

- [ ] Source repo cloned to `AsterGrid` local dir.
- [ ] Source provenance recorded (`SOURCE_PROVENANCE.md`).
- [ ] `Strategy.md` SHA-256 verified unchanged.
- [ ] Package renamed (`hypergrid` → `astergrid`); `pytest` count unchanged.
- [ ] Old remote removed; new remote `AsterGrid` set.
- [ ] `aster-migration` branch created.
- [ ] `research/migration/MIGRATION.md` written.
- [ ] `OWNER_GATE_ASTER_001.md` (G-1) drafted in Persian, self-contained.
- [ ] **Stop and wait for Owner's G-1 answer before any ASTER-specific code.**
- [ ] After G-1: proceed to 7h-5a-ASTER per §6.
- [ ] After 7h-5a-ASTER: commit on `claude/7h-5a-aster-venue-port`; do NOT push; produce the report.

---

**End of migration prompt.** Execute Steps 2.1 → 2.4, then Step 3 → Step 4 → stop for G-1. Do not begin Step 6 until the Owner answers G-1.

---

## B. افزودنی به Migration Prompt — Multi-Agent Ground, git check, optional tooling

**متن زیر را در انتهای Migration Prompt (قبل از `End of migration prompt`) درج کنید.**

---

### Part 9 — Multi-agent coordination context

**Multiple AI agents are working on this project concurrently.** At any moment, more than one CLI AI agent may be running against the same `AsterGrid` remote — different agents on different branches, or the same branch at different times.

This is not a bug; it is the working model. But it imposes strict rules that every agent MUST follow:

#### 9.1 — Before touching git, check the ground state

Before any `git` operation that creates, moves, or rewrites history (`commit`, `branch`, `merge`, `rebase`, `reset`, `push --force`, `checkout -b`, `cherry-pick`, `amend`), run and **read**:

```powershell

git status

git branch --all

git log --oneline -10 --all

git remote -v

git rev-parse HEAD

git rev-parse origin/main

```

**Never assume** the branch, HEAD, or remote is what it was when the session started. Another agent may have committed, pushed, switched branches, or created branches since.

#### 9.2 — Never rewrite shared history

- Do not `push --force` to `main`.

- Do not `rebase` or `reset` a branch that has been pushed without explicit Owner authorization.

- Do not `commit --amend` a commit that has been pushed.

- Do not delete remote branches.

If a conflict arises because another agent pushed to the same branch: **stop, report, do not resolve silently**.

#### 9.3 — Branch discipline

- Work on a dedicated branch (e.g., `claude/7h-5a-aster-venue-port`).

- Do not commit directly to `main`.

- Do not merge to `main` without Owner cross-check.

- Before creating a new branch, confirm it does not already exist (`git branch --all | Select-String <branch>`).

#### 9.4 — Evidence-first, artifact-first

Because multiple agents share the repo, **artifacts are the ground truth**, not chat context. Every material decision, finding, or change MUST be recorded as a durable file in `research/` (or `research/migration/` for this phase). Another agent reading the repo next session must be able to reconstruct your work from the artifacts alone, without your chat history.

#### 9.5 — Claim hygiene

Every material claim in a report or artifact must carry:

- **source class** (`STRATEGY_SOURCE`, `VENUE_PRIMARY_SOURCE`, `CODEBASE_SOURCE`, `OBSERVATION`, `ASSUMPTION`, `OWNER_DECISION`, …);

- **anchor** (`file:line`, contract line, or URL + retrieval timestamp);

- **status** (`VERIFIED` / `PARTIALLY_VERIFIED` / `UNVERIFIED` / `CONFLICTED`).

No claim without an anchor. No count without a grep command. No "VERBATIM" without a quote.

---

### Part 10 — Optional tooling (paper-clip, Graphify, Spec-Kit)

If — **and only if** — you judge the tooling materially helps this migration or the AsterGrid program, you may adopt any of the following. **Do not adopt them by default.** Adoption requires an explicit justification recorded in `research/tooling/TOOLING_DECISION.md` (with the standard artifact fields: purpose, alternatives considered, decision, rejected alternatives, risk, reversibility).

#### 10.1 — `paper-clip`

**What it is:** a filesystem/clipboard scratchpad for handing files or excerpts between agents and sessions without pasting them into prompts.

**When it helps:**

- When multiple agents need to exchange large evidence files (e.g., the ASTER docs extracts) without bloating any agent's context.

- When the Owner needs to move artifacts between machines.

**When it does not help:**

- The AsterGrid repo already uses the file system as the durable store. Adding a second scratchpad risks divergence.

- If used, it MUST live **outside** the repo tree (e.g., `%USERPROFILE%\.paper-clip\`) so it never conflicts with git.

**Decision rule:** adopt only if a specific multi-agent handoff in this program cannot be satisfied by `research/` artifacts alone. Otherwise: `NOT_APPLICABLE`, with reason.

#### 10.2 — Graphify

**What it is:** a graph-based spec/architecture visualizer (dependency graph, state-machine graph, entity-relationship extraction).

**When it helps:**

- The AsterGrid program has **many coupled state machines** (Generation/Cycle/Level, exposure triple ST-07/08/09, P1 hedge, P6 arming, hedge-mode). Visualizing them can reduce review cost.

- A graph of the **state-ownership map** (`STATE_OWNERSHIP.md`) as it evolves through the ASTER migration could catch single-owner violations earlier.

**When it does not help:**

- Graphify output is **derived**, never authority. It must not enter the runtime.

- If it generates files inside the repo, they belong under `research/graphs/` (or similar), and **must be regenerable from source** (a `make graph` target or equivalent), never hand-edited.

**Decision rule:** adopt if the Owner asks, or if during the migration a state-ownership or dependency question is repeatedly asked. Otherwise: `NOT_APPLICABLE`, with reason.

#### 10.3 — Spec-Kit

**What it is:** a tool for authoring and validating structured specifications, with traceability from spec → test → code.

**When it helps:**

- AsterGrid already has a **hand-rolled equivalent**: `STRATEGY_CONTRACT.md` (382 STR-*), `STRATEGY_COVERAGE.md`, `TRACEABILITY_MATRIX.md`, `SEMANTIC_AMBIGUITIES.md`, `DECISION_REGISTER.md`, `OWNER_GATE_*.md`, `VALIDATION_PLAN.md`. These have been working well.

- Spec-Kit **might** reduce the maintenance cost of the contract once the ASTER migration changes 8+ STR sections (STR-0200, §6.2, §6.3, STR-0224, §10, §13.4, plus new startup section).

- But migrating a **working** traceability system to a new tool is a heavy move that risks losing provenance — the exact opposite of what the program wants.

**When it does not help:**

- If the existing hand-rolled system is still healthy at the point of adoption, replacing it is **regression risk**, not improvement.

- Any adoption MUST preserve the existing STR-* IDs and their provenance; a "spec-kit from scratch" that renumbers or re-derives requirements is a **defect**, not a migration.

**Decision rule:** adopt only if a specific pain point is documented (e.g., the contract has become unmaintainable after the ASTER delta), and only if the migration path preserves STR-* stability. Otherwise: `NOT_APPLICABLE`, with reason.

---

### Part 11 — What to do if you (the agent) are unsure

If at any point you cannot decide whether to adopt a tool, split a phase, edit a file, or interpret a piece of the strategy:

1. **Do not guess.**

2. Record the uncertainty as an entry in `research/migration/OPEN_MIGRATION_QUESTIONS.md` (or `research/decisions/OPEN_QUESTIONS.md` if the source repo has one).

3. If the uncertainty blocks a step, **stop** at the last completed step and report.

4. If the uncertainty does not block progress, continue with the parts that are unambiguous, and leave the blocked parts flagged with a `TODO: pending Owner/Reviewer` marker.

**Fail-closed is the default. Silence is never a decision.**

---

### Part 12 — Multi-agent ownership model (informal)

The working model for this program, recorded so every agent understands its scope:

- **Owner (human):** holds semantic authority — strategy interpretation, safety policy, wallet/signing boundary, Live authorization. Answers Owner Gates.

- **Architect (one specific agent):** drafts phases, writes prompts, does second-eye review of reports.

- **Reviewer (one specific agent):** pre-flights drafts against the tree, gates merges, runs independent cross-checks on reports.

- **Executor (whichever agent is running Claude Code against the repo):** executes the prompt on a dedicated branch, produces artifacts and a report.

No agent may fill more than one of these roles within a single artifact. Specifically:

- The **Executor's report** must be cross-checked by the **Reviewer**, not by the **Architect**.

- The **Architect's draft** must be pre-flighted by the **Reviewer**, not self-approved.

- **Owner Gates** must be answered by the **Owner**, never inferred by any agent.

**End of migration prompt (with Parts 9–12 appended).**
