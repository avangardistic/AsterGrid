# OWNER_GATE_020 — انتخابِ زبان/پارادایمِ runtimeِ production (پیاده‌سازِ CAND-B)

> خودبسنده. شناسه‌های فنی به انگلیسی. مرتبط با: DECISION-022 (PENDING). منابع: `prompt.md` (ترجیحِ backend)؛ `research/decisions/DECISION_REGISTER.md` DECISION-015 (CAND-B)، DECISION-021 (REF-D فانکشنال)؛ `research/architecture/ARCHITECTURE_DECISION.md` §3 (قیودِ تفسیری)؛ `research/audits/ga_arena.py` (ابزارِ GA موجود، Python). این gate یک تصمیمِ لایهٔ runtime است؛ هیچ STR-* normative را تغییر نمی‌دهد.

## ۱. زمینه (Context)
runtime باید **قطعی (deterministic)**، **AI-independent** و مطابقِ **CAND-B** (event-sourced، تک-پراسس، core تک‌مرجعِ خالص، replayِ قطعی) باشد (ARCHITECTURE_DECISION §3). زبانِ production باید **پیش از Phase 7** (پیاده‌سازیِ Deterministic Core) انتخاب شود. این آخرین بلاکرِ ورود به Phase 7 است.

## ۲. شواهد (Evidence)
- **prompt.md (ترجیحِ backend):** «Python-first مگر آنکه فناوریِ دیگری به‌طور مادّی correctness/safety/performance/operability/maintainability را بهبود دهد.»
- **DECISION-021 (GATE-019):** CAP-0024 = **REF-D (فانکشنال)** با الزامِ **paradigm-distinct**؛ بنابراین production باید **غیرِفانکشنال** باشد تا استقلالِ common-mode حفظ شود.
- **ابزارِ GA موجود:** `ga_arena.py` در همین برنامه به Python نوشته و اجرا شده — اکوسیستم و آشناییِ موجود.
- **ARCHITECTURE_DECISION §3:** تک-پراسس؛ core تک‌مرجع؛ replayِ قطعی؛ **بدونِ external workflow engine**؛ **بدونِ actor model** (CAND-E رد شده، DECISION-015).

## ۳. تصمیم دقیق موردنیاز (Exact decision)
کدام زبان/پارادایمِ runtimeِ production، CAND-B را پیاده می‌کند؟

## ۴. گزینه‌ها (Options)
- **A — Python:** امری (imperative)؛ اکوسیستمِ بالغ؛ `asyncio` برای I/O؛ ابزارِ GAِ موجودِ این برنامه Python است؛ typingِ قوی از طریقِ `mypy`؛ پول با `Decimal`/`int`؛ coreِ تک‌نخی. مطابقِ ترجیحِ prompt.md.
- **B — Rust:** سیستمی؛ memory-safe؛ typesِ قوی؛ کارایی بالا؛ هزینهٔ توسعهٔ بیشتر؛ مالک باید مسلط باشد.
- **C — Go:** ساده؛ concurrencyِ خوب؛ stdlibِ قوی؛ برای domain-logicِ خالص کمتر طبیعی؛ مالک باید مسلط باشد.
- **D — TypeScript/Node:** async/streamingِ عالی؛ typingِ زمانِ توسعه از TS؛ event-loopِ تک‌نخی؛ مالک باید مسلط باشد.
- **رد‌شده (مستند، نه گزینه):** **خانوادهٔ زبان‌های فانکشنال برای production** — چون DECISION-021، CAP-0024 را به **REF-D (فانکشنال)** با الزامِ paradigm-distinctness قفل کرده، production باید **غیرِفانکشنال** (imperative / OOP / systems) باشد. نمونهٔ مستند: **Elixir/Erlang — رد** (هم با DECISION-015 برخورد می‌کند — CAND-B، نه actor model؛ CAND-E رد شده — و هم با DECISION-021 — productionِ فانکشنال با CAP-0024ِ فانکشنال هم‌خانواده می‌شود و استقلال را نقض می‌کند). همین منطقِ DECISION-021، هر productionِ فانکشنالِ دیگر (مثلِ Haskell/Clojure-family) را نیز بدونِ نیاز به ردیفِ گزینهٔ جداگانه کنار می‌گذارد.

## ۵. پیامدها (Consequences)
- **A (Python):** بالاترین سرعتِ توسعه و هم‌راستا با prompt.md و ابزارِ موجود؛ determinism نیازمندِ انضباط (اجتناب از float در تصمیم — `Decimal`/`int`؛ core تک‌نخی)؛ typing از `mypy` (نه compile-enforced)؛ اکوسیستمِ Hyperliquid SDK قوی (SDK رسمی Python است)؛ ریسکِ common-mode با CAP-0024ِ فانکشنال **پایین** (پارادایمِ متفاوت)؛ پیچیدگیِ عملیاتی پایین؛ هزینهٔ مهاجرت پایین.
- **B (Rust):** determinism و type-safety در سطحِ کامپایلر قوی‌ترین؛ کارایی بالا؛ هزینهٔ توسعه/مهارت بالا؛ SDK رسمی Python است (نیازمندِ کلاینتِ Rust یا bindings)؛ common-mode با REF-D پایین.
- **C (Go):** سادگی و عملیاتِ خوب؛ domain-logicِ خالص کمتر طبیعی (بدونِ genericsِ غنیِ قدیمی، الگوهای جبری محدود)؛ SDK رسمی Python؛ common-mode پایین.
- **D — TypeScript/Node:** streaming/async عالی؛ typing زمانِ توسعه؛ ریسکِ float/عددی نیازمندِ دقت (BigInt/کتابخانهٔ decimal)؛ SDK رسمی Python (کلاینتِ TS جداگانه)؛ common-mode پایین.
- همهٔ A–D **غیرِفانکشنال**‌اند ⇒ استقلالِ پارادایمی از CAP-0024 (REF-D) حفظ می‌شود.

## ۶. آنچه مسدود می‌ماند (What remains blocked)
بدون این انتخاب: **Phase 7 (Deterministic Core Implementation)** آغاز نمی‌شود؛ زبانِ REF-D در Phase 6b-2 **قابلِ pin نیست** (مشروط بر انتخابِ production، DECISION-021)؛ و **differential harness** ساخته نمی‌شود.

## ۷. توصیه (Recommendation)
شواهد (ترجیحِ صریحِ prompt.md بر Python-first؛ SDK رسمیِ Python؛ ابزارِ GAِ موجودِ Python؛ استقلالِ پارادایمی از REF-Dِ فانکشنال که با هر گزینهٔ A–D حفظ می‌شود) به‌طور عینی از **گزینه A (Python)** به‌عنوانِ گزینهٔ پیش‌فرضِ منطقی پشتیبانی می‌کنند، **مشروط بر** رعایتِ انضباطِ determinism (بدونِ float در مسیرِ تصمیم؛ `Decimal`/`int`؛ core تک‌نخی و خالص؛ typing با `mypy`). **این توصیه الزام‌آور نیست**؛ اگر مالک correctness/performance را بر velocity مقدم بداند، **B (Rust)** جایگزینِ قویِ type-safe است. انتخابِ نهایی با مالک است؛ هیچ گزینه‌ای در این run انتخاب نمی‌شود.

**STATUS: OPEN — awaiting Owner selection of production runtime language (GATE-020).**
