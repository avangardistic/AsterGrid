# دفترچهٔ جامع ایرادات، نقاط تاریک و نواحی خاکستری Strategy

**مبنای بررسی:** `Strategy.md`، `prompt.md`، artifacts فازهای 0 تا 4 و شواهد venue ثبت‌شده در repository.

**دامنه:** این فایل عمداً فقط فهرست ایرادات، تناقض‌ها، ابهام‌ها و حالت‌های شکست است. راه‌حل، roadmap و توصیهٔ اجرایی در آن نیامده است.

## راهنمای شدت

| شدت | معنا |
|---|---|
| بحرانی | می‌تواند حقیقت پوزیشن، ریسک، liquidation یا هویت state را نادرست کند. |
| زیاد | می‌تواند باعث transition، sizing، accounting یا execution نادرست شود. |
| متوسط | در شرایط خاص رفتار مبهم، غیرقابل‌تکرار یا غیرقابل‌ممیزی ایجاد می‌کند. |
| کم | بیشتر به provenance، خوانایی یا نگهداری مربوط است، اما هنوز مانع audit کامل است. |

---

## A. تناقض‌ها و ابهام‌های فلسفی Strategy

### A-001 — fail-closed در برابر default پنهان

**شدت:** بحرانی

Strategy در چند بخش بر fail-closed بودن تأکید می‌کند، اما در بخش‌هایی مانند `CycleReferenceDerivation` یک default معرفی می‌کند و هم‌زمان می‌گوید policy باید explicit باشد. معلوم نیست در نبود owner binding کدام قاعده حاکم است. این تضاد می‌تواند دو implementation compliant اما متفاوت تولید کند.

### A-002 — authoritative state در برابر account-wide state

**شدت:** بحرانی

`clearinghouseState` به‌عنوان authoritative state انتخاب شده، اما این state حقیقت کل account است، نه الزاماً حقیقت Basket یا Generation. اگر account فعالیت خارج از Basket داشته باشد، authoritative بودن account state به‌تنهایی انتساب آن به Basket را ثابت نمی‌کند.

### A-003 — «verified» در برابر «قابل انتساب»

**شدت:** بحرانی

Strategy تأیید را به وجود fill و position delta وابسته می‌کند، اما وجود هر دو evidence لزوماً نشان نمی‌دهد delta متعلق به همان order یا Level است. فلسفهٔ truth verification بدون attribution یکتا ناقص است.

### A-004 — استقلال Profit و Hedge در برابر مشترک‌بودن account state

**شدت:** زیاد

Profit Layer و Hedge Layer از نظر policy مستقل فرض شده‌اند، اما هر دو روی یک account، یک exposure و گاهی یک position عمل می‌کنند. در حضور fill هم‌زمان، معلوم نیست precedence فقط در تصمیم است یا در attribution و accounting نیز اعمال می‌شود.

### A-005 — disabled بودن Generation در برابر ادامهٔ obligation آن

**شدت:** متوسط

Generation غیرفعال می‌شود، ولی همچنان ممکن است accounting، hedge یا closure obligation داشته باشد. مرز دقیق میان «دیگر حق تولید intent ندارد» و «هنوز در محاسبات فعال است» در تمام stateها یکسان تعریف نشده است.

### A-006 — immutable history در برابر اصلاح accounting

**شدت:** زیاد

Event history immutable معرفی می‌شود، اما funding، fee، fill correction و reconciliation ممکن است بعداً تغییر کنند یا دیر برسند. معلوم نیست correction به‌صورت event جدید چگونه با fact قبلی و derived accounting سازگار می‌شود.

### A-007 — عدم استفاده از AI در runtime در برابر پارامترهای calibration‌شده

**شدت:** متوسط

Runtime باید AI-independent باشد، اما calibration، dynamic defaults و بعضی برآوردهای هزینه و liquidity ممکن است از فرآیندهای بیرونی تولید شوند. مرز میان پارامتر deterministic و خروجی تصمیم‌گیر غیرقابل‌بازسازی صریح نیست.

### A-008 — semantics ثابت در برابر venue متغیر

**شدت:** زیاد

Strategy خود را immutable می‌داند، درحالی‌که tick، lot، fee، max leverage، risk tier، API schema و market rules ممکن است تغییر کنند. معلوم نیست immutable بودن specification چگونه با تغییر معتبر venue سازگار می‌شود.

---

## B. ایرادات منطقی و state-machine

### B-001 — انتساب non-unique به `POSITION_VERIFIED`

**شدت:** بحرانی

یک fill و یک delta می‌تواند با چند intent نزدیک به هم سازگار باشد. Strategy تابعی تعریف نمی‌کند که در این حالت کدام Level مالک evidence است. خطر، تأیید جعلی Level و پیشروی اشتباه lifecycle است.

### B-002 — تفکیک نکردن external position change

**شدت:** بحرانی

Manual trade، liquidation، transfer، funding و order قدیمی می‌توانند position را تغییر دهند. Strategy همهٔ تغییرات position را به‌صورت شفاف به strategy intent یا external contamination تفکیک نمی‌کند.

### B-003 — ابهام در partial fill

**شدت:** زیاد

مشخص نیست Level با اولین partial fill، مجموع fillها، آخرین fill یا تکمیل quantity به مرحلهٔ بعد می‌رود. cumulative fill، remaining quantity و وضعیت fillهای دیررس در همهٔ transitionها یکسان تعریف نشده‌اند.

### B-004 — out-of-order event

**شدت:** زیاد

ممکن است `userFill` قبل از `orderStatus`، snapshot قبل از event قدیمی یا position state بعد از تصمیم محلی دریافت شود. ترتیب منطقی eventها و precedence میان sourceهای مختلف کامل تعریف نشده است.

