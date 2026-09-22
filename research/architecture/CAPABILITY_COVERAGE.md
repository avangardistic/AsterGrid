# CAPABILITY_COVERAGE.md — STR-* → CAP-* coverage (Phase 3)

- **Purpose:** Reverse map from every `STR-*` requirement to ≥1 capability (`CAP-*`), guaranteeing no requirement is dropped in capability discovery. Companion to `CAPABILITY_MAP.md`.
- **Producer:** Claude Code (Opus 4.8), Phase 3.
- **Inputs:** `STRATEGY_CONTRACT.md` (382 STR-*, incl. Phase 4.6/4.10/6c additions), `CAPABILITY_MAP.md` (24 CAP-*).
- **Status:** COMPLETE — all 382 STR-* mapped (343 Phase 1 + STR-0344 Phase 4.6 + STR-0345..0362 Phase 4.10 + STR-0363..0382 Phase 6c); "STR-* without a CAP-*" section is empty.

> Notation: primary capability first; additional capabilities that also cover the requirement follow. §5.7 scenarios additionally map to CAP-0024 (differential-test inputs) — noted once here rather than repeated per row.

## Mapping (by requirement, grouped in contract order)

| STR range | Topic | CAP-* |
|-----------|-------|-------|
| STR-0001 | Hedge Layer authority | CAP-0016, CAP-0017 |
| STR-0002 | Profit Layer bounded | CAP-0010, CAP-0017 |
| STR-0003 | Basket→Gen→Cycle→Level hierarchy | CAP-0004 |
| STR-0004 | verified-delta principle | CAP-0003, CAP-0002 |
| STR-0005 | Basket def | CAP-0018 |
| STR-0006 | Generation def | CAP-0006 |
| STR-0007 | Group def | CAP-0009 |
| STR-0008 | Cycle def | CAP-0008 |
| STR-0009 | Level def | CAP-0009, CAP-0004 |
| STR-0010 | Reference Price def | CAP-0008 |
| STR-0011 | Evolution def | CAP-0007 |
| STR-0012 | Terminal Event def | CAP-0008 |
| STR-0013 | Successor Lock def | CAP-0006 |
| STR-0014 | Disabled Generation def | CAP-0006 |
| STR-0015 | Naming (Evolution) | CAP-0006, CAP-0007 |
| STR-0016..0024 | Canonical identity model | CAP-0004 |
| STR-0025..0035 | Evolution trigger (path-dependent) | CAP-0007 |
| STR-0036..0040 | Evolution confirmation window | CAP-0007 (STR-0036 also CAP-0020) |
| STR-0041..0048 | Generation states | CAP-0006 |
| STR-0049..0054 | One-successor lock | CAP-0006 |
| STR-0055..0057 | Post-evolution dominance | CAP-0007 |
| STR-0058..0062 | Generation 99 | CAP-0006 |
| STR-0063..0070 | Precedence P0–P6 | CAP-0005 |
| STR-0071..0073 | Terminal event / POSITION_VERIFIED | CAP-0008, CAP-0003 |
| STR-0074..0083 | Standard cycle transition | CAP-0008 (0076→CAP-0002; 0080→CAP-0009; 0083→CAP-0016) |
| STR-0084..0090 | Cycle-limit disable | CAP-0008, CAP-0006 |
| STR-0091..0095 | Cycle reference price | CAP-0008 (0091 policy→CAP-0020) |
| STR-0096..0100 | Reference-price tolerance | CAP-0008 (0096,0100→CAP-0020) |
| STR-0101 | Generation question | CAP-0007, CAP-0006 |
| STR-0102 | Cycle question | CAP-0008 |
| STR-0103 | Independent axes | CAP-0004 |
| STR-0104..0108 | Ladder non-overlap | CAP-0008 |
| STR-0109..0115 | Scenarios 01–07 (evolution) | CAP-0007 (0115 also CAP-0016) |
| STR-0116..0118 | Scenarios 08–10 (cycle/terminal) | CAP-0008 (0118 also CAP-0007) |
| STR-0119..0121 | Scenarios 11–13 (successor lock) | CAP-0006 (0121 also CAP-0008) |
| STR-0122..0123 | Scenarios 14–15 (C98/C99) | CAP-0008, CAP-0006 |
| STR-0124 | Scenario 16 (disabled below target) | CAP-0018, CAP-0006 |
| STR-0125 | Scenario 17 (disabled acute delta) | CAP-0016 |
| STR-0126 | Scenario 18 (G1 own evolution) | CAP-0006, CAP-0007 |
| STR-0127 | Scenario 19 (G99 reject) | CAP-0006 |
| STR-0128 | Scenario 20 (G99-C99 closure) | CAP-0018 |
| STR-0129..0132 | State pipeline / POSITION_VERIFIED | CAP-0003 (0129 also CAP-0015; 0132 also CAP-0002) |
| STR-0133 | Venue mechanisms | CAP-0001, CAP-0003, CAP-0015, CAP-0014 |
| STR-0134 | Trigger→mark price | CAP-0001 |
| STR-0135..0138 | Precision | CAP-0014 |
| STR-0139..0150 | Grid geometry | CAP-0009 (0148,0150→CAP-0010; params→CAP-0020) |
| STR-0151..0152 | Protection locking/unlock | CAP-0009 (0152 also CAP-0011) |
| STR-0153..0162 | Position sizing & caps | CAP-0010 |
| STR-0163..0164 | Pre-arm + AUTO | CAP-0011 |
| STR-0165..0167 | SEMI/WEBHOOK/defaults | CAP-0019, CAP-0011 |
| STR-0168..0169 | Arm invariants 1–2 | CAP-0011 |
| STR-0170..0172 | Arm invariants 3–5 | CAP-0019, CAP-0011 |
| STR-0173..0178 | Arm gates 1–9 | CAP-0011 |
| STR-0179 | Gate 10 Cost Analyzer | CAP-0013, CAP-0011 |
| STR-0180 | Generation-state arming | CAP-0011, CAP-0006 |
| STR-0181 | Fillability Analyzer | CAP-0012 |
| STR-0182..0187 | Emergency execution | CAP-0015 (0183→CAP-0020; 0185→CAP-0012/0013) |
| STR-0188..0189 | Maker→taker re-eval | CAP-0013 |
| STR-0190..0192 | Level skip | CAP-0015, CAP-0023 |
| STR-0193..0198 | Execution economics | CAP-0013 |
| STR-0199..0205 | Expected vs actual exposure | CAP-0016 (0200→CAP-0002; 0203→CAP-0005) |
| STR-0206..0207 | Hedge cost-awareness | CAP-0016 |
| STR-0208..0211 | Mirroring | CAP-0016 |
| STR-0212..0214 | Partial fill ↔ hedge | CAP-0016 |
| STR-0215..0222 | Range survivability bounds | CAP-0017 (0219,0222 leverage inputs→CAP-0020) |
| STR-0223 | MaxExposureImbalance | CAP-0016, CAP-0020 |
| STR-0224 | CapitalBase | CAP-0002 |
| STR-0225..0230 | MaxBasketNotional inputs/goal | CAP-0017, CAP-0010 (0227→CAP-0010/0020; 0229→CAP-0020) |
| STR-0231..0233 | Two-layer framing / risk precedence | CAP-0017 (0231 also CAP-0016) |
| STR-0234..0236 | Basket PnL | CAP-0018 (0236 funding→CAP-0001) |
| STR-0237..0238 | Basket states | CAP-0018 |
| STR-0239 | Freeze | CAP-0018 |
| STR-0240..0242 | Intent tagging/classification | CAP-0014, CAP-0018 |
| STR-0243..0256 | Closure | CAP-0018 (0248→CAP-0020; 0254→CAP-0015; 0255→CAP-0012) |
| STR-0257..0292 | §14 parameter reference | CAP-0020 |
| STR-0293 | FILLED⇔ invariant | CAP-0003 |
| STR-0294 | actual-only-authoritative | CAP-0002 |
| STR-0295 | expected≠actual | CAP-0016 |
| STR-0296 | progression gated | CAP-0016, CAP-0005 |
| STR-0297 | emergency ≤ tolerance | CAP-0015 |
| STR-0298..0299 | cloid persist / normalize before sign | CAP-0014 |
| STR-0300..0301 | maker/taker economics | CAP-0013 |
| STR-0302 | mirror validation | CAP-0016 |
| STR-0303 | closed requires both | CAP-0018 |
| STR-0304 | evolution not raw crossing | CAP-0007 |
| STR-0305 | no overlap | CAP-0008 |
| STR-0306 | IDs independent | CAP-0004 |
| STR-0307 | range no corrupt | CAP-0017, CAP-0023 |
| STR-0308 | hedge/profit separate | CAP-0016 |
| STR-0309 | profit within envelope | CAP-0010, CAP-0017 |
| STR-0310 | NET PnL | CAP-0018 |
| STR-0311 | skip preferable | CAP-0013, CAP-0023 |
| STR-0312 | slower verified | CAP-0003, CAP-0023 |
| STR-0313 | deterministic identity | CAP-0004 |
| STR-0314 | no transition from intent | CAP-0003 |
| STR-0315 | reconstructable | CAP-0021 |
| STR-0316..0319 | ID ranges / no 100 | CAP-0004 |
| STR-0320 | terminal→cycle | CAP-0008 |
| STR-0321 | terminal not gen | CAP-0006 |
| STR-0322 | verified return→successor | CAP-0007 |
| STR-0323..0324 | one successor / no second | CAP-0006 |
| STR-0325 | disable at limit | CAP-0006, CAP-0008 |
| STR-0326..0327 | disabled≠closed / in accounting | CAP-0006, CAP-0018 |
| STR-0328 | closure both | CAP-0018 |
| STR-0329 | acute hedge override | CAP-0016 |
| STR-0330 | raw crossing no trigger | CAP-0003 |
| STR-0331 | IDs independent | CAP-0004 |
| STR-0332 | historical immutable | CAP-0004, CAP-0021 |
| STR-0333 | ineligible not silent | CAP-0006 |
| STR-0334 | reconstructable G/C | CAP-0021 |
| STR-0335 | no bypass gates | CAP-0005, CAP-0023 |
| STR-0336 | §16 dynamic-default handling | CAP-0020, CAP-0022 |
| STR-0337 | contract mechanics (margin/funding/mark/max-lev) | CAP-0001, CAP-0002, CAP-0017 |
| STR-0338..0341 | 4 dynamic defaults | CAP-0020 |
| STR-0342 | consistency-ordering note | CAP-0020, CAP-0022 |
| STR-0343 | no invented values | CAP-0020, CAP-0023 |

