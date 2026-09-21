# OWNER_GATE_004 — طبقه‌بندی و مدیریت تغییرات پوزیشن خارج از استراتژی (External position changes)

> خودبسنده. شناسه‌های فنی انگلیسی. مرتبط با: AMB-0002. منابع: SRC-202 (B-002, D-011, D-012, D-013, G-010, H-008, J-004)، SRC-201 (§4.10)، N#11. STR متأثر: STR-0200, STR-0201, STR-0294, STR-0239. CAP: CAP-0002, CAP-0016, CAP-0018, CAP-0023.

## ۱. زمینه (Context)
`ActualExposure` تنها از `clearinghouseState` خوانده می‌شود (DECISION-002). اما position می‌تواند به‌دلایل خارج از intent استراتژی تغییر کند: معاملهٔ دستی اپراتور، liquidation/forced-reduction، transfer/deposit/withdrawal، funding، یا order متعلق به نسخهٔ قبلی/bot دیگر. استراتژی همهٔ تغییرات را یکسان نمی‌بیند و مرز «تغییر ناشی از استراتژی» و «آلودگی خارجی» را تعریف نکرده است.

## ۲. شواهد (Evidence)
- liquidation نه rejection عادی است نه partial fill معمولی؛ اگر در همان کلاس پردازش شود، state و accounting فاسد می‌شود (SRC-202 H-008, D-012).
- transfer/deposit/withdrawal، `CapitalBase` و `accountValue` را تغییر می‌دهد (D-013)؛ funding، PnL را بدون order تغییر می‌دهد (D-011).
- order دستی یا bot دیگر روی همان asset ممکن است exposure ایجاد کند (G-010, J-004).

## ۳. تصمیم دقیق موردنیاز (Exact decision)
سیستم چگونه تغییر پوزیشن «خارج از استراتژی» را تشخیص، طبقه‌بندی و مدیریت می‌کند؟ و آیا account اختصاصی فرض می‌شود؟

## ۴. گزینه‌ها (Options)
- **A (dedicated-account domain constraint):** فرض account اختصاصی/تک-Basket؛ هر exposure غیرقابل‌انتساب به intentهای استراتژی به‌عنوان contamination تلقی و منجر به `RECONCILIATION_REQUIRED`/`FREEZE` می‌شود؛ liquidation یک event class جدا با accounting و freeze مخصوص.
- **B (shared-account با allocation):** تعریف policy انتساب برای جداکردن فعالیت خارجی از عملکرد Basket؛ ادامهٔ کار در حضور فعالیت خارجی.
- **C:** ترکیب — account اختصاصی + کلاس‌بندی صریح liquidation/funding/transfer به‌عنوان eventهای خاص با رفتار تعریف‌شده.
- **D:** گزینهٔ دیگر مالک.

## ۵. پیامدها (Consequences)
- **A:** ساده‌ترین و ایمن‌ترین؛ اما هر دخالت خارجی سیستم را به freeze می‌برد (ممکن است عملیاتی محدودکننده باشد).
- **B:** انعطاف بیشتر، پیچیدگی و ریسک attribution بالاتر (به GATE-010 گره می‌خورد).
- **C:** ایمن و صریح؛ نیازمند مدل‌سازی رسمی liquidation/funding/transfer.

## ۶. آنچه مسدود می‌ماند (What remains blocked)
تا این تصمیم، صحت `ActualExposure`، رفتار در برابر liquidation و مرز accounting در حضور فعالیت خارجی نامعین است. Reconciliation (CAP-0002) و Risk (CAP-0017) نمی‌توانند به‌صورت deterministic طراحی شوند. به GATE-010 (scope حسابداری) وابسته است.

## ۷. توصیه (Recommendation)
**گزینه C** به‌طور عینی پشتیبانی می‌شود: `Strategy.md` صریحاً «یک Basket فعال per market» و «top-5 asset» را هدف می‌گیرد و AI-independent/fail-closed است؛ بنابراین فرض account اختصاصی با کلاس‌بندی صریح liquidation/funding/transfer کمترین ابهام و بیشترین انطباق با اصل «Actual Exposure فقط از وضعیت معتبر صرافی» را دارد. این تصمیم باید با GATE-010 هماهنگ ثبت شود.
