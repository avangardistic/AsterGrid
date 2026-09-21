# OWNER_GATE_012 — کامل‌کردن رابطهٔ گذارِ Evolution برای مسیرهای پیچیده

> خودبسنده. شناسه‌های فنی انگلیسی. مرتبط با: AMB-0010. منابع: SRC-202 (B-007, B-009, B-010, E-008, E-011)، SRC-201 (§4.8). STR متأثر: STR-0025, STR-0029, STR-0034, STR-0035, STR-0055. CAP: CAP-0006, CAP-0007.

## ۱. زمینه (Context)
§4.1 ماشهٔ Evolution را با شرط path-dependent return و confirmation window تعریف می‌کند، و §4.7 precedence دارد. اما رفتار در چند حالت مرزی کامل نیست: (۱) چند traversal در یک Cycle و تعیین origin group؛ (۲) skip بین origin و return level؛ (۳) بازگشت به سطحی **پایین‌تر** از return level تثبیت‌شده؛ (۴) ساخت candidate جدید پس از `INELIGIBLE_EVOLUTION_CANDIDATE`؛ (۵) هم‌زمانی terminal و return verification.

## ۲. شواهد (Evidence)
- §4.1: return level = بالاترین سطح گروه مقابل که در traversal قبلی POSITION_VERIFIED شده؛ deferred-not-cancelled (STR-0034)؛ fail-closed روی return تأییدنشده (STR-0035).
- §4.7 P3: در هم‌زمانی disable و Evolution، disable مقدم است (STR-0067). §4.5: dominance = origin/traversed group (STR-0055).
- ممیزی: transition relation برای مسیرهای پیچیده و reason codeهای یکتا کامل نیست (B-009, B-010, E-011).

## ۳. تصمیم دقیق موردنیاز (Exact decision)
برای هر یک از پنج حالت مرزی بالا، گذار قطعی (ایجاد/عدم‌ایجاد successor)، origin group، و reason code یکتا چیست؟

## ۴. گزینه‌ها (Options)
- **A (strict/verified-only):** origin = گروهی که نخستین سطحش در Cycle جاری POSITION_VERIFIED شده؛ چند traversal ⇒ نخستین traversalِ تأییدشده مبنا؛ بازگشت به سطح پایین‌تر از return level ⇒ Evolution فایر نمی‌شود (کمتر از شرط)؛ پس از ineligible، فقط re-formation کاملِ شرط در Cycle بعد candidate جدید می‌سازد (STR-0034/0035)؛ هم‌زمانی terminal+return ⇒ طبق §4.7 (Evolution قبل از Cycle، مگر disable که مقدم است).
- **B (permissive):** اجازهٔ candidate جدید در همان Cycle پس از ineligible و پذیرش بازگشت به سطوح نزدیک با tolerance — مستعد double-evolution/starvation.
- **C:** گزینهٔ دیگر مالک.

## ۵. پیامدها (Consequences)
- **A:** با fail-closed، single-in-flight lock و «deferred-not-cancelled» سازگار؛ کمترین ریسک double-evolution؛ محافظه‌کار (ممکن است برخی فرصت‌ها را از دست بدهد).
- **B:** فرصت‌طلب‌تر اما پرریسک از نظر double-evolution و starvation و ابهام reason code.

## ۶. آنچه مسدود می‌ماند (What remains blocked)
تا این تصمیم، CAP-0007 (evolution) و سناریوهای §5.7 در حالات مرزی به‌صورت deterministic قابل پیاده‌سازی/آزمون نیستند؛ differential testing (CAP-0024) نمی‌تواند expected را قطعی کند.

## ۷. توصیه (Recommendation)
**گزینه A** به‌طور عینی پشتیبانی می‌شود: کاملاً از اصول موجود §4.1/§4.4/§4.5/§4.7 مشتق می‌شود (verified-only، single-successor، origin=traversed، disable مقدم)، با fail-closed و «deferred-not-cancelled» سازگار است و double-evolution/starvation را کمینه می‌کند. هر حالت باید reason code یکتا (مثلاً `RETURN_LEVEL_UNVERIFIED`, `SUCCESSOR_LOCK_ACTIVE`, `CYCLE_LIMIT_REACHED`, `GENERATION_ID_LIMIT`) بگیرد.

**STATUS: RESOLVED — Option A (owner, 2026-09-21). See DECISION_REGISTER.md DECISION-013.**
