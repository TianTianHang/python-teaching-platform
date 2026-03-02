# 增强缓存日志记录 - 阶段 1：技术设计

## Context

当前系统使用 Prometheus 收集缓存性能指标，通过 `record_cache_hit()`, `record_cache_miss()` 等函数记录到 Counter 和 Gauge 指标中。这些数据可通过 Grafana 可视化，但无法持久化存储或追溯历史。现有的日志系统在 `cache_mixin.py` 中有少量 DEBUG 级别的缓存日志，但在生产环境不可见。

**约束条件**：
- 必须保持向后兼容，不能破坏现有的 Prometheus 指标收集
- 日志写入不能显著影响缓存性能（目标：< 0.5ms 额外耗时）
- 需要支持现有日志系统的结构化日志格式（JSON）
- 需要与现有的 `DetailedFormatter` 兼容

## Goals / Non-Goals

**Goals:**
- 在所有缓存操作中记录结构化日志，包含 endpoint、状态、耗时等关键信息
- 当缓存性能异常（如慢查询、低命中率）时自动记录告警日志
- 日志格式统一为 JSON，便于后续使用 ELK/Loki 等工具分析
- 不影响现有的 Prometheus 指标收集功能

**Non-Goals:**
- 本阶段不实现周期性的性能汇总报告（阶段 2）
- 不修改缓存行为本身（TTL、预热策略等）
- 不引入新的外部依赖（如 structlog 等日志库）

## Decisions

### 1. 日志记录位置：在 `cache_metrics.py` 中统一记录

**选择**：在 `record_cache_hit()`, `record_cache_miss()`, `record_cache_null_value()` 函数中同时记录日志

**理由**：
- 这些函数已被 `cache_utils.py` 调用，是缓存操作的统一入口
- 可确保所有缓存操作都被记录，无遗漏
- Prometheus 指标和日志在同一个位置，便于维护数据一致性

**替代方案**：在 `cache_mixin.py` 中记录
- **缺点**：只能记录视图层的缓存操作，无法覆盖直接调用 `get_cache()` 的场景

### 2. 日志格式：使用 JSON 格式化器

**选择**：复用现有的 `pythonjsonlogger.jsonlogger.JsonFormatter`

**理由**：
- 生产环境已使用 JSON 格式（api.log, security.log）
- 便于机器解析和分析
- 支持嵌套结构，适合记录复杂的 extra 字段

**替代方案**：使用自定义格式化器
- **缺点**：增加维护成本，现有格式化器已满足需求

### 3. 日志级别：INFO 为主，WARNING 用于异常

**选择**：
- 正常缓存操作：INFO 级别
- 慢操作（> 100ms）：WARNING 级别
- 缓存穿透：WARNING 级别（已存在）

**理由**：
- INFO 级别在生产环境开启，可记录完整操作日志
- WARNING 级别用于需要关注但不影响系统运行的异常
- 避免过度使用 ERROR 级别

### 4. 日志内容：结构化字段设计

**选择**：在日志的 `extra` 字段中包含以下信息
```json
{
  "event": "cache_hit|cache_miss|cache_null_value",
  "endpoint": "CourseViewSet|ChapterViewSet|...",
  "status": "hit|miss|null_value",
  "duration_ms": 2.5,
  "hit_rate": 0.85,
  "operation": "get|set|delete"
}
```

**理由**：
- `event` 字段便于按事件类型过滤日志
- `endpoint` 支持按视图分析缓存性能
- `duration_ms` 用于检测慢缓存操作
- `hit_rate` 提供实时性能上下文

### 5. 日志文件：独立的 cache.log

**选择**：新增 `cache.log` 文件，使用 RotatingFileHandler（10MB，保留 10 个文件）

**理由**：
- 与 api.log, django.log 等文件保持一致的轮转策略
- 独立文件便于单独分析缓存性能
- 避免污染其他日志文件

**替代方案**：写入现有的 api.log
- **缺点**：api.log 已较大（6.9MB），混合缓存日志会增加查询复杂度

## Risks / Trade-offs

### Risk 1: 日志量过大导致磁盘压力
**影响**：高流量场景下，每秒可能有数千次缓存操作，产生大量日志

**缓解措施**：
- 使用 RotatingFileHandler 自动轮转，总大小控制在 100MB
- 在阶段 2 考虑添加日志采样策略（如只记录 10% 的 HIT 操作）
- 监控磁盘使用，必要时调整轮转策略

### Risk 2: 日志写入影响缓存性能
**影响**：同步写入日志可能增加缓存操作的延迟

**缓解措施**：
- 日志级别设置为 INFO，避免不必要的 DEBUG 日志
- 使用性能测试验证（locustfile.py）影响 < 0.5ms
- 阶段 2 考虑使用 QueueHandler 实现异步日志

### Risk 3: 日志与 Prometheus 指标不一致
**影响**：日志和指标可能因异常情况（如日志写入失败）而不一致

**缓解措施**：
- 日志记录使用 try-except 包裹，避免异常影响指标收集
- 关键操作（如穿透尝试）同时在指标和日志中记录
- 定期对比日志和指标数据的一致性

### Trade-off 1: 日志详细程度 vs 性能
**选择**：优先保证性能，日志内容精简但包含关键字段

**权衡**：
- 不记录完整的 cache_key（可能很长），只记录 endpoint
- 不记录缓存值的大小（需要额外计算）
- 如需更详细的信息，可临时调整为 DEBUG 级别

### Trade-off 2: 命中率计算频率
**选择**：每次缓存操作时实时计算当前 endpoint 的命中率

**权衡**：
- 优点：日志中包含实时命中率，便于分析
- 缺点：需要读取 Prometheus 指标值，增加少量开销
- 备选方案：阶段 2 改为批量计算，减少查询频率

## Migration Plan

### 部署步骤
1. 更新 `settings.py`，添加 `cache_file` handler 和 `teaching_platform.cache` logger
2. 修改 `cache_metrics.py`，在记录函数中添加日志调用
3. 更新 `cache_mixin.py`，增强日志信息（如添加耗时、TTL 等）
4. 部署后观察 `logs/cache.log` 文件生成情况
5. 运行性能测试（locustfile.py），验证性能影响在可接受范围内

### 回滚策略
- 保留原有 Prometheus 指标收集功能，日志为纯增量功能
- 如出现性能问题，可在 settings.py 中将 `teaching_platform.cache` logger 级别调整为 WARNING
- 如磁盘压力过大，可临时禁用 cache_file handler

## Open Questions

1. **是否需要记录缓存 key 的 hash 值？**
   - 当前方案只记录 endpoint，不记录具体的 cache_key
   - 如需追踪热点 key，可在阶段 2 添加

2. **慢操作的阈值是否可配置？**
   - 当前硬编码为 100ms
   - 可考虑在 settings.py 中添加 `CACHE_SLOW_THRESHOLD` 配置项

3. **是否需要记录缓存写入操作？**
   - 当前只记录读操作（get），不记录写操作（set/delete）
   - 如需分析缓存更新频率，可在后续阶段添加
