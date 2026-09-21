# فلسفه و ممیزی منطقی Hypergrid

**وضعیت:** ممیزی مستقل پیش از Phase 5

**مبنای بررسی:** `Strategy.md` نسخهٔ 2.3-final با SHA-256 برابر با `085044e72efa75e7dd7e812588d8247c8e60152eecb233bd6969f6545a825e18`، `prompt.md`، artifacts فازهای 0 تا 4، تصمیم‌های مالک و مستندات رسمی Hyperliquid.

## 1. نتیجهٔ نهایی

| پرسش | نتیجه |
|---|---|
| آیا فازهای 0 تا 4 از نظر روش تحقیق و traceability درست انجام شده‌اند؟ | **عمدتاً بله.** استخراج requirementها، ثبت hash، source governance، capability map، state ownership، failure boundaries و مقایسهٔ معماری با دقت خوبی انجام شده‌اند. |
| آیا `Strategy.md` از نظر مفهومی specification جدی و نسبتاً منسجم است؟ | **بله، اما هنوز اثبات‌شده نیست.** منطق مرکزی قابل فهم است، ولی چند تعریف برای اجرای deterministic کافی نیستند یا به فرض‌های venue وابسته‌اند. |
| آیا همین حالا برای تبدیل مستقیم به ربات production یا Live آماده است؟ | **خیر.** باید ابهام‌های معنایی، attribution پوزیشن، زمان، margin، accounting، replay و recovery حل و با آزمون مستقل تأیید شوند. |

**Traceability مساوی proof نیست.** اینکه هر requirement شناسه دارد ثابت نمی‌کند که requirementها با هم سازگارند یا روی venue قابل تحقق‌اند. چهار فاز اول نقشهٔ خوبی ساخته‌اند، اما هنوز گواهی آمادگی اجرا نیستند.

> یک ربات deterministic زمانی قابل اتکا است که برای هر ورودی معتبر یک گذار یکتا، قابل ثبت و قابل replay داشته باشد؛ و برای هر وضعیت نامعلوم، پاسخ آن fail-closed باشد.

## 2. فلسفهٔ منطقی استراتژی

استراتژی دو لایهٔ مستقل دارد. **Profit Layer** از حرکت رفت‌وبرگشتی بازار در grid استفاده می‌کند. **Hedge Layer** exposure واقعی را داخل envelope نگه می‌دارد و در وضعیت خطر بر Profit Layer مقدم است. سودآوری هیچ‌وقت مجوز عبور از محدودیت ریسک نیست.

ساختار هویتی چنین است:

```text
Basket → Generation → Cycle → Level
```

`Generation` یک epoch استراتژیک، `Cycle` یک traversal در همان Generation و `Level` یک rung قیمت‌گذاری‌شده است. `GenerationID` و `CycleID` مستقل‌اند و هر دو در بازهٔ `0..99` هستند. terminal reach فقط Cycle جدید در همان Generation می‌سازد؛ Generation جدید فقط با traversal-and-return تأییدشده ساخته می‌شود.

اصل کلیدی سند این است:

```text
POSITION_VERIFIED
  = verified exchange fill
    AND authoritative position delta
```

بنابراین acknowledgement، price crossing، requested quantity، یک fill message یا یک رویداد WebSocket به‌تنهایی مجوز transition نیست. تصمیم مالک نیز `clearinghouseState` را تنها منبع معتبر `ActualExposure` و `CapitalBase` قرار داده است؛ این تصمیم با مستندات فعلی Hyperliquid سازگار است.[1] [2]

هرجا evidence ناقص است، سیستم باید `BLOCKED`، `RECONCILIATION_REQUIRED`، `INELIGIBLE_EVOLUTION_CANDIDATE`، `LEVEL_SKIPPED`، `FREEZE` یا `RECOVERY` تولید کند، نه default پنهان.

## 3. ارزیابی چهار فاز اول

### نقاط قوت

1. hash، نسخه و provenance منبع canonical ثبت شده و `Strategy.md` immutable تعریف شده است.
2. `STRATEGY_CONTRACT.md` شامل 343 requirement پیوستهٔ `STR-0001..STR-0343` است.
3. `STRATEGY_COVERAGE.md` headingها را به requirementها متصل می‌کند.
4. ادعاهای venue-dependent در manifest، topic evidence و conflict recordها ثبت شده‌اند.
5. capability map، state ownership و failure-boundary analysis از نظر طراحی منسجم‌اند.
6. تفکیک `desired`، `observed` و `authoritative` state و تقدم Hedge بر Profit تصمیم‌های صحیحی هستند.
7. سه خانوادهٔ معماری materially different مقایسه شده‌اند و برنده‌ای بدون Owner Gate تحمیل نشده است.

