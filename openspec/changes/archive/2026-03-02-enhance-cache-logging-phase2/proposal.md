# 增强缓存日志记录 - 阶段 2：性能统计与告警

## Why

阶段 1 实现了基础缓存操作日志，但缺少汇总统计和主动告警能力。当缓存命中率下降、缓存穿透频繁发生时，运维人员需要主动查询日志才能发现问题，响应延迟。此外，当前没有集中的性能统计视图，无法快速了解各端点的缓存效率。本阶段旨在建立自动化的性能统计和告警机制，让系统能够主动报告异常情况。

## What Changes

- **实现 CachePerformanceLogger 类**：提供内存中的性能统计收集器，按 endpoint 聚合 hits、misses、平均延迟等指标
- **添加周期性性能汇总日志**：每分钟生成一次性能统计报告，包含总体命中率、各端点表现、慢操作 Top N
- **增强性能异常告警**：自动检测低命中率（< 80%）、高频穿透（> 10次/分钟）、缓存错误等异常情况
- **集成到请求中间件**：在 LoggingMiddleware 中记录每个请求的缓存性能统计（hits、misses、duration）
- **添加缓存性能日志到中间件**：在请求结束时汇总缓存操作，提供请求维度的缓存性能视图

## Capabilities

### New Capabilities
- `cache-performance-stats`: 缓存性能统计能力，提供实时统计、周期汇总、异常检测功能
- `cache-performance-alerts`: 缓存性能告警能力，自动检测并记录性能异常

### Modified Capabilities
- 无需修改现有 capabilities，本阶段在阶段 1 基础上增强，不改变基础日志行为

## Dependencies

- **依赖阶段 1**：本阶段建立在阶段 1 的基础日志之上，需要 `cache.log` 中已有单次操作的日志记录
- **依赖现有的中间件系统**：将在 `LoggingMiddleware` 中集成缓存性能统计

## Impact

- **代码变更**：
  - `backend/common/utils/logging.py`：新增 `CachePerformanceLogger` 类
  - `backend/common/middleware/logging_middleware.py`：集成缓存性能统计
  - `backend/common/metrics/cache_metrics.py`：添加性能汇总和告警函数

- **新增功能**：
  - 每分钟自动生成性能汇总日志
  - 自动检测并告警缓存异常情况

- **性能影响**：
  - 内存统计：每个 endpoint 约 100 bytes，100 个端点约 10KB（可忽略）
  - 汇总计算：每分钟一次，耗时约 10-50ms
  - 中间件开销：每个请求额外 0.1-0.2ms

- **日志量影响**：每分钟新增 1 条汇总日志，每天约 1440 条（~100KB），对整体日志量影响很小
