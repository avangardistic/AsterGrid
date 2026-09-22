# OWNER_GATE_018 — تثبیتِ Margin Mode (U-7)

> خودبسنده. شناسه‌های فنی به انگلیسی. مرتبط با: AMB-0054. منابع: SRC-204 (`strategy_audit.md` §1 U-7 / R-8)، سند راستی‌آزمایی: `research/findings/U7_VERIFICATION.md` (حکم U_VERIFIED، HIGH). STR متأثر: STR-0223, STR-0340, STR-0225, STR-0227, STR-0337. CAP: CAP-0002, CAP-0017, CAP-0020.

## ۱. زمینه (Context)
Strategy.md هرگز margin mode حساب را تثبیت نمی‌کند؛ حسابِ D-16 (arithmetic ریسک) به‌طور ضمنی **cross** (account-level liquidation) را فرض می‌کند، حال آنکه صرافی حالتِ **isolated** را هم پشتیبانی می‌کند و در آن `margin_available` و `liquidationPx` per-position‌اند. یک حسابِ isolated، حساب‌های D-16 را بی‌اعتبار می‌کند — بی‌سروصدا.

## ۲. شواهد (Evidence)
- **§12.1 (L952–956):** `MaxSafeNotional_margin = CapitalBase × Leverage_effective / 2` — «margin-account liquidation distance … see §16's margin mechanics».
- **§16 D-16 (L1298–1312):** `0.5 / Leverage_effective = MaintenanceMarginFraction`.
- **venue (SRC-107):** `clearinghouseState.assetPositions[].leverage.type ∈ {cross, isolated}`، `position.type` (مثلاً `oneWay`).
- **جست‌وجوی کل‌سند:** هیچ پارامترِ `MarginMode` در Strategy.md وجود ندارد (U7_VERIFICATION.md §4).

## ۳. تصمیم دقیق موردنیاز (Exact decision)
تثبیتِ margin mode به‌صورتِ config‌ِ FIXED.

## ۴. گزینه‌ها (Options)
- **A:** `MarginMode ∈ {cross, oneWay, account-level} = cross` (FIXED؛ تغییرِ مالک تنها از طریقِ یک Owner Gate صریح). بررسیِ config-resolution: اگر حاضر نباشد → **ABORT** پیش از هر side effect. اثباتِ P0 در هر pass: هر position در `clearinghouseState.assetPositions[].leverage.type == MarginMode` و `position.type == oneWay`؛ در غیرِاین‌صورت → **FREEZE**.
- **B:** بدونِ تثبیت (رفتارِ فعلی).
- **C:** حالتِ موردنظرِ مالک.

## ۵. پیامدها (Consequences)
- **A:** یک کلاسِ کاملِ بی‌اعتبارسازیِ خاموشِ مدلِ ریسک را حذف می‌کند.
- **B:** arithmetic ریسک در معرضِ بی‌اعتبارسازیِ خاموش می‌ماند.
- **C:** وابسته به مالک.

## ۶. آنچه مسدود می‌ماند (What remains blocked)
تا تثبیت، اعتبارِ مدلِ ریسک در سراسرِ margin modeها تضمین نمی‌شود (CAP-0002/CAP-0017/CAP-0020).

## ۷. توصیه (Recommendation)
بر پایهٔ U7_VERIFICATION.md (غیرالزام‌آور): **گزینه A**.

**STATUS: RESOLVED — Option A (owner, 2026-09-22). See DECISION_REGISTER.md DECISION-020.**
