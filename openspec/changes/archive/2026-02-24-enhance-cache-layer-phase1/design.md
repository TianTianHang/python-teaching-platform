## Context

当前缓存系统的核心问题：
1. **穿透漏洞**：`get_cache()` 无法区分空值和未命中，导致对不存在的资源（如 `/api/v1/courses/99999`）持续穿透到数据库
2. **固定 TTL**：所有数据使用 900 秒固定超时，无法根据访问热度调整
3. **缺乏预热**：应用启动时缓存为空，用户面临冷启动延迟
4. **监控盲区**：无法追踪缓存命中率和穿透情况

现有缓存实现：
- 使用 `django-redis` 作为缓存后端
- `CacheListMixin` 和 `CacheRetrieveMixin` 处理缓存逻辑
- 信号驱动的缓存失效机制
- 所有缓存数据序列化为 JSON 存储在 Redis

## Goals / Non-Goals

**Goals:**
- 实现缓存穿透保护，区分空值和未命中状态
- 引入动态 TTL 策略，根据访问频率调整超时时间
- 建立异步缓存预热机制，减少冷启动延迟
- 集成缓存监控指标，支持可视化分析
- 实现限流保护，防止恶意请求

**Non-Goals:**
- 不引入多层缓存架构（L1+L2）
- 不使用布隆过滤器（将在第二阶段考虑）
- 不修改前端代码或 API 接口
- 不实现缓存分片或 Redis 集群（基础设施优化阶段）

## Decisions

### 1. 哨兵值模式（Sentinel Value）

**Decision**: 使用 `CacheResult` 类封装缓存结果，包含数据、状态和元信息。

**Alternative**: 使用返回元组 `(data, status)`，但缺乏类型安全和可扩展性。

```python
class CacheResult:
    data: Any
    status: Literal['HIT', 'MISS', 'NULL_VALUE']
    cached_at: Optional[float]
    ttl: Optional[int]

    @classmethod
    def hit(cls, data, cached_at=None, ttl=None):
        return cls(data, 'HIT', cached_at, ttl)

    @classmethod
    def miss(cls):
        return cls(None, 'MISS', None, None)

    @classmethod
    def null_value(cls, cached_at=None, ttl=None):
        return cls(None, 'NULL_VALUE', cached_at, ttl)
```

### 2. 自适应 TTL 策略

**Decision**: 基于访问频率和数据特性动态调整 TTL。

**Rationale**: 热点数据应该缓存更长时间，冷数据适当缩短 TTL 以释放内存。

```python
class AdaptiveTTLCalculator:
    @staticmethod
    def calculate(hits, misses, last_accessed, data_age):
        # 基于命中率
        hit_rate = hits / (hits + misses + 1)

        # 基于访问频率
        if hit_rate > 0.5 and hits > 100:
            return 1800  # 热点数据 30 分钟
        elif hit_rate > 0.2 and hits > 10:
            return 900   # 常规数据 15 分钟
        else:
            return 300   # 冷数据 5 分钟
```

### 3. 缓存预热策略

**Decision**: 实现三级预热策略：启动预热、按需刷新、定时刷新。

**Alternative**: 仅使用定时刷新，但无法应对流量突发。

- **启动预热**：应用启动时预热核心数据
- **按需刷新**：首次访问过期数据时异步刷新
- **定时刷新**：后台任务定期刷新热点数据

### 4. 监控指标设计

**Decision**: 集成 Prometheus 指标，使用 Django Prometheus 库。

**Rationale**: 标准化监控方案，便于 Grafana 可视化。

关键指标：
- `cache_requests_total`: 请求总数
- `cache_hits_total`: 命中总数
- `cache_misses_total`: 未命中总数
- `cache_hit_rate`: 命中率
- `cache_warming_tasks_count`: 预热任务数

### 5. 限流策略

**Decision**: 使用 DRF 内置限流，配置差异化速率限制。

**Alternative**: 使用 Redis 实现分布式限流，但增加复杂度。

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',      # 匿名用户 100次/小时
        'user': '1000/hour',     # 认证用户 1000次/小时
    }
}
```

## Risks / Trade-offs

**[Risk] 新缓存 API 破坏现有代码**
→ **Mitigation**: 保持 `get_cache()` 和 `set_cache()` 函数接口不变，内部重构为返回 `CacheResult`

**[Risk] 空值短 TTL 导致频繁刷新**
→ **Mitigation**: 实现最小间隔限制，同一空值至少间隔 60 秒才能刷新

**[Risk] 预热任务占用过多资源**
→ **Mitigation**: 配置 Celery 任务优先级，限制并发数，使用错峰预热

**[Trade-off] 复杂度 vs 灵活性**
→ 更详细的监控和策略带来配置复杂度，但提供了更多优化空间

**[Trade-off] 内存使用**
→ 预热数据会占用更多内存，但通过动态 TTL 可以控制增长

## Migration Plan

### 实施步骤
1. 创建新缓存工具类，保持向后兼容
2. 更新 CacheMixin 类使用新缓存功能
3. 实现缓存预热模块
4. 集成监控和限流功能
5. 全面测试性能和功能

### 回退策略
1. 代码层面的开关控制：
   - 在 `settings.py` 中添加 `ENABLE_ENHANCED_CACHE = False`
   - 新缓存工具类检查此开关，默认使用原逻辑
2. 如遇问题，简单修改代码开关即可回退
3. 缓存数据结构保持兼容，无需重建

## Open Questions

1. **预热数据优先级**：如何确定哪些数据应该优先预热？
   → 决策：基于历史访问频率，预热 TOP 100 的课程和题目

2. **TTL 动态调整的触发时机**：实时调整还是定期重新计算？
   → 决策：使用滑动窗口，每 5 分钟重新计算一次

3. **监控告警阈值**：命中率达到多少需要告警？
   → 决策：命中率 < 80% 且请求量 > 100/min 时触发告警