# AsterGrid — Handoff Summary for a New Session

**Filename suggestion for your local copy:** `ASTERGRID_HANDOFF.md`
**Purpose:** You're opening a fresh session on a new repository to build the ASTER-adapted grid bot. This file gives you (and any future Claude Code session) everything needed to pick up cleanly without re-deriving what's already known.

---

## 1. Project context — what exists today

### 1.1 The Hyperliquid source repo (`hypergrid`)

- **Repo:** `github.com/avangardistic/hypergrid` (private)
- **Local path (Windows):** `C:\Users\Avangard\Desktop\hypergrid`
- **Canonical strategy:** `Strategy.md` v2.3-final
  - SHA-256: `085044e72efa75e7dd7e812588d8247c8e60152eecb233bd6969f6545a825e18`
  - 92,686 bytes, 1,368 lines (1-based)
  - **Immutable** — never edited across all phases
- **Program protocol:** `prompt.md` v3.0 (Master Control Prompt) — the operating rulebook
- **Framework:** 382 STR-* requirements, 23 DECISIONs, 21 OWNER_GATEs
- **Test suite:** 544 tests passing at latest merge (`6a854c5`)
- **Code phases completed:** Phase 0 → Phase 7h-4b-2 (see §3)

### 1.2 The blocker that forces this migration

**Hyperliquid is one-way only.** It does not support hedge mode. The strategy **requires** hedge mode (two-sided per market). Full reasoning:

1. **Groups BU/SL are both live** (Strategy §2) — the grid is two-sided; both positions must be open simultaneously.
2. **Mirroring** (§11.3) fires an "opposite hedge leg" while the original leg stays open. On one-way, the opposite leg just nets away the primary position — the grid-profit mechanism is destroyed.
3. **Exposure accounting collapses.** `ExpectedExposure` is a sum over verified levels; `ActualExposure` on HL is only the signed net (`szi`). With both sides filled, `ExposureDelta ≠ 0` **structurally** — and since grid progression is hard-gated on the tolerance (§11.1), the bot effectively locks or loops in Hedge Recovery.

### 1.3 Migration candidates evaluated

| Venue | Hedge mode | Maker fee | Taker fee | Model | Session | Regulation (EU) | Verdict |
|---|---|---|---|---|---|---|---|
| **ASTER DEX** | ✅ API (`positionSide/dual`) | 0.5 bps | 4 bps | perp | 24/7 | ❌ unregulated DEX | **Chosen (first venue)** |
| **Binance/Bybit/OKX Futures** | ✅ | 2 bps | 5 bps | perp | 24/7 | ⚠️ MiCA-ish | Alternative |
| **Forex broker (ECN, cTrader/MT5)** | ✅ | ~0 | ~1.5 bps | FX/CFD | 24/5 + weekend gap | ✅ ESMA/CySEC | Second venue (later) |

**Decision:** migrate to **ASTER DEX** first.

**Rationale:**
- ASTER's perp model ≈ Hyperliquid's (funding, mark price, margin) → minimal core changes.
- ASTER hedge-mode is settable via API (`POST /fapi/v1/positionSide/dual`, `{"dualSidePosition": "true"}`, **affects every symbol**) — this enables a fail-closed startup assertion, which forex may not.
- ASTER is deliberately designed for grid bots / APIs.
- HMAC signing is simpler than HL's secp256k1 (stdlib only).
- ASTER fees, with maker-heavy discipline (which the strategy already has — §8/§10 Alo prefer), are competitive.

**Forex remains a second venue** for later (diversification + calibration data from Dukascopy), but is a bigger rewrite (session hours, weekend gap, swap vs funding, digits/lot/contract size, mid vs mark).

---

## 2. What needs to change in the strategy (contract delta)

This is the **conceptual delta** — not the final contract text yet.

### 2.1 Three strategic anchors that break on one-way

- `STR-0200` — `ActualExposure` from "net position" → **two-sided**: `(actual_long, actual_short, actual_net)`.
- `DECISION-002` — source of truth from `clearinghouseState` → **ASTER account/position endpoint**.
- `§11.1` — `ExposureDelta` computed **per side**, not just net.

### 2.2 Full delta table (informal — to be formalized)

