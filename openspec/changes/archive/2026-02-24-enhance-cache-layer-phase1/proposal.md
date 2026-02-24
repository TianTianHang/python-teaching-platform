## Why

当前缓存实现存在缓存穿透风险和性能优化空间。具体问题：
- 缓存无法区分空值和未命中，导致对不存在的资源请求持续穿透到数据库
- 缓存命中率低，无法根据访问模式动态调整策略
- 缺乏预热机制，冷启动时用户等待时间长
- 无监控指标，难以排查和优化缓存问题

这些影响了系统性能和用户体验，需要在第一阶段的架构优化中解决。

## What Changes

### Core Changes
- **增强缓存穿透保护**：实现哨兵值模式，区分缓存空值和未命中
- **智能缓存策略**：实现空值短 TTL、自适应 TTL 策略
- **异步缓存预热**：启动预热、按需刷新、定时刷新三种预热模式
- **监控与限流**：缓存命中率统计、穿透检测、DRF 限流保护

### Technical Changes
- 重构 `common/utils/cache.py`：返回 `CacheResult` 元组封装状态
- 更新 `CacheMixin`：支持哨兵值和空值短 TTL
- 新增 `cache_warming` 模块：Celery 任务驱动预热
- 集成监控指标：Prometheus + Grafana 可视化
- 配置 DRF 限流：匿名和认证用户的差异化限流

## Capabilities

### New Capabilities
- `cache-penetration-protection`: 实现缓存穿透保护机制，区分空值和未命中状态
- `adaptive-cache-ttl`: 基于访问频率和数据特性的动态 TTL 调整策略
- `async-cache-warming`: 支持启动预热、按需刷新和定时刷新的异步缓存预热系统
- `cache-metrics-and-monitoring`: 缓存命中率、穿透检测等监控指标采集

### Modified Capabilities
- `route-caching`: 需要增强缓存控制 headers，支持 stale-while-revalidate
- `nested-route-cache`: 哨兵值模式下嵌套路由的缓存键需要特殊处理

## Impact

### Backend
- `backend/common/utils/cache.py` - 重构核心缓存工具函数
- `backend/common/mixins/cache_mixin.py` - 更新 Mixin 类
- `backend/common/` - 新增 cache_warming 模块
- `backend/core/settings.py` - 配置限流策略

### Frontend
- `frontend/web-student/` - 无需改动，通过 API 影响数据加载速度

### Operations
- `docker-compose.yml` - 可选添加 Redis 连接池配置
- 新增 Prometheus + Grafana 监控栈
- Celery 队列管理预热任务

### Risks
- 中小缓存数据库（Redis）存储需求增加约 10-20%
- Celery 预热任务占用服务器资源
- 短期过渡期可能出现缓存一致性问题