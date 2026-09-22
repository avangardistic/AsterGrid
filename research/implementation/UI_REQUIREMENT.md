# UI_REQUIREMENT.md — ورودیِ نام‌گذاری‌شده برای فازِ UI (forward input)

> **وضعیت:** این سند یک **ورودیِ forward** برای فازِ UI (Phase 7b+) است — **نه یک DECISION، نه یک Owner Gate، نه یک STR جدید.** الزامِ مالک را برای فازِ بعد ثبت می‌کند. Producer: Claude Code (Opus 4.8), Phase 7a. شناسه‌های فنی انگلیسی.

## هدف (Purpose)
ثبتِ الزامِ مالک: کاربرِ نهایی (بدونِ دانشِ برنامه‌نویسی) باید بتواند **هر پارامترِ §14 را به‌صورت دستی وارد کند**، پیش از هر فعال‌سازی. این سند مرجعِ آن فاز است؛ در Phase 7a هیچ کدِ UI نوشته نمی‌شود.

## الزام (Requirement)
- **ورودِ کاملِ §14:** فرمِ ورودی از مدلِ Pydantic §14 تولید می‌شود (`hypergrid.config.schema`).
- **۶ tab** مطابقِ ۶ گروهِ پارامتر: Lifecycle & evolution · Grid geometry · Arming & order gates · Execution & emergency · Exposure & risk bounds · Basket closure & economics.
- هر فیلد نمایش می‌دهد: **unit + description + status badge** (FIXED / CALIBRATABLE / [DYNAMIC — CALIBRATION PENDING] / [DYNAMIC-CALIBRATABLE] / DERIVED) **+ validation**.
- فیلدهای **DERIVED** فقط-خواندنی‌اند (محاسبه‌شده؛ کاربر واردشان نمی‌کند).

## گردشِ کار (Workflow)
- **draft → validate → lock** (طبقِ قاعدهٔ سراسریِ §14): مقدارها پیشنهاد می‌شوند، اعتبارسنجی می‌شوند، سپس قفل و binding می‌شوند.
- پارامترهای §14ِ **bind‌شده روی یک Basketِ ACTIVE قابلِ ویرایش نیستند** (قاعدهٔ سراسریِ §14؛ STR-0381).

## پروفایل‌ها (Profiles)
- پروفایل‌های **testnet / live** جدا.

## داشبورد (Dashboard)
- status، NET PnL، funding accumulator، breakerها، reason codeها، freshness، و **tailِ فقط-خواندنیِ operational log**.

## تأییدها (Approvals)
- **owner clearance + kill-switch** با identity + timestamp + audit trail (طبقِ STR-0171 / STR-0380).

## ارجاعاتِ متقابل (Cross-references)
- DECISION-023 (استکِ UI: FastAPI + Jinja/HTMX؛ بدونِ مرحلهٔ build).
- STR-0257 (قاعدهٔ سراسریِ §14 — computed once → binding).
- STR-0171 (auditِ arm/approval — identity + timestamp).
- STR-0380 (kill-switch / cancel-all / flatten-all — اثرِ یکنواخت + audit).
- STR-0381 (versioning/عدمِ ویرایشِ mid-Basket).
- `hypergrid.config.schema` (منبعِ تولیدِ فرم + JSON schema export).
