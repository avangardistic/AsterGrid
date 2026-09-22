# OWNER_GATE_019 — انتخابِ زبان/پارادایمِ CAP-0024 (Reference Model)

> خودبسنده. شناسه‌های فنی به انگلیسی. مرتبط با: DECISION-021 (OPEN). منابع: `research/validation/VALIDATION_PLAN.md` §4 (استقلال)؛ `research/implementation/CAP0024_DESIGN.md` (طراحی + فهرست کاندیداها Part C)؛ `research/architecture/ARCHITECTURE_DECISION.md` §4 (لایهٔ Research، آفلاین/NON_RUNTIME). این gate یک تصمیمِ لایهٔ verification است؛ هیچ STR-* normative را تغییر نمی‌دهد.

## ۱. زمینه (Context)
CAP-0024 اوراکلِ اصلیِ هستهٔ قطعی است (VALIDATION_PLAN §2/§3.2). طبق VALIDATION_PLAN §4، CAP-0024 **نباید هیچ کدی را با production به اشتراک بگذارد** (برای جلوگیری از باگِ common-mode). مالک باید زبان/پارادایمی را برگزیند که استقلالِ ساختاریِ کافی فراهم کند.

## ۲. شواهد (Evidence)
- VALIDATION_PLAN §4: بدونِ کدِ مشترک؛ هر artifact نسخه‌ها را ثبت می‌کند؛ production در runtime به CAP-0024 وابسته نیست.
- ARCHITECTURE_DECISION §4: لایهٔ Research آفلاین است و هرگز به entrypointِ runtime لینک نمی‌شود.
- CAP0024_DESIGN.md Part B: ۲۰ الزامِ رفتاری (B-01..B-20) که مرجع باید بازتولید کند.
- CAP0024_DESIGN.md Part C: کاندیداهای REF-A..F با trade-offها.

## ۳. تصمیم دقیق موردنیاز (Exact decision — با یادداشتِ وابستگی)
کدام زبان/پارادایم برای CAP-0024؟ **وابستگیِ مهم:** زبانِ runtimeِ production هنوز انتخاب نشده (یک Owner Gateِ آیندهٔ جداگانه، پیش از Phase 7). بنابراین پاسخِ مالک می‌تواند یکی از این سه شکل باشد:
- **ABSOLUTE:** یک انتخابِ مشخص، مستقل از production (مثلاً REF-C فرمال، REF-D فانکشنال).
- **CONDITIONAL:** «پارادایم/خانوادهٔ متفاوت از هرچه production باشد» (مثلاً REF-B/REF-D به‌صورت نسبی)، با pin‌شدنِ زبانِ مشخص هنگام انتخابِ production.
- **DEFER:** به‌تعویق‌انداختنِ گزینه‌های نسبی تا انتخابِ production.

## ۴. گزینه‌ها (Options) — REF-A..F (خلاصه؛ جزئیات در CAP0024_DESIGN.md Part C)
- **REF-A** — همان زبانِ production، codebaseِ جدا، بدونِ ماژولِ مشترک. **CONDITIONAL.** استقلال: ضعیف–متوسط.
- **REF-B** — زبانِ عمومیِ متفاوت برای جداییِ ساختاری. **ABSOLUTE** (یا CONDITIONAL اگر «متفاوت از production»). استقلال: متوسط–قوی.
- **REF-C** — زبانِ فرمال/ابزارِ property (TLA+ / Alloy / مشابه). **ABSOLUTE.** استقلال: قوی؛ عالی برای invariant/exhaustive، ضعیف‌تر برای برابریِ کاملِ emitted-event.
- **REF-D** — پیاده‌سازیِ مرجع در زبانِ فانکشنال. **ABSOLUTE** (یا CONDITIONAL مانند REF-B). استقلال: متوسط–قوی؛ سازگار با fold.
- **REF-E** — مدلِ declarative/constraint-based. **ABSOLUTE.** استقلال: قوی؛ برابریِ emitted-event نیازمندِ دقت.
- **REF-F** — هیبریدِ پیشنهادیِ طراح: مرجعِ فانکشنال/فرمال برای fold + comparatorِ نازک؛ پارادایم‌متمایز از production. **ABSOLUTE** یا CONDITIONAL. پوششِ کامل‌تر، بیشترین هزینهٔ طراحی.

## ۵. پیامدها (Consequences)
- استقلالِ قوی‌تر (REF-C/E/F و تا حدی REF-B/D) ⇒ کاهشِ ریسکِ common-mode bug، اما هزینهٔ توسعه/مهارتِ بیشتر و گاه دشواریِ برابریِ emitted-event.
- REF-A کمترین هزینه ولی ضعیف‌ترین استقلال — هدفِ CAP-0024 (اوراکلِ مستقل) را تضعیف می‌کند.
- انتخابِ CONDITIONAL به انتخابِ production گره می‌خورد؛ pinِ نهایی پس از آن Gate.

## ۶. آنچه مسدود می‌ماند (What remains blocked)
بدون انتخاب، **پیاده‌سازیِ reference-model و harnessِ differential (Phase 7)** در زبانِ برگزیده ساخته نمی‌شود. طراحیِ رفتاریِ Phase 6b-2 (Part B) نهایی است و **Phase 6c (حلِ قیودِ non-blocking) می‌تواند مستقل از این انتخاب پیش برود** — 6c به این انتخاب نیاز ندارد.

## ۷. توصیه (Recommendation)
شواهدِ Part C به‌طور عینی از **استقلالِ ساختاریِ قوی** پشتیبانی می‌کنند (یعنی نه REF-A). میانِ گزینه‌های مستقل، **REF-D (فانکشنال، سازگار با fold)** یا **REF-F (هیبرید)** بیشترین پوششِ برابریِ رفتاری را با استقلالِ خوب می‌دهند، و **REF-C** برای لایهٔ invariant/exhaustive قوی‌ترین است (احتمالاً مکمّلِ REF-B/D برای برابریِ emitted-event). **این توصیه الزام‌آور نیست**؛ انتخابِ نهایی — و شکلِ ABSOLUTE/CONDITIONAL/DEFER — با مالک است. هیچ گزینه‌ای در این run انتخاب نمی‌شود.

**STATUS: OPEN — awaiting Owner selection of language/paradigm (GATE-019).**
