# 实施任务清单

> **注意**：本阶段专注于实现通用 Mixin 并迁移 ProblemViewSet。其他 ViewSet（Submission、Chapter 等）的应用暂不实施，留待后续阶段。

## 1. 核心Mixin实现

- [x] 1.1 创建 `DynamicFieldsMixin` 在 `backend/common/mixins/__init__.py`
  - 实现 `get_exclude_fields()` 方法：解析 `exclude` 查询参数
  - 实现字段验证逻辑：检查字段名是否在序列化器的 `fields` 中
  - 实现 `get_serializer_context()` 方法：将 `exclude_fields` 传递到 serializer context
  - 添加类型提示和完整的 docstring

- [x] 1.2 创建 `DynamicFieldsSerializerMixin` 在 `backend/common/serializers.py`
  - 实现 `to_representation()` 方法：从响应中移除 `exclude_fields` 中的字段
  - 处理嵌套序列化器的情况（移除整个嵌套对象）
  - 添加类型提示和完整的 docstring

- [x] 1.3 修改 `CacheListMixin._get_allowed_cache_params()` 在 `backend/common/mixins/cache_mixin.py`
  - 在 `common_params` 中添加 `'exclude'`
  - 确保所有使用 `CacheListMixin` 的 ViewSet 都能正确处理 `exclude` 参数

- [x] 1.4 实现 exclude 参数规范化逻辑
  - 在缓存键生成逻辑中对 `exclude` 参数值进行排序
  - 确保 `code,output` 和 `output,code` 生成相同的缓存键
  - 在 `backend/common/utils/cache.py` 的 `get_cache_key()` 函数中实现

## 2. 单元测试

- [ ] 2.1 创建 `backend/common/tests/test_dynamic_fields_mixin.py`
  - 测试 `get_exclude_fields()` 正确解析参数
  - 测试字段验证逻辑（有效/无效字段名）
  - 测试空参数、重复字段名、空白字符串等边界情况
  - 测试字段顺序规范化

- [ ] 2.2 创建 `backend/common/tests/test_dynamic_fields_serializer_mixin.py`
  - 测试 `to_representation()` 正确移除字段
  - 测试嵌套序列化器的处理
  - 测试多个字段同时排除
  - 测试不排除任何字段的情况

- [ ] 2.3 创建缓存相关测试
  - 测试不同的 `exclude` 参数生成不同的缓存键
  - 测试相同字段组合（不同顺序）生成相同的缓存键
  - 测试缓存数据不会互相干扰

## 3. 迁移 ProblemViewSet

- [x] 3.1 移除 ProblemViewSet 中的自定义 exclude 实现
  - 删除 `get_exclude_fields()` 方法（现在由 Mixin 提供）
  - 删除 `list()` 和 `retrieve()` 中手动传递 context 的代码
  - 保留 `get_serializer_context()` 中的其他逻辑（enrollment、unlock_states 等）

- [x] 3.2 为 ProblemViewSet 添加 `DynamicFieldsMixin`
  - 在 `backend/courses/views.py` 中导入 `DynamicFieldsMixin`
  - 将 `DynamicFieldsMixin` 添加到 `ProblemViewSet` 的继承链（在 `CacheListMixin` 之后）
  - 确保 `get_serializer_context()` 正确调用父类方法

- [x] 3.3 为 ProblemSerializer 添加 `DynamicFieldsSerializerMixin`
  - 在 `backend/courses/serializers.py` 中导入 `DynamicFieldsSerializerMixin`
  - 将 `DynamicFieldsSerializerMixin` 添加到 `ProblemSerializer` 的继承链
  - 移除现有的字段排除逻辑（如果有）

- [x] 3.4 更新 ProblemViewSet 的 get_serializer_context() 方法
  - 调用 `super().get_serializer_context()` 获取基础 context（现在包含 exclude_fields）
  - 保留现有的 enrollment、unlock_states 等字段添加逻辑
  - 移除手动添加 exclude_fields 的代码（已由 Mixin 处理）

- [x] 3.5 运行 Problem API 的现有测试
  - 运行 `backend/courses/tests/test_views.py` 中的 ProblemViewSet 测试
  - 确保所有测试通过
  - 验证行为与迁移前完全一致

## 4. 集成测试

- [x] 4.1 添加 Problem API 的字段排除测试
  - 测试 `GET /api/problems/?exclude=content` 返回正确数据
  - 测试 `GET /api/problems/?exclude=content,test_cases,recent_threads` 返回正确数据
  - 测试无效字段名返回 400 错误
  - 测试分页响应中的字段排除

- [x] 4.2 测试缓存键生成
  - 验证不同的 exclude 参数生成不同的缓存键
  - 验证相同字段组合（不同顺序）生成相同的缓存键
  - 验证缓存数据正确性

## 5. 文档和清理

- [x] 5.1 更新 ProblemViewSet 文档
  - 在 docstring 中说明使用通用 `DynamicFieldsMixin`
  - 保留 `exclude` 参数的使用示例

- [x] 5.2 代码审查和清理
  - 确保所有新增代码都有类型提示
  - 确保所有新增代码都有完整的 docstring
  - 移除 ProblemViewSet 中不再需要的代码
  - 运行 `uv run python manage.py test` 确保测试通过

## 6. 性能验证

- [x] 6.1 验证 Problem API 性能
  - 使用 `curl` 或浏览器 DevTools 测量响应大小
  - 确认优化效果与迁移前一致（70-80% 数据量减少）
  - 验证缓存命中率没有显著下降

## 后续阶段（暂不实施）

以下任务留待后续阶段，本变更不包含：

- [ ] 应用到 SubmissionViewSet
- [ ] 应用到 ChapterViewSet
- [ ] 应用到 ExamViewSet
- [ ] 前端集成（Submission、Chapter 等页面）
- [ ] 其他 ViewSet 的迁移
