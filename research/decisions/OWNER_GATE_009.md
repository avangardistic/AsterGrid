# OWNER_GATE_009 — معنای دقیق پیشروی Level تحت partial fill (Terminal eligibility)

> خودبسنده. شناسه‌های فنی انگلیسی. مرتبط با: AMB-0007. منابع: SRC-202 (B-003, B-008, F-009). STR متأثر: STR-0071, STR-0074, STR-0199, STR-0212. CAP: CAP-0003, CAP-0008, CAP-0016.

## ۱. زمینه (Context)
`POSITION_VERIFIED` = fill تأییدشده ∧ position delta (STR-0072)، و exposure از «verified filled quantity» ساخته می‌شود (STR-0199). اما مشخص نیست یک Level با **اولین partial fill**، **مجموع fillها**، **آخرین fill** یا **تکمیل کامل quantity** به مرحلهٔ بعد (مثلاً terminal event / پیشروی lifecycle) می‌رود. §5.1 می‌گوید سطح ترمینال باید POSITION_VERIFIED شود، ولی آستانهٔ کامل‌بودن fill برای «reach» تعریف نشده.

## ۲. شواهد (Evidence)
- venue، partial fill می‌دهد و `userFills`/`clearinghouseState` مقدار تجمعی را نشان می‌دهند (SRC-105/107)؛ §11.4 می‌گوید حین `PARTIALLY_FILLED` سهم exposure = مقدار fillِ تأییدشده تا کنون است (STR-0212).
- ابهام: آیا «terminal reach» نیازمند fillِ **کامل** سطح ترمینال است یا partialِ تأییدشده هم کافی است؟ دو implementation می‌توانند lifecycle را متفاوت جلو ببرند (B-003, B-008).

## ۳. تصمیم دقیق موردنیاز (Exact decision)
آستانهٔ کامل‌بودن fill برای «reach»/terminal-eligibility و برای پیشروی هر Level چیست؟

## ۴. گزینه‌ها (Options)
- **A (full-fill):** یک Level تنها با تکمیل کاملِ quantity (در حد tolerance/quantization) به عنوان «reached/POSITION_VERIFIED کامل» تلقی می‌شود؛ باقیماندهٔ پرنشده طبق §9/§11.4 مدیریت می‌شود.
- **B (verified-cumulative-threshold):** رسیدن exposure تجمعیِ تأییدشده به یک آستانهٔ تعریف‌شده (مثلاً ≥ ۱۰۰٪ − tolerance) کافی است.
- **C:** تفکیک: exposure از هر partialِ تأییدشده شمرده می‌شود (طبق STR-0199/0212)، اما «terminal reach» و پیشروی Cycle نیازمند full-fill است.
- **D:** گزینهٔ دیگر مالک.

## ۵. پیامدها (Consequences)
- **A:** ساده و ایمن؛ اما ممکن است در fillهای همیشه-partial به liveness برخورد کند (به GATE-013 گره می‌خورد).
- **B:** انعطاف بیشتر؛ نیازمند تعریف دقیق tolerance/quantization (به AMB-0014 گره می‌خورد).
- **C:** منطبق‌ترین با متن فعلی (exposure تجمعی + terminal کامل)؛ نیازمند سیاست باقیمانده.

## ۶. آنچه مسدود می‌ماند (What remains blocked)
تا این تصمیم، `TerminalEvent` (STR-0071) و پیشروی Cycle/Generation قطعی نیست؛ CAP-0003/0008 در Phase 7 بلوکه است. با GATE-003 (attribution) و GATE-013 (liveness) و AMB-0014 (quantization) مرتبط است.

## ۷. توصیه (Recommendation)
**گزینه C** به‌طور عینی از متن پشتیبانی می‌شود: STR-0199/0212 صریحاً exposure را از «verified filled quantity» می‌سازند (پس partial باید شمرده شود)، اما §5.1 «reach» سطح ترمینال را برای پیشروی می‌خواهد؛ لذا شمردن exposure از partial + الزام full-fill برای terminal reach، سازگارترین و fail-safe است. سیاست باقیمانده به §9.1/§9.3 (Emergency/Skip) واگذار می‌شود.
