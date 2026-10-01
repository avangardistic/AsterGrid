# AsterGrid — نقشه راه (Roadmap)

**تاریخ:** 2026-10-01 · **وضعیت:** پیش‌نویس برای تأیید Owner
**ورودی‌ها:** `ASTERGRID_HANDOFF.md`, `docs/contract/CONTRACT_DELTA_ASTER.md` (rev 2), `research/aster/SOURCE_MANIFEST.md`
**این سند فقط برنامه است؛ هیچ کدی را تغییر نمی‌دهد.**

---

## ۰. تصمیم‌های قفل‌شده (OWNER_DECISION، 2026-10-01)

| کد | تصمیم |
|---|---|
| Venue | ASTER DEX (perp, hedge-native). Hyperliquid کنار گذاشته شد (one-way). فارکس ECN = venue دوم، بعداً. |
| G-1 | ST-08 **دوطرفه** (`actual_long`, `actual_short`؛ `actual_net` مشتق) |
| G-2 | endpoint موقعیت Aster = **تنها مرجع** exposure |
| G-3 | شروع برنامه: hedge-mode را **write-then-verify**؛ اگر هنوز false بود → ABORT |
| G-4 | احراز هویت **V3** (API wallet / EIP-712). V1-HMAC استفاده نمی‌شود (کلید جدید V1 از 2026-03-25 ساخته نمی‌شود) |
| OPEN-2 | tolerance **روی هر طرف** (یک مقدار، روی هر طرف اعمال می‌شود؛ پارامتر جدید نداریم) |
| OPEN-3 | margin = **cross**، **Multi-Assets mode** روشن؛ در startup فقط **assert** (نوشتن مجاز نیست مگر Owner بگوید) |

## ۱. نقش‌ها (هیچ نقشی artifact خودش را تأیید نمی‌کند)

| نقش | مسئولیت |
|---|---|
| **Owner** | تصمیم‌های semantic، کلید/امضا، اجازه‌ی Live، پاسخ به Gate‌ها |
| **Architect** (DeepSeek) | پیش‌نویس فاز و پرامپت |
| **Reviewer** | pre-flight پرامپت روی tree واقعی، cross-check گزارش اجرا |
| **Executor** (freebuff / Claude Code) | اجرا روی branch اختصاصی + گزارش |

قاعده‌ی عبور از هر فاز: **Executor → گزارش کامل → Reviewer cross-check → ACCEPT صریح Owner → merge**. بدون ACCEPT هیچ merge یا push به `main` نداریم.

## ۲. گراف وابستگی فازها

```
M ──► P1(ACCEPT) ──► P2 ──► P3a ──► P3b ──► P5b ──► P5c ──► P4 testnet ──► P4 mainnet-small
 │        ▲            ▲
 │        └── P0b ─────┘(کمک می‌کند ولی بلاک نمی‌کند، جز آیتم‌های مشخص)
 └─ (mechanics: بدون وابستگی به قرارداد)
```

---

## ۳. فازها

### فاز M — Migration mechanics (آماده‌ی اجرا)
**هدف:** کد 7h-4b-2 از `hypergrid` وارد `AsterGrid` شود، package → `astergrid`، بدون بازنویسی history.
**کار:** import با `--allow-unrelated-histories` روی branch جدید، provenance، rename، `MIGRATION.md`.
**پرامپت:** `docs/prompts/PROMPT_MIGRATION_FREEBUFF.md`
**Done =** SHA `Strategy.md` ثابت، `pytest` هم‌تعداد baseline، mypy/ruff بدون بدتر شدن، `MIGRATION.md` + `SOURCE_PROVENANCE.md` موجود.
**خطر اصلی:** replace کورکورانه‌ی `hypergrid`→`astergrid` می‌تواند ثابت‌های hash/serialization و golden fileها را عوض کند → در پرامپت STOP دارد.
**بلاک می‌کند:** همه‌ی فازهای کد.

