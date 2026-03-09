## Context

当前缓存操作（`get_cache` / `set_cache`）在每次缓存命中时都会执行多次 Redis 往返：

1. `cache.get(key)` - 1 次 RTT
2. `AdaptiveTTLCalculator.record_hit()` - 3 次独立 RTT (hincrby + hset + expire)
3. `record_cache_hit()` - 触发 Redis pipeline (4 次操作)
4. 日志记录 - JSON 序列化开销

这导致本应快速的缓存操作产生 800-1700ms 的延迟。

## Goals / Non-Goals

**Goals:**
- 消除正常缓存操作（< 100ms）的 Redis 统计写入开销
- 保留慢操作的详细日志和统计能力
- 保留 Prometheus 基本计数器（内存操作，开销可忽略）

**Non-Goals:**
- 不改变缓存逻辑本身（命中率、TTL 计算等）
- 不删除任何现有的监控能力，只是延迟/采样执行

## Decisions

### D1: 仅在慢操作时触发完整统计

**决定**: 只有当缓存操作时间 >= 100ms 时才执行 Redis 统计写入和详细日志。

**理由**: 100ms 以上的操作本身就是异常情况，此时的 Redis 开销相对请求总时间可忽略。正常路径（90%+ 的请求）零额外开销。

### D2: 移除热路径的 AdaptiveTTLCalculator 调用

**决定**: 从 `get_cache()` 中移除 `AdaptiveTTLCalculator.record_hit()` 调用。

**理由**: 每次缓存命中都写 3 次 Redis (hincrby + hset + expire)，这是主要开销来源。统计可以采样或异步写入。

**替代方案考虑**:
- 保留但用 Pipeline - 仍需每次 RTT
- 异步队列写入 - 复杂度高，收益不确定

### D3: 保持 Prometheus counter 正常执行

**决定**: 不修改 `cache_requests_total` 等 Prometheus 指标的递增。

**理由**: Prometheus counter 是内存操作，开销可忽略，且提供全局聚合能力。

## Risks / Trade-offs

| 风险 | 影响 | 缓解 |
|------|------|------|
| 统计精度下降 | 采样导致数据不精确 | 采样率 10% 仍足够反映趋势 |
| 慢日志噪声 | 100ms 阈值可能产生大量日志 | 仅记录 WARNING 级别，自动聚合 |
| TTL 自适应失效 | `record_hit` 不再被调用 | 考虑定时批量同步或保留采样 |

## Migration Plan

1. 修改 `cache.py` 中 `get_cache()` - 条件化 `record_hit()` 调用
2. 修改 `cache_metrics.py` 中 `record_cache_hit()` - 添加阈值判断
3. 验证: 检查 cache.log 不再每条都是 WARNING
4. 监控: 确认缓存延迟下降到合理范围