### مشکلات مستندسازی

| شدت | مشکل | اقدام |
|---|---|---|
| متوسط | footer `STRATEGY_CONTRACT.md` هنوز snapshot تاریخی Phase 1 را نشان می‌دهد که `[HC]`ها را `UNVERIFIED` اعلام می‌کند، درحالی‌که statusهای بعدی تغییر کرده‌اند. | آن بخش را صریحاً `historical` کنید یا current validation section اضافه کنید. |
| متوسط | `STR-0342` به `CALIBRATION-REPORT.md` ارجاع می‌دهد، اما این فایل در ریپو وجود ندارد. | گزارش را اضافه کنید یا status را `NOT_YET_VERIFIED` کنید. |
| کم | `research/README.md` توضیحات قدیمی Phase 0 را کنار statusهای فازهای بعد نگه داشته است. | snapshots تاریخی را label کنید و current status را جدا بنویسید. |

نتیجه: چهار فاز اول از نظر **روش تحقیق** قابل قبول‌اند، اما از نظر **اثبات runtime** کامل نیستند؛ چون implementation، verification، replay، failure injection و venue integration هنوز انجام نشده‌اند.

## 4. اشکالات منطقی و اجرایی

### 4.1 Attribution برای `POSITION_VERIFIED` — بحرانی

داشتن fill و position delta کافی نیست؛ باید معلوم شود delta به کدام order، intent، Level و زمان تعلق دارد. این مسئله در چند order هم‌زمان، partial fill، fill strategy و hedge نزدیک به هم، manual trade، liquidation، funding، snapshot چندتغییره و eventهای duplicated یا out-of-order دشوار است.

جمع‌کردن exposure به‌تنهایی attribution یکتا ایجاد نمی‌کند. باید matching rule بر اساس local intent ID، cloid، venue oid، side، asset، cumulative fill، sequence، freshness و reconciliation window تعریف شود. اگر انتساب یکتا نیست، Level نباید `POSITION_VERIFIED` شود.

### 4.2 فرض margin در D-16 — بحرانی

Strategy از رابطهٔ `0.5 / Leverage_effective` به‌عنوان maintenance-margin fraction استفاده می‌کند. مستندات Hyperliquid می‌گویند maintenance margin در سطح **maximum leverage دارایی** نصف initial margin همان سطح است؛ این گزاره ثابت نمی‌کند که با user leverage برابر 3، maintenance fraction برابر `0.5/3` است.[3] [4]

باید میان user/effective leverage و maintenance-margin schedule مربوط به asset، tier و account تفاوت گذاشت. بنابراین ادعای «در 3x liquidation distance تقریباً 16.7% است» بدون مدل رسمی liquidation equation theorem نیست. تا زمان مدل‌سازی و controlled observation، D-16 باید hypothesis باقی بماند.

### 4.3 `ExposureTolerance` از minimum trade کوچک‌تر است — زیاد

مثال سند برای BTC در mark price برابر 100,000 دلار، `ExposureTolerance = 0.00005 BTC` است. با minimum trade notional ده دلار، حداقل اندازه در همان قیمت `0.0001 BTC` می‌شود.[5] پس عبارت «one minimum-lot equivalent» دقیق نیست.

Implementation باید تعیین کند tolerance قبل یا بعد از quantization مقایسه می‌شود، tolerance زیر minimum tradable size مجاز است یا نه، round-to-zero چه معنایی دارد و `szDecimals` چگونه از minimum notional جدا می‌شود. Precision lattice و minimum notional باید دو constraint مستقل باشند.

### 4.4 تناقض `CycleReferenceDerivation` — متوسط اما blocking

`§5.4`، `TERMINAL_EXECUTION` را default معرفی می‌کند و هم‌زمان می‌گوید policy باید explicit باشد. این همان `OPEN-01` است. علاوه بر آن، `nominal expected reference price` algorithmically تعریف نشده است. باید معلوم شود nominal از کدام event و کدام قیمت ساخته می‌شود و در partial fill، چند fill، `TERMINAL_MID` و `TERMINAL_VWAP` چه رفتاری دارد.

### 4.5 اثبات non-overlap پس از rounding — زیاد

N1 تا N3 باید روی قیمت نهایی قابل ارسال بررسی شوند، نه فقط real-valued price. full-precision reference، tick rounding و multiplierها می‌توانند دو ladder را پس از normalization روی یک tick بیندازند. آزمون باید تمام priceهای normalized و tick-rounded را بررسی کند؛ overlap باید fail-closed باشد.