### فاز P0b — تکمیل Grounding (موازی با M)
**هدف:** بستن مواردی که در manifest «NOT verified» ماندند.
**کار (هرکدام یک evidence-file در `research/aster/`):**
1. `exchangeInfo` فیلترها (`tickSize`, `stepSize`, `minNotional`) → §6.3
2. فرمول و cadence funding → §10
3. شکل payload وب‌سوکت: `ACCOUNT_UPDATE`, `ORDER_TRADE_UPDATE`, mark price, depth
4. جدول rate-limit (exchangeInfo `rateLimits`)
5. **تست روی testnet** (نیازمند API wallet برای testnet): OPEN-1 (ردیف leg صفر)، OPEN-4 (سوئیچ hedge با position باز)، OPEN-8 (hedge + Multi-Assets همزمان)، OPEN-9 (مقدار wire برای cross)
6. فیلدهای پاسخ `accountWithJoinMargin` → OPEN-7 (CapitalBase)
**Done =** هر مورد با URL + hash + timestamp + اقتباس verbatim.
**نیاز از Owner:** یک API wallet **testnet** (کلید خصوصی هرگز وارد repo نمی‌شود).

### فاز P1 — Contract delta (پیش‌نویس موجود)
**وضعیت:** `docs/contract/CONTRACT_DELTA_ASTER.md` rev 2 نوشته شده؛ ASTR-001..013.
**باقی‌مانده:**
- ACCEPT رسمی Owner روی سند.
- **OPEN-7** (کدام فیلد = CapitalBase در Multi-Assets) و **OPEN-10** (آیا bot اجازه‌ی write برای `multiAssetsMargin`/`marginType` دارد؟ پیش‌فرض: خیر).
- **OPEN-5**: پیدا کردن همه‌ی «reduce-only»ها در `Strategy.md` (بعد از فاز M ممکن است).
- **مسئله‌ی معماری مهم:** `Strategy.md` immutable است ولی STR-0200/§6.2/§13.4 را عوض می‌کنیم. پیشنهاد: امضای تغییرات در لایه‌ی **overlay** (`STRATEGY_VENUE_ADDENDUM_ASTER.md` + `DECISION_REGISTER`/`STRATEGY_CONTRACT` مشتق)، نه ویرایش `Strategy.md`. **Owner باید تأیید کند** (Gate جدید G-5).
**Done =** سند ACCEPT شده + overlay + رجیستر به‌روز، شمارش‌ها فقط با grep.

### فاز P2 — Engine delta (کد، محدود)
بیشترین ریسک پروژه؛ همه‌ی cascade که pre-flight پیدا کرد اینجاست (C1–C3, C5).
| زیرفاز | محتوا |
|---|---|
| **P2a** | `ActualExposureState` دوطرفه (`exposure_state.py`)، invariant `net = long − short`، `compute_actual_exposure` و `build_exposure_singletons` (`exposure.py`, `hedge.py`)، `P1ExposureMarkers` دوطرفه (`hedge_state.py`) |
| **P2b** | allow-list بسته‌ی `source` (exact-match، بدون prefix) برای `AccountEquityState` و `ActualExposureState` — ASTR-006 |
| **P2c** | `ExposureDelta` per-side + **gate per-side** + تست non-vacuity (ASTR-004): net=0 ولی delta هر طرف > tol ⇒ باید block شود؛ تست باید روی gate قدیمی fail شود |
| **P2d** | `FillEvent.position_side` (`core/events/kinds.py`) — ASTR §7.4 |
| **P2e** | closure §13.4 مستقل برای LONG و SHORT؛ سقف close-qty ≤ `actual_<leg>` (جایگزین reduce-only، ASTR-010) |
| **P2f** | `MaxExposureImbalance` per-side (ASTR-005) |
**قاعده:** هر زیرفاز یک پرامپت جدا + pre-flight جدا؛ ۵۴۴ تست baseline نباید بشکند مگر با توجیه مستند؛ no `float`، no `logging` در core، Decimal، canonical JSON.
**Done =** گیت per-side واقعاً *خوانده* می‌شود (نه فقط ذخیره)، suite سبز، mypy/ruff بدتر نشده.

