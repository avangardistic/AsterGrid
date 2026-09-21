# OWNER_GATE_011 — زمان‌بندی هزینه در closure target و هزینه‌های دیررس (lifetime-to-date vs computed-once)

> خودبسنده. شناسه‌های فنی انگلیسی. مرتبط با: AMB-0009. منابع: SRC-202 (A-006, E-009, G-014, I-004, I-005, I-008)، SRC-201 (§4.9)، N#10. STR متأثر: STR-0243, STR-0245, STR-0246, STR-0256. CAP: CAP-0018, CAP-0020.

## ۱. زمینه (Context)
`BasketNetProfitClosureTarget = 3 × (TotalSystemCosts + StepBps_as_USD)` (STR-0245) و `TotalSystemCosts` بر پایهٔ **lifetime-to-date** (D-15) است، اما طبق قاعدهٔ سراسری §14 فرمول **یک‌بار** محاسبه و مقدارش binding می‌شود (STR-0246). اگر پس از first-eligibility، funding یا closing cost جدید ایجاد شود، معلوم نیست در target می‌آیند یا نه؛ و اگر correction بعد از closure برسد، آیا Basket بسته می‌ماند.

## ۲. شواهد (Evidence)
- تنش صریح: «lifetime-to-date» (هزینهٔ متغیر و افزایشی) در برابر «computed once → binding» (STR-0246, §14 global rule).
- funding/fee ممکن است پس از close order یا پس از eligibility ثبت شوند (G-014, I-008). closure واقعی تنها پس از fill + delta + residual verification معتبر است (STR-0249/I-005).
- خطر look-ahead accounting اگر target با هزینه‌های آینده محاسبه شود (E-009).

## ۳. تصمیم دقیق موردنیاز (Exact decision)
`TotalSystemCosts` در چه لحظه‌ای snapshot و target قفل می‌شود، هزینه‌های ایجادشده پس از قفل چه اثری دارند، و correction دیررس پس از closure چگونه رفتار می‌شود؟

## ۴. گزینه‌ها (Options)
- **A (lock-at-first-eligibility):** target در نخستین لحظهٔ eligibility با TotalSystemCosts تا آن لحظه قفل می‌شود؛ هزینه‌های بعدی target را تغییر نمی‌دهند اما در `BasketNetPnL` لحاظ می‌شوند (یعنی برای بستن باید NET پس از هزینه‌های جدید همچنان ≥ target باشد). correction پس از closure، closure را بازنمی‌گرداند؛ فقط در accounting تاریخی ثبت می‌شود.
- **B (recompute-until-close):** target تا لحظهٔ closure واقعی با TotalSystemCosts جاری بازمحاسبه می‌شود (نقض ظاهری «computed once» → نیازمند تأیید مالک).
- **C:** ترکیب — target قفل، اما یک آستانهٔ ایمنیِ اضافه برای پوشش هزینه‌های دیررسِ برآوردی.
- **D:** گزینهٔ دیگر مالک.

## ۵. پیامدها (Consequences)
- **A:** با §14 «computed once» سازگار؛ چون هزینه‌های جدید در NET می‌آیند، بستنِ زیان‌ده رخ نمی‌دهد؛ ساده و ایمن. نیازمند سیاست صریح «correction پس از closure = فقط ثبت تاریخی».
- **B:** دقیق‌تر اقتصادی، اما با قاعدهٔ سراسری §14 در تضاد است و نیازمند بازتعریف owner-authorized.
- **C:** محافظه‌کارتر؛ آستانهٔ اضافه ممکن است بستن را دیر کند.

## ۶. آنچه مسدود می‌ماند (What remains blocked)
تا این تصمیم، شرط (a) closure (STR-0244) و رفتار پس از closure در حضور هزینهٔ دیررس نامعین است؛ CAP-0018 (closure) در Phase 7 بلوکه است.

## ۷. توصیه (Recommendation)
**گزینه A** به‌طور عینی پشتیبانی می‌شود: با قاعدهٔ سراسری §14 (formula computed once → binding) سازگار است، از look-ahead accounting جلوگیری می‌کند، و چون هزینه‌های بعدی در `BasketNetPnL` (STR-0234, NET) لحاظ می‌شوند، شرط «net ≥ target» همچنان مانع بستنِ زیان‌ده می‌شود. سیاست «correction پس از closure فقط ثبت تاریخی است» با immutability (STR-0332) سازگار است.