### B-005 — duplicate event و duplicate snapshot

**شدت:** زیاد

Subscription reconnect ممکن است snapshot تکراری بدهد و fill یا update ممکن است دوباره دیده شود. قواعد deduplication برای هر نوع event، snapshot و cumulative state صریح نیست.

### B-006 — one-successor-per-Generation در برابر concurrent trigger

**شدت:** زیاد

قانون یک successor منطقی است، اما در اجرای هم‌زمان چند worker یا restart میان persist و transition معلوم نیست قفل مالکیت successor کجا و چگونه برقرار می‌شود.

### B-007 — independent بودن GenerationID و CycleID در برابر lifecycle وابسته

**شدت:** متوسط

دو محور مستقل معرفی شده‌اند، اما successor Generation به traversal و return Cycle قبلی وابسته است. مرز «استقلال هویتی» و «وابستگی transition» در چند حالت مرزی مبهم است.

### B-008 — terminal reach در برابر terminal execution

**شدت:** زیاد

Strategy به‌درستی price crossing را کافی نمی‌داند، اما شرایطی که execution از نظر venue پذیرفته، partially filled، cancelled یا expired است برای terminal eligibility کاملاً جدا نشده‌اند.

### B-009 — return verification چندمعیاره

**شدت:** زیاد

برای return ممکن است هم price reference، هم strategy order، هم position delta و هم confirmation window لازم باشد. precedence و ترتیب evaluation این شروط در حالت‌هایی که بعضی شواهد دیر می‌رسند مشخص نیست.

### B-010 — Evolution پس از candidate نامعتبر

**شدت:** متوسط

پس از `INELIGIBLE_EVOLUTION_CANDIDATE` معلوم نیست candidate برای همیشه مرده است، قابل revalidation است یا یک candidate جدید با identity جدید ساخته می‌شود. این ابهام می‌تواند باعث double evolution یا starvation شود.

### B-011 — skip به‌عنوان fact در برابر re-entry

**شدت:** زیاد

`LEVEL_SKIPPED` نهایی فرض می‌شود، اما معلوم نیست پس از تغییر market metadata، اصلاح calibration یا restart آیا همان Level دوباره ارزیابی می‌شود یا نه.

### B-012 — precedence میان P0 تا P6 در هم‌زمانی

**شدت:** زیاد

اولویت‌های global تعریف شده‌اند، اما اگر در یک event window هم‌زمان emergency hedge، closure eligibility، Evolution و manual intervention رخ دهند، ترتیب atomic تصمیم‌ها به‌طور کامل formal نشده است.

### B-013 — وضعیت نامعلوم پس از timeout

**شدت:** بحرانی

پس از timeout در ارسال order، ممکن است order در venue پذیرفته شده باشد. Strategy ممنوعیت blind retry را القا می‌کند، اما state رسمی میان `UNKNOWN_SUBMISSION`، `RECONCILING` و `CANCEL_PENDING` کامل نیست.

### B-014 — recovery در میانهٔ transition

**شدت:** زیاد

اگر process بعد از fill و قبل از persistence state متوقف شود، معلوم نیست event authority از log محلی است یا venue snapshot. احتمال ایجاد state دوگانه وجود دارد.

### B-015 — لiveness نامشخص

**شدت:** زیاد

Safety rules فراوان‌اند، اما شرایطی تعریف نشده که ثابت کند سیستم از `BLOCKED`، `FREEZE`، `RECONCILIATION_REQUIRED` یا `RECOVERY` می‌تواند دوباره خارج شود. سیستم ممکن است از نظر safety امن اما از نظر liveness دائماً متوقف باشد.

### B-016 — نبود invariant برای عدم تولید order متناقض

**شدت:** زیاد

one-successor و exposure rules وجود دارند، اما invariant عمومی برای جلوگیری از دو order مخالف یا order جدید روی Levelی که هنوز outcome قبلی آن نامعلوم است صریح نیست.

---

## C. ایرادات ریاضی، فرمولی و واحدها

### C-001 — maintenance margin به‌صورت `0.5 / EffectiveLeverage`

**شدت:** بحرانی

این رابطه maintenance schedule دارایی و tier را با user leverage مخلوط می‌کند. از مستندات venue نمی‌توان بدون مدل بیشتر نتیجه گرفت که maintenance fraction در user leverage برابر `L` دقیقاً `0.5/L` است. هر threshold مبتنی بر این فرض بالقوه نادرست است.

### C-002 — liquidation distance غیراثبات‌شده

**شدت:** بحرانی

عبارت‌هایی مانند «در 3x فاصلهٔ liquidation تقریباً 16.7% است» بدون واردکردن mark price، account equity، maintenance tier، fee، funding، cross-margin و سایر قواعد venue، برهان کامل نیستند.

### C-003 — واحدهای مخلوط در `StepBps_as_USD`

**شدت:** زیاد

تبدیل StepBps به هزینهٔ دلاری به قیمت، quantity، notional و side وابسته است. معلوم نیست در همهٔ فرمول‌ها bps بر price اعمال شده، بر notional یا بر quantity. احتمال خطای واحد وجود دارد.

### C-004 — `ExposureTolerance` زیر minimum tradable size

**شدت:** زیاد

در مثال BTC با قیمت 100,000 دلار، tolerance برابر 0.00005 BTC و minimum trade ده دلار برابر 0.0001 BTC است. مقایسهٔ raw quantity با tolerance کوچک‌تر از lattice قابل معامله ممکن است به unreachable target منجر شود.

### C-005 — floating-point و equality

**شدت:** زیاد

Strategy برای price، quantity، exposure، tolerance و PnL به equality و inequality حساس است، اما representation عددی و rounding mode رسمی در همهٔ فرمول‌ها مشخص نیست.

