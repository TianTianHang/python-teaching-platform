## 1. 内部导航改为 useNavigate

- [x] 1.1 修改 `_layout.courses_.$courseId/route.tsx:79` - `window.location.href = '/courses'` → `navigate('/courses')` (已使用 Link 组件)
- [x] 1.2 确认 `utils/http/client.ts:96` 的 `window.location.href = '/auth/login'` 保持不变（HTTP 拦截器非组件上下文）

## 2. 页面刷新改为 router.revalidator()

- [x] 2.1 修改 `_layout.courses_.$courseId/route.tsx:104` - `window.location.reload()` → `revalidate()` (已使用 revalidator.revalidate())
- [x] 2.2 修改 `_layout.courses_.$courseId_.chapters/route.tsx:110` - `window.location.reload()` → `revalidate()` (已使用 Link 组件)
- [x] 2.3 修改 `_layout.courses_.$courseId_.chapters_.$chapterId/route.tsx:120` - `window.location.reload()` → `revalidate()`
- [x] 2.4 修改 `_layout.courses_.$courseId_.chapters_.$chapterId_.locked.tsx:58` - `window.location.reload()` → `revalidate()`
- [x] 2.5 修改 `_layout.problems.tsx:83` - `window.location.reload()` → `revalidate()`

## 3. 保持外部 URL 跳转不变

- [x] 3.1 确认 `CheckoutModal.tsx:69` 的 `window.location.href = pay.data.pay_url` 保持不变（支付回调）
- [x] 3.2 确认 `payment.pay.tsx:61` 的注释保持不变

## 4. 验证

- [x] 4.1 运行 `pnpm run typecheck` 确保类型正确
- [x] 4.2 运行 `pnpm run lint` 确保代码风格正确（如果存在 lint 命令）(项目未配置 lint 命令)