### فاز P3 — Adapter (7h-5a-ASTER، دو بخش)
**P3a — adapter-only (بدون mapping به state):**
`venue_port.py` (PositionSide فقط `{LONG,SHORT}` روی order؛ `BOTH` هرگز ارسال نمی‌شود)، `mock_venue.py` (دوطرفه، deterministic)، `command_sink.py`، `hedge_mode_assert.py` (الگوریتم کامل ASTR-007 روی port) و `margin_mode_assert.py` (ASTR-012)، رکوردهای venue-neutral (`VenueFill` با `position_side`؛ **بدون** ساخت `FillEvent`). تست ساختاری D16: هیچ import شبکه.
**P3b — mapping (بعد از P2):**
`venue_mapping.py`: positionRisk → `ActualExposureState` دوطرفه (قاعده‌ی sign: SHORT منفی→قدرمطلق؛ ردیف `BOTH` ⇒ read نامعتبر)، account → `AccountEquityState`، mark → `MarketObservationState`.

### فاز P5b — Real V3 client
امضای EIP-712 (وابستگی crypto فقط در `adapters/`؛ انتخاب کتابخانه = تصمیم جدا در `research/tooling/`)، REST، `nonce` میکروثانیه (از `ObservedMeta`)، rate-limit governor (وزن‌ها: GET dual=30، positionRisk=5)، listenKey + WS برای `ACCOUNT_UPDATE` (hint برای re-read، نه مرجع)، خطای `-4225 Nonce Expired` = resync نه blind-retry، `newClientOrderId` ≤ ۳۶ کاراکتر + **query-before-resubmit** (ASTR-011).
**Done =** تست روی testnet؛ هیچ secret در log/event/fixture.

### فاز P5c — `PassRunner` loop
حلقه‌ی اجرا (re-home از طرح HL)، re-assert hedge/margin روی reconnect و خطای positionSide (ASTR-008).

### فاز P4 — تست و gray-launch
1. MockVenue دوطرفه + E3 integration
2. **Testnet paper** (fapi.asterdex-testnet.com) — حداقل یک چرخه‌ی کامل BU+SL همزمان، mirroring، closure دوطرفه
3. **Mainnet اندازه‌ی کوچک** روی **حساب/sub-account اختصاصی** (چون `positionSide/dual` و `multiAssetsMargin` روی *همه‌ی symbolها* اثر می‌گذارند)
4. سپس scale، فقط با اجازه‌ی صریح Owner (Live authorization)

### بعداً — Venue دوم (فارکس ECN)
جلسه‌ی ساعت، gap آخر هفته، swap به‌جای funding، digits/lot/contract-size، mid vs mark. خارج از این نقشه.

---

## ۴. رجیستر ریسک (خلاصه)

| ریسک | کاهش |
|---|---|
| rename خراب‌کننده‌ی hash/golden | grep قبل از rename؛ فقط import و مسیر ماژول؛ STOP در صورت ثابت serialization |
| قراردادِ `Strategy.md` immutable در برابر تغییر STR | overlay + Gate G-5 |
| Cross + Multi-Assets با Hedge ممکن است همزمان ممکن نباشد | OPEN-8 روی testnet قبل از P3a freeze |
| CapitalBase نامشخص در Multi-Assets | OPEN-7 قبل از P3b |
| retry کورکورانه‌ی سفارش (id فقط بین open orders یکتاست) | query-before-resubmit |
| over-close بدون `reduceOnly` | سقف close-qty در bot (ASTR-010) |
| کلید خصوصی نشت کند | signer object، نه رشته‌ی کلید؛ نمونه‌ی کلید داخل مستندات vendor را هرگز کپی نکنید |
| چند agent هم‌زمان روی repo | Part 9 پرامپت: چک git state قبل از هر عملیات؛ branch اختصاصی؛ بدون force-push |

## ۵. اولین سه حرکت

1. Owner: پرامپت `PROMPT_MIGRATION_FREEBUFF.md` را به freebuff بدهد (فاز M).
2. Owner: API wallet testnet بسازد → P0b شروع شود. و OPEN-7/OPEN-10/G-5 را جواب دهد.
3. بعد از گزارش M: Reviewer روی tree واقعی pre-flight پرامپت P2a را انجام دهد.