### C-006 — rounding direction در risk

**شدت:** زیاد

در order sizing، exposure tolerance، max basket notional و hedge quantity معلوم نیست rounding به سمت محافظه‌کارانه، نزدیک‌ترین tick یا سمت دیگر انجام می‌شود. جهت rounding مستقیماً بر ریسک اثر دارد.

### C-007 — non-overlap فقط پیش از normalization

**شدت:** زیاد

ممکن است دو قیمت real-valued جدا باشند، اما پس از tick rounding یکسان شوند. اگر invariant روی قیمت نهایی قابل ارسال اعمال نشود، non-overlap اثبات نشده است.

### C-008 — dynamic defaultهای وابسته به زمان

**شدت:** متوسط

پارامترهایی که با mark، leverage، liquidity یا cost تغییر می‌کنند، زمان snapshot واحدی ندارند. نتیجه ممکن است به ترتیب رسیدن data وابسته شود.

### C-009 — حد نظری state بدون مدل storage

**شدت:** متوسط

حد نظری 240,000 Level instance وجود دارد، اما complexity فرمول‌ها، حجم event، retention و query cost در specification وارد نشده است. امکان دارد implementation از نظر محاسباتی به state درست دسترسی نداشته باشد.

### C-010 — جمع‌پذیری هزینه‌ها

**شدت:** زیاد

فرض شده هزینه‌های strategy order، hedge، close، funding و fee به‌سادگی جمع می‌شوند. تفاوت realized و accrued cost و timing settlement ممکن است این جمع را غیرخطی یا زمان‌مند کند.

---

## D. ایرادات دریافت اطلاعات از venue

### D-001 — کفایت `clearinghouseState` برای attribution

**شدت:** بحرانی

`clearinghouseState` exposure فعلی را نشان می‌دهد، اما به‌تنهایی تاریخچهٔ intent و ownership را نشان نمی‌دهد. استفاده از آن به‌عنوان تنها authority برای account state، attribution را حل نمی‌کند.

### D-002 — محدودیت depth در `l2Book`

**شدت:** زیاد

تعداد levelهای بازگشتی الزاماً کل price window مورد نیاز را پوشش نمی‌دهد. snapshot ناقص ممکن است به‌اشتباه به‌عنوان MarketDepth کامل وارد sizing شود.

### D-003 — freshness و stale data

**شدت:** زیاد

حداکثر عمر مجاز برای mark، book، meta، fees، leverage، account state و fills یکسان یا به‌صورت کامل تعریف نشده است.

### D-004 — قطع WebSocket و فقدان gap

**شدت:** بحرانی

در زمان قطع stream معلوم نیست چه eventهایی از دست رفته‌اند و از کدام نقطه باید replay یا snapshot انجام شود. absence of data نباید به استمرار condition تعبیر شود، اما این قاعده در همهٔ بخش‌ها صریح نیست.

### D-005 — اختلاف REST و WebSocket

**شدت:** زیاد

اگر REST snapshot و WebSocket event با هم متفاوت باشند، source precedence، timestamp precedence و reconciliation outcome مشخص نیست.

### D-006 — API schema drift

**شدت:** متوسط

تغییر field، enum، endpoint یا semantics در venue می‌تواند parser را silently خراب کند. Strategy version و API version binding کامل نیست.

### D-007 — تغییر market metadata در طول lifecycle

**شدت:** زیاد

تغییر tick، szDecimals، max leverage، fee tier یا risk tier می‌تواند Levelهای قبلی را نامعتبر کند. اثر این تغییر بر immutable history و active orders مشخص نیست.

### D-008 — mark price در برابر mid و execution price

**شدت:** زیاد

Strategy از mark، mid، execution و reference price استفاده می‌کند، اما در تمام triggers و eligibilityها مرز این قیمت‌ها و precedence آن‌ها یکسان نیست.

### D-009 — timestamp و clock skew

**شدت:** زیاد

زمان venue، زمان local و زمان دریافت پیام ممکن است متفاوت باشند. Strategy tolerance زمانی و source زمان معتبر را برای همهٔ تصمیم‌ها مشخص نمی‌کند.

### D-010 — user fills history ناقص

**شدت:** زیاد

history API ممکن است window محدود داشته باشد یا در زمان reconnect همهٔ fillها در دسترس نباشند. Strategy معلوم نمی‌کند با evidence ناقص چگونه ownership را رد یا تأیید می‌کند.

### D-011 — funding event و position delta

**شدت:** متوسط

Funding می‌تواند account value و PnL را تغییر دهد بدون اینکه strategy order ایجاد شده باشد. خطر اشتباه‌گرفتن accounting change با position change وجود دارد.

### D-012 — liquidation و forced reduction

**شدت:** بحرانی

Forced close یا liquidation می‌تواند exposure را تغییر دهد و lifecycle را از مسیر عادی خارج کند. رفتار رسمی Strategy در این حالت، از تشخیص تا accounting و freeze، کامل نیست.

### D-013 — انتقال وجه و account contamination

**شدت:** زیاد

Deposit، withdrawal، transfer یا activity خارج از Basket می‌تواند CapitalBase و accountValue را تغییر دهد. allocation rule برای جداکردن این تغییرات از performance Strategy کامل نیست.

### D-014 — open-order state ناقص

**شدت:** زیاد

محدودیت تعداد open order، orderهای قدیمی، orderهای متعلق به نسخهٔ قبلی و orderهای manual در Strategy به‌صورت کامل از هم جدا نشده‌اند.

### D-015 — نرخ درخواست و محدودیت venue

**شدت:** متوسط

Backoff، rate-limit exhaustion، order cap و محدودیت connection می‌توانند باعث تأخیر شوند، اما مدل تأخیر و اثر آن بر timer و risk window صریح نیست.