| STR / section | Current (Hyperliquid) | ASTER |
|---|---|---|
| `STR-0200` | net signed `szi` | `actual_long` / `actual_short` / `actual_net` |
| `DECISION-002` | `clearinghouseState` | ASTER `/fapi/v2/positionRisk` (authoritative) |
| `§6.2` | HL mechanisms | ASTER mechanisms (HMAC signing, `clientOrderId`) |
| `§6.3` | HL precision (5 sig figs, szDecimals) | ASTER precision (`tickSize`, `stepSize`, `minNotional`) |
| `STR-0224` | CapitalBase from `marginSummary.accountValue` | ASTER account equity |
| `§10` | funding 8h (HL formula) | ASTER funding 8h (peer-to-peer) |
| `§13.4` | close HL position | close LONG and SHORT separately |
| **New: §startup** | — | `assert_hedge_mode` fail-closed gate |
| **New: §6.4** (forex only, later) | — | session hours, weekend gap, gap detector |

---

## 3. Phase history in the Hyperliquid repo (for reference)

| Phase | Commit | Deliverable |
|---|---|---|
| 0–6c | several | design + research (no runtime code) |
| 7a | `2e886f0` | scaffolding (pyproject, config, logging) |
| 7b | `0219b26` | event model + append-only log + canonical JSON |
| 7c | `048548f` | state + pure fold |
| 7d | `d51fb21` | P0–P6 skeleton + P2/P3/P4 (locks + precedence) |
| 7e | `141f4e1` | §4 Evolution trigger + ST-15 successor lock |
| 7f | `c2ad43f` | §5 Cycle lifecycle + reference capture + non-overlap |
| 7g-1 | `6ee967d` | §7.1 geometry + §7.2 protection locking + ST-04 |
| 7g-2 | `c916a71` | §7.3 sizing + caps + D-14 helpers |
| 7g-3a | — | §11.1 exposure derivatives + ST-07/08/09 |
| 7g-3b | — | §11.2/§11.3 hedge + mirroring + ST-17/19 |
| 7h-1 | — | P0 real + P1 real + ST-04 completion |
| 7h-2 | `a8c2d00` | §8 arming gates + ST-05 + ST-12 |
| 7h-3 | `7489848` | §9 submission + remainder + emergency + skip + cancel selector |
| 7h-4a | `0d6748f` | §12.1 bounds + three-layer breach + ST-17/20/21/22 |
| 7h-4b-1 | `e36ff02` | §10 economics + §5.2 step-8 ladder issuance |
| cleanup ruff | `43e3170` | ruff-format on 9 pre-existing files |
| 7h-4b-2 | `6a854c5` | P6-real + coupling + 3-tuple + PassReport sub-decisions |

**Only remaining pre-migration code:**
- `7h-5a-hyperliquid` (was drafted but **abandoned** — venue is wrong).
- `7h-5b` real HL client (abandoned).
- `7h-5c` `PassRunner` loop (abandoned for HL; will be re-homed for ASTER).

**What stays venue-agnostic** (≈80% of the code):
- Basket / Generation / Cycle / Level
- Evolution, successor lock, dominance
- Cycle lifecycle, reference capture, non-overlap
- Grid geometry, protection locking, sizing, caps
- All economics: `NetExpectedEdge`, `GGE`, floors
- All risk bounds, breach ladder, closure
- P0–P6 pass engine, deterministic core, canonical JSON
- Event log, hash chain, replay
- Full test philosophy (differential, invariant, exhaustive bounded)

---

## 4. ASTER technical facts (verified from docs)

### 4.1 Hedge-mode endpoints

```
GET  /fapi/v1/positionSide/dual      Weight: 30   →  {"dualSidePosition": true|false}
POST /fapi/v1/positionSide/dual      Weight: 1    body {"dualSidePosition": "true"}
                                                   →  {"code": 200, "msg": "success"}
                                                   AFFECTS EVERY SYMBOL.
```

Implication: **one POST at startup locks hedge mode globally**. A mismatch invalidates every position across the account → **fail-closed is mandatory**.

### 4.2 Position and order endpoints

```
GET  /fapi/v2/positionRisk           →  per-symbol, per-positionSide positions
POST /fapi/v3/order                  →  positionSide is REQUIRED in hedge mode
                                        ∈ {"LONG", "SHORT"}
TIF ∈ {"GTC", "IOC", "FOK", "GTX"}   (GTX = post-only)
```

### 4.3 Signing

