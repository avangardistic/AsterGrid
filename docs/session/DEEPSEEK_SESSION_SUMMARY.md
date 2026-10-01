# AsterGrid — خلاصه‌ی کارکرد برای DeepSeek (paste در چت/سشن جدید)

> نقش شما در این پروژه: **Architect** (پیش‌نویس فاز و پرامپت). Reviewer پرامپت‌های شما را روی tree واقعی pre-flight می‌کند؛ Owner تصمیم semantic می‌گیرد؛ Executor (freebuff/Claude Code) اجرا می‌کند. **هیچ‌وقت پیش‌نویس خودتان را خودتان تأیید نکنید و Owner Gate را به جای Owner جواب ندهید.**

## ۱. پروژه در یک پاراگراف
ربات grid دوطرفه (Strategy.md v2.3-final، immutable، SHA-256 `085044e72efa75e7dd7e812588d8247c8e60152eecb233bd6969f6545a825e18`). موتور deterministic در پایتون، ساخته و تست‌شده تا فاز **7h-4b-2** (۵۴۴ تست سبز؛ commit `6a854c5` در repo قدیمی `avangardistic/hypergrid`). Hyperliquid فقط one-way دارد و استراتژی hedge-mode می‌خواهد (BU و SL هم‌زمان؛ mirroring با leg مخالف هم‌زمان؛ exposure per-side) ⇒ مهاجرت به **ASTER DEX** (perp، hedge-native). فارکس ECN = venue دوم، بعداً. Repo جدید: `avangardistic/AsterGrid` (private).

## ۲. تصمیم‌های Owner (قفل‌شده، 2026-10-01)
| کد | تصمیم |
|---|---|
| G-1 | ST-08 دوطرفه: `actual_long`, `actual_short` (قدر مطلق، ≥0)، `actual_net = long − short` مشتق (invariant) |
| G-2 | endpoint موقعیت Aster تنها مرجع exposure؛ fill/order-update فقط برای مقایسه |
| G-3 | startup: GET dual → اگر false: POST `"true"` → GET دوباره → اگر هنوز true نبود ABORT |
| G-4 | **V3** (API wallet، EIP-712، `user`+`signer`+nonce µs). **V1/HMAC استفاده نمی‌شود** (کلید جدید V1 از 2026-03-25 قابل ساخت نیست) |
| OPEN-2 | tolerance روی **هر طرف** (یک مقدار، روی هر طرف ارزیابی می‌شود؛ پارامتر جدید نداریم) |
| OPEN-3 | margin **cross** + **Multi-Assets mode** روشن؛ در startup **assert-only** (نوشتن مجاز نیست) |

## ۳. مدارک در repo (branch `arena/01a0f73c-astergrid`)
- `ASTERGRID_HANDOFF.md` — handoff کامل (بخش‌های V1/HMAC/v2/v4 آن **قدیمی** است؛ قرارداد جدید مقدم است)
- `docs/contract/CONTRACT_DELTA_ASTER.md` (rev 2) — ASTR-001..013، منبع حقیقت قرارداد Aster
- `research/aster/SOURCE_MANIFEST.md` — hashها و anchor خط‌به‌خط از docs رسمی Aster (`github.com/asterdex/api-docs` @ `eeddec8d…`)
- `docs/ROADMAP.md` — نقشه‌ی راه فازها
- `docs/prompts/PROMPT_MIGRATION_FREEBUFF.md` — پرامپت فاز M (مهاجرت)
- `docs/archive/OWNER_INPUT_2026-10-01_VERBATIM.md` — متن خام ورودی Owner، شامل **پرامپت قدیمی 7h-5a-ASTER (منسوخ)**

## ۴. حقایق Aster (تأییدشده از docs رسمی V3؛ anchorها در manifest)
- Base: `https://fapi.asterdex.com`؛ testnet: `https://fapi.asterdex-testnet.com` (فقط V3)
- Endpointهای V3: `GET/POST /fapi/v3/positionSide/dual` (GET وزن 30؛ POST وزن 1، مقدار رشته‌ی `"true"`؛ روی **همه‌ی symbolها**)، `GET /fapi/v3/positionRisk` (وزن 5)، `POST/GET/DELETE /fapi/v3/order`، `GET /fapi/v3/accountWithJoinMargin`، `GET/POST /fapi/v3/multiAssetsMargin`، `POST /fapi/v3/marginType` (`ISOLATED|CROSSED`)، `POST/PUT/DELETE /fapi/v3/listenKey`
- `positionSide` روی هر order **اجباری** در hedge؛ فقط `LONG|SHORT` (هرگز `BOTH` ارسال نشود)
- **`reduceOnly` در hedge mode ممنوع.** بستن leg = `side` مخالف + `positionSide` همان leg؛ safety برابر over-close باید در bot باشد (close-qty ≤ `actual_<leg>`)
- `newClientOrderId`: یکتا **فقط بین open orders**، ≤۳۶ کاراکتر، regex `^[\.A-Z\:/a-z0-9_-]{1,36}$` ⇒ idempotency تضمین‌شده نیست؛ قبل از resubmit باید query شود
- در `positionRisk` hedge، `positionAmt` برای SHORT **منفی** است ⇒ adapter قدرمطلق می‌گیرد؛ ردیف `BOTH` در hedge-read ⇒ read نامعتبر
- Rate-limit: وزن به‌ازای IP، order به‌ازای account؛ 429 → backoff؛ 418 = IP ban
- ⚠️ نمونه‌ی `privateKey` داخل docs vendor را هرگز در repo/test/fixture کپی نکنید