---

## E. ایرادات پردازش و تصمیم‌گیری اطلاعات

### E-001 — نبود event ordering رسمی

**شدت:** بحرانی

معلوم نیست eventها بر اساس venue sequence، local receive time، server timestamp یا logical clock مرتب می‌شوند. بدون ordering رسمی، replay قطعی نیست.

### E-002 — نبود مدل atomicity

**شدت:** زیاد

مرز atomic میان persist intent، sign، send، receive fill، reconcile و transition مشخص نیست. crash در هر مرز می‌تواند state محلی و venue را جدا کند.

### E-003 — وضعیت `UNKNOWN`

**شدت:** بحرانی

برای بسیاری از موارد failure حالت‌های `UNKNOWN` وجود دارد، اما distinction میان unknown order، unknown fill، unknown exposure و unknown accounting به‌صورت رسمی تعریف نشده است.

### E-004 — freshness در confirmation window

**شدت:** زیاد

«continuous confirmation» معلوم نمی‌کند آیا condition باید پیوسته در زمان واقعی برقرار باشد یا فقط در eventهای دریافت‌شده. gap داده ممکن است به false continuity منجر شود.

### E-005 — محاسبه با snapshotهای ناهم‌زمان

**شدت:** زیاد

Price، depth، account state، fills و metadata ممکن است متعلق به زمان‌های مختلف باشند. Strategy یک consistency boundary برای snapshot ترکیبی تعریف نمی‌کند.

### E-006 — race بین Hedge و Profit

**شدت:** بحرانی

Profit order ممکن است درست پیش از مشاهدهٔ exposure breach ارسال شود و Hedge order هم‌زمان فعال شود. precedence در سطح intent کافی نیست؛ ordering side effect و cancellation نیز باید یک معنا داشته باشد، اما کامل تعریف نشده است.

### E-007 — race میان closure و new entry

**شدت:** زیاد

ممکن است Basket واجد شرایط closure شود، اما قبل از ثبت closure order، market condition یک entry تازه را فعال کند. lock و lifecycle boundary این رقابت کاملاً formal نشده است.

### E-008 — race میان Evolution و disable

**شدت:** زیاد

ممکن است return و risk breach هم‌زمان مشاهده شوند. معلوم نیست Evolution candidate قبل از disable معتبر می‌ماند یا global risk آن را باطل می‌کند.

### E-009 — محاسبهٔ هزینه با اطلاعات آینده

**شدت:** زیاد

اگر target closure با هزینه‌های آینده یا lifetime cost محاسبه شود، خطر look-ahead accounting وجود دارد. زمان مشاهده و زمان binding در همهٔ فرمول‌ها جدا نشده‌اند.

### E-010 — وابستگی پنهان به ترتیب iteration

**شدت:** متوسط

اگر چند Level یا چند event واجد شرایط باشند، معلوم نیست انتخاب بر اساس price، ID، زمان، severity یا ترتیب ذخیره‌سازی انجام می‌شود. این می‌تواند خروجی را به implementation detail وابسته کند.

### E-011 — نبود دلیل یکتای transition

**شدت:** متوسط

در بعضی transitionها چند شرط هم‌زمان می‌توانند برقرار باشند، اما reason code و causal chain یکتا نیست. audit بعدی نمی‌تواند بفهمد کدام شرط غالب بوده است.

### E-012 — state derivation غیرقابل بازسازی

**شدت:** زیاد

برخی stateها از dynamic default، آخرین snapshot یا cache محاسبه می‌شوند، اما ورودی دقیق آن‌ها در event history ذخیره نمی‌شود. replay ممکن است با live execution متفاوت شود.

### E-013 — calibration versioning

**شدت:** زیاد

پارامترهای calibration، liquidity factor و cost assumption نسخه و effective time مشخص ندارند. تغییر آن‌ها ممکن است گذشته را در replay بازنویسی کند.

### E-014 — failure در parser یا schema validation

**شدت:** متوسط

رفتار در برابر field ناشناخته، field مفقود، مقدار خارج از domain و schema version ناشناخته در تمام sourceها یکسان نیست.

---

## F. ایرادات خروجی‌ها و stateهای تولیدشده

### F-001 — خروجی تصمیم بدون evidence کافی

**شدت:** بحرانی

برخی خروجی‌های lifecycle مانند eligibility، closure یا Evolution ممکن است از چند evidence مشتق شوند، اما contract اجباری برای فهرست کامل evidenceهای مؤثر وجود ندارد.

### F-002 — تفاوت desired و observed در خروجی نهایی

**شدت:** زیاد

ممکن است desired state بسته یا hedge شده باشد، درحالی‌که observed state هنوز باز است. نام‌گذاری و نمایش این تفاوت در خروجی نهایی می‌تواند باعث گزارش closure جعلی شود.

### F-003 — اعلام success پیش از settlement

**شدت:** بحرانی

acknowledgement یا order submission ممکن است در خروجی به‌عنوان success گزارش شود، درحالی‌که fill و position delta هنوز تأیید نشده‌اند.

### F-004 — گزارش exposure بدون freshness

**شدت:** زیاد

عدد exposure بدون timestamp، source، age و reconciliation status ممکن است current تلقی شود، درحالی‌که stale است.

### F-005 — گزارش PnL بدون allocation proof

**شدت:** زیاد

NET PnL account ممکن است به Basket نسبت داده شود بدون اینکه سهم funding، fee، manual activity یا سایر marketها اثبات شده باشد.

### F-006 — نبود reason code برای block

**شدت:** متوسط

اگر خروجی فقط `BLOCKED` باشد، معلوم نیست علت missing evidence، stale data، ambiguity، risk breach، venue rejection یا owner gate بوده است.