## Coverage counts

## Phase 4.10 STR additions

> STR-0344 (Phase 4.6, previously unmapped — auditb6 GAP-1) and STR-0345..0362 (Phase 4.10) mapped here. Existing STR-0001..0343 mappings above unchanged; no CAP-* renumbered.

| STR range | Topic | CAP-* |
|-----------|-------|-------|
| STR-0344 | one active order per Level (DECISION-004) | CAP-0003, CAP-0015 (enforcement projection CAP-0005) |
| STR-0345..0348 | tradability-quantized exposure gate / round-to-zero / calibration warning / margin tracking (DECISION-016) | CAP-0016, CAP-0023, CAP-0020 |
| STR-0349..0351 | GrossGridEdge closed form / validity condition / α·S/2 proposal (DECISION-017) | CAP-0013 |
| STR-0352..0355 | funding accumulator / FUNDING_BREAK / response ladder / β_F (DECISION-018) | CAP-0017, CAP-0018 |
| STR-0356..0357 | acute-correction precedence / acute() predicate (DECISION-019) | CAP-0011, CAP-0016 |
| STR-0358..0360 | MarginMode pin / init abort / P0 assertion (DECISION-020) | CAP-0002, CAP-0017, CAP-0020 |
| STR-0361 | N3 min-separation ε (Phase-4.9 recommendation; Phase 6) | CAP-0008, CAP-0009 |
| STR-0362 | REST rate-budget rule (Phase-4.9 recommendation; Phase 6) | CAP-0001, CAP-0015 |

