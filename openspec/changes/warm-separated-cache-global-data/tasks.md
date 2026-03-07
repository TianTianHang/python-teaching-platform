## 1. 删除旧的预热任务

- [x] 1.1 备份当前的 `backend/common/cache_warming/tasks.py` 文件
- [x] 1.2 删除所有旧的预热辅助函数：
  - `_warm_course_list()`
  - `_warm_popular_courses()`
  - `_warm_course_chapters()`
  - `_warm_popular_problems()`
  - `_warm_high_priority_courses()`
  - `_warm_high_priority_problems()`
  - `_warm_by_view_name()`
  - `_get_popular_course_ids()`
- [x] 1.3 删除旧的Celery任务：
  - `warm_startup_cache`
  - `warm_on_demand_cache`
  - `warm_scheduled_cache`
- [x] 1.4 保留辅助工具类：
  - `WarmingPriority`
  - `get_warming_lock_key()`
  - `get_warming_stats_key()`
  - `acquire_warming_lock()`
  - `release_warming_lock()`
  - `record_warming_stats()`
- [x] 1.5 保留 `cache_performance_summary()` 任务（与新预热系统无关）

## 2. 创建GLOBAL层预热辅助函数

- [x] 2.1 创建 `_warm_chapters_global(course_limit: int = 100)` 函数
  - 使用 `Course.objects.all()[:course_limit]` 获取课程
  - 为每个课程的章节列表生成GLOBAL缓存key
  - 使用 `ChapterGlobalSerializer` 序列化数据
  - 使用 `set_cache()` 存储到Redis，TTL=1800秒
  - 返回预热的课程数量
- [x] 2.2 创建 `_warm_problems_global(chapter_limit: int = 100, problems_per_chapter: int = 10)` 函数
  - 获取指定章节ID列表
  - 为每个章节的题目列表生成GLOBAL缓存key
  - 使用 `ProblemGlobalSerializer` 序列化数据
  - 使用 `set_cache()` 存储到Redis，TTL=1800秒
  - 返回预热的题目数量
- [x] 2.3 创建 `_warm_high_priority_chapters_global()` 函数
  - 遍历前50个课程的章节
  - 使用 `AdaptiveTTLCalculator.get_hit_rate()` 检查命中率
  - 只预热命中率>30%的章节GLOBAL缓存
  - TTL=1800秒
- [x] 2.4 创建 `_warm_high_priority_problems_global()` 函数
  - 遍历前100个章节的题目
  - 使用 `AdaptiveTTLCalculator.get_hit_rate()` 检查命中率
  - 只预热命中率>30%的题目GLOBAL缓存
  - TTL=1800秒
- [x] 2.5 创建 `_warm_chapter_global_by_pk(chapter_pk: int, course_pk: int)` 按需预热函数
  - 根据chapter_pk预热单个章节的GLOBAL缓存
- [x] 2.6 创建 `_warm_problems_global_by_chapter(chapter_pk: int, course_pk: int, limit: int = 10)` 按需预热函数
  - 根据chapter_pk预热单个章节的题目列表GLOBAL缓存

## 3. 创建新的Celery预热任务

- [x] 3.1 创建 `warm_separated_global_startup()` 启动预热任务
  - 调用 `_warm_chapters_global(course_limit=100)`
  - 调用 `_warm_problems_global(chapter_limit=1000, problems_per_chapter=10)`
  - 记录预热统计信息（数量、耗时）
  - 添加分布式锁防止重复执行
  - 超时时间设置为10分钟
- [x] 3.2 创建 `warm_separated_global_scheduled()` 定时预热任务
  - 调用 `_warm_high_priority_chapters_global()`
  - 调用 `_warm_high_priority_problems_global()`
  - 记录预热统计信息
  - 添加分布式锁
- [x] 3.3 创建 `warm_separated_global_on_demand(cache_key: str, view_name: str, pk: int, parent_pks: dict)` 按需预热任务
  - 根据view_name调用相应的按需预热函数
  - 支持 ChapterViewSet 和 ProblemViewSet
  - 添加分布式锁（单个资源级别）

## 4. 更新应用启动逻辑

- [x] 4.1 更新 `backend/courses/apps.py`
  - 修改导入：从 `warm_startup_cache` 改为 `warm_separated_global_startup`
  - 更新调用：`warm_startup_cache.delay()` 改为 `warm_separated_global_startup.delay()`
- [x] 4.2 添加注释说明新预热任务的预热范围和预期耗时

## 5. 更新Celery Beat定时任务配置

- [x] 5.1 更新 `backend/core/settings.py` 中的 `CELERY_BEAT_SCHEDULE`
  - 将 `warm-scheduled-cache` 任务名改为 `warm-separated-global-scheduled`
  - 将任务路径改为 `common.cache_warming.tasks.warm_separated_global_scheduled`
  - 保持调度频率不变（每小时执行一次）
- [x] 5.2 验证定时任务配置格式正确

## 6. 添加单元测试

- [x] 6.1 创建测试文件 `backend/common/tests/test_separated_cache_warming.py`
- [x] 6.2 添加 `_warm_chapters_global()` 单元测试
  - Mock数据库查询
  - 验证生成的缓存key格式正确（包含 `SEPARATED:GLOBAL`）
  - 验证使用了 `ChapterGlobalSerializer`
  - 验证 `set_cache()` 被正确调用
- [x] 6.3 添加 `_warm_problems_global()` 单元测试
  - Mock数据库查询
  - 验证生成的缓存key格式正确
  - 验证使用了 `ProblemGlobalSerializer`
  - 验证只预热前N个题目
- [x] 6.4 添加 `warm_separated_global_startup()` 集成测试
  - Mock所有辅助函数
  - 验证任务调用顺序
  - 验证分布式锁逻辑
  - 验证统计信息记录
- [x] 6.5 添加按需预热任务的单元测试
- [x] 6.6 运行所有测试：`uv run python manage.py test common.tests.test_separated_cache_warming`

## 7. 验证和监控

- [x] 7.1 在本地开发环境启动应用
  - 检查日志中是否有 "Startup warming task queued" 消息
  - 检查 Celery worker 日志，确认预热任务执行
  - 记录预热耗时
- [x] 7.2 验证Redis缓存数据
  - 使用 `redis-cli` 连接Redis
  - 执行 `KEYS *SEPARATED:GLOBAL*` 查看预热的缓存key
  - 随机抽取几个key验证数据格式正确
  - 检查TTL设置是否正确（应为1800秒）
- [ ] 7.3 测试按需预热
  - 清空某个章节的GLOBAL缓存
  - 访问该章节的list接口
  - 验证按需预热任务被触发
  - 验证缓存被正确写入
- [ ] 7.4 测试定时预热
  - 手动触发 `warm_separated_global_scheduled` 任务
  - 验证高命中率数据被刷新
  - 检查统计信息记录
- [ ] 7.5 性能测试
  - 记录启动预热耗时（目标<10分钟）
  - 记录Redis内存占用（目标<150MB增量）
  - 记录缓存命中率提升（应显著提高）

## 8. 文档和清理

- [x] 8.1 更新 `backend/common/cache_warming/tasks.py` 模块级文档字符串
  - 说明新的预热机制
  - 说明预热范围和数据量估算
  - 添加关键函数的使用示例
- [ ] 8.2 在 `docs/` 或项目根目录添加预热系统说明文档（如果存在）
- [ ] 8.3 删除备份文件（确认所有测试通过后）
- [ ] 8.4 提交代码变更（git commit）
- [ ] 8.5 创建Pull Request并关联到OpenSpec变更
