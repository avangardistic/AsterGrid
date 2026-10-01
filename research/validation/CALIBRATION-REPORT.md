# CALIBRATION-REPORT.md — STUB

**STATUS: NOT_YET_PRODUCED — will be produced in a later calibration phase.**

- **Purpose (when produced):** Record calibration of the four dynamic defaults (D-16 ×3: `EmergencyTolerance`, `ExposureTolerance`, `MaxExposureImbalance`; D-17: `ReferencePriceToleranceBps`) and verify the §16 mutual-ordering consistency note — `ExposureTolerance < MaxExposureImbalance < NotionalPerLevel / MarkPrice` — holds across the candidate input sets (`Leverage_effective ∈ {2,3,5}`, `StepBps ∈ {5,10,20}`), reporting any failure rather than silently adjusting coefficients (per `Strategy.md` §16 and STR-0342/STR-0336).
- **Producer:** to be produced in the calibration phase (post-architecture, per `prompt.md` `<calibration>`); requires offline analysis / backtest / shadow evidence and Owner confirmation.
- **Referenced by:** `STRATEGY_CONTRACT.md` STR-0342 (`dynamic_note`, PENDING_ARTIFACT). `Strategy.md` §16 also names `CALIBRATION-REPORT.md` for the mutual-ordering verification; that reference is upstream and immutable.
- **Why a stub now:** Phase 4.5 documentation cleanup created this placeholder so the STR-0342 reference resolves to a real path with an explicit NOT_YET_PRODUCED status, rather than dangling. No calibration has been performed; the dynamic defaults remain `[DYNAMIC — CALIBRATION PENDING]` / `[DYNAMIC-CALIBRATABLE]`.
- **Non-authority:** this file is a derived artifact; `Strategy.md` remains the authority. It does not authorize freezing any dynamic default.
