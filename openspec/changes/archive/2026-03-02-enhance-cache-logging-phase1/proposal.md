# 增强缓存日志记录 - 阶段 1：基础日志增强

## Why

当前系统虽然有 Prometheus 指标收集缓存性能数据，但这些指标仅在 `/metrics` 端点可用，缺少持久化的日志记录。当需要追溯历史问题、审计缓存性能趋势、或在没有 Prometheus 环境下分析问题时，无法获取缓存性能的历史数据。此外，现有的缓存日志仅限于 DEBUG 级别的简单记录，在生产环境中无法输出，且缺少关键的性能指标信息。

## What Changes

- **在 `cache_metrics.py` 的记录函数中添加日志输出**：`record_cache_hit()`, `record_cache_miss()`, `record_cache_null_value()` 在更新 Prometheus 指标的同时，记录结构化日志到专门的缓存日志文件
- **增强 `cache_mixin.py` 的日志信息**：在缓存命中/未命中的日志中添加性能指标，包括响应时间、TTL、命中率等
- **配置专用的缓存日志文件**：新增 `cache.log` 文件，使用 JSON 格式记录缓存操作，便于后续分析
- **添加性能异常检测日志**：当缓存操作耗时超过阈值（100ms）时，自动记录 WARNING 级别日志

## Capabilities

### New Capabilities
- `cache-logging`: 缓存操作日志记录能力，涵盖缓存命中、未命中、空值、穿透等场景的结构化日志记录

### Modified Capabilities
- 无需修改现有 capabilities，本阶段仅为日志增强，不改变业务行为

## Impact

- **代码变更**：
  - `backend/common/metrics/cache_metrics.py`：在现有指标记录函数中添加日志调用
  - `backend/common/mixins/cache_mixin.py`：增强缓存操作的日志信息
  - `backend/core/settings.py`：新增缓存日志配置

- **新增文件**：
  - `backend/logs/cache.log`：缓存操作日志文件

- **日志量影响**：每个缓存操作会额外产生一条 INFO 级别日志，预计在高流量场景下每日新增约 10-50MB 日志

- **性能影响**：日志写入采用同步方式，单次操作耗时约 0.1-0.5ms，对缓存性能影响可忽略

- **依赖项**：无新增依赖，使用现有的 logging 和 pythonjsonlogger 库