## Phase 6c STR additions (STR-0363..STR-0382)

> Resolutions of the 22 SEMANTIC_NON_BLOCKING findings (STRATEGY_CONTRACT §19). Mapped from each STR's `affects`/`verify` fields to existing CAP-* — no CAP-* invented, none renumbered. (AMB-0014 and AMB-0025 were resolved as phase6c_note annotations on STR-0345 / STR-0358 and are already covered by those rows above.)

| STR | Topic | CAP-* |
|-----|-------|-------|
| STR-0363 | non-overlap on tick/lot-normalized submittable prices | CAP-0008, CAP-0009 |
| STR-0364 | MarketDepth coverage-completeness vs l2Book window | CAP-0001, CAP-0010 |
| STR-0365 | rounding-direction & boundary-equality canon | CAP-0013, CAP-0014 |
| STR-0366 | record dynamic-default inputs + calibration version for replay | CAP-0021, CAP-0005 |
| STR-0367 | side-effect ordering / atomic decision boundary beyond §4.7 | CAP-0005 |
| STR-0368 | evidence gap ≠ continuity in confirmation window | CAP-0007, CAP-0002 |
| STR-0369 | per-data-type freshness/age policy | CAP-0001, CAP-0002 |
| STR-0370 | REST vs WS precedence/reconciliation | CAP-0002 |
| STR-0371 | TWAP parent/child, remaining-qty, crash-mid-TWAP | CAP-0015, CAP-0018 |
| STR-0372 | cancellation-in-flight state | CAP-0015 |
| STR-0373 | rejection taxonomy → skip/retry/recalc/freeze | CAP-0015 |
| STR-0374 | market/IOC slippage propagation to reference/cost | CAP-0008, CAP-0013 |
| STR-0375 | venue drift handling + version binding | CAP-0001, CAP-0020 |
| STR-0376 | output/reporting contract; no success-before-settlement | CAP-0022, CAP-0021 |
| STR-0377 | rate-limit/backoff/open-order-cap model | CAP-0001, CAP-0015 |
| STR-0378 | signer verifies correct non-stale intent; forensic trail | CAP-0014 |
| STR-0379 | API-key rotation/revoke/recovery lifecycle | CAP-0014 |
| STR-0380 | kill-switch / cancel-all / flatten-all semantics | CAP-0018, CAP-0019 |
| STR-0381 | owner-gate/policy/calibration versioning during active Basket | CAP-0020 |
| STR-0382 | numeric domain/type system & boundary cases | CAP-0013, CAP-0023 |