- HMAC-SHA256 over the query string.
- Header `X-MBX-APIKEY`.
- **No secp256k1** — stdlib Python only (`hmac`, `hashlib`).

### 4.4 Base URL and testnet

- Mainnet: `https://fapi.asterdex.com`
- **Testnet availability: TO BE VERIFIED in Phase 0 grounding** (crucial).

### 4.5 Fees (as of last check)

- Maker: **0.5 bps** (0.005%)
- Taker: **4 bps** (0.04%)
- Funding: 8-hour, peer-to-peer

---

## 5. Migration plan — 4 phases (adopted from reviewer's plan)

### Phase 0 — Grounding (days)

**Goal:** read ASTER docs, verify all facts above are current.

**Verify:**
- ✅ `positionSide/dual` API set/get works
- ✅ per-symbol `positionRisk` returns LONG and SHORT rows
- ✅ `positionSide` required on orders in hedge mode
- ✅ TIF set
- ✅ precision filters (`tickSize`, `stepSize`, `minNotional`)
- ✅ rate limits
- ✅ **testnet availability** (URL + whether hedge mode is settable there)
- ✅ HMAC signing recipe
- ✅ funding formula and cadence
- ✅ Python SDK if any

**Deliverable:** a `research/aster/` folder with verbatim docs, hashes, timestamps.

### Phase 1 — Contract delta (document, not code)

**Goal:** rewrite only what changes, with citations.

**Deliverables:**
- `STR-0200` → two-sided `ActualExposureState`
- `DECISION-002` → ASTER position endpoint
- `§6.2` → ASTER mechanisms
- `§6.3` → ASTER precision
- `§10` → ASTER funding
- `§13.4` → per-side closure
- **New startup section** → `assert_hedge_mode`

### Phase 2 — Engine delta (medium, bounded)

**Code changes:**
- `risk_state`: two-sided `ActualExposureState`
- `§11.1` `ExposureDelta`: per-side
- `MaxExposureImbalance` per-side wiring (was not possible on one-way)
- `§13.4` closure: separate LONG and SHORT
- **New startup assertion** in `adapters/hedge_mode_assert.py`
- **No change** to: TWAP, Fillability Analyzer, cost analyzer, most of the pass engine

### Phase 3 — Adapter rewrite

**New adapter (replaces the abandoned 7h-5a-HL):**
- `venue_port.py` — hedge-aware, `PositionSide` enum
- `mock_venue.py` — deterministic, two-sided
- `venue_mapping.py` — read→marker, including two-sided ST-08
- `command_sink.py` — with `PositionSide` on submits
- `hedge_mode_assert.py` — startup gate
- HMAC signing (stdlib)
- REST + WS client
- `clientOrderId` (idempotency)

### Phase 4 — Test + gray-launch

- MockVenue two-sided tests
- E3 two-sided integration
- Testnet paper trading
- Mainnet small size
- Then scale

---

## 6. Working notes for the new session

### 6.1 Process discipline (carried over)

The Hyperliquid repo ran under a strict process that worked well:
1. **Draft** (from the architect) with **pinned readings**, VERBATIM evidence, `file:line` citations, no paraphrase-as-VERBATIM.
2. **Pre-flight** (by a reviewer) — re-verify every path, every count, every schema claim against the current tree before the draft runs.
3. **Execution** by Claude Code on a branch.
4. **Report** back with true counts, mypy/ruff evidence, coined-vocab inventory.
5. **Independent cross-check** by the reviewer.
6. **Owner Gate** for any genuinely semantic decision.

**Adopted rules that must carry over:**
- No `float` in core. `Decimal` for money; `int` for counts/seconds.
- Every `log_sequence` / `monotonic_counter` is allocated by the log, not the caller.
- No `logging` in `core/`.
- Canonical JSON with `sort_keys=True`; `Decimal` as `{"__decimal__": "<string>"}`.
- Frozen dataclasses, slots.
- Fail-closed on any ambiguity.
- **Cite-or-coin**: every new enum member, every new field, every new comparator gets a `VERBATIM` or `COINED` marker with an anchor.
- **No counts asserted** beyond what the contract states (382 STR / 23 DECISIONs).
- Every count claim cites its grep command.

### 6.2 The renamed repository

**New repo:** `github.com/avangardistic/AsterGrid` (private).