### 4.6 `MaxBasketNotional` و depth ناقص — زیاد

استراتژی depth را در بازهٔ `±(10 × StepBps)` از mid می‌سنجد، اما `l2Book` حداکثر 5 level در fast و 20 level در slow ارائه می‌کند.[2] تعداد levelهای موجود تضمین نمی‌کند کل price window پوشش داده شده باشد.

باید `coverage completeness` تعریف شود. اگر snapshot کل window را پوشش نمی‌دهد، `MarketDepth` معتبر نیست و `MaxBasketNotional` باید fail-closed شود.

### 4.7 مدل زمان و clock — زیاد

استراتژی به confirmation شصت‌ثانیه‌ای، emergency wait سی‌ثانیه‌ای، nonce، timestamp و event ordering وابسته است، ولی clock model کامل نیست. باید clock authoritative، رفتار WS gap، ترتیب timestampهای برابر، clock skew هنگام sign و ثبت timer event در replay مشخص شود. برای replay deterministic، observation و timer eventهای مؤثر بر تصمیم باید record شوند.

### 4.8 Evolution برای pathهای پیچیده — زیاد

prior traversal، origin group، highest return level و future re-formation مفاهیم مفیدی هستند، اما transition relation کامل نیست. چند traversal در یک Cycle، skip بین origin و return، بازگشت به سطح پایین‌تر، candidate جدید پس از ineligible candidate و هم‌زمانی terminal و return verification باید به state machine رسمی و reason code یکتا تبدیل شوند.

### 4.9 زمان قفل‌شدن closure target — زیاد

`TotalSystemCosts` lifetime-to-date است، اما `BasketNetProfitClosureTarget` یک‌بار binding می‌شود. اگر بعد از first eligibility funding یا closing costs جدید ایجاد شود، باید مشخص شود در target می‌آیند یا نه. این تنش بین «lifetime-to-date» و «computed once» باید با sequence زمانی رسمی حل شود.

### 4.10 Basket accounting در برابر account accounting — زیاد

`clearinghouseState.accountValue` حقیقت account است، نه لزوماً حقیقت یک Basket. اگر account چند market، manual position یا transfer داشته باشد، نسبت‌دادن accountValue، PnL، funding و fee به یک Basket نیازمند policy جداست. source و attribution برای realized PnL، unrealized PnL، funding، fees، liquidation و transfer باید تعریف شود.

### 4.11 idempotency و identity — زیاد

`cloid` باید از nonce و local intent identity جدا باشد. cloid برای correlation مفید است، اما نباید به‌تنهایی تضمین duplicate-submission deduplication تلقی شود. در timeout بعد از send، سیستم باید با `orderStatus`، open orders، fills و `clearinghouseState` reconcile کند و پیش از روشن‌شدن outcome side effect تازه ندهد.[1] [6]

### 4.12 TWAP parent و closure state — متوسط تا زیاد

TWAP parent با child slices اجرا می‌شود.[1] submission نباید closed تلقی شود، اما mapping parent/child، remaining quantity، cancellation، expiration، crash وسط TWAP و position verification باید formal شود.

### 4.13 operational limits — متوسط

باید برای fill-history window، duplicate snapshots، WS reconnect، REST/WS disagreement، open-order cap، rate-limit backoff، stale meta، تغییر `szDecimals` و تغییر API schema رفتار دقیق تعیین شود.

### 4.14 continuous confirmation — متوسط

اگر evidence بیست ثانیه قطع شود، نبودن داده نباید استمرار condition تفسیر شود. safe default این است که confirmation pause یا reset شود، مگر اینکه freshness proof مستقل وجود داشته باشد.

### 4.15 اندازهٔ بالقوهٔ state — طراحی/کارایی

حد نظری Level instanceها:

```text
100 Generations × 100 Cycles × 12 Levels × 2 Groups = 240,000
```

این مشکل correctness نیست، اما event schema، snapshot، index، retention و query design را به جزء مهم reliability تبدیل می‌کند.

## 5. اصولی که نباید ضعیف شوند

- هیچ transition بر اساس raw price crossing یا intent تنها.
- `clearinghouseState` تنها authority برای ActualExposure و CapitalBase.
- skip یک fact نهایی برای همان instance است و retry نامحدود نیست.
- one-successor-per-Generation دائمی است.
- Generation و Cycle دو محور مستقل‌اند.
- Generation disabled همچنان در accounting و hedge باقی می‌ماند.
- Basket فقط پس از net-profit و residual-exposure verification بسته می‌شود.
- signing از core و event log جداست و secret هرگز وارد آن‌ها نمی‌شود.
- conflict باید ثبت شود، نه اینکه با انتخاب خاموش حذف شود.
- runtime نهایی باید AI-independent باشد.

