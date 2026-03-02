# 增强缓存日志记录 - 阶段 2：实施任务

## 1. 实现 CachePerformanceLogger 类

- [x] 1.1 在 `common/utils/logging.py` 中创建 `CachePerformanceLogger` 类
- [x] 1.2 实现统计数据结构：使用 `defaultdict` 存储每个 endpoint 的 hits、misses、null_values、total_duration、slow_operations
- [x] 1.3 实现 `record_cache_operation()` 方法，用于记录单次缓存操作并更新统计数据
- [x] 1.4 实现 `get_endpoint_stats(endpoint)` 方法，返回单个端点的统计信息
- [x] 1.5 实现 `get_all_endpoint_stats()` 方法，返回所有端点的统计信息
- [x] 1.6 实现 `get_global_stats()` 方法，返回全局聚合统计
- [x] 1.7 实现 `reset_stats()` 方法，清空所有统计数据
- [x] 1.8 添加 `_calculate_hit_rate()` 等辅助方法，用于计算派生指标

## 2. 集成性能统计到现有代码

- [x] 2.1 在 `common/metrics/cache_metrics.py` 中导入 `CachePerformanceLogger`
- [x] 2.2 修改 `record_cache_hit()` 函数，调用 `CachePerformanceLogger.record_cache_operation()`
- [x] 2.3 修改 `record_cache_miss()` 函数，同样调用统计记录方法
- [x] 2.4 修改 `record_cache_null_value()` 函数，同样调用统计记录方法
- [x] 2.5 在调用统计记录时使用 try-except，确保统计失败不影响指标收集

## 3. 增强 Cache Mixin 统计收集

- [x] 3.1 在 `common/mixins/cache_mixin.py` 的 `CacheListMixin.list()` 中初始化 `request._cache_stats` 字典
- [x] 3.2 每次缓存命中时，更新 `request._cache_stats['hits']`
- [x] 3.3 每次缓存未命中时，更新 `request._cache_stats['misses']`
- [x] 3.4 累计缓存操作耗时到 `request._cache_stats['duration_ms']`
- [x] 3.5 同样在 `CacheRetrieveMixin.retrieve()` 中实现相同的统计收集

## 4. 中间件集成

- [x] 4.1 在 `common/middleware/logging_middleware.py` 的 `LoggingMiddleware.__call__()` 中检查 `request._cache_stats`
- [x] 4.2 如果缓存统计存在，在请求日志中添加缓存性能字段（cache_hits、cache_misses、cache_hit_rate、cache_duration_ms）
- [x] 4.3 确保缓存统计日志使用 INFO 级别，包含 request_id 以便关联

## 5. 实现性能告警检测

- [x] 5.1 在 `CachePerformanceLogger` 类中添加 `check_low_hit_rate()` 方法，检测命中率低于阈值的端点
- [x] 5.2 实现 `check_high_penetration_rate()` 方法，检测穿透率高于阈值的端点
- [x] 5.3 实现 `check_high_error_rate()` 方法，检测错误率高于阈值的端点
- [x] 5.4 实现 `check_slow_operations()` 方法，检测慢操作率过高的情况
- [x] 5.5 在 `core/settings.py` 中添加 `CACHE_PERFORMANCE_ALERT_THRESHOLDS` 配置项，包含默认阈值
- [x] 5.6 实现告警抑制机制，使用 `_last_alert_time` 字典避免 5 分钟内重复告警

## 6. 实现周期性汇总日志

- [x] 6.1 在 `common/utils/logging.py` 中实现 `CachePerformanceLogger.log_performance_summary()` 方法
- [x] 6.2 汇总日志包含全局统计、各端点统计、Top 5 慢端点、Top 5 高未命中率端点
- [x] 6.3 在汇总日志中包含所有触发的告警，使用 alerts 字段
- [x] 6.4 在 `common/celery.py` 或新建 `common/cache_warming/tasks.py` 中创建周期性任务
- [x] 6.5 使用 Celery Beat 配置每 60 秒执行一次 `cache_performance_summary` 任务
- [x] 6.6 在任务中调用 `CachePerformanceLogger.log_performance_summary()` 和 `reset_stats()`

## 7. 测试和验证

- [ ] 7.1 手动触发缓存操作，验证统计数据正确累加
- [ ] 7.2 等待一个汇总周期（60 秒），检查 `cache.log` 中是否生成汇总日志
- [ ] 7.3 验证汇总日志的 JSON 格式正确，包含所有必需字段
- [ ] 7.4 触发低命中率场景（清空缓存后大量请求），验证告警日志生成
- [ ] 7.5 使用性能测试工具（locustfile.py）验证中间件开销 < 0.2ms
- [ ] 7.6 验证告警抑制机制：重复告警在 5 分钟内只记录一次
- [ ] 7.7 测试配置项覆盖：修改 settings.py 中的阈值，验证告警使用新阈值
- [ ] 7.8 测试异常场景：统计记录失败时，确保缓存操作仍正常工作

## 8. 文档和清理

- [x] 8.1 在 `common/utils/logging.py` 中为 `CachePerformanceLogger` 添加完整的 docstring
- [x] 8.2 在 `backend/core/settings.py` 中添加 `CACHE_PERFORMANCE_ALERT_THRESHOLDS` 配置说明
- [x] 8.3 创建示例日志文件 `backend/logs/cache.log.example`，展示汇总和告警日志格式
- [x] 8.4 更新 README 或文档，说明如何查看和解读缓存性能日志