**Clone-and-replace procedure:**
```powershell
# Clone the old repo (source of truth for code history)
git clone https://github.com/avangardistic/hypergrid.git AsterGrid
cd AsterGrid

# Optionally rename the remote
git remote remove origin
git remote add origin https://github.com/avangardistic/AsterGrid.git

# Create the AsterGrid branch off main (preserves history)
git checkout -b aster-migration
```

**Do NOT rewrite the git history.** The Hyperliquid phases are the reference for what was built and why. Preserve them. The migration is additive: ASTER-specific files live alongside, and the old `adapters/` (HL-oriented) is either replaced in-place or moved to `adapters/_legacy_hyperliquid/`.

### 6.3 The three critical Owner Gates to answer before code

1. **G-1 (already drafted)** — ST-08: two-sided `ActualExposureState` vs folded-to-net. **Recommendation: two-sided.**
2. **G-2 (to draft)** — source-of-truth doctrine: is ASTER's `/fapi/v2/positionRisk` the sole authority (like HL's `clearinghouseState` was)? **Recommendation: yes.**
3. **G-3 (to draft)** — startup hedge-mode: should the client **write** `POST /fapi/v1/positionSide/dual {"dualSidePosition": "true"}` on boot, or **refuse and abort** if not already true? **Recommendation: write-then-verify (idempotent), with abort if still false.**

---

## 7. What to say at the start of the new session

Copy this to a new Claude Code session opened in `C:\Users\Avangard\Desktop\AsterGrid` (or wherever the clone lives):

> **New session. Repo migrated from `hypergrid` to `AsterGrid`. The canonical strategy is `Strategy.md` (unchanged). The canonical protocol is `prompt.md`. The Hyperliquid venue is abandoned — one-way only, incompatible with hedge mode. We are migrating to ASTER DEX.**
>
> **Read `ASTERGRID_HANDOFF.md` at repo root first, then `Strategy.md` header, then `prompt.md`. Do not start coding. Do not modify `Strategy.md`. Do not open any Owner Gate on your own — I (the Owner) will answer the three pre-listed gates (G-1, G-2, G-3) first.**
>
> **Your first task is Phase 0 — Grounding: fetch and quote the ASTER endpoints listed in §4 of the handoff, verify all facts, produce a `research/aster/SOURCE_MANIFEST.md` and `research/aster/VENUE_EVIDENCE.md` with verbatim excerpts and hashes. No architecture decisions. No code. Just grounding.**

---

## 8. Open questions to resolve in the new session

- **Testnet availability** on ASTER — critical for Phase 4.
- **Python SDK** — does ASTER publish one? If not, hand-rolled REST client.
- **WebSocket** — order updates, fills, mark price, L2 book.
- **Rate limits** — exact weight table.
- **`clientOrderId`** semantics — idempotency guarantee? dedup on resubmit?
- **Precision model** — `tickSize`, `stepSize`, `minNotional` per symbol.
- **Funding formula** — is it identical to Binance's (since the API shape is)?
- **Account/margin structure** — cross vs isolated; margin mode pin.
- **Hedge-mode edge cases** — reduce-only orders, position-side mismatch on cancel, partial close semantics.
- **Fees** — tier structure, whether staking changes tiers.

---

**End of handoff.** Save this as `ASTERGRID_HANDOFF.md` at the root of the new repo before starting the new session. The full Hyperliquid `hypergrid` repo remains as the reference for all venue-agnostic logic.

---

## Postscript — one small correction to the previous draft

The previous draft I sent (titled `7h-5a-ASTER`) assumed the repo was still `hypergrid`. With the repo renamed to `AsterGrid` and cloned fresh, all path references in that draft remain valid **relative to the new repo root** — nothing about the file paths changes. But you should treat that draft as a **reference** for the shape of the ASTER adapter, not as a prompt to be sent verbatim to Claude Code, because:

1. The base hash will differ (the new repo starts from the AsterGrid clone).
2. The Owner Gates G-1, G-2, G-3 need to be answered first.
3. Phase 0 grounding must complete before Phase 1 contract delta.

The right sequence is: **handoff → new session → Phase 0 grounding → Owner Gates → Phase 1 contract delta → Phase 2 engine delta → Phase 3 adapter (the 7h-5a-ASTER draft, re-based) → Phase 4 tests.**

Good luck with the new repo.