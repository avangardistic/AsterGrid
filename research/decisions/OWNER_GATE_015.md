# OWNER_GATE_015 — تعریفِ closed-form برای GrossGridEdge (U-1)

> خودبسنده. شناسه‌های فنی به انگلیسی. مرتبط با: AMB-0048. منابع: SRC-204 (`strategy_audit.md` §1 U-1)، سند راستی‌آزمایی: `research/findings/U1_VERIFICATION.md` (حکم U_VERIFIED، HIGH). STR متأثر: STR-0193, STR-0179, STR-0197, STR-0273. CAP: CAP-0013, CAP-0011.

## ۱. زمینه (Context)
`GrossGridEdge` در §10 (L810–819) یک‌بار به‌صورت نمادین به‌کار می‌رود ولی هیچ closed-form ندارد. دروازهٔ الزام‌آورِ arming (`NetExpectedEdge > NetExpectedEdgeFloor`، §8 gate 10) بنابراین از متن استراتژی **محاسبه‌پذیر نیست**؛ دو پیاده‌سازیِ سازگار می‌توانند مقادیرِ متفاوتِ GGE و در نتیجه تصمیم‌های arming متفاوت بدهند (نقض determinism، §15 inv.19).

## ۲. شواهد (Evidence)
- **Strategy.md §10 (L810–819):** `NetExpectedEdge(path) := GrossGridEdge(level, bps) − Fee − EstimatedSlippage − FundingCostEstimate − OtherExecutionCosts`.
- **§8 gate 10 (L752–754):** arming نیازمند `NetExpectedEdge > NetExpectedEdgeFloor (پیش‌فرض StepBps/10 = 1)`.
- **§10 floor (L827–830):** `NetExpectedEdge ≤ floor (either path) → do not arm / do not attempt`.
- `NetExpectedEdgeFloor` در §14 (L1143) تعریف شده؛ اما `GrossGridEdge` در کل سند فقط یک‌بار (L812) ظاهر می‌شود و هیچ فرم بسته/ردیف §14 ندارد (U1_VERIFICATION.md §2/§3).

## ۳. تصمیم دقیق موردنیاز (Exact decision)
تعریفِ `GrossGridEdge` به‌صورت یک closed-form قطعی و replay-safe.

## ۴. گزینه‌ها (Options)
- **A:** `GrossGridEdge := StepBps` (ثابت، قطعی). شرط اعتبار: `GGE − 2·fee_maker − funding_est > floor` در کارمزد Tier-0.
- **B:** فاصله‌تا-ترمینال به‌ازای هر level: `GrossGridEdge := (P_terminal − P_k)/P_terminal × 10⁴`.
- **C:** جایگزینِ موردنظرِ مالک.

## ۵. پیامدها (Consequences)
- **A:** کوچک‌ترین و قطعی؛ سازگار با floorِ StepBps-محور و `StepBps_as_USD` (D-06)؛ یک ثابت.
- **B:** به‌ازای هر level متفاوت است و یک متغیرِ وابسته-به-level وارد می‌کند که در طراحیِ فعلیِ دروازه حاضر نیست.
- **C:** وابسته به ورودی مالک.

## ۶. آنچه مسدود می‌ماند (What remains blocked)
تا تصمیم، قابلیتِ arming دروازهٔ §8 gate-10 به‌شکلِ قطعی و replay-safe قابل‌پیاده‌سازی نیست (CAP-0013/CAP-0011).

## ۷. توصیه (Recommendation)
بر پایهٔ U1_VERIFICATION.md (غیرالزام‌آور): **گزینه A**.

**STATUS: RESOLVED — Option A (owner, 2026-09-22). See DECISION_REGISTER.md DECISION-017.**
