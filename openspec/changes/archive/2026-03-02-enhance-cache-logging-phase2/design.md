# 增强缓存日志记录 - 阶段 2：技术设计

## Context

阶段 1 实现了基础缓存操作日志，每次缓存命中/未命中都会记录一条日志。但这些日志是分散的，缺少汇总统计和主动告警能力。当前系统已有的 Prometheus 指标可以实时查询，但无法记录历史趋势，也缺少异常检测机制。

**前置条件**：
- 阶段 1 已完成，`cache.log` 中已有单次操作日志
- 现有的 Prometheus 指标系统正常运行
- `LoggingMiddleware` 已在每个请求中记录 request_id

**约束条件**：
- 不能显著增加请求处理延迟（目标：< 0.2ms）
- 内存占用必须可控（目标：< 100MB）
- 周期性任务不能阻塞主线程
- 告警不能过于频繁，避免告警疲劳

## Goals / Non-Goals

**Goals:**
- 提供实时的缓存性能统计（命中率、平均延迟、QPS）
- 每分钟自动生成性能汇总日志
- 自动检测并告警性能异常（低命中率、高频穿透、慢操作）
- 在请求日志中包含缓存性能统计

**Non-Goals:**
- 不实现可视化的监控面板（可由 Prometheus/Grafana 提供）
- 不实现自动化的故障修复（只记录告警，不采取行动）
- 不修改缓存的业务逻辑（TTL、预热策略等）

## Decisions

### 1. 统计存储方式：Redis Hash

**选择**：使用 Redis Hash 存储统计数据

```python
# Redis Key 格式
CACHE_STATS_KEY_PREFIX = "cache:perf:stats"

# 每个端点使用一个 Hash
# Key: cache:perf:stats:{endpoint}
# Fields: hits, misses, null_values, total_duration_ms, slow_operations
redis_conn.hincrby(f"cache:perf:stats:{endpoint}", 'hits', 1)
redis_conn.hincrbyfloat(f"cache:perf:stats:{endpoint}", 'total_duration_ms', 2.5)
```

**理由**：
- **跨进程共享**：Django 进程和 Celery 进程可以访问同一份数据
- **原子操作**：使用 HINCRBY/HINCRBYFLOAT 保证并发安全
- **性能优秀**：Redis 内存操作，延迟 < 1ms
- **持久化**：数据不会因进程重启而丢失
- **TTL 支持**：可自动清理过期统计数据
- **已有基础设施**：项目已使用 Redis，无需额外依赖

**替代方案**：使用内存中的 defaultdict
- **缺点**：数据无法跨进程共享，Django 和 Celery 进程的内存隔离
- **优点**：访问速度快，无网络延迟
- **决策不采纳原因**：虽然速度快，但在实际部署中 Django 和 Celery 是分离的进程，内存方案导致汇总任务无法访问统计数据（已在实践中验证）

**性能优化**：
- 使用 Redis Pipeline 批量操作减少网络往返
- 本地 Redis 实例，延迟 < 0.5ms
- 异步写入，不阻塞主请求流程

### 2. 周期汇总方式：Celery Beat 定时任务

**选择**：使用 Celery Beat 每分钟执行一次汇总任务

**理由**：
- 系统已有 Celery 用于异步任务
- Celery Beat 支持周期性任务调度
- 任务在 worker 进程中执行，不阻塞主线程

**替代方案**：在中间件中检查时间戳
- **缺点**：每个请求都需要检查，增加开销
- **优点**：简单，无需额外组件

### 3. 异常检测阈值：可配置的硬编码默认值

**选择**：在代码中设置默认阈值，通过 settings.py 提供配置选项

```python
CACHE_PERFORMANCE_ALERT_THRESHOLDS = {
    'low_hit_rate': 0.8,        # 命中率 < 80%
    'high_penetration_rate': 0.1,  # 穿透率 > 10%
    'slow_operation_ms': 100,   # 操作耗时 > 100ms
    'high_error_rate': 0.05,    # 错误率 > 5%
}
```

**理由**：
- 默认值基于行业最佳实践
- 可根据实际情况调整
- 避免过度告警

### 4. 中间件集成：在请求结束时统计缓存性能

**选择**：在 `LoggingMiddleware` 中检查 `request._cache_stats`，存在则记录

```python
cache_stats = getattr(request, '_cache_stats', None)
if cache_stats:
    logger.info("Request cache performance", extra={
        'request_id': request.id,
        'cache_hits': cache_stats['hits'],
        'cache_misses': cache_stats['misses'],
        ...
    })
```