## Summary (updated Phase 6c)

- **STR-* total:** 382 (STR-0001..0382). **Mapped to ≥1 CAP-*:** 382 (100%) — 343 (Phase 1) + STR-0344 (Phase 4.6) + STR-0345..0362 (Phase 4.10) + STR-0363..0382 (Phase 6c).
- **Capabilities:** 24 (CAP-0001…CAP-0024). One (CAP-0024) is RESEARCH-ONLY / NON_RUNTIME.
- **Capabilities with zero STR-* mapped:** none (every CAP-* is justified by ≥1 STR-*).
- **Unmapped STR-*:** none (0). No STR-0363..0382 required a new capability.

### Approx. primary-coverage load per capability (primary mentions)
CAP-0004 (identity) and CAP-0006 (generation), CAP-0008 (cycle), CAP-0016 (exposure/hedge), CAP-0018 (basket/closure), CAP-0020 (config/calibration) carry the largest primary loads; CAP-0005/0021/0022/0023 are cross-cutting; CAP-0024 is non-runtime.

## STR-* without a CAP-*

**EMPTY.** No requirement is left unmapped. (If any had been unmappable, it would be listed here with reasoning and reported as OPEN — never assigned an invented capability.)

## RESEARCH-ONLY / NON_RUNTIME notes

- CAP-0024 (Reference Model & Differential Testing) is explicitly non-runtime; the §5.7 scenarios (STR-0109..0128) are covered at runtime by CAP-0006/0007/0008 and additionally serve as differential-test inputs to CAP-0024.
- Offline *calibration research* (finding calibrated values for the four `[DYN]` defaults) is non-runtime; the runtime only *resolves* parameters deterministically (CAP-0020).
