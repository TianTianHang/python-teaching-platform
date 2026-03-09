## Why

当前缓存操作存在严重的性能问题：每次缓存命中（cache hit）都会触发多次 Redis 往返和日志记录操作，导致 800-1700ms 的延迟。缓存本应加速请求，却因过度统计成为瓶颈。

## What Changes

- **移除热路径统计**: 缓存命中时不再调用 `AdaptiveTTLCalculator.record_hit()` 写入 Redis 统计
- **延迟统计记录**: 统计数据改为采样或异步批量写入
- **精简日志**: 只在缓存操作超过 100ms 阈值时记录详细日志
- **保留 Prometheus 计数**: 基本的 counter 指标保留（内存操作，开销可忽略）

## Capabilities

### New Capabilities
- `lightweight-cache-stats`: 轻量化缓存统计机制，减少 Redis 往返次数

### Modified Capabilities
- (无)

## Impact

- `common/utils/cache.py`: 修改 `get_cache()` 和 `set_cache()` 的统计逻辑
- `common/metrics/cache_metrics.py`: 优化 `record_cache_hit()` 等函数
- 性能收益: 每次缓存操作减少 2-5 次 Redis RTT