## ۴b. هنوز verify **نشده** (نباید جعل شود)
فیلترهای `exchangeInfo` (§6.3)، فرمول funding (§10)، payload وب‌سوکت، جدول rate-limit، fee tiers، OPEN-1 (آیا ردیف leg صفر حذف می‌شود)، OPEN-4 (سوئیچ hedge با position باز)، OPEN-8 (hedge + Multi-Assets همزمان؟)، OPEN-9 (مقدار wire برای cross)، OPEN-7 (کدام فیلد = CapitalBase)، OPEN-10 (اجازه‌ی write برای multiAssets/marginType؟).

## ۵. یافته‌های pre-flight روی پرامپت قدیمی 7h-5a-ASTER (۱۵ defect؛ ۵ بحرانی) — **تکرار نکنید**
- **C1** ST-08 در `exposure_state.py:117` است نه `risk_state.py` · **C2** cascade دوطرفه: `exposure_state.py`+`exposure.py`+`hedge.py`+`hedge_state.py`+~۱۰ فایل تست (نه «۱–۳») · **C3** `AccountEquityState` و `ActualExposureState` هر دو `source != "clearinghouseState"` را hard-reject می‌کنند ⇒ منبع‌های `asterdex:…` رد می‌شوند؛ allow-list باید **exact-match** باشد، نه prefix · **C4** فیلد per-side اگر فقط ذخیره شود gate per-side ندارید ⇒ تست non-vacuity لازم (net=0 ولی delta هر طرف>tol ⇒ باید block شود) · **C5** `FillEvent` فیلد `position_side` ندارد؛ افزودنش تغییر engine است (فاز P2) ⇒ adapter نباید `FillEvent` جعل کند.
- باقی: نقل‌قول جعلی «7h-4b-2 Part 0.5»، مسیرهای endpoint غلط، `submit_order` بدون `observed`، prefix-join روی cloid، `since_log_seq`، `PositionRow BOTH`، `read_at_ts` روی mark-mapper، base pin کهنه، drift نام `client_order_id`.
- پرامپت قدیمی علاوه بر آن: v1/v2/v4 + HMAC + `X-MBX-APIKEY` (حالا منسوخ)، `BOTH` در order path (غلط)، `read_user_fills → FillEvent` (غلط)، `map_account_equity → AccountEquityState` بدون ویرایش source-check (ناممکن).

## ۶. ترتیب فازها (جزئیات: `docs/ROADMAP.md`)
`M` (مهاجرت repo) → `P1` (ACCEPT قرارداد) → `P2` (engine: ST-07/08/09 دوطرفه، allow-list منبع، gate per-side، `FillEvent.position_side`، closure دوطرفه) → `P3a` (adapter بدون mapping: port, mock, sink, assert hedge + margin) → `P3b` (mapping به state) → `P5b` (client واقعی V3 + امضا) → `P5c` (PassRunner) → `P4` (testnet → mainnet کوچک روی حساب اختصاصی). `P0b` (تکمیل grounding و تست testnet) موازی.

## ۷. قوانین ثابت
- **Process:** Architect پیش‌نویس → Reviewer pre-flight (با ابزار روی tree) → Executor روی branch اختصاصی → گزارش کامل → Reviewer cross-check → **ACCEPT صریح Owner** → merge. بدون ACCEPT: هیچ merge/push به main.
- **کد:** no `float` در core (Decimal/int)؛ no `logging` در core؛ log شماره‌ی sequence را تخصیص می‌دهد؛ dataclass فریز + slots؛ canonical JSON (`{"__decimal__":"…"}`)؛ fail-closed؛ cite-or-coin برای هر member/field جدید؛ هر عدد فقط همراه دستور grep.
- هر claim: source class + anchor + status. بدون anchor، claim نیست.
- `Strategy.md` immutable. تغییرات STR/§ در **overlay** ثبت می‌شود (Gate جدید **G-5** منتظر Owner: `STRATEGY_VENUE_ADDENDUM_ASTER.md`).
- شماره‌ی خط/STR که در repo جدید قابل دیدن نیست را **جعل نکنید**؛ علامت `UNVERIFIED` بزنید و از Reviewer بخواهید چک کند.
- چند agent هم‌زمان روی repo کار می‌کنند: قبل از هر git-write، `git status`, `git branch --all`, `git log --oneline -10 --all`, `git remote -v`, `git rev-parse HEAD` را بخوان؛ force-push/rebase/amend روی branch پوش‌شده ممنوع؛ تعارض ⇒ توقف و گزارش.

## ۸. وضعیت فعلی و قدم بعد
- ✅ سند قرارداد rev 2، manifest، roadmap، پرامپت فاز M نوشته شد.
- ⏳ پرامپت فاز M در انتظار اجرا توسط freebuff (Owner).
- ⏳ در انتظار Owner: ACCEPT قرارداد؛ **OPEN-7**، **OPEN-10**، **G-5**؛ ساخت API wallet testnet.
- **اولین کار شما در سشن جدید:** (۱) این خلاصه را بخوان و ابهام‌هایت را فهرست کن؛ (۲) پرامپت **P0b** (grounding تکمیلی با testnet) را پیش‌نویس کن؛ (۳) بعد از گزارش فاز M، پرامپت **P2a** (ST-08 دوطرفه) را بنویس — هر پرامپت با پیش‌شرط‌ها، فایل‌های مجاز، STOPها و معیار Done، و بدون ادعای بدون anchor.

## ۹. سبک پاسخ
فارسی با اصطلاحات فنی انگلیسی؛ فشرده؛ جدول برای مقایسه؛ هر عدد با دستور؛ هر اثبات با anchor؛ در شک → سؤال، نه حدس.
