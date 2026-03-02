# HTTP Connection Pool Optimization

## Why

当前前端 SSR 服务在高并发场景下存在性能瓶颈：每个 API 请求都创建新的 Axios 实例和 TCP 连接，导致重复的 TCP 握手开销（约 1-3ms/请求）。在高负载下，这个额外开销会累积，显著增加响应延迟。

## What Changes

- 在 `frontend/web-student/app/utils/http/index.server.ts` 中添加全局 HTTP/HTTPS Agent 配置
- 启用 TCP Keep-Alive 连接复用
- 配置合理的连接池参数（maxSockets, maxFreeSockets, keepAliveMsecs）
- 添加连接池监控和日志（可选）

## Capabilities

### New Capabilities

- `http-connection-pool`: 为 SSR 服务端的 HTTP 请求提供连接池管理，实现 TCP 连接复用，降低高并发场景下的请求延迟

### Modified Capabilities

无。此改动仅优化实现细节，不影响对外 API 行为。

## Impact

- **Affected Code**: `frontend/web-student/app/utils/http/index.server.ts`
- **Performance**: 预期降低高并发场景下的 API 请求延迟 10-30%
- **Compatibility**: 完全向后兼容，不破坏现有功能
- **Dependencies**: 无新增依赖（使用 Node.js 内置 `http` 和 `https` 模块）
- **Systems**: 仅影响前端 SSR 服务，无需改动后端
