# Strategy logic on ASTER — deployment problems and findings

**Status:** findings for Owner/Reviewer · 2026-10-01 · document-only (no code)
**Method:** strategy text read in **this tree** (`Strategy.md` SHA
`085044e7…`, verified); venue facts from `research/aster/SOURCE_MANIFEST.md`
(F1–F16, `VENDOR_DOC`); deltas already coined in
`docs/contract/CONTRACT_DELTA_ASTER.md` (ASTR-001..013). New findings here get
IDs **R-#** (risk) with source class + anchor. `OBSERVATION` = verified in this
session's tree; `VENDOR_DOC` = manifest fact; `COINED` = new proposal needing
Owner ACCEPT.

## 1. Verified strategy-side facts this analysis rests on

| Fact | Anchor | Status |
|---|---|---|
| §6.2 mechanism list is Hyperliquid-specific (`cloid`, `/exchange`, `orderStatus`, WS `orderUpdates`/`userFills`, `clearinghouseState`/`webData2`, TIF `Gtc/Ioc/Alo`, oracle-mark triggers) | `Strategy.md` l.572–574 | OBSERVATION |
| §6.3 precision rule (≤5 sig-figs, `MAX_DECIMALS=6`, `szDecimals`) is the HL rule | `Strategy.md` l.576–580 | OBSERVATION |
| §10 fee inputs: "pulled live from userFees — Tier-0 base ≈ taker 0.045%, maker 0.015%, NEVER hardcoded" | `Strategy.md` l.812–816 | OBSERVATION |
| §10 paths: maker = `Alo` (reject-instead-of-cross), taker = `Ioc` | `Strategy.md` l.818–824 | OBSERVATION |
| §11.1 actual exposure authority = "clearinghouseState/webData2 ONLY" | `Strategy.md` l.845–846 | OBSERVATION |
| §11.1 gate: "Grid progression is hard-gated on exposure being within tolerance" | `Strategy.md` l.874 | OBSERVATION |
| §12/D-13 margin model: `MaxSafeNotional_margin := CapitalBase × Leverage_effective / 2`; maintenance fraction read as **1.25%** (HL 40x) and **16.7%** (`0.5/3`) in worked examples | `Strategy.md` l.1233, l.1235, D-13 row | OBSERVATION |
| Reduce-only reliance is already *non-essential*: §13.3 FREEZE text classifies intents "by projected `ExposureDelta`… **not by the exchange's reduce-only flag alone**"; the only other `reduce` hit is §8's order-count-limit note (~1000 open orders; "reduce-only/trigger orders rejected above that") | `Strategy.md` l.1009, l.747 | OBSERVATION |

## 2. Venue mapping table (what each HL mechanism becomes on Aster V3)

| HL mechanism (§6.2) | Aster V3 replacement | Anchor | Gap class |
|---|---|---|---|
| `cloid` (128-bit, idempotent identity) | `newClientOrderId` ≤36 chars, unique **among open orders only** | F9, ASTR-011 | **semantic gap** — idempotency lost post-close → query-before-resubmit |
| `POST /exchange` ack (`resting/filled/error`) | `POST /fapi/v3/order` response | F6 | simple mapping |
| `orderStatus` endpoint | `GET /fapi/v3/order` (+`openOrders`) | F6/F9 | simple mapping |
| WS `orderUpdates` | WS `ORDER_TRADE_UPDATE` (user stream, listenKey) | F12, F14 | shape needed (W3) |
| WS `userFills` + REST history | `GET /fapi/v3/userTrades` (+ `ACCOUNT_UPDATE` as hint) | F11/F12 | fills must carry `positionSide` → engine change (§7.4) |
| `clearinghouseState`/`webData2` | `GET /fapi/v3/positionRisk` (weight 5) as sole exposure authority | F10, G-2/ASTR-006 | solved by contract |
| TIF `Gtc/Ioc/Alo` | `GTC` / `IOC` / `GTX`? — **post-only TIF name unverified** | — | **R-6 (below)** |
| Oracle-mark trigger evaluation | mark-price source on Aster | — | **R-5 (below)** |
| (none) | hedge mode read/write `/fapi/v3/positionSide/dual` | F5, ASTR-007/008 | new startup gate |
| (none) | `reduceOnly` **forbidden** in hedge mode | F7, ASTR-010 | solved by contract (§7.2 table) |

## 3. Problems (ranked; each with engine consequence)

