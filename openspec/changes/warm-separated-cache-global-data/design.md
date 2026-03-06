## Context

当前系统使用**分离缓存架构**（SeparatedCacheService），将数据分为两层：
- **GLOBAL层**：所有用户共享的静态数据（如章节列表、题目列表），key格式为 `courses:ChapterViewSet:SEPARATED:GLOBAL:course_pk=1`
- **STATUS层**：用户特定的状态数据（如完成进度），key格式为 `courses:ChapterViewSet:SEPARATED:STATUS:course_pk=1:user_id=123`

然而，cache_warming/tasks.py中的预热任务仍然预热旧格式的缓存key（`api:ChapterViewSet:course_pk=1`），导致预热完全无效。ChapterViewSet和ProblemViewSet已经在views.py中使用了SeparatedCacheService.get_global_data()来获取数据，但预热任务没有预热对应的GLOBAL层key。

## Goals / Non-Goals

**Goals:**
- 完全替换现有的无效预热任务，使其预热分离缓存的GLOBAL层数据
- 预热前100个课程的所有章节列表GLOBAL缓存
- 预热每个章节的前10个题目列表GLOBAL缓存
- 支持按需预热单个资源的GLOBAL缓存
- 定期刷新高命中率（>30%）的GLOBAL缓存
- 使用正确的序列化器（ChapterGlobalSerializer、ProblemGlobalSerializer）

**Non-Goals:**
- 不预热STATUS层用户状态数据（用户特定数据无法提前预热）
- 不预热Course、Exam等未使用分离缓存的ViewSet（这些保持现状或后续优化）
- 不改变分离缓存的核心逻辑（SeparatedCacheService本身不需要修改）

## Decisions

### 1. 完全重写cache_warming/tasks.py

**决策**: 删除所有旧的预热函数（`_warm_course_list`, `_warm_popular_courses`, `_warm_course_chapters`, `_warm_popular_problems`等），新建针对GLOBAL层的预热函数。

**理由**:
- 旧函数预热的是错误的key格式，完全无效
- 新函数需要使用get_standard_cache_key(is_separated=True, separated_type="GLOBAL")
- 需要使用ChapterGlobalSerializer和ProblemGlobalSerializer（而非普通Serializer）
- 代码复用困难，因为缓存key格式和序列化器都不同

**替代方案**: 保留旧函数，添加新函数 → 被拒绝，因为会制造混乱和冗余代码。

### 2. 预热范围：前100个课程的所有章节 + 每章节前10个题目

**决策**: 启动预热覆盖所有章节列表（不限制数量），但每个章节只预热前10个题目。

**理由**:
- 章节数量通常较少（每课程10-30个），100个课程约1000-3000个章节，可接受
- 题目数量可能很大（每章节20-100个），如果全量预热可能导致启动时间过长
- 前10个题目是最常访问的，预热价值最高

**数据量估算**:
- 100课程 × 20章节/课程 = 2000章节列表缓存
- 2000章节 × 10题目/章节 = 20000题目列表缓存
- 总计约22000个缓存项，每个约1-5KB，总计约22-110MB Redis内存

**替代方案**:
- 预热所有题目 → 被拒绝，可能导致启动时间过长（可能>10分钟）
- 只预热前50个课程 → 被拒绝，覆盖率太低

### 3. 使用SeparatedCacheService还是直接set_cache？

**决策**: 预热任务直接使用set_cache()，不通过SeparatedCacheService.get_global_data()。

**理由**:
- SeparatedCacheService.get_global_data()设计用于请求处理（有回调、metrics记录）
- 预热任务是批量写入，直接set_cache()性能更高
- 避免不必要的回调函数和metrics开销

**实现细节**:
```python
# 旧格式（错误）
cache_key = get_standard_cache_key(
    prefix="api",
    view_name="ChapterViewSet",
    pk=chapter.pk
)

# 新格式（正确）
cache_key = get_standard_cache_key(
    prefix="courses",
    view_name="ChapterViewSet",
    pk=chapter.pk,
    parent_pks={"course_pk": course_id},
    is_separated=True,
    separated_type="GLOBAL"
)
```

### 4. 定时预热策略

**决策**: 继续使用AdaptiveTTLCalculator.get_hit_rate()来识别高命中率缓存，只预热命中率>30%的数据。

**理由**:
- 与现有策略一致，已经过验证
- 避免预热不常访问的数据（浪费内存）
- 命中率>30%意味着该资源至少被访问3次以上，有预热价值

## Risks / Trade-offs

### Risk 1: 启动预热时间过长

**风险**: 预热20000+缓存项可能导致启动时间从几十秒增加到数分钟。

**缓解措施**:
- 使用批量操作（pipeline）减少Redis往返
- 设置合理的超时时间（如10分钟）
- 在Celery中异步执行，不阻塞应用启动
- 添加日志监控预热进度和耗时
- 如果超时，记录警告但不失败（部分预热总比没有好）

### Risk 2: Redis内存占用增加

**风险**: 22000个缓存项可能占用额外22-110MB内存。

**缓解措施**:
- 监控Redis内存使用情况
- 设置合理的TTL（30分钟），不活跃数据会自动过期
- 如果内存不足，可以减少预热范围（如只预热前50个课程）

### Risk 3: 与业务代码的序列化器不一致

**风险**: 如果ChapterGlobalSerializer或ProblemGlobalSerializer的字段发生变化，预热任务可能需要同步更新。

**缓解措施**:
- 在tasks.py中明确注释使用的是GlobalSerializer
- 添加单元测试验证预热的数据格式与ViewSet返回的一致
- 代码审查时检查序列化器变更

## Migration Plan

### Phase 1: 准备工作（1-2小时）
1. 创建新的预热函数（保留旧函数，并行存在）
2. 添加单元测试验证新预热函数生成的缓存key正确
3. 在测试环境运行新预热任务，验证无错误

### Phase 2: 切换预热逻辑（30分钟）
1. 更新courses/apps.py，调用新的预热任务
2. 删除旧的预热函数和任务调用
3. 更新CELERY_BEAT_SCHEDULE配置（如果定时任务名称有变化）

### Phase 3: 验证和监控（1天）
1. 部署到生产环境
2. 监控启动预热任务的执行时间和成功率
3. 监控Redis缓存命中率（应显著提升）
4. 监控Redis内存使用情况
5. 检查日志中是否有预热失败或超时

### Rollback Strategy
如果出现严重问题：
1. 回滚到旧代码（保留旧预热函数作为备份直到验证通过）
2. 清理新预热的缓存（使用flushdb或重启Redis）
3. 恢复旧预热任务调用

## Open Questions

1. **是否需要预热Problem详情（retrieve）？**
   - 当前只预热Problem列表（list），不预热单个Problem详情
   - 建议暂不预热，因为用户更多访问列表，详情按需加载

2. **定时预热频率应该多久？**
   - 建议保持每小时一次，与现有策略一致
   - 可以根据实际命中率监控调整

3. **是否需要添加预热任务的健康检查？**
   - 建议添加Prometheus metrics记录预热成功/失败次数
   - 如果预热失败率超过阈值，触发告警
