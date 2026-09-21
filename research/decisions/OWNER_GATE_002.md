# OWNER_GATE_002 — منبع معتبر برای ActualExposure طبق §11.1: «clearinghouseState/webData2» و تغییر نام به webData3

> این پرونده خودبسنده است. شناسه‌های فنی به انگلیسی‌اند.

## ۱. زمینه (Context)
`Strategy.md` (§6.1، §6.2، §11.1) به‌طور مکرر «`clearinghouseState/webData2`» را به‌عنوان منبع معتبرِ وضعیت پوزیشن/مارجین معرفی می‌کند؛ به‌ویژه `ActualExposure` (STR-0200) و `CapitalBase` (STR-0224) باید «فقط» از این منبعِ معتبر خوانده شوند، نه از دفترداریِ محلیِ سفارش‌ها.

## ۲. شواهد (Evidence)
- سند رسمی WebSocket/Subscriptions: اکنون نوع اشتراک **`webData3`** است (نه webData2)، و در بخش data-formats، `WebData2` این‌گونه توصیف شده: **"Aggregate information about a user, used primarily for the frontend"** (یعنی دادهٔ تجمیعی برای رابط کاربری، نه یک منبع سطح‌پایینِ معتبر).
- `clearinghouseState` هم از طریق REST و هم WS در دسترس است و در صفحات Perpetuals-info/Margining/Liquidations به‌عنوان مرجعِ پوزیشن/مارجین استفاده می‌شود؛ فیلدهای آن شامل `assetPositions[].position.szi` (اندازهٔ خالص علامت‌دار)، `marginSummary.accountValue` (ارزش حساب شامل unrealized PnL) و `withdrawable` است.
- جمع‌بندی: `clearinghouseState` منبعِ معتبر است؛ `webData2`/`webData3` یک تجمیعِ سمتِ frontend است و برای POSITION_VERIFIED نباید مبنا قرار گیرد.

## ۳. تصمیم دقیق موردنیاز (Exact decision)
برای `ActualExposure` و `CapitalBase`، منبعِ معتبرِ واحد کدام است؟ آیا تأیید می‌کنید که `clearinghouseState` تنها منبعِ معتبر باشد و `webData2/webData3` صرفاً کمکی/غیرمعتبر تلقی شود؟ (این یک تثبیتِ تفسیر در لایهٔ قابلیت است؛ `Strategy.md` ویرایش نمی‌شود.)

## ۴. گزینه‌ها (Options)
- **گزینه A:** `clearinghouseState` (REST + WS) تنها منبعِ معتبرِ ActualExposure/CapitalBase؛ `webData2/webData3` فقط برای نمایش/کمکی و هرگز مبنای POSITION_VERIFIED نباشد.
- **گزینه B:** استفادهٔ ترکیبی: `clearinghouseState` معتبر، ولی `webData3` به‌عنوان منبع کمکیِ کم‌تأخیر برای هشدارهای اولیه (با راستی‌آزماییِ نهایی توسط clearinghouseState).
- **گزینه C:** هیچ‌کدام؛ مالک منبع دیگری را دستور می‌دهد.

## ۵. پیامد هر گزینه (Consequences)
- **A:** ساده و ایمن؛ کاملاً منطبق بر اصلِ «Actual Exposure فقط از وضعیت معتبرِ صرافی» (§15). ریسک: تأخیر جزئی نسبت به فید تجمیعیِ frontend.
- **B:** واکنش سریع‌تر برای هشدار، اما پیچیدگی بیشتر و ریسکِ تکیه بر دادهٔ frontend اگر راستی‌آزماییِ نهایی رعایت نشود.
- **C:** بسته به دستور مالک.

## ۶. آنچه مسدود می‌ماند (What remains blocked)
- طراحیِ قابلیتِ Reconciliation در فاز ۳ (Capability Discovery) منتظر این تصمیم است تا «منبع حقیقت» برای exposure/مارجین قطعی شود.
- در `STRATEGY_CONTRACT.md`، `STR-0200` و `STR-0224` به‌صورت **VERIFIED** ثبت شده‌اند (چون clearinghouseState تأییدشده است)؛ این گیت فقط دربارهٔ نقشِ `webData2/webData3` است و متنِ نرمانیِ نیازمندی را تغییر نمی‌دهد.

## ۷. توصیه (Recommendation)
**گزینه A.** به‌طور عینی از شواهد پشتیبانی می‌شود: خودِ سند صرافی `webData2` را «برای frontend» توصیف کرده و `clearinghouseState` را به‌عنوان منبعِ معتبرِ پوزیشن/مارجین ارائه می‌دهد؛ همچنین ثابتِ §15 می‌گوید «Actual Exposure فقط از وضعیت معتبرِ صرافی». `webData3` می‌تواند بعداً به‌عنوان بهینه‌سازیِ اختیاری بررسی شود، بدون آنکه منبعِ معتبر باشد.
