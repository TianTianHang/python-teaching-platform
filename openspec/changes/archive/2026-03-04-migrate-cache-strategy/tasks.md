## 1. 移除 ViewSet 中的旧缓存 Mixin

- [x] 1.1 从 ChapterViewSet 移除 `CacheListMixin`、`CacheRetrieveMixin`、`InvalidateCacheMixin` 继承
- [x] 1.2 从 ProblemViewSet 移除 `CacheListMixin`、`CacheRetrieveMixin`、`InvalidateCacheMixin` 继承
- [x] 1.3 清理 views.py 中不再使用的 import 语句

## 2. 删除旧的信号处理器

- [x] 2.1 删除 `invalidate_problem_progress_cache` 信号处理器 (signals.py:32-43)
- [x] 2.2 删除 `invalidate_chapter_progress_cache` 信号处理器 (signals.py:46-97)
- [x] 2.3 清理 signals.py 中不再使用的 import 语句 (`delete_cache_pattern`, `get_cache_key` 等)
- [x] 2.4 确认保留新的信号处理器：
  - `on_chapter_progress_change` (signals.py:324)
  - `on_problem_progress_change` (signals.py:346)
  - `on_chapter_content_change` (signals.py:368)
  - `on_problem_content_change` (signals.py:393)

## 3. 清理旧缓存 Key 相关代码

- [x] 3.1 检查并清理 `ChapterUnlockService._invalidate_cache` 中的旧 Key 引用
- [x] 3.2 检查 `ExamViewSet` 中是否使用了旧缓存 Key（如使用则更新为分离策略或保持不变）
- [x] 3.3 检查 `EnrollmentViewSet` 中 `invalidate_enrollment_cache_on_create` 信号是否需要更新

## 4. 测试验证

- [x] 4.1 运行 `uv run python manage.py test courses.tests.test_cache` 验证缓存测试通过
- [x] 4.2 运行 `uv run python manage.py test courses.tests.test_cache_performance` 验证性能测试通过
- [x] 4.3 运行 `uv run python manage.py test courses.tests.test_signals` 验证信号测试通过
- [x] 4.4 验证 ChapterViewSet 的 list/retrieve 使用新缓存策略（全局 + 用户状态分离）
- [x] 4.5 验证 ProblemViewSet 的 list/retrieve 使用新缓存策略
- [x] 4.6 验证信号处理器仅触发细粒度缓存失效

## 5. Redis 清理脚本

- [x] 5.1 创建管理命令清理旧缓存 Key：`api:ChapterViewSet:*` 和 `api:ProblemViewSet:*`
- [x] 5.2 清理脚本支持 dry-run 模式预览将被删除的 Key
- [x] 5.3 运行完整测试套件：`uv run python manage.py test courses`

## 6. 文档更新

- [x] 6.1 更新相关代码注释，说明新缓存策略的设计意图
- [x] 6.2 确认 AGENTS.md 中无需更新（如有缓存相关说明则更新）