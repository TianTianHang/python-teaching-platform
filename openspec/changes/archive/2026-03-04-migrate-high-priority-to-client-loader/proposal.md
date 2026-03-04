## Why

当前高优先级页面使用 `useEffect + clientHttp.get()` 在组件内部获取数据，这种方式：
- 无法利用 React Router 7 的 SSR + Hydration 能力
- 组件代码重复 loading、error、401 处理逻辑
- 不符合 React Router 7 的官方推荐模式

迁移到 `clientLoader` 模式可以利用 SSR 水合机制，提升首屏加载性能和 SEO。

## What Changes

- 将 `_layout.home.tsx` 从 useEffect 迁移到 clientLoader
- 将 `_layout.courses/route.tsx` 从 useEffect 迁移到 clientLoader
- 将 `_layout.courses_.$courseId/route.tsx` 从 useEffect 迁移到 clientLoader
- 移除组件内的 useEffect 和相关 state 代码
- 添加 `clientLoader.hydrate = true` 支持 SSR 水合
- 保持相同的错误处理和 401 重定向逻辑

## Capabilities

### New Capabilities
<!-- 这是一个纯技术迁移，不涉及新功能 -->
- 无新功能

### Modified Capabilities
- 无需求变更

## Impact

- 3 个页面组件代码重构
- 数据加载逻辑从组件移到 clientLoader
- 错误处理通过 React Router 的 errorElement 机制
- 依赖 `clientHttp` 在客户端执行