### R-1 — Maintenance-margin model mismatch (highest economic risk)
`Strategy.md` §12/§16/D-13 derives `MaxSafeNotional_margin` and the acute-hedge
trigger from `maintenance fraction = 0.5 / leverage` with worked values 1.25%
and 16.7% (HL-shaped). Aster's actual per-asset maintenance tiers are **not in
the examined docs** (OWNER_GATE_005 resolved "use venue's real schedule" —
already flagged pre-migration). Consequence: if Aster's real maintenance
fraction at 3x is *stricter* than 16.7%, the acute-hedge trigger fires **too
late** (safety); if looser, capital is underused (economics). **Engine
consequence:** D-16 becomes a calibration input fed from `premiumIndex`/
`positionRisk` liquidation data (P0b W2/W4), not a constant. (OWNER_DECISION
GATE-005 + OBSERVATION; consequence analysis COINED.)

### R-2 — CapitalBase under Multi-Assets cross is undefined (blocks sizing)
Sizing (§7.3) and D-13 bound every notional to `CapitalBase` = "account equity
incl. unrealized PnL". Under OPEN-3 (cross + Multi-Assets), equity is
multi-asset; which V3 field is CapitalBase is **OPEN-7** and the
`accountWithJoinMargin` schema is unverified (F11 lists V1 `assets[]`). Wrong
choice ⇒ wrong `MaxBasketNotional` ⇒ wrong level sizes everywhere. **Engine
consequence:** none until P3b mapping; but P2 sizing tests must not hard-code a
choice. (HANDOFF + VENDOR_DOC F11; OPEN-7.)