### F-007 — فقدان provenance در dynamic values

**شدت:** زیاد

برای dynamic defaults معلوم نیست مقدار با کدام mark، book، fee، calibration version و timestamp ساخته شده است.

### F-008 — ناسازگاری خروجی در restart

**شدت:** زیاد

اگر خروجی شامل cache، local time یا ترتیب دریافت باشد، ممکن است پس از restart همان inputها خروجی متفاوت تولید کنند.

### F-009 — خروجی ناقص در وضعیت partial success

**شدت:** زیاد

TWAP، partial fill، partial hedge و partial close به خروجی‌هایی نیاز دارند که مقدار باقی‌مانده و exposure residual را نشان دهند. contract این وضعیت‌ها را در همهٔ مسیرها یکسان مشخص نمی‌کند.

### F-010 — ambiguity در output identity

**شدت:** متوسط

شناسهٔ output، intent، order و state همیشه از هم جدا نیستند. امکان دارد consumer یک output را به‌اشتباه به‌عنوان venue fact تفسیر کند.

---

## G. ایرادات اجرایی و تعامل با Hyperliquid

### G-001 — تفاوت acknowledgement و execution

**شدت:** بحرانی

پذیرفته‌شدن request در exchange اثبات fill، position change یا closure نیست. اگر consumer این سطوح را تفکیک نکند، side effectهای زنجیره‌ای نادرست می‌شوند.

### G-002 — cloid به‌عنوان idempotency کامل

**شدت:** زیاد

cloid برای correlation مفید است، اما به‌تنهایی هویت local intent، nonce و deduplication venue را حل نمی‌کند. timeout و duplicate submission همچنان ambiguous می‌مانند.

### G-003 — nonce و replay control

**شدت:** زیاد

مدل nonce، clock skew، expiresAfter، persistence و recovery آن به‌اندازهٔ lifecycle order formal نشده است.

### G-004 — TWAP parent/child mapping

**شدت:** زیاد

parent order، child slice، remaining quantity، cancellation، expiration و fill aggregation به‌طور کامل به Level و Basket متصل نشده‌اند.

### G-005 — cancellation outcome

**شدت:** زیاد

ارسال cancel اثبات cancellation نیست. Strategy وضعیت order در فاصلهٔ send cancel تا authoritative confirmation را کامل مدل نمی‌کند.

### G-006 — order rejection و retry

**شدت:** زیاد

برای rejectionهای مختلف مانند precision، margin، rate limit، invalid price و risk limit، تفاوت میان skip، retry، recalculation و freeze همیشه روشن نیست.

### G-007 — market order و slippage

**شدت:** زیاد

در market order، execution price می‌تواند از nominal price فاصله بگیرد. اثر slippage بر reference، cost، closure و non-overlap در همهٔ مسیرها کامل نیست.

### G-008 — trigger basis

**شدت:** زیاد

استفاده از mark، oracle، mid یا execution برای triggerها باید یکتا باشد؛ تفاوت این price bases در Strategy و venue evidence می‌تواند باعث trigger ناهمسان شود.

### G-009 — تغییر position mode یا margin mode

**شدت:** زیاد

cross/isolated، one-way/hedge mode و تنظیمات account می‌توانند semantics exposure و liquidation را تغییر دهند، اما precondition آن‌ها در Strategy کامل نیست.

### G-010 — external manual order

**شدت:** زیاد

order manual یا bot دیگری ممکن است همان asset را معامله کند. Strategy قواعد مالکیت account و رفتار در برابر interference را کامل نمی‌کند.

### G-011 — open-order limit و collision

**شدت:** متوسط

Grid با تعداد زیاد Level ممکن است به محدودیت open orders یا collision با orderهای قبلی برسد. تخصیص cap به Basket و recovery بعد از cap روشن نیست.

### G-012 — reconnect و snapshot replay

**شدت:** بحرانی

بدون gap detection و snapshot reconciliation، order یا fill ممکن است از دست‌رفته، تکراری یا با ترتیب غلط پردازش شود.

### G-013 — API version drift

**شدت:** متوسط

وابستگی به SDK یا endpoint بدون pin کردن semantics نسخه می‌تواند رفتار runtime را بدون تغییر Strategy تغییر دهد.

### G-014 — هزینه و funding بعد از close

**شدت:** زیاد

ممکن است fee یا funding پس از close order یا پس از eligibility ثبت شود. این موضوع closure و NET PnL را در زمان‌های مختلف تغییر می‌دهد.

---

## H. ایرادات ریسک، margin و survivability

### H-001 — threshold ریسک بر مبنای user leverage

**شدت:** بحرانی

اگر maintenance schedule تابع user leverage نباشد، thresholdهای Hedge و acute state ممکن است فاصلهٔ واقعی تا liquidation را بیش‌برآورد کنند.

### H-002 — gap risk

**شدت:** بحرانی

فرمول‌های thresholdی که بر حرکت تدریجی price فرض می‌کنند، در gap یا jump ممکن است پیش از ارسال Hedge بی‌اعتبار شوند.

### H-003 — execution latency risk

**شدت:** زیاد

Emergency hedge به زمان ارسال، صف venue، rejection و partial fill وابسته است. Strategy ریسک فاصلهٔ محاسبه تا fill واقعی را کامل وارد threshold نمی‌کند.

### H-004 — liquidity collapse

**شدت:** زیاد

MarketDepth در snapshot عادی ممکن است هنگام volatility spike ناپدید شود. مقدار گذشتهٔ liquidity برای تصمیم جاری قابل اعتماد نیست.

### H-005 — adverse selection

**شدت:** زیاد

Grid fill ممکن است دقیقاً در شروع trend یک‌طرفه رخ دهد. منطق تاریخی traversal لزوماً این ریسک path-dependent را در exposure envelope نشان نمی‌دهد.

