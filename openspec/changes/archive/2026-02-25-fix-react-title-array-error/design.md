## Context

React 的 `<title>` 元素要求 children 必须是单个字符串值。当 JSX 中混合使用文本字面量和变量时（如 `<title>text {variable}</title>`），React 会创建一个数组 `["text ", variable]`，这会导致运行时错误。

当前代码库中，约 5 个路由文件使用了这种有问题的模式：
```jsx
<title>课程详情 - {DEFAULT_META.siteName}</title>
```

而代码库中的其他文件（约 20+ 个路由）已经正确地使用了 `formatTitle()` 函数，该函数返回格式化的字符串。

## Goals / Non-Goals

**Goals:**
- 修复 React `<title>` 标签数组报错
- 统一使用 `formatTitle()` 函数以保持代码一致性

**Non-Goals:**
- 修改 `formatTitle()` 函数的行为
- 改变页面标题的显示内容（保持用户可见的标题不变）

## Decisions

### 使用 formatTitle() 而非模板字面量

**选择**: 使用 `formatTitle('课程详情')` 而非 `{`课程详情 - ${DEFAULT_META.siteName}`}`

**理由**:
1. **一致性**: 代码库中约 80% 的路由文件已经使用 `formatTitle()`
2. **DRY 原则**: 站点名称集中在 `DEFAULT_META.siteName` 中维护
3. **可维护性**: 如果未来需要修改标题格式，只需修改 `formatTitle()` 函数
4. **类型安全**: `formatTitle()` 函数提供类型检查

### 替代方案（未采用）

**模板字面量**: `{`课程详情 - ${DEFAULT_META.siteName}`}`
- ❌ 与其他文件不一致
- ❌ 如果站点名称变更，需要修改多处

## Risks / Trade-offs

### Risk: 修改后页面标题可能变化

**缓解措施**: `formatTitle()` 函数的实现已经验证，它会返回 `${title} - ${siteName}` 的格式，与原来的混合内容完全一致。

### Risk: 可能存在其他未发现的类似问题

**缓解措施**: 建议在修复后添加 ESLint 规则或单元测试，防止将来再次出现此类问题。

## Migration Plan

1. 修改 5 个目标文件中的 `<title>` 标签
2. 运行 `pnpm dev` 验证不再有报错
3. 可选：添加测试或 ESLint 规则防止回归

## Open Questions

无
