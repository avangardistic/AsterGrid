# U4_VERIFICATION.md — Independent verification of audit finding U-4 (Phase 4.9)

- **Producer:** Claude Code (Opus 4.8), Phase 4.9. **No fix applied; no gate opened; no DECISION created.**
- **Primary sources:** `Strategy.md` §8 (arm-gate invariants + gate 10 + disabled-gen rule), §9.1, §10, §11.2, §13.3.

## 1. Finding (verbatim, SRC-204 §1 / S-8.3)
> "The correction path's gate set is *contradictory as written*: §8-inv.1 exempts corrections from arm-approval, the disabled-gen clause makes them pass 'every other gate', §10's 'either path' floors them economically, §11.2's acute branch exempts them economically. Resolvable only by an implicit precedence … The strategy never states that precedence. Two compliant implementations diverge observably."

## 2. Primary-source extraction
- **§8 inv.1 (L730):** "The arm gate NEVER applies to `EXPOSURE_CORRECTION_INTENT` — hedge/survival paths are never gated on human or service latency".
- **§8 disabled-gen rule (L759):** correction intents "are exempt from gate 9's FREEZE block and from this progression prohibition, but **pass every other gate**."
- **§8 gate 10 / §10 (L752–754, L827–830):** arming requires `NetExpectedEdge > floor`; "`NetExpectedEdge ≤ floor (either path) → do not arm / do not attempt`."
- **§9.1 (L781–784):** emergency `Ioc` submitted only IF "best executable price within band **AND NetExpectedEdge (§10) clears the configured floor**"; else `LEVEL_SKIPPED`.
- **§11.2 (L869–874):** "IF risk … ACUTE …: hedge immediately via Ioc **regardless of cost — unconditional**; ELSE: evaluate via §10's NetExpectedEdge model".

## 3. Independent derivation
For an **acute** `EXPOSURE_CORRECTION_INTENT` whose `NetExpectedEdge ≤ floor` (e.g. a hedge in a liquidity void), the text yields two contradictory instructions:
- §11.2 acute branch ⇒ **fire unconditionally, regardless of cost**;
- §8 disabled-gen "pass every other gate" (L759) **plus** §9.1's emergency precondition (L782, requires the floor to clear) **plus** §10 "either path → do not attempt" (L829) ⇒ **skip (uneconomic)**.
Two compliant implementations: A treats §11.2 acute as overriding (fires); B applies gate 10 / §9.1 floor to the correction (skips). Different observable behavior (position corrected vs left un-hedged) exactly when correction matters most. The strategy states **no precedence** between "§11.2 acute unconditional" and "§9.1/§8-gate-10 floor."

## 4. Counter-example search (is it already resolved?)
§11.2 *does* provide an acute/non-acute split (acute → skip economics; non-acute → apply §10), which resolves the **non-acute** correction case cleanly (consistent with gate 10). It does **not** state that the acute branch overrides §9.1's explicit floor precondition (L782) or §8's "every other gate" (L759). §12.2 (L983) gives risk precedence over the *profit target* but not over the *economics floor for a correction*. So the contradiction survives specifically for **acute corrections**. Audit not over-generalized; if anything it under-states that §9.1 *also* imposes the floor.

## 5. Verdict
**U_VERIFIED** — a real, reachable contradiction for acute `EXPOSURE_CORRECTION_INTENT` with `NetExpectedEdge ≤ floor`; the strategy fixes no precedence.

## 6. Impact
- affects_str: STR-0168 (arm-gate inv.1), STR-0197 (floor either-path), STR-0185 (§9.1 emergency requires floor), STR-0206 (acute unconditional), STR-0207 (non-acute → §10).
- affects_cap: CAP-0011 (arm/gating), CAP-0015 (execution), CAP-0016 (hedge recovery).
- severity: audit **⚠️/U**; independently **HIGH** (governs whether a survival hedge fires in a void).

## 7. Recommendation (PROPOSAL, not a decision)
Add a one-sentence precedence rule (audit R-5 family): the NetExpectedEdge floor applies to `ENTRY_INTENT` and to **non-acute** `EXPOSURE_CORRECTION_INTENT`; it never applies to **acute** Hedge Recovery (§11.2), which is size-bounded by `|ExposureDelta|` and band-bounded by `EmergencyTolerance`. Justification: it reconciles §8-inv.1, §9.1, §10, §11.2 into a total gating order; the choice affects survival behavior → **SEMANTIC_BLOCKING_PENDING**.
