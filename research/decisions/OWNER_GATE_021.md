# OWNER_GATE_021 — استکِ runtime/UI و سیستمِ logging

> خودبسنده. شناسه‌های فنی به انگلیسی. مرتبط با: DECISION-023. منابع: `prompt.md`؛ `research/architecture/ARCHITECTURE_DECISION.md` §3–§8؛ `DECISION_REGISTER.md` DECISION-007، DECISION-022. این gate یک تصمیمِ لایهٔ runtime/logging است؛ هیچ STR-* normative را تغییر نمی‌دهد. پاسخ‌ها از پیش توسط مالک تعیین شده‌اند.

## ۱. زمینه (Context)
با تعیینِ زبانِ production (**Python**، DECISION-022) و زبانِ REF-D (**OCaml**، DECISION-021 ADDENDUM)، تصمیم‌های باقی‌ماندهٔ Phase 7 عبارت‌اند از: **(a) استکِ runtime/UI** و **(b) سیستمِ logging**. مالک پاسخ‌ها را از پیش داده است.

## ۲. شواهد (Evidence)
- **prompt.md:** ترجیحِ backend؛ بدونِ external workflow engine؛ بدونِ microservices؛ بدونِ Redis/Kafka برای CAND-B.
- **ARCHITECTURE_DECISION §3–§8:** قیودِ CAND-B؛ signing boundary؛ event log به‌عنوان source of truth؛ recovery/replay.
- **DECISION-007:** ترتیبِ canonical رویداد — logging باید sequenceِ monotonic + timestampها را حفظ کند.
- **DECISION-022:** Python با int/`Decimal` (بدونِ float در مسیرِ تصمیم).

## ۳. تصمیم دقیق موردنیاز (Exact decision)
(a) استکِ runtime/UI؛ (b) سیستمِ logging.

## ۴. گزینه‌ها (Options)

### (a) Runtime / UI stack — پاسخِ مالک (انتخاب‌شده)
- Core: **pure Python، فقط stdlib**، بدونِ هیچ frameworkِ third-party در `core/`.
- Service: **single-process asyncio** (فقط در adapters/runtime).
- Venue client: کلاینتِ نازکِ دست‌ساز HTTP+WS (`httpx` + `websockets`) پشتِ port؛ امضا با `eth-account`؛ SDK رسمیِ Hyperliquid فقط **REFERENCE**، نه وابستگیِ runtime.
- Event store: **SQLite** فایل‌محور پشتِ port (Redis/Kafka طبقِ CAND-B ممنوع).
- Config: مدل‌های **Pydantic v2** مشتق از §14؛ **TOML** روی دیسک، نسخه‌دار.
- UI: **FastAPI (API-first) + Jinja/HTMX** (بدونِ مرحلهٔ build JS).
- Auth: login با username/password + roleهای جدا + آمادهٔ TOTP.
- Deployment: **Docker تک-کانتینر**.

**گزینه‌های خنثیِ مستند (انتخاب‌نشده):** Streamlit برای کنسولِ عملیاتی (فقط ابزارِ offline آینده)؛ کلاینتِ UI مبتنی بر Node/JS build (به‌نفعِ HTMX کنار گذاشته شد).

### (b) Logging system — پاسخِ مالک (انتخاب‌شده)
- **سه log جدا:** (1) DOMAIN event log = همان append-only event store در SQLite (source of truth؛ replayable؛ دائمی)؛ (2) OPERATIONAL log = JSON lines، چرخشی (rotating)؛ (3) OWNER AUDIT trail = دائمی، نمایش در UI.
- `core/` خالص **هرگز log نمی‌کند**؛ تصمیم/رویداد برمی‌گرداند و shellِ runtime log می‌کند (با تستِ خودکار: نبودِ `import logging` در `core/`).
- stdlib `logging` + JSON formatter؛ هر خط دارای `run_id`, `basket_id`, شمارندهٔ monotonic، و timestampهای wall-clock + monotonic؛ server-timestampِ صرافی فقط روی رکوردهای مربوط به رویدادِ صرافی (tuple‌ی watermark، B4).
- **secrets هرگز در هیچ log**؛ payloadِ خامِ صرافی فقط در لبهٔ adapter، فقط در سطحِ debug، با سقفِ اندازه.
- گذارهای fail-closedِ روتین در سطحِ **INFO** با reason code (نه ERROR)؛ ERROR فقط برای شرایطِ نیازمندِ توجهِ اپراتور؛ **بدونِ log-and-continue** در مسیرِ domain.
- **hash chain** روی domain event log (tamper-evident)؛ تستِ redaction در CI.

**گزینه‌های خنثیِ مستند (انتخاب‌نشده):** logging متمرکز از داخلِ core (رد — ناقضِ خلوصِ core)؛ یک log واحدِ درهم (رد — سه نگرانیِ متمایز).

## ۵. پیامدها (Consequences)
همهٔ اجزا **پشتِ port** و درون‌سازگار با CAND-B‌اند (تک‌پراسس، بدونِ engineِ خارجی)؛ هر جزء با یک DECISION قابلِ تعویض است (reversibility متوسط). جداییِ سه‌گانهٔ log با DECISION-007 (ترتیبِ رویداد) و اصلِ «core خالص است» سازگار است.

## ۶. آنچه مسدود می‌ماند (What remains blocked)
بدون این تصمیم‌ها **Phase 7 (Deterministic Core Implementation)** آغاز نمی‌شود.

## ۷. توصیه (Recommendation)
**هیچ** — مالک تصمیم گرفته است؛ تصمیم بدونِ توصیه ثبت می‌شود.

**STATUS: RESOLVED — runtime/UI stack + logging system as specified (owner, 2026-09-22).** See DECISION_REGISTER.md DECISION-023.
