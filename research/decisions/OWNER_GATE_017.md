# OWNER_GATE_017 — تقدمِ گیتینگ برای اصلاحِ acute (U-4)

> خودبسنده. شناسه‌های فنی به انگلیسی. مرتبط با: AMB-0051. منابع: SRC-204 (`strategy_audit.md` §1 U-4)، سند راستی‌آزمایی: `research/findings/U4_VERIFICATION.md` (حکم U_VERIFIED، HIGH). STR متأثر: STR-0168, STR-0197, STR-0185, STR-0206, STR-0207. CAP: CAP-0011, CAP-0015, CAP-0016.

## ۱. زمینه (Context)
برای یک `EXPOSURE_CORRECTION_INTENT` از نوعِ **acute** که `NetExpectedEdge ≤ floor` است (مثلاً hedge در یک liquidity void)، §11.2 («regardless of cost — unconditional») با §8-inv.1/L759، §9.1/L782، و §10 («floor → do not attempt») در تضاد است؛ هیچ تقدمی بیان نشده. دو پیاده‌سازیِ سازگار دقیقاً وقتی یک hedgeِ بقا در میان است، متفاوت رفتار می‌کنند.

## ۲. شواهد (Evidence)
- **§8 inv.1 (L730):** «arm gate NEVER applies to EXPOSURE_CORRECTION_INTENT».
- **§8 (L759):** اصلاح‌ها «pass every other gate» (شاملِ gate 10 economics).
- **§9.1 (L781–784):** emergency Ioc فقط اگر «NetExpectedEdge … clears the configured floor».
- **§10 (L827–830):** «NetExpectedEdge ≤ floor (either path) → do not attempt».
- **§11.2 (L869–874):** acute ⇒ «hedge immediately via Ioc regardless of cost — unconditional»؛ else ⇒ مدلِ §10.

## ۳. تصمیم دقیق موردنیاز (Exact decision)
بیانِ قاعدهٔ تقدم + تثبیتِ گزارهٔ `acute()`.

## ۴. گزینه‌ها (Options)
- **A:** یک قاعدهٔ تقدمِ تک‌جمله‌ای — «کفِ NetExpectedEdge بر `ENTRY_INTENT` و بر `EXPOSURE_CORRECTION_INTENT`ِ **غیرِ-acute** اعمال می‌شود؛ هرگز بر Hedge Recovery‌ِ **acute** (§11.2) اعمال نمی‌شود، که با |ExposureDelta| کران-اندازه و با EmergencyTolerance کران-باند است.» به‌همراه تثبیتِ: `acute(Δ) := |Δ| > τ_I ∨ margin_distance < 2·d_emergency` (τ_I از MaxExposureImbalance §12.1؛ d_emergency از EmergencyTolerance §9.1).
- **B:** تقدم را ضمنی رها کن.
- **C:** جایگزینِ موردنظرِ مالک.

## ۵. پیامدها (Consequences)
- **A:** ترتیبِ گیتینگ را به یک تابعِ تام (بدون هم‌پوشانی، بدون شکاف) تبدیل می‌کند.
- **B:** ابهامی می‌ماند که دو پیاده‌سازی، دقیقاً وقتی یک hedgeِ بقا در خطر است، متفاوت حل می‌کنند.
- **C:** وابسته به مالک.

## ۶. آنچه مسدود می‌ماند (What remains blocked)
بدون این قاعده، رفتارِ اصلاحِ acute در یک void قطعی نیست (CAP-0016/CAP-0011/CAP-0015).

## ۷. توصیه (Recommendation)
بر پایهٔ U4_VERIFICATION.md (غیرالزام‌آور): **گزینه A**.

**STATUS: RESOLVED — Option A (owner, 2026-09-22). See DECISION_REGISTER.md DECISION-019.**
