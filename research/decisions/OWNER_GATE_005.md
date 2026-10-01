# OWNER_GATE_005 — اعتبار مدل maintenance-margin/liquidation نسبت به user leverage (اعتبار D-16)

> خودبسنده. شناسه‌های فنی انگلیسی. مرتبط با: AMB-0003 (و AMB-0045 residual). منابع: SRC-202 (C-001, C-002, H-001, K-007)، SRC-201 (§4.2)، N#2. STR متأثر: STR-0223, STR-0337, STR-0340, STR-0206. CAP: CAP-0016, CAP-0017. **این گیت GATE-001 را باز نمی‌کند**؛ GATE-001 دربارهٔ عددِ max leverage (۴۰x/۵۰x، illustrative) بود، این گیت دربارهٔ *اعتبار فرمول* maintenance است.

## ۱. زمینه (Context)
§16 و D-16 از رابطهٔ `maintenance_margin_fraction = 0.5 / Leverage_effective` و `MaxSafeNotional_margin = CapitalBase × Leverage_effective / 2` استفاده می‌کنند و `MaxExposureImbalance` (STR-0340) و آستانهٔ hedge حاد (STR-0206) بر آن بنا شده‌اند.

## ۲. شواهد (Evidence)
- مستندات Hyperliquid: «maintenance margin = نصف initial margin در **max leverage** دارایی» و «initial margin fraction = 1/leverage» (SRC-115 margining، SRC-116 contract-specifications، SRC-118 liquidations: «۱٫۲۵٪ برای داراییِ ۴۰x»).
- این گزاره‌ها maintenance را در **max leverage دارایی** تعریف می‌کنند، نه به‌صورت `0.5/user_leverage`. با `Leverage_user = 3`، اینکه maintenance fraction دقیقاً `0.5/3 ≈ 16.7%` باشد از مستندات مستقیماً نتیجه نمی‌شود (C-001).
- بنابراین ادعای «در 3x فاصلهٔ liquidation ≈ 16.7%» بدون مدل رسمی و مشاهدهٔ کنترل‌شده اثبات‌شده نیست (C-002, K-007).

## ۳. تصمیم دقیق موردنیاز (Exact decision)
مدل معتبر maintenance-margin/liquidation برای محاسبهٔ آستانه‌های ریسک چیست؟ آیا `0.5/Leverage_effective` به‌عنوان hypothesis پذیرفته می‌شود تا با مشاهدهٔ زنده تأیید/اصلاح شود، یا مدل دقیق‌تری الزامی است؟

## ۴. گزینه‌ها (Options)
- **A:** آستانه‌ها را از **maintenance-margin schedule واقعیِ per-asset/tier** (از `meta`/margin tiers و liquidationPx در `clearinghouseState`) محاسبه کن، نه از `0.5/user_leverage`؛ فرمول §16 به‌عنوان کف محافظه‌کارانهٔ illustrative بماند.
- **B:** `0.5/Leverage_effective` را موقتاً به‌عنوان **hypothesis محافظه‌کارانه** نگه‌دار، مشروط به controlled observation در Phase 8/12 و بازبینی D-16 پیش از Live.
- **C:** ترکیب — استفاده از `liquidationPx`/maintenance واقعی venue در runtime + نگه‌داشتن فرمول §16 صرفاً برای sizing محافظه‌کارانهٔ اولیه.
- **D:** گزینهٔ دیگر مالک.

## ۵. پیامدها (Consequences)
- **A/C:** دقیق‌ترین از نظر ریسک؛ نیازمند خواندن maintenance/liquidation واقعی از venue و مدل‌سازی tier؛ ایمن‌تر برای Hedge.
- **B:** ساده، اما اگر maintenance واقعی سخت‌گیرانه‌تر باشد، آستانهٔ hedge حاد ممکن است دیر فعال شود (ریسک ایمنی) — لذا مشروط به راستی‌آزمایی زنده.

## ۶. آنچه مسدود می‌ماند (What remains blocked)
اعتبار `MaxExposureImbalance` و آستانهٔ Hedge حاد (که مستقیماً بر survivability اثر دارند) نامطمئن می‌ماند. Live readiness نباید بدون بستن این گیت و مشاهدهٔ کنترل‌شدهٔ liquidation اعطا شود.

## ۷. توصیه (Recommendation)
**گزینه C** به‌طور عینی پشتیبانی می‌شود: venue مقدار `liquidationPx` و maintenance را بر پایهٔ max leverage و tier تعریف می‌کند (SRC-115/116/118)، پس استفادهٔ مستقیم از این مقادیر در runtime دقیق‌تر از فرض `0.5/user_leverage` است؛ نگه‌داشتن فرمول §16 به‌عنوان کف محافظه‌کارانهٔ اولیه با اصل fail-safe سازگار است. تا مشاهدهٔ کنترل‌شده، D-16 باید صریحاً hypothesis علامت بخورد.

**STATUS: RESOLVED — Option C (owner, 2026-09-21). See DECISION_REGISTER.md DECISION-006.**
