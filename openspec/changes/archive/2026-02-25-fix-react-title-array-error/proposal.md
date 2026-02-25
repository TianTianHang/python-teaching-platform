## Why

前端多个路由文件中的 `<title>` 标签使用了混合内容（文本 + JSX 变量），导致 React 报错："React expects the `children` prop of <title> tags to be a string... but found an Array with length 2 instead." 这是一个常见的 React 错误，当 `<title>` 标签的子元素是数组时会发生。

## What Changes

- 修复 5 个路由文件中的 `<title>` 标签，将混合内容改为模板字符串或使用 `formatTitle()` 函数
- 统一使用 `formatTitle()` 函数以保持与其他文件的一致性

**影响文件**:
1. `_layout.courses_.$courseId/route.tsx` - `<title>课程详情 - {DEFAULT_META.siteName}</title>`
2. `payment.pay.tsx` - `<title>支付页面 - {DEFAULT_META.siteName}</title>`
3. `_layout.threads_.$threadId.tsx` - `<title>讨论帖 - {DEFAULT_META.siteName}</title>`
4. `_layout.membership.tsx` - `<title>会员方案 - {DEFAULT_META.siteName}</title>`
5. `auth.tsx` - `<title>认证布局 - {DEFAULT_META.siteName}</title>`

## Capabilities

### New Capabilities
*无新增功能*

### Modified Capabilities
*无需求变更，纯 Bug 修复*

## Impact

- **前端代码**: 5 个 TypeScript/TSX 文件
- **无破坏性变更**: 仅修复 Bug，不改变任何 API 或用户可见行为
- **无依赖变更**: 使用现有的 `formatTitle()` 函数
