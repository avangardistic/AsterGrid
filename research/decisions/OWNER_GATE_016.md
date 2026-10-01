# OWNER_GATE_016 — کران/بریکرِ funding-bleed (U-2)

> خودبسنده. شناسه‌های فنی به انگلیسی. مرتبط با: AMB-0049. منابع: SRC-204 (`strategy_audit.md` §1 U-2)، سند راستی‌آزمایی: `research/findings/U2_VERIFICATION.md` (حکم U_CONDITIONAL، MED–HIGH). STR متأثر: STR-0234, STR-0235, STR-0236, STR-0246, STR-0221. CAP: CAP-0017, CAP-0018, CAP-0016.

## ۱. زمینه (Context)
هیچ کرانِ ریسکی نرخِ funding-bleed را محدود نمی‌کند؛ تنها کرانِ NET-drawdown یعنی `MaxRangeInducedDD = 100%` **بی‌اثر** است (فقط در equity=0 فایر می‌شود). مسیرِ فاجعه‌بار `6% E₀/hr` تنها تحتِ **halt لایهٔ hedge / اکسپوژرِ گیرکرده** باز می‌شود (تحتِ hedge-liveness عادی، bleed با imbalance کران می‌خورد ~$8/hr).

## ۲. شواهد (Evidence)
- **Strategy.md §12.1 (L908–936):** کران‌ها (`MaxRangeInducedDD=100%`، `MaxExposureImbalance`، `MaxExecutionCost`=فقط fees+slippage، `MaxHedgeCost`، `MaxFailedLevelRate`) — هیچ‌کدام funding را نمی‌بیند.
- **§13.1 (L992–996):** `BasketNetPnL … − BasketFees + BasketFunding`؛ «NET … freeze trigger … closure target»؛ «funding … not negligible».
- **venue AA-4:** funding ساعتی، سقفِ **4%/hour**؛ notional = position × oracle × rate.

## ۳. تصمیم دقیق موردنیاز (Exact decision)
تعریفِ یک funding circuit-breaker با آستانه و پاسخ.

## ۴. گزینه‌ها (Options)
- **A (two-leg breaker):** انباشتگرِ علامت‌دارِ خالص `ACC` روی رویدادهای `userFunding` (dedupِ idempotent با کلید (time,coin,delta))؛ تریگرِ reactive (`ACC ≥ X`) و predictive (`ACC + r̂_F·T_close ≥ X`). نردبانِ پاسخ: warn → suspend new ENTRY_INTENT → emergency Basket closure تحتِ §12.2 (پیش‌شرطِ net-profit **waived**؛ پیش‌شرطِ residual **kept**). `β_F = 0.02` CALIBRATABLE (پیش‌فرضِ fail-closed)؛ `X = β_F·E₀`؛ `T_close = 180 s`.
- **B:** آستانهٔ freeze-trigger مبتنی بر NET را صریح کن (بدون بریکرِ اختصاصی).
- **C:** جایگزینِ موردنظرِ مالک.

## ۵. پیامدها (Consequences)
- **A:** نخستین escalationِ خودکار به closure است — که خودِ §12.2 (تقدمِ ریسک بر انتظارِ سود) مجاز می‌کند؛ bleed را به `X + r̂_F·T_close` کران می‌زند.
- **B:** به معناشناسیِ موجودِ NET-freeze واگذار می‌کند اما کرانِ نرخ را ضمنی می‌گذارد.
- **C:** وابسته به مالک.

## ۶. آنچه مسدود می‌ماند (What remains blocked)
بدون این کران، funding فاجعه‌بار تحتِ hedge-halt هیچ کرانِ محافظتی ندارد (CAP-0017/CAP-0018).

## ۷. توصیه (Recommendation)
بر پایهٔ U2_VERIFICATION.md (غیرالزام‌آور): **گزینه A**.

**STATUS: RESOLVED — Option A (owner, 2026-09-22). See DECISION_REGISTER.md DECISION-018.**