### H-006 — funding shock

**شدت:** زیاد

Funding می‌تواند در طول holding هزینهٔ غیرخطی ایجاد کند. dynamic cost estimate و closure target ممکن است آن را دیر یا ناقص وارد کنند.

### H-007 — fee-tier تغییرپذیر

**شدت:** متوسط

Fee ممکن است با volume، account tier یا نوع order تغییر کند. استفاده از fee estimate ثابت می‌تواند eligibility اقتصادی را نادرست کند.

### H-008 — liquidation event به‌عنوان failure عادی

**شدت:** بحرانی

Liquidation نه یک rejection عادی و نه یک partial fill معمولی است. اگر آن را به‌عنوان همان event class پردازش کنند، state و accounting ممکن است فاسد شود.

### H-009 — capital contamination

**شدت:** زیاد

CapitalBase account-wide ممکن است با فعالیت خارج از Basket تغییر کند و sizing، max notional و closure eligibility را منحرف کند.

### H-010 — نبود survivability proof

**شدت:** بحرانی

Strategy safety invariant دارد، اما اثبات نمی‌کند که تحت trend طولانی، volatility spike، قطع venue و کاهش نقدشوندگی سرمایه و state قابل‌کنترل باقی می‌مانند.

---

## I. ایرادات accounting و closure

### I-001 — realized و unrealized PnL

**شدت:** زیاد

مرز زمانی و source میان realized PnL و unrealized PnL در lifecycleهای partial close و restart کاملاً formal نیست.

### I-002 — funding allocation

**شدت:** زیاد

Funding account ممکن است در timestampهای جدا و خارج از order lifecycle ثبت شود. انتساب آن به Generation، Cycle و Basket مشخص نیست.

### I-003 — fee allocation

**شدت:** زیاد

fee order، builder fee، close fee و hedge fee باید به owner مشخص متصل شوند، اما mapping در همهٔ حالت‌ها یکسان تعریف نشده است.

### I-004 — cost target binding

**شدت:** زیاد

معلوم نیست `TotalSystemCosts` در چه لحظه‌ای snapshot می‌شود و هزینه‌های بعدی چه اثری بر target binding دارند.

### I-005 — closure به‌عنوان intent یا fact

**شدت:** بحرانی

بسته‌شدن Basket ممکن است با ارسال close order اشتباه شود، درحالی‌که closure fact فقط پس از fill، position delta و residual exposure verification معتبر است.

### I-006 — residual exposure در چند market

**شدت:** زیاد

اگر Basket چند asset یا چند position داشته باشد، residual exposure در quantity، notional، delta و risk units چگونه تجمیع می‌شود روشن نیست.

### I-007 — accountValue و Basket capital

**شدت:** زیاد

accountValue بدون allocation به Basket قابل استفادهٔ مستقیم برای performance و sizing نیست.

### I-008 — دیررسیدن correction

**شدت:** متوسط

اگر fee یا fill correction بعد از closure برسد، آیا Basket بسته باقی می‌ماند یا historical closure بازنگری می‌شود، معلوم نیست.

---

## J. ایرادات امنیتی، عملیاتی و governance

### J-001 — مرز signing و state authority

**شدت:** بحرانی

Signing باید جدا باشد، اما مشخص نیست signer چگونه مطمئن می‌شود intent درستی را sign می‌کند و state آن نسبت به venue stale نیست.

### J-002 — secret، log و forensic trail

**شدت:** زیاد

ممنوعیت log کردن secret روشن است، اما سطح جزئیات لازم برای forensic replay، request hash و signature metadata کامل مشخص نشده است.

### J-003 — key rotation و signer recovery

**شدت:** زیاد

rotation، revoke، expiry و recovery کلید API در lifecycle operational تعریف نشده است.

### J-004 — manual intervention

**شدت:** زیاد

اگر operator order دستی، cancel دستی یا emergency action انجام دهد، source of truth و تأثیر آن بر immutable history معلوم نیست.

### J-005 — kill switch semantics

**شدت:** زیاد

FREEZE، shutdown، cancel-all و flatten-all از نظر اثر روی open order، position، accounting و recovery یکسان تعریف نشده‌اند.

### J-006 — owner gate بعد از شروع runtime

**شدت:** زیاد

معلوم نیست تغییر policy یا approval در زمان active بودن Basket چگونه versioned می‌شود و روی state قبلی اثر می‌گذارد.

### J-007 — تغییر ناگهانی venue rules

**شدت:** زیاد

Strategy status و operational gate برای تغییر ناگهانی max leverage، tick، margin، fee یا API behavior کامل نیست.

### J-008 — نبود readiness evidence مستقل

**شدت:** متوسط

بعضی claims به artifactsی ارجاع می‌دهند که ناقص یا مفقودند، از جمله `CALIBRATION-REPORT.md`. در نتیجه current readiness قابل ممیزی کامل نیست.

### J-009 — عدم تطابق statusهای تاریخی

**شدت:** متوسط

footer تاریخی contract با statusهای فازهای بعدی هم‌زمان است و ممکن است خواننده را دربارهٔ current verification گمراه کند.

### J-010 — وابستگی به processهای بیرونی

**شدت:** متوسط

اگر calibration، metadata refresh یا evidence collection بیرون از runtime انجام شود، failure و version آن processها در Strategy owner مشخصی ندارد.

---

## K. ایرادات اعتبارسنجی، آزمون و اثبات

### K-001 — نبود reference model مستقل

**شدت:** بحرانی

بدون مدل مرجع مستقل، معلوم نیست implementation منطق Strategy را اجرا می‌کند یا فقط interpretation خودش را.

### K-002 — نبود exhaustive state exploration