## 6. چگونه منطق Strategy را اثبات کنیم؟

هیچ خوانش انسانی به‌تنهایی proof نیست. اطمینان باید از آزمون‌های مستقل ساخته شود.

### 6.1 type و unit system

برای قیمت، quantity، bps، USD، زمان، identity، evidence و state domain مشخص تعریف کنید. هر variable باید range، رفتار zero/negative/missing و policy مربوط به NaN/infinite داشته باشد. `szDecimals` و minimum notional را دو constraint جدا نگه دارید.

### 6.2 property-based و invariant testing

حداقل این properties باید همیشه برقرار باشند:

- هیچ G100 یا C100 ساخته نمی‌شود؛
- هر Generation حداکثر یک successor دارد؛
- terminal reach به‌تنهایی Evolution نیست؛
- `POSITION_VERIFIED` بدون fill و delta صادر نمی‌شود؛
- skipped instance resurrect نمی‌شود؛
- freeze، ENTRY_INTENT را متوقف ولی correction را ممکن می‌گذارد؛
- divergence progression را متوقف می‌کند؛
- intent و cloid قبل از side effect durable می‌شوند؛
- replay همان state و decision را می‌دهد؛
- normalization باعث overlap نمی‌شود؛
- tolerance و quantity خارج از domain پذیرفته نمی‌شوند.

### 6.3 exhaustive exploration و reference model

در دامنهٔ کوچک، مثلاً دو Generation، دو Cycle و دو Level، تمام sequenceهای ممکن را explore کنید. سپس reference model مستقلی بسازید که command و observation ثبت‌شده را مصرف کند و `next_state`، intentهای accepted/blocked، eventهای emitted، reason code و invariant result را برگرداند. implementation و model باید differential-test شوند.

### 6.4 crash/replay/failure injection

Process را قبل و بعد از هر نقطهٔ side effect متوقف کنید: قبل از intent، بعد از persist، بعد از sign، بعد از send، بعد از ack، بعد از fill، قبل و بعد از `clearinghouseState`، وسط TWAP و هنگام reconnect. پس از restart، هیچ blind retry مجاز نیست؛ outcome باید از venue reconcile شود.

### 6.5 controlled venue observation

قبل از Testnet یا Live، این موارد را با evidence دارای timestamp، asset، account context و request/response hash اندازه بگیرید: ack در برابر orderStatus؛ fills در برابر position delta؛ partial fills؛ ordering کانال‌های WS؛ mark price؛ depth coverage؛ min notional، tick و lot؛ fee و funding؛ nonce و timeout؛ cloid ambiguity؛ TWAP parent/child؛ reconnect snapshot و gap detection.

### 6.6 معیار عبور پیش از Phase 6

این موارد باید بسته شوند:

1. `OPEN-01`؛
2. nominal reference و attribution rule؛
3. maintenance/liquidation model و بازبینی D-16؛
4. tolerance زیر minimum tradable size؛
5. depth coverage؛
6. clock و event ordering؛
7. closure-cost timing؛
8. Basket/account accounting scope؛
9. statusهای تاریخی contract و artifact مفقود `CALIBRATION-REPORT.md`؛
10. acceptance criteria برای replay، recovery و venue observation.

## 7. تصمیم دربارهٔ Phase 5

Phase 5 می‌تواند از نظر process شروع شود، اما انتخاب معماری هیچ‌کدام از ابهام‌های semantics را حل نمی‌کند. Event sourcing reconstructability را بهتر می‌کند؛ یک log دقیق از تصمیم مبهم، تصمیم درست ایجاد نمی‌کند.

اگر CAND-B انتخاب شود، `ARCHITECTURE_DECISION.md` باید صریحاً بگوید موارد این سند constraints ورودی Phase 6 هستند. هیچ schema یا implementation نباید بر اساس فرض پنهان ساخته شود. هر ambiguity که به دو رفتار ممکن می‌انجامد باید قبل از production به Owner Gate برسد.

## 8. جمع‌بندی فلسفی

ایدهٔ مرکزی Hypergrid درست است: **سرعت کمتر، حقیقت بیشتر**. حقیقت از local bookkeeping، intent یا یک پیام منفرد venue نمی‌آید؛ از observation معتبر، identity matching، authoritative reconciliation، pure decision، event persistence و replay مستقل می‌آید.

