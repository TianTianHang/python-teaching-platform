## Why

当前cache_warming预热任务预热的是**普通缓存的ViewSet数据**（如 `api:ChapterViewSet:course_pk=1`），但实际的ChapterViewSet和ProblemViewSet已经迁移到**分离缓存系统**，使用 `SeparatedCacheService` 来缓存GLOBAL层数据（如 `courses:ChapterViewSet:SEPARATED:GLOBAL:course_pk=1`）。这导致预热任务和实际使用的缓存key不匹配，预热完全无效，用户首次访问章节/题目时仍然缓存未命中。

## What Changes

- **BREAKING**: 删除现有的所有cache_warming预热任务（包括启动预热、按需预热、定时预热）
- 新增分离缓存GLOBAL层的预热任务：
  - 启动预热：预热前100个课程的所有章节列表（GLOBAL层）
  - 启动预热：预热每个章节的前10个题目列表（GLOBAL层）
  - 按需预热：支持单个章节/题目的GLOBAL层缓存异步刷新
  - 定时预热：定期刷新高命中率（>30%）的章节/题目GLOBAL缓存
- 更新courses/apps.py中的启动触发逻辑，调用新的预热任务
- 删除旧的全局缓存预热函数（`_warm_course_list`, `_warm_popular_courses`等）

## Capabilities

### New Capabilities
- `separated-cache-global-warming`: 分离缓存GLOBAL层数据预热系统

### Modified Capabilities
- `async-cache-warming`: 原有的异步缓存预热能力将完全迁移到分离缓存GLOBAL层

## Impact

### Backend
- `backend/common/cache_warming/tasks.py` - 完全重写，删除所有旧预热函数，添加新的GLOBAL层预热函数
- `backend/courses/apps.py` - 更新启动预热的任务调用
- `backend/core/settings.py` - 更新CELERY_BEAT_SCHEDULE配置

### Operations
- 启动时的预热时间可能增加（预热更多数据）
- Redis缓存命中率应显著提升（预热key与实际使用key匹配）
- 需要监控新预热任务的执行时间和成功率