### R-3 — Fees: HL numbers are placeholders on Aster (economics can invert)
§10 NetExpectedEdge subtracts fees "pulled live… NEVER hardcoded" (taker
0.045%/maker 0.015% are HL Tier-0 figures). Aster's taker/maker schedule (and
whether a maker rebate or only a discount exists) is **unverified** — and the
grid's whole arithmetic is `GrossGridEdge − fees − slippage − funding ≥
floor`. With StepBps=10 and floor=1 bps, a fee delta of a few bps flips
arm/skip decisions across the ladder. Manifest lists fee tiers as NOT
verified. **Engine consequence:** fee source endpoint + tier table = P0b item
(was missing from W-list → **add to W1 output**, COINED here). (OBSERVATION
§10 + MANIFEST gap.)

### R-4 — No idempotent order identity (correctness under retries)
Already ASTR-011: `newClientOrderId` uniqueness is open-orders-only (F9). The
strategy's §8/§9 timeout-and-retry paths (emergency execution, maker→taker
escalation) are exactly where an ambiguous timeout + resubmit can
double-execute. The contract's query-before-resubmit rule is correct; the
**new** nuance found in-tree: §9.2's maker→taker re-evaluation must cancel-
then-confirm (read-back) before resubmitting, not fire-and-forget. **Engine
consequence:** P2/P5c tests must include the ambiguous-timeout path.
(OBSERVATION §9.2 + VENDOR_DOC F9.)

### R-5 — Trigger-order mark price source unverified (protection timing)
HL triggers evaluate against oracle mark. The strategy's stop/protection logic
(§7.2 fillability, §12 breach ladder) assumes a specific, non-manipulable mark.
Which Aster price (last? mark? index?) drives `STOP_MARKET`/`TAKE_PROFIT_MARKET`
is not in the examined excerpts — and mark-price **convergence to index**
(spreads widely on small DEX perps) could fire protection levels early/late.
**Engine consequence:** P0b W2 must name the authoritative trigger price;
engine keeps "mark" as an injected input (no change). (ASSUMPTION → needs
W2; risk COINED.)

### R-6 — TIF translation: no `Alo`/post-only equivalent confirmed (maker path)
The strategy's normal arming path *prefers* `Alo` (post-only, reject-instead-
of-cross) and its economics lean on maker fees. Aster's TIF set is not
excerpted in the manifest. If Aster's post-only equivalent does not exist
(only GTC/IOC/FOK/`GTX`-style), either (a) post-only semantics must be
emulated (limit-then-monitor-then-replace — latency-sensitive), or (b) §10
path selection changes. **Engine consequence:** blocks P3a port design; needs
one V3-doc lookup (cheap). **Newly added to W1/W3 evidence list.** (OBSERVATION
§8/§10 + MANIFEST gap.)

### R-7 — Funding cadence vs holding-period economics
§10 subtracts `FundingCostEstimate(holding_period)`. HL funds hourly; **Aster's
interval and cap are unverified** (OPEN-6b). A grid that holds both legs
indefinitely pays funding on *both* legs; if Aster's funding is 8h and
asymmetric between symbols, the mirror-pair economics (§11.3) shift. **Engine
consequence:** W2 evidence + no code change (estimator input). (OBSERVATION
§10 + OPEN-6b.)

### R-8 — Startup mode-writes are account-global (deployment constraint, not engine)
F5/F16: `positionSide/dual`, `multiAssetsMargin` apply to **every symbol** on
the account. ASTR-007 writes hedge mode at startup (G-3) and ASTR-012 asserts
cross+Multi-Assets assert-only (OPEN-10 pending). Consequence for *this
strategy's logic*: none in core; but the bot must run on a dedicated
account/sub-account, else coexisting strategies break. Also OPEN-8 (can hedge
+ Multi-Assets coexist?) is a **hard pre-req for P3a**. (VENDOR_DOC F5/F16 +
CONTRACT §5.)

### R-9 — `closePosition=true` conditional-stop hedge restrictions (F8) intersect §12 breach ladder
The breach ladder's conditional exits must respect: in hedge mode,
`closePosition=true` cannot pair BUY-with-LONG / SELL-with-SHORT. The contract
says "the contract does not use it" — but §12's emergency paths (§9.1 taker
escalation, breach ladder) should be checked once, explicitly, that they emit
plain opposite-side orders with `positionSide` (ASTR-010 table) and never
`closePosition=true`. **Engine consequence:** one P2d/P2e test case. (VENDOR_DOC
F8 + OBSERVATION §12; verification COINED.)

### R-10 — Precision rule replacement must be *derived per symbol*, not ported
§6.3's HL rule (≤5 sig-figs / MAX_DECIMALS−szDecimals) has no meaning on
Aster; the correct rule is: round price to `tickSize`, size to `stepSize`,
check `minQty`/`minNotional`, computed **per symbol from exchangeInfo** (W1).
Strategy text says normalization happens in the engine before signing — the
principle ports; the constants do not. Level geometry (§7.1 step prices) must
be quantized to tickSize, which can shift effective step spacing at small
price levels. **Engine consequence:** P0b W1 evidence feeds a per-symbol
precision table; geometry quantization goes to P2/P3a review. (OBSERVATION §6.3
+ §7.1.)

## 4. OPEN items this analysis resolves or advances

| OPEN | New status | Anchor |
|---|---|---|
| OPEN-5 (find every reduce-only reading) | **ANALYTICALLY RESOLVED in-tree**: exactly 2 `reduce` hits (`grep -n -i reduce Strategy.md`): l.1009 (explicitly *not* reliant on the venue flag — intent classified by projected ExposureDelta) and l.747 (§8 open-order-count note — informational). Nothing in the engine path depends on a venue reduce-only flag. Adapter must still never send `reduceOnly` (F7). | `Strategy.md` l.747, l.1009 |
| ASTR count (contract §8) | **13** ASTR IDs — `grep -o 'ASTR-0[0-9][0-9] —' docs/contract/CONTRACT_DELTA_ASTER.md \| sort -u \| wc -l` = 13 (ASTR-001..013) | command above |
| OPEN-6a/6b, OPEN-7/8/9, R-3/R-5/R-6/R-7 evidence gaps | scheduled into `API_RESEARCH_ROADMAP.md` W1–W6 (fee-tier table and TIF/post-only set **added** to W1/W3 scope) | roadmap this PR |

## 5. Conclusion

No finding invalidates the migration or the contract delta. The strategy's
semantic core (two-sided exposure, per-side gate, leg-based closure, mirror
recompute) is representable on Aster — that was the premise of choosing a
hedge-native venue and it holds. The material risks are **economic-input**
risks (R-1 margin model, R-2 CapitalBase, R-3 fees, R-7 funding) and **two
cheap-but-blocking wire facts** (R-6 TIF/post-only, R-5 trigger mark source)
— all closable by the W1/W2/W4/W6 evidence pass before any engine code.
Recommended order: W1+W2+W3+W5 (doc-only) → Owner answers OPEN-7/OPEN-10 →
testnet wallet → W6 → then P1 ACCEPT, then P2.
