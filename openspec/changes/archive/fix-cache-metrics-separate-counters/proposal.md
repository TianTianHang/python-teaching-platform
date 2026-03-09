# Fix Cache Metrics - Separate Counters for Total and Slow Operations

## Why

当前缓存性能监控存在严重的统计偏差：**只记录慢操作（>100ms）**，导致计算出的慢操作率永远是 100%，平均响应时间也被严重高估。这使得性能日志完全失去参考价值，无法准确反映缓存系统的真实运行状况。

## What Changes

**核心改动**：分别维护总操作计数器和慢操作计数器，实现准确的性能统计

- **分离计数器**：新增独立的总操作计数器（total_operations），与现有的慢操作详细记录分离
- **调整记录逻辑**：在所有缓存操作时更新总计数，仅在慢操作时记录详细信息
- **修正比例计算**：慢操作率 = slow_operations / total_operations（而非 slow_operations / hits）
- **修正平均值计算**：平均响应时间基于所有操作计算，而不仅仅是慢操作

## Capabilities

### Modified Capabilities

- **cache-monitoring**: 修正性能统计的准确性要求
  - **问题**：当前实现只记录慢操作，导致统计指标失真
  - **变更**：必须分别追踪总操作数和慢操作数，确保百分比和平均值基于完整样本集计算
  - **影响范围**：性能日志、告警阈值判断

## Impact

**受影响的代码模块**：

- `backend/common/metrics/cache_metrics.py`
  - 修改 `record_cache_hit/miss/null_value` 函数，总是更新总计数
  - 保持慢操作详细记录逻辑不变（仍然只记录 >100ms 的操作）

- `backend/common/utils/logging.py`
  - 修改 `CachePerformanceLogger.record_cache_operation` 方法
  - 新增 `total_operations` 计数器字段
  - 修改 `get_endpoint_stats` 和 `get_global_stats` 的比例计算逻辑

- `backend/common/utils/cache.py`
  - 调整调用 `record_cache_hit/miss` 的逻辑，移除 `duration > 0.1` 的条件判断

**Redis 数据结构变化**：

```
现有字段：
- hits: 缓存命中次数（只记录慢操作）
- misses: 缓存未命中次数（只记录慢操作）
- null_values: 空值次数（只记录慢操作）
- slow_operations: 慢操作次数（等于 hits + misses + null_values）
- total_duration_ms: 总耗时（只包含慢操作）

新增字段：
- total_operations: 总操作次数（所有操作，包括快速和慢速）
```

**性能影响**：

- **正面**：Redis 写入频率增加（每次操作都记录），但单次操作开销极小（HINCRBY）
- **内存开销**：每个端点多一个整数字段（约 8 bytes），可忽略
- **准确性提升**：获得真实的慢操作率和平均响应时间

**兼容性**：

- **BREAKING**: 日志格式和 Redis 数据结构变化
- 告警阈值判断逻辑需要相应调整（基于真实比例判断）