**理由**：
- 不修改现有 Mixin，减少侵入性
- 统计信息通过 request 对象传递，解耦清晰
- 可选择性启用（Mixins 可选择是否收集统计）

**数据流**：
```
CacheMixin → request._cache_stats → LoggingMiddleware → 日志
```

### 5. 性能汇总日志格式：结构化的 JSON

**选择**：使用单条 JSON 日志记录所有端点的统计

```json
{
  "event": "cache_performance_summary",
  "timestamp": "2026-03-01T16:30:00Z",
  "period": "60s",
  "global": {
    "total_requests": 10000,
    "hit_rate": 0.85,
    "avg_duration_ms": 2.5
  },
  "endpoints": {
    "CourseViewSet": {
      "hits": 5000,
      "misses": 500,
      "hit_rate": 0.91
    },
    ...
  },
  "alerts": [
    {
      "type": "low_hit_rate",
      "endpoint": "ProblemViewSet",
      "value": 0.65,
      "threshold": 0.8
    }
  ]
}
```

**理由**：
- 单条日志便于查询和分析
- JSON 格式支持结构化查询
- 包含全局和端点两个维度的数据

**替代方案**：每个端点一条日志
- **缺点**：日志量增加 100 倍，查询复杂

## Risks / Trade-offs

### Risk 1: 内存泄漏风险
**影响**：长期运行可能积累大量统计数据

**缓解措施**：
- 使用最近 1 小时的滑动窗口，定期清理旧数据
- 监控内存使用，超过阈值时主动清理
- 在汇总完成后重置计数器（而非累加）

### Risk 2: Redis 连接失败导致统计数据丢失
**影响**：Redis 不可用时统计数据无法记录

**缓解措施**：
- 所有统计操作使用 try-except 包装，失败时不影响缓存操作
- Redis 短暂不可用时，统计数据暂时丢失但不影响业务
- 监控 Redis 连接状态，及时告警
- 统计数据设置 TTL（300 秒），自动清理避免堆积

**替代方案（已采纳）**：使用 Redis 存储天然支持多实例部署
- 所有实例共享同一份统计数据
- 汇总任务只需读取一次，无需额外聚合

### Risk 3: 告警过于频繁
**影响**：可能产生大量告警日志，影响日志查询

**缓解措施**：
- 使用告警抑制：同一类告警 5 分钟内只记录一次
- 设置告警级别：低命中率为 WARNING，错误为 ERROR
- 提供告警开关配置

### Trade-off 1: 实时性 vs 性能
**选择**：每分钟汇总一次，而非每次操作

**权衡**：
- 优点：减少 CPU 和 I/O 开销
- 缺点：最长有 1 分钟的告警延迟
- 判断：对于缓存性能监控，1 分钟延迟可接受

### Trade-off 2: 统计精度 vs 内存
**选择**：只统计聚合数据，不保留原始操作记录

**权衡**：
- 优点：内存占用小，查询快
- 缺点：无法回溯到单次操作
- 判断：单次操作已有日志（阶段 1），汇总统计不需要原始数据

## Migration Plan

### 部署步骤
1. 实现 `CachePerformanceLogger` 类，添加到 `common/utils/logging.py`
2. 在 `cache_metrics.py` 中添加 `record_cache_*` 函数调用性能统计器
3. 修改 `cache_mixin.py`，收集统计信息到 `request._cache_stats`
4. 在 `LoggingMiddleware` 中集成缓存性能日志
5. 创建 Celery 周期性任务 `cache_performance_summary`，每分钟执行
6. 在 settings.py 中添加告警阈值配置
7. 部署后验证：
   - 检查 `cache.log` 中是否有汇总日志
   - 触发异常场景（如低命中率），验证告警生成
   - 使用性能测试验证中间件开销 < 0.2ms

### 回滚策略
- Celery 任务失败不影响主业务，可单独禁用
- 中间件集成是增量功能，可通过配置关闭
- 性能统计器异常时降级为不记录统计，保留基础日志（阶段 1）

## Open Questions

1. **是否需要持久化统计数据？**
   - 当前方案仅在内存中，服务重启后丢失
   - 如需持久化，可考虑在阶段 3 中添加

2. **告警是否需要发送通知（如邮件、钉钉）？**
   - 当前方案只记录日志
   - 可在阶段 3 集成通知系统

3. **是否需要支持动态调整告警阈值？**
   - 当前方案需要重启服务才能修改阈值
   - 可考虑使用 Django 动态配置或特性开关

4. **周期汇总的时间窗口是否可配置？**
   - 当前固定为 1 分钟
   - 可考虑支持 5 分钟、10 分钟等不同粒度
