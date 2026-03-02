# HTTP Connection Pool Optimization - Design

## Context

### 当前架构

前端 SSR 服务使用 React Router v7，每个 loader 中通过 `createHttp(request)` 创建新的 HTTP 客户端实例来请求后端 API。当前实现中，每次请求都创建新的 Axios 实例，没有配置 HTTP Agent，导致：

1. **无 TCP 连接复用**：每个请求都进行完整的 TCP 三次握手
2. **额外延迟累积**：高并发时 1-3ms/连接 的开销会累积
3. **连接效率低**：请求结束后立即关闭连接，无法复用

### 部署环境

- **SSR 服务**：使用 PM2 集群模式（`instances: "max"`），每个 Node 进程独立运行
- **后端通信**：直接调用 Django API (http://backend:8000/api/v1)
- **客户端通信**：通过 Nginx 代理到后端

### 约束

- 必须保持 SSR 兼容性（Agent 仅在服务端使用）
- 不能破坏现有的 JWT 认证流程
- 必须与 PM2 集群模式兼容（每个进程独立连接池）

## Goals / Non-Goals

**Goals:**
- 实现 TCP 连接复用，降低高并发场景下的 API 请求延迟
- 在 SSR 服务端配置全局 HTTP/HTTPS Agent
- 确保向后兼容，不破坏现有功能
- 提供合理的连接池参数配置

**Non-Goals:**
- 不改动客户端（浏览器）的 HTTP 行为（浏览器自动管理连接池）
- 不修改后端 API 或配置
- 不添加复杂的连接池监控（可后续优化）

## Decisions

### 1. 使用 Node.js 内置 http/https.Agent

**决定**：使用 Node.js 原生 `http.Agent` 和 `https.Agent`，而非第三方库。

**理由**：
- Node.js 内置 Agent 已支持 Keep-Alive 和连接池
- 无需引入新依赖，降低维护成本
- 性能成熟稳定，被广泛使用

**替代方案**：使用 `undici` 库
- ❌ 更复杂，需要更多改动
- ❌ 与现有 Axios 集成需要额外配置

### 2. 进程级全局单例 Agent

**决定**：在每个 Node 进程中创建全局单例 Agent，所有 Axios 实例共享。

**理由**：
- PM2 集群模式下，每个进程独立内存，天然隔离
- 全局单例确保连接池复用
- 简单高效，无需状态管理

**代码位置**：`frontend/web-student/app/utils/http/index.server.ts`

### 3. 连接池参数配置

**决定参数值**：
```typescript
{
  keepAlive: true,          // 启用 Keep-Alive
  maxSockets: 50,           // 每个目标主机的最大连接数
  maxFreeSockets: 10,       // 空闲时保留的连接数
  keepAliveMsecs: 1000,     // Keep-Alive 探测间隔
  timeout: 30000,           // socket 超时
}
```

**参数选择理由**：

| 参数 | 值 | 理由 |
|------|-----|------|
| `maxSockets` | 50 | 4 核 CPU × 4 PM2 进程 × 50 = 200 总连接。后端 Django (Gunicorn) 通常处理 16-32 并发，200 连接有充足余量 |
| `maxFreeSockets` | 10 | 平衡内存占用和连接复用效率，保留少量空闲连接以备复用 |
| `keepAliveMsecs` | 1000 | 1 秒探测间隔，及时发现死连接 |
| `timeout` | 30000 | 30 秒超时，避免长时间占用连接 |

**可调优**：如果后端性能更强（如异步框架），可提高 `maxSockets` 到 100。

### 4. 仅服务端使用 Agent

**决定**：仅在 `isServer` 为 `true` 时创建 Agent，客户端不配置。

**理由**：
- 浏览器环境已自动管理 HTTP 连接池
- 避免客户端代码引入 Node.js 模块（导致构建错误）
- 保持代码同构性

```typescript
const isServer = typeof window === 'undefined';
const globalHttpAgent = isServer ? new http.Agent({...}) : undefined;
```

### 5. 集成方式：修改 globalConfig

**决定**：在 `globalConfig` 中添加 `httpAgent` 和 `httpsAgent` 字段。

**理由**：
- 最小化改动，仅需修改一个文件
- 所有通过 `createHttp()` 创建的实例自动继承
- 无需修改现有的 loader 代码

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|----------|
| **连接池耗尽**：高并发时所有连接被占用，新请求排队 | `maxSockets: 50` 限制单进程连接数，配合 PM2 集群模式，总连接数充足 |
| **内存占用**：保持空闲连接占用内存 | `maxFreeSockets: 10` 限制空闲连接数，`timeout: 30000` 自动回收 |
| **死连接**：后端重启或网络问题导致连接失效 | `keepAliveMsecs: 1000` 探测，Node.js Agent 自动处理 |
| **PM2 集群兼容**：多进程可能共享端口导致冲突 | PM2 自动处理端口复用 (SO_REUSEPORT)，每个进程独立连接池 |
| **调试困难**：连接池状态不可见 | 可通过 `agent.sockets` 和 `agent.freeSockets` 监控（后续优化） |

## Migration Plan

### 部署步骤

1. **代码改动**：修改 `frontend/web-student/app/utils/http/index.server.ts`
2. **本地测试**：运行 SSR 服务，验证功能正常
3. **构建部署**：`pnpm run build`，重启 PM2 服务
4. **监控验证**：观察响应延迟和错误率

### 回滚策略

- 如果出现连接问题，立即删除 Agent 配置，恢复原代码
- 无需数据库迁移或后端改动，回滚零风险

## Open Questions

无。此优化方案明确且低风险，可直接实施。
