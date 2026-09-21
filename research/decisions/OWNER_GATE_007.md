# OWNER_GATE_007 — بازیابی پس از ارسال مبهم (UNKNOWN_SUBMISSION)، مرزهای atomicity و idempotency

> خودبسنده. شناسه‌های فنی انگلیسی. مرتبط با: AMB-0005. منابع: SRC-202 (B-013, B-014, E-002, E-003, G-002, G-003, G-005)، SRC-201 (§4.11)، SRC-203 (§3.5)، N#6. STR متأثر: STR-0004, STR-0132, STR-0298, STR-0314, STR-0133, STR-0138. CAP: CAP-0014, CAP-0015, CAP-0021, CAP-0002. FM مرتبط: FM-08, FM-09, FM-10.

## ۱. زمینه (Context)
پس از ارسال order و timeout، ممکن است order در venue پذیرفته شده یا نشده باشد. استراتژی blind retry را ممنوع می‌کند، اما stateهای رسمی میان `UNKNOWN_SUBMISSION`، `RECONCILING`، `CANCEL_PENDING` و مرزهای atomic (persist intent → sign → send → ack → fill → reconcile → transition) کامل تعریف نشده‌اند. cloid برای correlation است، نه تضمین dedup در venue.

## ۲. شواهد (Evidence)
- venue replay را با **nonce set** (۱۰۰ بالا، هرگز-استفاده‌نشده، پنجرهٔ زمانی) کنترل می‌کند؛ dedup بر پایهٔ cloidِ تکراری در مستندات نیامده (SRC-110؛ STR-0133/0138 = PARTIALLY / FM-09).
- ارسال cancel، اثبات cancellation نیست (G-005). ack ≠ fill ≠ position delta (STR-0131، G-001).
- crash بین fill و persist می‌تواند state محلی و venue را جدا کند (B-014, E-002).

## ۳. تصمیم دقیق موردنیاز (Exact decision)
ماشین state رسمی و رویهٔ بازیابی برای «نتیجهٔ نامعلومِ ارسال» چیست، و مرزهای atomic/persist-before-side-effect کدام‌اند؟

## ۴. گزینه‌ها (Options)
- **A:** stateهای صریح `UNKNOWN_SUBMISSION`/`RECONCILING`/`CANCEL_PENDING`؛ persist «intent+cloid پیش از send» (STR-0298)؛ پس از timeout هیچ side effect جدید تا reconcile با `orderStatus`(by cloid)+`openOrders`+`userFills`+`clearinghouseState`؛ فقط پس از روشن‌شدن outcome اقدام بعدی.
- **B:** مثل A، به‌علاوهٔ استفاده از `expiresAfter` روی actionها برای محدودکردن پنجرهٔ ابهام (order کهنه به‌جای اجرای دیرهنگام رد شود).
- **C:** گزینهٔ دیگر مالک.

## ۵. پیامدها (Consequences)
- **A:** ایمن و منطبق بر «هرگز retry کور»؛ نیازمند reconcile قوی و persist پیش از side effect.
- **B:** پنجرهٔ ابهام کوچک‌تر و بازیابی ساده‌تر؛ اما `expiresAfter` هزینهٔ rate-limit دارد (۵× در stale-cancel، SRC-104) و نیازمند تنظیم دقیق.

## ۶. آنچه مسدود می‌ماند (What remains blocked)
recovery ایمن پس از crash/timeout و idempotency side-effectها (FM-08/09/10) تعریف‌نشده می‌ماند؛ این پیش‌نیاز Phase 7 (core) و Phase 9 (failure-injection) است. Live بدون این گیت مجاز نیست.

## ۷. توصیه (Recommendation)
**گزینه B** (A + `expiresAfter`) به‌طور عینی پشتیبانی می‌شود: venue صریحاً `expiresAfter` و nonce-based replay control را فراهم می‌کند (SRC-104/110)، و ترکیب persist-before-send + reconcile-before-act با اصل «establish whether it already happened before retry» و fail-closed منطبق است. dedup بر cloid نباید فرض شود؛ راستی‌آزمایی همیشه از venue.