این فلسفه الزام سختی ایجاد می‌کند: جایی که evidence ناقص است، سیستم حق ندارد با شهود یا default ادامه دهد. robustness فقط به grid logic وابسته نیست؛ به زمان، identity، attribution، margin، accounting، recovery و freshness نیز وابسته است.

> Strategy زمانی واقعی و قابل اجرا است که برای هر رخداد قابل مشاهدهٔ بازار پاسخ یکتا داشته باشد، برای رخداد نامعلوم پاسخ fail-closed داشته باشد و پس از crash بتواند همان history و همان decision را دوباره بسازد.

در وضعیت فعلی، `Strategy.md` به این هدف نزدیک است، اما هنوز به آن نرسیده است. چهار فاز اول نقشهٔ خوبی ساخته‌اند؛ فازهای بعد باید این نقشه را به semantics قابل‌اثبات و سپس runtime قابل‌آزمون تبدیل کنند.

## References

[1]: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint "Hyperliquid Info endpoint"
[2]: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions "Hyperliquid WebSocket subscriptions"
[3]: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/margining "Hyperliquid margining"
[4]: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/contract-specifications "Hyperliquid contract specifications"
[5]: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/tick-and-lot-size "Hyperliquid tick and lot size"
[6]: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/nonces-and-api-wallets "Hyperliquid nonces and API wallets"
[7]: https://github.com/avangardistic/hypergrid/blob/main/Strategy.md "Hypergrid canonical strategy"
[8]: https://github.com/avangardistic/hypergrid/blob/main/research/strategy/STRATEGY_CONTRACT.md "Hypergrid strategy contract"
[9]: https://github.com/avangardistic/hypergrid/blob/main/research/architecture/STATE_OWNERSHIP.md "Hypergrid state ownership"
[10]: https://github.com/avangardistic/hypergrid/blob/main/research/architecture/FAILURE_BOUNDARIES.md "Hypergrid failure boundaries"
[11]: https://github.com/avangardistic/hypergrid/blob/main/research/architecture/ARCHITECTURE_CANDIDATES.md "Hypergrid architecture candidates"
[12]: https://github.com/avangardistic/hypergrid/blob/main/research/decisions/DECISION_REGISTER.md "Hypergrid owner decisions"
[13]: https://github.com/avangardistic/hypergrid/blob/main/research/sources/hyperliquid/TOPIC_EVIDENCE.md "Hypergrid venue evidence"
[14]: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/robust-price-indices "Hyperliquid robust price indices"
[15]: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint "Hyperliquid exchange endpoint"
[16]: https://github.com/avangardistic/hypergrid/blob/main/research/strategy/STRATEGY_COVERAGE.md "Hypergrid strategy coverage"
[17]: https://github.com/avangardistic/hypergrid/blob/main/research/architecture/CAPABILITY_MAP.md "Hypergrid capability map"
[18]: https://github.com/avangardistic/hypergrid/blob/main/research/findings/CONFLICT-001.md "Hypergrid leverage conflict"
[19]: https://github.com/avangardistic/hypergrid/blob/main/research/findings/CONFLICT-002.md "Hypergrid account-state conflict"
[20]: https://github.com/avangardistic/hypergrid/blob/main/research/findings/CONFLICT-003.md "Hypergrid trigger-basis conflict"
[21]: https://github.com/avangardistic/hypergrid/blob/main/CLAUDE.md "Hypergrid project invariants"
[22]: https://github.com/avangardistic/hypergrid/blob/main/research/README.md "Hypergrid research status"
[23]: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/funding "Hyperliquid funding"
[24]: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees "Hyperliquid fees"
[25]: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/order-types "Hyperliquid order types"
[26]: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/signing "Hyperliquid signing"
[27]: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits "Hyperliquid rate limits and user limits"
[28]: https://github.com/avangardistic/hypergrid/blob/main/research/sources/SOURCE_MANIFEST.md "Hypergrid source manifest"
[29]: https://github.com/avangardistic/hypergrid/blob/main/research/sources/hyperliquid/SDK_RECORD.md "Hypergrid SDK record"
[30]: https://github.com/avangardistic/hypergrid/blob/main/research/architecture/CAPABILITY_COVERAGE.md "Hypergrid capability coverage"
[31]: https://github.com/avangardistic/hypergrid/blob/main/research/architecture/BOUNDARY_CANDIDATES.md "Hypergrid boundary candidates"
[32]: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/twap "Hyperliquid TWAP documentation"
[33]: https://github.com/avangardistic/hypergrid/blob/main/prompt.md "Hypergrid control prompt"
[34]: https://github.com/avangardistic/hypergrid "Hypergrid repository"
