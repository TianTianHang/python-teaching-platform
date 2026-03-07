## 1. 准备工作

- [x] 1.1 创建 StandardCacheListMixin 在 `common/mixins/cache_mixin.py`
- [x] 1.2 创建 StandardCacheRetrieveMixin 在 `common/mixins/cache_mixin.py`
- [x] 1.3 实现 `_is_user_specific_queryset()` 检测逻辑
- [x] 1.4 添加 `get_standard_cache_key()` 调用逻辑到新Mixin
- [x] 1.5 为 StandardCacheListMixin 添加单元测试
- [x] 1.6 为 StandardCacheRetrieveMixin 添加单元测试
- [x] 1.7 创建 `mock_standard_cache_service()` 测试辅助函数

## 2. 迁移courses模块ViewSet

- [x] 2.1 迁移 CourseViewSet 继承到 StandardCacheMixin
- [x] 2.2 运行 CourseViewSet 单元测试验证迁移
- [x] 2.3 迁移 ExamViewSet 继承到 StandardCacheMixin
- [x] 2.4 更新 signals.py:137 的 ExamViewSet 缓存失效逻辑使用 CacheInvalidator
- [x] 2.5 运行 ExamViewSet 单元测试验证迁移
- [x] 2.6 迁移 EnrollmentViewSet 继承到 StandardCacheMixin
- [x] 2.7 验证 EnrollmentViewSet 的 user_id 自动注入逻辑
- [x] 2.8 更新 signals.py:167 的 EnrollmentViewSet 缓存失效逻辑使用 CacheInvalidator
- [x] 2.9 运行 EnrollmentViewSet 单元测试验证迁移
- [x] 2.10 迁移 ChapterProgressViewSet 继承到 StandardCacheMixin
- [x] 2.11 运行 ChapterProgressViewSet 单元测试验证迁移
- [x] 2.12 迁移 ProblemProgressViewSet 继承到 StandardCacheMixin
- [x] 2.13 运行 ProblemProgressViewSet 单元测试验证迁移
- [x] 2.14 迁移 ExamSubmissionViewSet 继承到 StandardCacheMixin
- [x] 2.15 运行 ExamSubmissionViewSet 单元测试验证迁移

## 3. 迁移file_management模块ViewSet

- [x] 3.1 迁移 FolderViewSet 继承到 StandardCacheMixin
- [x] 3.2 运行 FolderViewSet 单元测试验证迁移
- [x] 3.3 迁移 FileEntryViewSet 继承到 StandardCacheMixin
- [x] 3.4 运行 FileEntryViewSet 单元测试验证迁移

## 4. 统一signals.py缓存失效逻辑

- [x] 4.1 替换 ExamViewSet 缓存失效 (signals.py:137-140) 使用 CacheInvalidator.invalidate_viewset()
- [x] 4.2 替换 ExamViewSet 列表缓存失效 (signals.py:142-146) 使用 CacheInvalidator.invalidate_viewset_list()
- [x] 4.3 替换 EnrollmentViewSet 缓存失效 (signals.py:167-170) 使用 CacheInvalidator.invalidate_viewset_list()
- [x] 4.4 验证 signals.py 中所有缓存失效调用已统一使用 CacheInvalidator
- [x] 4.5 运行 signals.py 集成测试验证缓存失效逻辑

## 5. 更新测试用例

- [x] 5.1 更新 `backend/courses/tests/test_views.py` 中的 CourseViewSet 测试
- [x] 5.2 更新 `backend/courses/tests/test_views.py` 中的 ExamViewSet 测试
- [x] 5.3 更新 `backend/courses/tests/test_views.py` 中的 EnrollmentViewSet 测试
- [x] 5.4 更新 `backend/courses/tests/test_views.py` 中的 ProgressViewSet 测试
- [x] 5.5 更新 `backend/courses/tests/test_views.py` 中的 ExamSubmissionViewSet 测试
- [x] 5.6 更新 `backend/file_management/tests/` 中的 FolderViewSet 测试
- [x] 5.7 更新 `backend/file_management/tests/` 中的 FileEntryViewSet 测试
- [x] 5.8 更新 `backend/courses/tests/test_signals.py` 中的缓存失效测试
- [x] 5.9 创建新的测试文件 `test_cache_invalidator.py` 和 `test_separated_cache.py`

## 6. 迁移cache_warming到新系统

- [x] 6.1 迁移 `_warm_courses()` 使用 `get_standard_cache_key()` 替代 `get_cache_key()`
- [x] 6.2 迁移 `_warm_course_detail()` 使用新API
- [x] 6.3 迁移 `_warm_chapters()` 使用新API
- [x] 6.4 迁移 `_warm_chapter_detail()` 使用新API
- [x] 6.5 迁移 `_warm_enrollments()` 使用新API
- [x] 6.6 迁移 `_warm_exams()` 使用新API
- [x] 6.7 迁移 `_warm_exam_detail()` 使用新API

## 7. 清理旧代码

- [x] 7.1 从 `common/utils/cache.py` 删除 `get_cache_key()` 函数
- [x] 7.2 从 `common/mixins/cache_mixin.py` 删除 `CacheListMixin` 类
- [x] 7.3 从 `common/mixins/cache_mixin.py` 删除 `CacheRetrieveMixin` 类
- [x] 7.4 保留 `InvalidateCacheMixin` 类（仍被使用）
- [x] 7.4.1 更新 `InvalidateCacheMixin` 使用 `get_standard_cache_key()` 替代 `get_cache_key()`
- [x] 7.5 删除所有测试中对 `get_cache_key()` 的引用
- [x] 7.6 删除所有测试中对旧 Mixin 的 mock 引用
- [x] 7.7 运行完整测试套件验证清理后无遗留问题

## 8. 文档和代码注释

- [x] 8.1 为 StandardCacheListMixin 添加 docstring 说明
- [x] 8.2 为 StandardCacheRetrieveMixin 添加 docstring 说明
- [x] 8.3 为 `_is_user_specific_queryset()` 添加详细注释
- [x] 8.4 在所有迁移的 ViewSet 中添加 TODO 注释标记已迁移
- [x] 8.5 更新 `common/mixins/cache_mixin.py` 模块级文档字符串

