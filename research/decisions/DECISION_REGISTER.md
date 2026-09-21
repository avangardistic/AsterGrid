# DECISION_REGISTER.md

- **Purpose:** Authoritative register of material Owner decisions made during this program (per `prompt.md` `<decision_register>`). Each decision is traceable and supersedes nothing in `Strategy.md` (which is immutable); decisions bind interpretation/architecture layers only.
- **Producer:** Claude Code (Opus 4.8), Phase 3.
- **Status:** ACTIVE. Newest decisions appended.

---

## DECISION-001 — BTC/ETH max leverage figure in §16 (from OWNER_GATE_001 / CONFLICT-001)

- **decision_id:** DECISION-001
- **question:** Is the "BTC/ETH max leverage = 40x" figure in `Strategy.md` §16 binding, given the docs are internally inconsistent (liquidations prose 40x vs info `meta` example 50x) and the runtime clamps `Leverage_effective = min(Leverage_user=3, MaxLeverage_asset) = 3`?
- **context:** §16 uses "40x" only in the mechanics *preamble* to illustrate "initial margin fraction 2.5%, maintenance margin fraction 1.25%". All executed D-16 formulas take `Leverage_effective`, which is 3 regardless of 40 vs 50. D-13 defines `Leverage_effective = min(Leverage_user, MaxLeverage_asset)`, with `MaxLeverage_asset` read from `meta`.
- **evidence:** SRC-118 liquidations.md ("max leverage … varies from 3-40x … 1.25% for 40x max leverage assets") corroborates 40x; SRC-107 info-endpoint/perpetuals `meta` example shows `maxLeverage: 50` (illustrative/stale); SRC-115/116 margining + contract-specifications confirm maintenance = ½ initial at max leverage and per-asset max leverage.
- **decision:** **Option A** — the "40x" figure in §16 is **ILLUSTRATIVE / NON-BINDING**. Runtime MUST read `meta.maxLeverage` live (per D-13) and MUST NEVER hardcode 40 or 50. Live verification of the current BTC/ETH value is OPTIONAL and non-blocking (may be logged as an observation in Phase 8/12, never as a prerequisite).
- **alternatives:** B (mandatory live verification as a prerequisite); C (owner-specified other value).
- **rejected_alternatives:** B (rejected as *mandatory*/blocking — reduced to optional observation); C (no alternative proposed).
- **affected_strategy_requirements:** STR-0337 (venue-evidence-status change only; no normative content change).
- **risk:** LOW at runtime (Leverage_effective clamps to 3); MEDIUM as a documentation artifact (docs-internal inconsistency in the §16 preamble).
- **reversibility:** HIGH (interpretation only; `Strategy.md` unchanged).
- **owner_required:** YES.
- **owner_decision:** **Option A** (recorded 2026-09-21).
- **date:** 2026-09-21.
- **supersedes:** none (first resolution of CONFLICT-001 / GATE-001).

---

## DECISION-002 — Authoritative source for ActualExposure and CapitalBase (from OWNER_GATE_002 / CONFLICT-002)

- **decision_id:** DECISION-002
- **question:** Given `Strategy.md` pairs "clearinghouseState/webData2" but the venue documents `webData2` as a frontend aggregate (now `webData3`), which endpoint is the authoritative source for `ActualExposure` (STR-0200) and `CapitalBase` (STR-0224) per §11.1?
- **context:** §15 invariant: "Actual Exposure only from authoritative exchange state." Venue docs: `clearinghouseState` (REST + WS) is the authoritative position/margin source; `webData2`/`webData3` is "used primarily for the frontend".
- **evidence:** SRC-107 clearinghouseState schema (`assetPositions[].position.szi`, `marginSummary.accountValue` incl. unrealized PnL, `withdrawable`); SRC-109 websocket subscriptions (webData3 current; WebData2 described as frontend aggregate); margining/liquidations use mark price + account value from clearinghouse.
- **decision:** **Option A** — `clearinghouseState` (REST + WS) is the **SOLE authoritative source** for `ActualExposure` and `CapitalBase`. `webData2`/`webData3` MUST NEVER be used as the basis of `POSITION_VERIFIED`, `ActualExposure`, or `CapitalBase`, and MUST NOT drive any decision (arming, closure, evolution, hedge, reconciliation). They MAY be used later for display/observability only.
- **alternatives:** B (combined use with final reconciliation via clearinghouseState); C (owner-specified other).
- **rejected_alternatives:** B, C (owner chose A).
- **affected_strategy_requirements:** STR-0200, STR-0224 (annotation only); STR-0133 (order-lifecycle state authority must also never source from webData3).
- **risk:** LOW (aligns with §15 invariant "Actual Exposure only from authoritative exchange state").
- **reversibility:** HIGH.
- **owner_required:** YES.
- **owner_decision:** **Option A** (recorded 2026-09-21).
- **date:** 2026-09-21.
- **supersedes:** none (first resolution of CONFLICT-002 / GATE-002).