**شدت:** زیاد

تمام interleavingهای terminal، return، hedge، closure، timeout و restart در دامنهٔ کوچک به‌صورت exhaustive گزارش نشده‌اند.

### K-003 — نبود property برای attribution uniqueness

**شدت:** بحرانی

آزمونی که اثبات کند یک fill و delta فقط به یک intent قابل انتساب است وجود ندارد یا در artifacts ارائه نشده است.

### K-004 — نبود failure injection کامل

**شدت:** زیاد

crash در مرزهای persist/sign/send/ack/fill/reconcile و reconnect باید جداگانه آزموده شود؛ evidence موجود این پوشش را به‌طور کامل ثابت نمی‌کند.

### K-005 — نبود آزمون precision روی قیمت نهایی

**شدت:** زیاد

آزمون non-overlap و quantity validity باید پس از tick و lot normalization انجام شود؛ اثبات عمومی آن در وضعیت فعلی کامل نیست.

### K-006 — نبود آزمون depth completeness

**شدت:** زیاد

MarketDepth ناقص، stale، empty و asymmetric باید آزموده شوند. در غیر این صورت sizing ممکن است با دادهٔ ناقص افزایش یابد.

### K-007 — نبود venue observation برای margin

**شدت:** بحرانی

فرمول liquidation distance بدون controlled observation و مقایسه با asset/tier واقعی قابل اعتماد نیست.

### K-008 — نبود differential test برای replay

**شدت:** زیاد

مشخص نیست replay event history با اجرای زنده، در eventهای duplicate، دیررس و out-of-order دقیقاً یکسان می‌شود.

### K-009 — نبود mutation testing

**شدت:** متوسط

معلوم نیست test suite می‌تواند تغییر عمدی در threshold، precedence، rounding یا attribution را کشف کند.

### K-010 — نبود تست survivability

**شدت:** بحرانی

سناریوهای trend یک‌طرفه، gap، volatility spike، funding shock، liquidity collapse و venue outage برای اثبات حفظ کنترل کافی گزارش نشده‌اند.

### K-011 — coverage به‌جای correctness

**شدت:** متوسط

پوشش 343 requirement و capability mapping نشان می‌دهد متن به artifact متصل است، اما نشان نمی‌دهد requirementها قابل اجرا، سازگار و testable هستند.

### K-012 — نبود proof برای liveness

**شدت:** زیاد

Safety و block rules ممکن است سیستم را در حالت توقف دائمی نگه دارند. آزمون خروج معتبر از recovery و freeze به‌صورت formal مشخص نشده است.

---

## L. ایرادات عددی، حدی و حالت‌های مرزی

### L-001 — قیمت صفر یا بسیار نزدیک به صفر

**شدت:** زیاد

فرمول‌هایی که بر تقسیم بر mark price یا تبدیل notional به quantity تکیه دارند، برای قیمت صفر یا بسیار کوچک domain مشخص ندارند.

### L-002 — quantity صفر پس از rounding

**شدت:** زیاد

سایز محاسبه‌شده ممکن است پس از `szDecimals` به صفر برسد، اما policy آن نسبت به skip، hedge یا block صریح نیست.

### L-003 — tick بزرگ‌تر از فاصلهٔ Levelها

**شدت:** زیاد

دو Level نظری می‌توانند روی یک tick قرار گیرند و non-overlap را نقض کنند.

### L-004 — min notional بزرگ‌تر از Basket size

**شدت:** زیاد

Strategy ممکن است exposure یا hedge مطلوبی محاسبه کند که از حداقل order قابل‌ارسال کوچک‌تر است. رفتار در این حالت به‌صورت عمومی تعریف نشده است.

### L-005 — leverage در مرز minimum یا maximum

**شدت:** زیاد

فرمول‌ها در leverage حداقل، حداکثر، تغییر tier و leverage invalid به‌طور کامل بررسی نشده‌اند.

### L-006 — StepBps صفر یا منفی

**شدت:** زیاد

domain صریح برای صفر، منفی، بسیار بزرگ و مقادیر خارج از precision برای StepBps در همهٔ پارامترها یکسان نیست.

### L-007 — spread صفر، منفی یا غیرعادی

**شدت:** متوسط

MarketDepth و mid-price logic در spread صفر، crossed book یا book ناسازگار رفتار کاملاً مشخصی ندارد.

### L-008 — overflow در تعداد stateها

**شدت:** متوسط

محاسبات ID، index، event offset و counter در حد نظری 240,000 instance و history بزرگ باید overflow و collision نداشته باشند؛ این property صریح نیست.

### L-009 — timestamp برابر یا عقب‌رفته

**شدت:** متوسط

در clock rollback، timestamp مساوی و event با زمان گذشته، ordering و confirmation semantics روشن نیست.

### L-010 — exposure دقیقاً روی مرز tolerance

**شدت:** زیاد

مشخص نیست equality در thresholdها شامل مرز است یا exclusive. تفاوت `<=` و `<` می‌تواند در hedge و closure اثر مستقیم داشته باشد.

---

## M. خلأهای provenance و انسجام artifacts

### M-001 — artifact مفقود calibration

**شدت:** متوسط تا زیاد

یک verification claim به `CALIBRATION-REPORT.md` ارجاع می‌دهد، اما artifact در repository baseline موجود نیست.

### M-002 — status تاریخی با status جاری مخلوط شده است

**شدت:** متوسط

در contract، footer تاریخی و گزارش فازهای بعدی یک current truth واحد ارائه نمی‌کنند.

### M-003 — evidence source و current venue state

**شدت:** متوسط

مستندات venue تغییرپذیرند. snapshot source موجود ممکن است اثبات نکند که semantics در زمان اجرای آینده هنوز همان است.

