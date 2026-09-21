# OWNER_GATE_013 — شرایط خروج (liveness) از BLOCKED / FREEZE / RECONCILIATION_REQUIRED / RECOVERY

> خودبسنده. شناسه‌های فنی انگلیسی. مرتبط با: AMB-0011. منابع: SRC-202 (B-015, K-012, J-005)، N#13. STR متأثر: STR-0077, STR-0098, STR-0239, STR-0242. CAP: CAP-0018, CAP-0023.

## ۱. زمینه (Context)
سیستم قواعد safety فراوان دارد که به `BLOCKED`، `FREEZE`، `RECONCILIATION_REQUIRED` یا `RECOVERY` منتهی می‌شوند (fail-closed). اما شرط‌های خروج معتبر از این حالت‌ها تعریف نشده‌اند؛ سیستم ممکن است از نظر safety ایمن ولی از نظر liveness دائماً متوقف بماند.

## ۲. شواهد (Evidence)
- ورودها به fail-closed تعریف‌شده‌اند (STR-0077 §5.2، STR-0098 §5.4.1، §13.3 freeze)، اما خروج تعریف نشده (B-015, K-012).
- kill-switch/FREEZE/cancel-all/flatten-all اثرشان روی open order/position/accounting/recovery یکسان تعریف نشده (J-005).
- §13.3: FREEZE فقط ENTRY_INTENT را بلوکه می‌کند و EXPOSURE_CORRECTION مجاز است (STR-0239) — یعنی مبنایی برای resume ایمن وجود دارد.

## ۳. تصمیم دقیق موردنیاز (Exact decision)
شرایط دقیقِ خروج از هر حالت fail-closed چیست، کدام‌ها خودکار (پس از reconcile موفق) و کدام‌ها نیازمند owner clearance‌اند، و kill-switchها چه معنای یکسانی دارند؟

## ۴. گزینه‌ها (Options)
- **A (auto-resume-on-reconcile):** خروج از `RECONCILIATION_REQUIRED`/`BLOCKED` خودکار پس از reconcile موفق و بازگشت invariantها؛ خروج از `FREEZE`/`RECOVERY`/kill-switch نیازمند **owner clearance صریح**؛ همهٔ خروج‌ها با evidence و reason ثبت می‌شوند.
- **B (owner-clearance-for-all):** خروج از هر حالت fail-closed نیازمند تأیید مالک؛ ایمن‌ترین اما کم‌liveness.
- **C (auto-for-all-with-guards):** خروج خودکار از همه پس از تحقق شرط‌های تعریف‌شده؛ بیشترین liveness، نیازمند اثبات دقیق شرط‌ها.
- **D:** گزینهٔ دیگر مالک.

## ۵. پیامدها (Consequences)
- **A:** تعادل liveness/safety؛ حالات گذرا (reconcile) خودکار حل می‌شوند، حالات جدی (freeze/recovery) دست انسان می‌مانند.
- **B:** بیشترین کنترل انسانی، ریسک توقف عملیاتی طولانی.
- **C:** بیشترین liveness، ریسک resume زودهنگام اگر شرط‌ها ناقص باشند.

## ۶. آنچه مسدود می‌ماند (What remains blocked)
تا این تصمیم، اثبات liveness (خروج معتبر از freeze/recovery) در verification فاز ۹ ممکن نیست و رفتار عملیاتی kill-switch نامعین است؛ CAP-0018/0023 در Phase 7 ناقص می‌ماند.

## ۷. توصیه (Recommendation)
**گزینه A** به‌طور عینی پشتیبانی می‌شود: §13.3 صریحاً اجازهٔ EXPOSURE_CORRECTION حین FREEZE را می‌دهد (پس correction/hedge حتی در freeze زنده است)، و resume خودکارِ حالات گذرای reconcile با اصل fail-closed سازگار است، درحالی‌که freeze/recovery/kill-switch به‌دلیل شدت، owner clearance می‌خواهند. هر خروج باید با identity/timestamp/evidence ثبت شود (STR-0171/0315).
