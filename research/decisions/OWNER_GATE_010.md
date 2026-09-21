# OWNER_GATE_010 — دامنه و تخصیص حسابداری Basket در برابر account (accountValue → Basket)

> خودبسنده. شناسه‌های فنی انگلیسی. مرتبط با: AMB-0008 (و AMB-0002/GATE-004). منابع: SRC-202 (A-002, A-004, D-013, F-005, H-009, I-002, I-003, I-006, I-007)، SRC-201 (§4.10)، N#7. STR متأثر: STR-0224, STR-0234, STR-0248, STR-0159. CAP: CAP-0002, CAP-0010, CAP-0018.

## ۱. زمینه (Context)
`CapitalBase` = `clearinghouseState.marginSummary.accountValue` (incl. unrealized PnL) طبق DECISION-002 و D-13. اما accountValue حقیقتِ کل **account** است، نه لزوماً یک **Basket**. `MaxBasketNotional` (STR-0159/STR-0227)، `BasketNetPnL` (STR-0234)، closure target و residual exposure همه به تخصیص درست به Basket وابسته‌اند.

## ۲. شواهد (Evidence)
- funding/fee/transfer/deposit/withdrawal و فعالیت خارج از Basket، accountValue و PnL را تغییر می‌دهند بدون order استراتژی (D-011, D-013, H-009, I-002, I-003).
- انتساب realized/unrealized PnL، funding و fee به Generation/Cycle/Basket تعریف نشده (I-002, I-003, I-007).
- `Strategy.md` هدف را «یک Basket فعال per market» و top-5 asset می‌گیرد، اما تضمین account اختصاصی صریح نیست.

## ۳. تصمیم دقیق موردنیاز (Exact decision)
دامنهٔ حسابداری Basket چیست و PnL/funding/fee/residual چگونه از سطح account به Basket نسبت داده می‌شوند؟

## ۴. گزینه‌ها (Options)
- **A (dedicated account = Basket):** فرض account اختصاصی؛ accountValue ≈ Basket capital؛ هر انحراف (فعالیت خارجی) طبق GATE-004 contamination و منجر به freeze. تخصیص PnL/funding/fee مستقیم است.
- **B (allocation policy):** تعریف قواعد تخصیص per-Basket (بر پایهٔ fillها/cloidها/timestamp) برای جداکردن سهم Basket از فعالیت account؛ امکان اشتراک account.
- **C:** ترکیب — account اختصاصی به‌علاوهٔ ثبت صریح funding/fee per position از `userFunding`/fill fee برای تخصیص دقیق به Generation/Cycle.
- **D:** گزینهٔ دیگر مالک.

## ۵. پیامدها (Consequences)
- **A:** ساده‌ترین و کم‌ابهام‌ترین؛ اما استفادهٔ چندمنظوره از account را ممنوع می‌کند.
- **B:** انعطاف بالا، ریسک attribution و پیچیدگی زیاد (به GATE-003 وابسته).
- **C:** دقت حسابداری بالا با انضباط account اختصاصی.

## ۶. آنچه مسدود می‌ماند (What remains blocked)
تا این تصمیم، `MaxBasketNotional`، `BasketNetPnL`، closure target و residual-exposure از نظر معنایی به Basket قابل‌انتساب نیستند؛ CAP-0010/0018 و closure (Phase 7) بلوکه می‌ماند. با GATE-004 و GATE-011 هماهنگ شود.

## ۷. توصیه (Recommendation)
**گزینه C** به‌طور عینی پشتیبانی می‌شود: با «یک Basket per market» در `Strategy.md`، DECISION-002 (clearinghouseState authority)، و در دسترس بودن `userFunding`/fill fee در venue (SRC-105/107)، فرض account اختصاصی + تخصیص صریح funding/fee کمترین ابهام و بیشترین انطباق با NET-PnL accounting (STR-0234/0235) را دارد. باید هم‌راستا با GATE-004 ثبت شود.

**STATUS: RESOLVED — Option C (owner, 2026-09-21). See DECISION_REGISTER.md DECISION-011.**
