# AsterGrid — Contract Delta (Phase 1, document-only)

**Status:** DRAFT — Owner answers for G-1..G-4, OPEN-2, OPEN-3 recorded 2026-10-01 (rev 2); formal ACCEPT of the whole document still pending. No code. `Strategy.md` is not modified (and is not present in this tree).
**Date:** 2026-10-01
**Supersedes (for the ASTER venue):** the Hyperliquid-specific readings of STR-0200, DECISION-002, §11.1, §6.2, §6.3, §10, §13.4.
**Evidence:** `research/aster/SOURCE_MANIFEST.md` (facts cited as **F#**).

## 0. Provenance and honesty limits

| Marker | Meaning |
|---|---|
| **VERBATIM-F#** | Taken from the ASTER docs; anchor in the manifest. |
| **HANDOFF** | Carried from `ASTERGRID_HANDOFF.md` / the owner's session summary; **not re-verified here** because `Strategy.md`, `prompt.md`, `src/` and the hypergrid history are **not in this repo**. |
| **COINED** | New in this document; needs Owner ACCEPT. Every COINED item has a rationale. |
| **OPEN** | Cannot be decided from available evidence. |

Consequences of the missing tree:
1. Every STR/DECISION/§ number and file:line below is **HANDOFF** until the contract is re-checked in a tree that has `Strategy.md` (SHA `085044e7…`, per handoff).
2. New requirement IDs below use the provisional prefix `ASTR-` so they cannot collide with the 382 STR. No count is asserted; recompute with the grep command in §8 after merge into the Strategy-bearing tree.

## 1. Owner decisions recorded

| Gate | Decision (owner, 2026-10-01, via session) | Contract effect |
|---|---|---|
| **G-1** | **Two-sided** ST-08 (not net-fold). | §3 |
| **G-2** | ASTER's position endpoint is the **sole authority** for actual exposure (as `clearinghouseState` was). | §4 |
| **G-3** | **Write-then-verify** hedge mode at startup; abort if still not true. | §5 |
| **G-4** | **V3** (API-wallet / EIP-712 signing). V1-HMAC is not used. | §6 |
| **OPEN-2** | Tolerance applies **per side** (one tolerance value evaluated on each side; no new parameter introduced). | §3.3 |
| **OPEN-3** | Margin mode **cross**; **Multi-Assets mode** on. (Owner wording: "margin mode cross, Multi-Assets mode".) | §5.3, §9 |

## 2. Findings that change earlier assumptions

These came from re-reading the vendor docs on 2026-10-01 and bear on the handoff:

1. **V1 HMAC keys can no longer be created.** *"Starting from March 25, 2026, V1 new API Key creation is no longer supported. Existing API Keys will continue to work."* (**F1**). The handoff's "HMAC, stdlib only" premise holds only if the owner already holds a pre-March-2026 V1 key.
2. **V3 has the same hedge-mode surface** (`/fapi/v3/positionSide/dual`, `/fapi/v3/positionRisk`, `/fapi/v3/order`) (**F5, F6, F10**) and **a documented testnet**; V1 has none documented (**F13**). Hence the earlier "order is `/fapi/v1/order`, not v3" correction is correct *for V1 only*. **Owner chose V3 (G-4), so the V3 endpoint set binds**; every `/fapi/v1|v2|v4` path and the HMAC / `X-MBX-APIKEY` recipe in the handoff are legacy and not to be implemented.
3. **`reduceOnly` is forbidden in Hedge Mode** (**F7**). Any strategy text that closes/reduces a leg via a reduce-only flag has no ASTER equivalent; closing a leg = order on the opposite `side` with that leg's `positionSide` (§7).
4. **`newClientOrderId` is unique among *open* orders only**, ≤ 36 chars, restricted charset (**F9**). It is **not** a venue-side idempotency guarantee after an order closes (§7).
5. **SHORT `positionAmt` is negative** in both the V1 and V3 hedge samples (**F10, F16**), so per-side magnitudes need an explicit sign rule (§3.2).

## 3. G-1 — Two-sided exposure (replaces STR-0200 reading; HANDOFF anchor)

### 3.1 ASTR-001 — `ActualExposure` is a per-side triple (COINED; replaces "net signed `szi`")

Per market (symbol):

```
actual_long  : Decimal  >= 0     # LONG leg size, base units, magnitude
actual_short : Decimal  >= 0     # SHORT leg size, base units, magnitude
actual_net   : Decimal           # DERIVED = actual_long - actual_short; never independently sourced
```

- `actual_net` is a derived invariant, not a third observation. A state whose `actual_net != actual_long - actual_short` is rejected at construction (fail-closed). *Rationale:* avoids a net that disagrees with its legs (the exact desync the net-only model could not detect).
- No `float`; `Decimal` from the wire strings (e.g. `"20.000"`).

### 3.2 ASTR-002 — Sign normalisation at the adapter boundary (COINED)

Wire `positionAmt` for the SHORT leg is negative (**F10**). The adapter maps:

| Wire row | Mapping | Fail-closed rejection |
|---|---|---|
| `positionSide=LONG`, `positionAmt = a` | `actual_long = a` | `a < 0` |
| `positionSide=SHORT`, `positionAmt = b` | `actual_short = abs(b)` | `b > 0` |
| `positionSide=BOTH` | — | **any** `BOTH` row in a hedge-mode read ⇒ read is invalid (account is not in hedge mode, or the venue contradicts itself) |
| missing LONG or SHORT row for a tracked symbol | treat as `0` **only if** the venue is documented to omit zero rows; otherwise reject | **OPEN-1** (sign convention is now confirmed on V3 — **F16**; whether a flat leg's row is omitted is still unconfirmed; both samples return both rows) |

The sign rule lives in the adapter; core only ever sees non-negative magnitudes. (Core has no ASTER knowledge.)

### 3.3 ASTR-003 — The coupled triple ST-07/08/09 goes per-side (COINED; HANDOFF: ST-07 expected, ST-08 actual, ST-09 delta)

```
expected_long,  expected_short            # sum over verified levels, per side
actual_long,    actual_short              # §3.1
delta_long  = expected_long  - actual_long
delta_short = expected_short - actual_short
delta_net   = (expected_long - expected_short) - actual_net     # retained, derived
```

**Gate (§11.1 replacement):** grid progression is permitted only if
`|delta_long| ≤ tol_long` **and** `|delta_short| ≤ tol_short`. (`delta_net` is informational and logged; it is implied but not sufficient.)

**ASTR-004 — Non-vacuity requirement (COINED, addresses pre-flight C4).** The per-side fields MUST be *read* by the gate, not merely stored. Acceptance test (Phase 2): a state with `delta_net == 0` but `delta_long = +x`, `delta_short = +x` (x > tol) **must block** progression; the same state under a net-only gate would pass. If Phase 2 cannot show this test failing against the old gate and passing against the new, the phase has not delivered G-1.

**Tolerance (OWNER_DECISION OPEN-2: per side):** the strategy's existing tolerance symbol is evaluated **on each side** — `tol_long = tol_short = tol`. No new parameter is introduced; if the owner later wants independent per-side values that is a new, separate gate.

### 3.4 ASTR-005 — `MaxExposureImbalance` per side (COINED; handoff: "was not possible on one-way")

Imbalance is computed from `actual_long` vs `actual_short` directly. Exact bound semantics are taken from the existing §12 text (HANDOFF) with the operands changed from net to per-side; no new threshold is introduced.

## 4. G-2 — Source of truth (amends DECISION-002; HANDOFF anchor)

### 4.1 DECISION-002 (amended)

> The authority for actual exposure on the ASTER venue is the venue's **position read** (`GET positionRisk`, V1 `/fapi/v2/…` or V3 `/fapi/v3/…` per G-4). It is the sole source; no value derived from fills, order updates or local accumulation may overwrite it (they may only be *compared* to it, producing a divergence record).

- Push data (`ACCOUNT_UPDATE` on the user stream, **F12**) is a *timeliness hint* that triggers a re-read; it is not authority. *Rationale:* the vendor itself says positionRisk is to be used "with" the stream for accuracy.
- Capital base (STR-0224 reading): from the V3 account endpoint (**F11**). Account is in Multi-Assets mode (OPEN-3), so equity is not a single-asset number; **which field is CapitalBase is OPEN-7** (§9).

### 4.2 ASTR-006 — Source tag is a closed, venue-qualified set (COINED; addresses pre-flight C3)

The hypergrid check hard-rejects any `source != "clearinghouseState"` (HANDOFF). The replacement is a **closed allow-list of exact strings**, one per authoritative endpoint, e.g. `asterdex:v3:positionRisk`, `asterdex:v3:account`. Rules:

- exact-match membership, never prefix/`startswith`;
- the Hyperliquid tag `clearinghouseState` is **not** in the AsterGrid allow-list (HL is out);
- adding a tag requires an amendment to this section.

With G-4 = V3 the strings are: `asterdex:v3:positionRisk` (actual exposure) and `asterdex:v3:accountWithJoinMargin` (account equity; field choice per OPEN-7). The `positionSide/dual` and `multiAssetsMargin` reads are *configuration* reads, not exposure authority, and carry their own tags (`asterdex:v3:positionSide/dual`, `asterdex:v3:multiAssetsMargin`).

## 5. G-3 — Startup hedge-mode gate (new startup section)

### 5.1 ASTR-007 — `assert_hedge_mode` (COINED; fail-closed)

On every process start, **before any order-capable code runs**:

```
1. GET  positionSide/dual                      -> d0
2. if d0.dualSidePosition is the boolean true  -> PASS
3. else POST positionSide/dual {dualSidePosition:"true"}   (string "true", F5)
4. GET  positionSide/dual                      -> d1
5. d1.dualSidePosition is the boolean true     -> PASS   else ABORT
6. any transport error / non-2xx / non-bool / malformed body at any step -> ABORT
```

- **Abort** = no commands issued, a terminal event is logged, process exits non-zero. No retry loop that can eventually "pass" on a partial state.
- Type strictness: GET returns a JSON boolean, POST takes the *string* `"true"` (**F5**); the string `"true"` in a GET reply is a malformed response ⇒ ABORT.
- The POST affects **every symbol on the account** (**F5**). *Consequence recorded for the owner:* the bot must run on a dedicated account/sub-account; flipping the mode can break any other strategy on the same account. (This is a deployment constraint, not an engine one.)
- The venue may reject the POST while positions/orders exist (documented behaviour on the Binance-shaped API; **not confirmed for ASTER** — **OPEN-4**, test on testnet). Whatever the venue says, the gate's response is ABORT; the bot never attempts to flatten positions to make the switch succeed.

### 5.2 ASTR-008 — Re-assertion (COINED)

GET costs weight 30 (**F5**) so it is not run every pass. It re-runs: (a) on startup, (b) after every reconnect/resync, (c) immediately after any venue error that mentions position side, (d) whenever a `positionRisk` read contains a `BOTH` row (§3.2). Any failure ⇒ same ABORT semantics.

### 5.3 ASTR-012 — Margin configuration assertion (COINED; Owner decision OPEN-3: cross + Multi-Assets)

At startup, after `assert_hedge_mode` and before any order-capable code:

```
1. GET multiAssetsMargin          -> boolean multiAssetsMargin must be true
2. positionRisk rows for each configured symbol must report cross margin
   (exact wire value of `marginType` for cross is OPEN-9: the doc samples only show "isolated";
    the POST enum is ISOLATED|CROSSED)
3. any mismatch / malformed / error -> ABORT (same semantics as ASTR-007)
```

- **Assert-only, no write** (COINED default). `POST multiAssetsMargin` applies to *every symbol* (**F16**) and `POST marginType` is per-symbol; unlike hedge mode, the owner has not authorised the bot to flip them. A write path needs its own owner decision (**OPEN-10**).
- *Rationale:* a grid with two coexisting legs under cross margin shares collateral across both legs and across symbols; the risk-bound layer (§12) assumes the configured mode, so a silent mode drift must fail closed.
- Interaction risk: whether Multi-Assets mode and Hedge Mode can both be on simultaneously is **not stated in the docs examined** → **OPEN-8** (testnet).

## 6. G-4 — Authentication (DECIDED: V3)

| | **V1 (HMAC)** | **V3 (agent wallet)** |
|---|---|---|
| New credentials | **Cannot be created** since 2026-03-25 (**F1**) | Create an API wallet ("Pro API") (**S3 l.157**) |
| Signing | HMAC-SHA256, stdlib (**F2**) | EIP-712 signature with signer private key; `user`, `signer`, µs `nonce` (**F3**) → needs Keccak + secp256k1 (**F4**), **not stdlib-only** |
| Hedge endpoints | present (**F5**) | present (**F5**) |
| Testnet | none documented (**F13**) | documented (**F13**) |
| Replay | timestamp/recvWindow | µs nonce (a `-4225 Nonce Expired` error exists in the docs) |

**Decision (Owner, 2026-10-01): V3.** Consequences, all confined to `adapters/` (core stays dependency-free; "no `float`" / "no `logging` in core" unaffected):

- **ASTR-013 — endpoint set (COINED):** `GET/POST /fapi/v3/positionSide/dual`, `GET /fapi/v3/positionRisk`, `POST/GET/DELETE /fapi/v3/order`, `GET /fapi/v3/openOrders`, `GET /fapi/v3/userTrades`, `GET /fapi/v3/accountWithJoinMargin` (and `/fapi/v3/balance`), `GET/POST /fapi/v3/multiAssetsMargin`, `POST /fapi/v3/marginType`, `POST/PUT/DELETE /fapi/v3/listenKey` (**F5, F6, F10, F11, F14, F16**).
- **Signing is a Phase-5b concern** (EIP-712 / Keccak / secp256k1, `user`+`signer`+µs `nonce`). Needs a crypto dependency; adding it is a `pyproject.toml` change and requires its own owner-visible decision recorded in `research/tooling/` (candidate libraries are not evaluated here).
- **Secrets:** the API-wallet private key never enters the repo, logs, events, or test fixtures. Owner holds the key; the adapter receives a signer *object*, never a raw key string in config.
- **Testnet is available** (**F13**): `https://fapi.asterdex-testnet.com`. Phase 4 gray-launch starts there. Whether the testnet supports hedge mode / Multi-Assets mode identically is **OPEN-8**.
- **Nonce:** µs timestamp supplied by the caller via `ObservedMeta`-derived time, never sampled inside a deterministic module; `-4225 Nonce Expired` (docs) is a retriable-after-resync error class, not a blind-retry one.

## 7. §6.2 / §13.4 / §9 — order and closure semantics under hedge mode

### 7.1 ASTR-009 — `positionSide` is mandatory on every order (VERBATIM-F6)

Every order carries `positionSide ∈ {LONG, SHORT}`. `BOTH` is never sent. The command (port) layer takes a `PositionSide` enum with exactly those two members; there is no default.

### 7.2 ASTR-010 — Leg semantics replace reduce-only (COINED; VERBATIM-F7)

| Intent | `side` | `positionSide` |
|---|---|---|
| Open/add to LONG leg | BUY | LONG |
| Reduce/close LONG leg | SELL | LONG |
| Open/add to SHORT leg | SELL | SHORT |
| Reduce/close SHORT leg | BUY | SHORT |

- `reduceOnly` is **never sent** in hedge mode (**F7**). Safety against over-closing (a close quantity larger than the leg) therefore moves from the venue flag into the bot: close `qty ≤ actual_<leg>` from the latest authoritative read, else reject locally. *Rationale:* without the flag, an oversized SELL+LONG order would be rejected or misbehave on the venue's terms rather than ours.
- §13.4 closure = two independent closures (LONG, SHORT), each with its own completion check against `actual_long` / `actual_short` reaching 0.
- `closePosition=true` on conditional orders has hedge restrictions (**F8**); the contract does not use it.
- Any place the Strategy says "reduce-only" must be located (`grep -n -i "reduce" Strategy.md`) and re-expressed via the table above — **OPEN-5** (cannot be done here).

### 7.3 ASTR-011 — Client order id and idempotency (COINED; VERBATIM-F9)

- Format must satisfy `^[\.A-Z\:/a-z0-9_-]{1,36}$`. The bot's id scheme must be reversible within 36 chars and must not rely on opaque prefix-joining (pre-flight non-critical item).
- Because uniqueness is only among **open** orders, a retry after an ambiguous failure (timeout) must **first query by client order id** (`GET order`) and only resubmit if absent. A blind resubmit with the same id is *not* proven idempotent once the first order has filled or been cancelled.
- Field name in core stays `client_order_id`; the wire name is `newClientOrderId` on request and `clientOrderId` on response — mapped in the adapter only (pre-flight naming-drift item).

### 7.4 Fills carry their leg — scope ruling (COINED; addresses pre-flight C5)

A fill on ASTER is meaningless to two-sided accounting without its leg (`GET userTrades` rows include `positionSide`; S2 l.3316, S2 endpoint l.3324). The hypergrid `FillEvent` has no `position_side` (HANDOFF). Ruling: adding `position_side` to `FillEvent` is an **engine change (Phase 2)**, not an adapter change. Until then the adapter **must not** fabricate position-aware `FillEvent`s; it exposes venue records only. This is why §10 orders Phase 2 before the adapter's mapping layer.

## 8. Decision register and requirement delta (to apply in the Strategy-bearing tree)

Proposed — **IDs provisional**, counts to be recomputed, not asserted:

| Item | Action | Anchor |
|---|---|---|
| DECISION-002 | AMEND → §4.1 | HANDOFF |
| DECISION-A1 (new) | Exposure is per-side; net is derived | §3.1 |
| DECISION-A2 (new) | Hedge mode asserted/written at startup, fail-closed | §5 |
| DECISION-A3 (new) | Auth model = V3 (Owner, 2026-10-01); V1 HMAC not used | §6 |
| DECISION-A4 (new) | Margin config = cross + Multi-Assets, assert-only at startup | §5.3 |
| STR-0200 | AMEND → ASTR-001 | HANDOFF |
| §11.1 / ST-07/08/09 | AMEND → ASTR-003/004 | HANDOFF |
| §6.2 | AMEND → ASTR-009/010/011 | HANDOFF |
| §13.4 | AMEND → ASTR-010 closure | HANDOFF |
| New startup § | ADD → ASTR-007/008/012 | — |
| Adapter surface (V3 endpoint set, signing boundary, secrets) | ADD → ASTR-013 | §6 |
| §6.3 precision, §10 funding | **NOT covered here** — need Phase 0 evidence (`exchangeInfo`, funding) | — |

Count commands (run after merge; no count is asserted here): requirement headings in this file — `grep -o 'ASTR-0[0-9][0-9] —' docs/contract/CONTRACT_DELTA_ASTER.md | sort -u | wc -l`; STR count in the Strategy-bearing tree — command to be taken from that tree's own index (not known here).

## 9. Open items

| ID | Question | Needs |
|---|---|---|
| ~~G-4~~ | DECIDED: V3 | — |
| OPEN-1 | Does positionRisk omit a flat leg's row? (V3 sign convention confirmed; omission unconfirmed) | testnet |
| ~~OPEN-2~~ | DECIDED: per side (one tol evaluated on each side) | — |
| ~~OPEN-3~~ | DECIDED: cross + Multi-Assets | — |
| OPEN-7 | Which account field is CapitalBase under Multi-Assets (V3 `accountWithJoinMargin` response fields not yet inspected; `assets[]` is per asset in V1, **F11**) | Owner + Phase 0 |
| OPEN-8 | Can Hedge Mode and Multi-Assets Mode both be on? Does testnet mirror mainnet for both? | testnet |
| OPEN-9 | Exact wire value of `marginType` for cross in `positionRisk` | testnet |
| OPEN-10 | May the bot *write* `multiAssetsMargin` / `marginType`, or assert-only (current default)? | Owner |
| OPEN-4 | Is switching to hedge rejected while positions/orders exist on ASTER? | testnet |
| OPEN-5 | Locate every "reduce-only" reading in `Strategy.md` | tree with Strategy.md |
| OPEN-6 | §6.3 precision, §10 funding on ASTER | Phase 0 |

## 10. Sequencing consequence of the (a) split

1. **Phase 1 (this doc)** → Owner ACCEPT (G-4, OPEN-2, OPEN-3 already answered; OPEN-7/10 outstanding).
2. **Phase 2 — engine delta** (separate prompt): two-sided `ActualExposureState` + `ExpectedExposure`/`ExposureDelta` per side, relaxed source allow-list (§4.2), `FillEvent.position_side` (§7.4), non-vacuity test (ASTR-004). This is where the pre-flight's C1–C3, C5 cascade lives; it is *not* removed by the split, only isolated.
3. **7h-5a-ASTER — adapter only** (port + mock + sink + `assert_hedge_mode`), emitting venue-neutral two-sided position rows; **no** mapping into `ActualExposureState` until Phase 2 is merged. If the owner wants the mapping inside 7h-5a, Phase 2 must merge first.

> Correction to the "split removes C1–C5" claim: the split removes them from the *adapter prompt*. The same edits still have to happen once, in Phase 2.