### M-004 — نبود version pin برای source claims

**شدت:** متوسط

بعضی claims به URL جاری متکی‌اند و commit، تاریخ fetch یا نسخهٔ سند در همهٔ موارد یکسان ثبت نشده است.

### M-005 — coverage map و semantic completeness

**شدت:** متوسط

اتصال heading به STR و STR به CAP، نبود تناقض بین requirementها یا کافی‌بودن تعریف اجرایی آن‌ها را ثابت نمی‌کند.

### M-006 — conflict resolution ناقص

**شدت:** زیاد

ثبت conflict انجام شده است، اما ممکن است resolution یک source را authoritative کند بدون اینکه تمام پیامدهای فرمولی و runtime آن در Strategy بازنویسی شده باشد.

---

## N. خلاصهٔ نواحی کاملاً حل‌نشده

موارد زیر در وضعیت فعلی نباید به‌عنوان فرض حل‌شده تلقی شوند:

1. مالکیت یکتای fill و position delta؛
2. رابطهٔ user leverage با maintenance و liquidation؛
3. policy نهایی `CycleReferenceDerivation`؛
4. nominal reference price؛
5. clock و event ordering؛
6. behavior در `UNKNOWN_SUBMISSION`؛
7. accounting مستقل Basket از account؛
8. completion واقعی MarketDepth؛
9. parent/child semantics در TWAP؛
10. closure target و هزینه‌های دیررس؛
11. external manual یا liquidation position change؛
12. precision و rounding نهایی؛
13. liveness بعد از freeze و reconciliation؛
14. replay برابر با اجرای زنده؛
15. artifactهای ناقص و statusهای تاریخی؛
16. survivability در gap، trend، volatility و liquidity collapse.

## References

[1]: https://github.com/avangardistic/hypergrid/blob/main/Strategy.md "Hypergrid canonical strategy specification"
[2]: https://github.com/avangardistic/hypergrid/blob/main/prompt.md "Hypergrid control prompt"
[3]: https://github.com/avangardistic/hypergrid/blob/main/research/strategy/STRATEGY_CONTRACT.md "Hypergrid derived strategy contract"
[4]: https://github.com/avangardistic/hypergrid/blob/main/research/strategy/STRATEGY_COVERAGE.md "Hypergrid strategy coverage"
[5]: https://github.com/avangardistic/hypergrid/blob/main/research/architecture/STATE_OWNERSHIP.md "Hypergrid state ownership analysis"
[6]: https://github.com/avangardistic/hypergrid/blob/main/research/architecture/FAILURE_BOUNDARIES.md "Hypergrid failure boundary analysis"
[7]: https://github.com/avangardistic/hypergrid/blob/main/research/architecture/CAPABILITY_MAP.md "Hypergrid capability map"
[8]: https://github.com/avangardistic/hypergrid/blob/main/research/architecture/ARCHITECTURE_CANDIDATES.md "Hypergrid architecture candidates"
[9]: https://github.com/avangardistic/hypergrid/blob/main/research/decisions/DECISION_REGISTER.md "Hypergrid decision register"
[10]: https://github.com/avangardistic/hypergrid/blob/main/research/sources/hyperliquid/TOPIC_EVIDENCE.md "Hypergrid Hyperliquid topic evidence"
[11]: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint "Hyperliquid Info endpoint"
[12]: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions "Hyperliquid WebSocket subscriptions"
[13]: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/tick-and-lot-size "Hyperliquid tick and lot size"
[14]: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/margining "Hyperliquid margining"
[15]: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/contract-specifications "Hyperliquid contract specifications"
[16]: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint "Hyperliquid exchange endpoint"
[17]: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/nonces-and-api-wallets "Hyperliquid nonces and API wallets"
[18]: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/robust-price-indices "Hyperliquid robust price indices"
[19]: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits "Hyperliquid rate limits and user limits"
[20]: https://github.com/avangardistic/hypergrid/blob/main/research/sources/SOURCE_MANIFEST.md "Hypergrid source manifest"
[21]: https://github.com/avangardistic/hypergrid/blob/main/research/findings/CONFLICT-001.md "Hypergrid leverage conflict"
[22]: https://github.com/avangardistic/hypergrid/blob/main/research/findings/CONFLICT-002.md "Hypergrid account-state conflict"
[23]: https://github.com/avangardistic/hypergrid/blob/main/research/findings/CONFLICT-003.md "Hypergrid trigger-basis conflict"
[24]: https://github.com/avangardistic/hypergrid/blob/main/research/README.md "Hypergrid research status"
[25]: https://github.com/avangardistic/hypergrid/blob/main/CLAUDE.md "Hypergrid project invariants"
[26]: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/funding "Hyperliquid funding documentation"
[27]: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees "Hyperliquid fees documentation"
[28]: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/order-types "Hyperliquid order types documentation"
[29]: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/signing "Hyperliquid signing documentation"
[30]: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/twap "Hyperliquid TWAP documentation"
[31]: https://github.com/avangardistic/hypergrid/blob/main/research/sources/hyperliquid/SDK_RECORD.md "Hypergrid Hyperliquid SDK record"
[32]: https://github.com/avangardistic/hypergrid/blob/main/research/architecture/CAPABILITY_COVERAGE.md "Hypergrid capability coverage"
[33]: https://github.com/avangardistic/hypergrid/blob/main/research/architecture/BOUNDARY_CANDIDATES.md "Hypergrid architecture boundary candidates"
[34]: https://github.com/avangardistic/hypergrid/blob/main/research/decisions/OWNER_GATE_001.md "Hypergrid owner gate 001"
[35]: https://github.com/avangardistic/hypergrid/blob/main/research/decisions/OWNER_GATE_002.md "Hypergrid owner gate 002"
