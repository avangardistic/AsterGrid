# OWNER_GATE_008 — تعریف الگوریتمیِ nominal reference price (§5.4.1)

> خودبسنده. شناسه‌های فنی انگلیسی. مرتبط با: AMB-0006. منابع: SRC-201 (§4.4)، N#4. STR متأثر: STR-0091, STR-0096, STR-0097, STR-0098. CAP: CAP-0008, CAP-0020. مرتبط با OPEN-01/AMB-0042 (ولی جدا از آن).

## ۱. زمینه (Context)
§5.4.1 (STR-0096) الزام می‌کند قیمت reference گرفته‌شده در فاصلهٔ `0.33 × StepBps` از **nominal expected reference price** باشد، وگرنه transition به‌صورت fail-closed `BLOCKED` می‌شود (STR-0098). اما «nominal expected reference price» به‌صورت الگوریتمی تعریف نشده است: از کدام event و کدام قیمت ساخته می‌شود؟

## ۲. شواهد (Evidence)
- §5.4 چهار سیاست capture را تعریف می‌کند (`TERMINAL_EXECUTION` پیش‌فرض، `TERMINAL_VWAP`, `TERMINAL_MID`, `TERMINAL_PLUS_STEP`) که «captured reference» را می‌سازند (STR-0091).
- ولی «nominal» (مقدار موردانتظار که captured با آن مقایسه می‌شود) در سند تعریف نشده؛ ممیزی می‌گوید بدون آن، gateٔ §5.4.1 در دو implementation متفاوت عمل می‌کند (SRC-201 §4.4).
- رفتار nominal در partial fill، چند fill، `TERMINAL_MID` و `TERMINAL_VWAP` نامشخص است.

## ۳. تصمیم دقیق موردنیاز (Exact decision)
nominal expected reference price چگونه و از کدام رویداد/قیمت محاسبه می‌شود، و در partial/چند-fill چه رفتاری دارد؟

## ۴. گزینه‌ها (Options)
- **A:** nominal = قیمت موردانتظارِ سطح ترمینال بر پایهٔ هندسهٔ grid از reference قبلی (یعنی قیمت تئوریکِ همان سطح طبق StepBps/FirstLevelDistance)، و captured = میانگین اجرای واقعی (§5.4)؛ انحراف = |captured − nominal|.
- **B:** nominal = reference قبلی به‌علاوهٔ فاصلهٔ اسمی تا سطح ترمینال؛ معادل A اما با فرمول صریح مبتنی بر §7.1.
- **C:** nominal = mid/mark در لحظهٔ POSITION_VERIFIED سطح ترمینال (مرجع بازار)، با تعریف صریح freshness.
- **D:** گزینهٔ دیگر مالک.

## ۵. پیامدها (Consequences)
- **A/B:** با «execution-grounded reference» (§5.4) و هدف §5.4.1 (جلوگیری از drift) سازگارترند؛ nominal کاملاً از پارامترهای موجود مشتق می‌شود (بدون free parameter جدید).
- **C:** به قیمت بازار در یک لحظه وابسته است و freshness/latency را وارد می‌کند؛ مستعد نویز.

## ۶. آنچه مسدود می‌ماند (What remains blocked)
تا تعریف nominal، gate §5.4.1 (که هر fire شدن Cycle/Generation را کنترل می‌کند) قابل پیاده‌سازی deterministic نیست؛ CAP-0008 و بخش reference-capture در Phase 7 بلوکه است.

## ۷. توصیه (Recommendation)
**گزینه B** (nominal = reference قبلی + فاصلهٔ اسمی سطح ترمینال طبق §7.1) به‌طور عینی پشتیبانی می‌شود: از پارامترهای موجود مشتق می‌شود، free parameter جدید نمی‌سازد، با ماهیت execution-grounded §5.4 و هدف ضدِ-drift §5.4.1 (ضریب 0.33 < 1) سازگار است، و رفتار partial/چند-fill را به همان «captured per §5.4» واگذار می‌کند. OPEN-01 (default vs explicit) باید هم‌زمان تعیین تکلیف شود.
