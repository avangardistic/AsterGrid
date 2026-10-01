# OWNER_GATE_003 — قاعدهٔ انتساب یکتا برای POSITION_VERIFIED (Fill/Delta → Intent/Level)

> خودبسنده. شناسه‌های فنی به انگلیسی. مرتبط با: AMB-0001. منابع ممیزی: SRC-202 (A-003, B-001, D-001, D-010, K-003)، SRC-201 (§4.1)، SRC-203 (§3.5, NC-04). STR متأثر: STR-0071, STR-0072, STR-0129, STR-0131, STR-0199, STR-0293. CAP: CAP-0002, CAP-0003, CAP-0007, CAP-0016. Artifact مرتبط: STRATEGY_CONTRACT.md، STATE_OWNERSHIP.md (ST-04, ST-05, ST-08).

## ۱. زمینه (Context)
`POSITION_VERIFIED` نیازمند «verified exchange fill ∧ authoritative position delta» است (STR-0072). اما داشتن یک fill و یک delta ثابت نمی‌کند که آن delta به کدام order/intent/Level و در کدام زمان تعلق دارد. در حضور چند order نزدیک‌به‌هم، partial fill، hedge و profit هم‌زمان، manual trade، liquidation، funding و eventهای duplicate/out-of-order، انتساب یکتا دشوار است.

## ۲. شواهد (Evidence)
- `clearinghouseState` فقط exposure خالص فعلی (`assetPositions[].position.szi`) را می‌دهد، نه تاریخچهٔ ownership (D-001). `userFills` سقف ۲۰۰۰ و `userFillsByTime` تنها ۱۰۰۰۰ آخر را دارد (D-010).
- ممیزی می‌گوید بدون matching rule بر پایهٔ local intent ID، cloid، venue oid، side، asset، cumulative fill، sequence، freshness و reconciliation window، «Level نباید POSITION_VERIFIED شود» (SRC-201 §4.1).
- دو implementation compliant می‌توانند از یک delta، دو Level متفاوت را verified کنند → تفاوت مشاهده‌پذیر و مؤثر بر lifecycle، exposure، evolution و closure.

## ۳. تصمیم دقیق موردنیاز (Exact decision)
قاعدهٔ رسمی انتساب یک fill/delta به یک intent/Level چیست، و در حالت انتساب غیریکتا رفتار سیستم چیست؟

## ۴. گزینه‌ها (Options)
- **A:** انتساب مبتنی بر `cloid` (هر order یک cloid یکتا) + تطبیق `oid`↔`cloid` از `orderStatus` + تأیید نهایی با delta از `clearinghouseState`؛ در ابهام (چند intent سازگار)، **fail-closed**: Level تأیید نمی‌شود و `RECONCILIATION_REQUIRED` صادر می‌شود.
- **B:** انتساب مبتنی بر پنجرهٔ reconciliation و cumulative-fill matching (بدون اتکای اصلی به cloid)، با tie-break تعریف‌شده؛ در ابهام باز هم fail-closed.
- **C:** ترکیب A به‌علاوهٔ الزام «هر Level تنها یک order فعال دارد» تا انتساب ذاتاً یکتا شود.
- **D:** گزینهٔ دیگر مالک.

## ۵. پیامدها (Consequences)
- **A:** ساده و منطبق بر مکانیزم cloid؛ اما duplicate-cloid dedup در venue مستند نیست، پس باید با orderStatus راستی‌آزمایی شود.
- **B:** مقاوم‌تر در نبود cloid، اما پیچیده‌تر و مستعد ابهام بیشتر.
- **C:** قوی‌ترین تضمین یکتایی؛ محدودکنندهٔ طراحی grid (یک order فعال per Level).
- همهٔ گزینه‌ها در ابهام fail-closed می‌مانند؛ تفاوت در نرخ رخداد ابهام و پیچیدگی است.

## ۶. آنچه مسدود می‌ماند (What remains blocked)
تا تعیین این قاعده، معنای دقیق `POSITION_VERIFIED` (پایهٔ کل سیستم) و در نتیجه پیشروی Cycle، ماشهٔ Evolution و closure از نظر پیاده‌سازی deterministic تعریف‌نشده باقی می‌ماند. Phase 7 (deterministic core) نباید بدون این قاعده شروع شود.

## ۷. توصیه (Recommendation)
**گزینه C** (A + یک order فعال per Level) به‌طور عینی از شواهد پشتیبانی می‌شود: cloid یک هویت مشتری‌محورِ ۱۲۸بیتی است (venue-verified، STR-0133) که با orderStatus و delta قابل راستی‌آزمایی است؛ محدودیت «یک order فعال per Level» ابهام انتساب را ساختاری حذف می‌کند و با اصل «slower verified over fast unverified» (STR-0312) سازگار است. در هر حال، رفتار ابهام باید fail-closed بماند.

**STATUS: RESOLVED — Option C (owner, 2026-09-21). See DECISION_REGISTER.md DECISION-004.**
