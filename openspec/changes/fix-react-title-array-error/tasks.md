## 1. Fix Title Tags in Route Files

- [x] 1.1 Fix `_layout.courses_.$courseId/route.tsx` - Change `<title>课程详情 - {DEFAULT_META.siteName}</title>` to `<title>{formatTitle('课程详情')}</title>`
- [x] 1.2 Fix `payment.pay.tsx` - Change `<title>支付页面 - {DEFAULT_META.siteName}</title>` to `<title>{formatTitle('支付页面')}</title>`
- [x] 1.3 Fix `_layout.threads_.$threadId.tsx` - Change `<title>讨论帖 - {DEFAULT_META.siteName}</title>` to `<title>{formatTitle('讨论帖')}</title>`
- [x] 1.4 Fix `_layout.membership.tsx` - Change `<title>会员方案 - {DEFAULT_META.siteName}</title>` to `<title>{formatTitle('会员方案')}</title>`
- [x] 1.5 Fix `auth.tsx` - Change `<title>认证布局 - {DEFAULT_META.siteName}</title>` to `<title>{formatTitle('认证布局')}</title>`

## 2. Verification

- [x] 2.1 Run `pnpm run typecheck` to verify no TypeScript errors
- [x] 2.2 Run `pnpm dev` to verify the application starts without React errors
- [x] 2.3 Test affected pages in browser to confirm titles display correctly
