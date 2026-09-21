# OWNER_GATE_006 — مدل ترتیب رویداد و ساعت برای replay قطعی (Event ordering & clock)

> خودبسنده. شناسه‌های فنی انگلیسی. مرتبط با: AMB-0004. منابع: SRC-202 (B-004, E-001, D-009, L-009)، SRC-201 (§4.7)، SRC-203 (NC-03). STR متأثر: STR-0063, STR-0315, STR-0334. CAP: CAP-0005, CAP-0021, CAP-0001.

## ۱. زمینه (Context)
runtime باید deterministic و قابل replay باشد (STR-0315, STR-0334) و passهای §4.7 total-order دارند. اما «ترتیب مرجع» رویدادها (venue sequence، local receive time، server timestamp، logical clock)، رفتار در timestampهای برابر/عقب‌رفته، clock skew هنگام sign و ثبت timer/observation eventها تعریف نشده است. CAND-B (event-sourced) بدون ترتیب canonical، replay غیرقطعی می‌شود.

## ۲. شواهد (Evidence)
- `userFill` ممکن است قبل از `orderStatus`، یا snapshot reconnect قبل از eventهای قدیمی برسد (B-004). ترتیب منطقی و precedence میان REST/WS تعریف نشده (E-001, D-005).
- nonceها در پنجرهٔ `(T-2d, T+1d)` معتبرند و «۱۰۰ nonce بالا» نگه‌داشته می‌شوند (SRC-110)؛ این زمان‌بندی با clock گره خورده است (D-009, L-009).
- برای replay برابر با live، هر observation و timer eventِ مؤثر بر تصمیم باید record شود (SRC-201 §4.7).

## ۳. تصمیم دقیق موردنیاز (Exact decision)
منبع ترتیبِ canonical رویدادها و مدل clock (شامل tie-break، رفتار gap/skew و ثبت eventهای مؤثر بر تصمیم) چیست؟

## ۴. گزینه‌ها (Options)
- **A:** ترتیب canonical = «ترتیب پذیرش رویداد در event log محلی» (ingestion order) با ثبت (venue seq در صورت وجود، server timestamp، local receive time) در هر event؛ tie-break قطعی (venue seq → server ts → local ts → monotonic counter)؛ همهٔ observation/timer eventهای مؤثر record می‌شوند.
- **B:** ترتیب canonical = venue sequence هرجا موجود است، و برای رویدادهای بدون seq، logical clock محلی؛ gap در WS ⇒ `RECONCILIATION_REQUIRED` تا snapshot.
- **C:** ترکیب A+B با قاعدهٔ صریح gap-detection و snapshot reconciliation.
- **D:** گزینهٔ دیگر مالک.

## ۵. پیامدها (Consequences)
- **A:** ساده‌ترین برای replay قطعی (log = مرجع)، اما نیازمند انضباط در ثبت همهٔ ورودی‌های مؤثر بر تصمیم.
- **B:** نزدیک‌تر به «حقیقت venue»، اما جاهایی که seq نیست پیچیدگی logical clock دارد.
- **C:** کامل‌ترین؛ بیشترین کار طراحی.

## ۶. آنچه مسدود می‌ماند (What remains blocked)
بدون این مدل، replay قطعی (سنگ‌بنای CAND-B و verification فاز ۹) و بازسازی state پس از crash تضمین‌شدنی نیست. Phase 6 (implementation plan) و انتخاب رسمی event-model نباید بدون این تصمیم قطعی شود.

## ۷. توصیه (Recommendation)
**گزینه C**: چون معماری منتخب event-sourced (CAND-B) است، «log محلی به‌عنوان مرجع ترتیب» (A) با «gap-detection/snapshot reconciliation» (B) ترکیب می‌شود تا هم replay قطعی و هم سازگاری با حقیقت venue حاصل شود. این با STR-0315/0334 و اصل fail-closed سازگار است. (توصیه از نظر روش پشتیبانی می‌شود؛ جزئیات tie-break باید در Phase 6 ثبت و در CALIBRATION/verification آزموده شوند.)
