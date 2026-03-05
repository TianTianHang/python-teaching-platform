# 统一Cache服务层 - 实施任务

## 1. 项目结构准备

- [x] 1.1 创建 `backend/common/services/` 目录
- [x] 1.2 在 `services/` 目录中创建 `__init__.py`，导出所有服务类
- [ ] 1.3 验证新目录可以被导入（运行 `python -c "from common.services import SeparatedCacheService"`）

## 2. 增强 utils/cache.py 的标准化key生成

- [ ] 2.1 在 `utils/cache.py` 中添加 `get_standard_cache_key()` 函数签名，添加 `is_separated` 参数
- [ ] 2.2 实现 `is_separated=True` 时的key格式逻辑，添加 `SEPARATED:GLOBAL` 和 `SEPARATED:STATUS` 标记
- [ ] 2.3 为 `get_standard_cache_key()` 添加完整的docstring，包含参数说明和返回示例
- [ ] 2.4 编写单元测试验证key格式：测试普通缓存、分离缓存全局、分离缓存用户状态的key生成
- [ ] 2.5 运行现有测试，确保向后兼容性（不破坏现有的 `get_cache_key()` 调用）

## 3. 实现 SeparatedCacheService

- [ ] 3.1 创建 `backend/common/services/separated_cache.py` 文件
- [ ] 3.2 实现 `SeparatedCacheService` 类骨架，使用 `@staticmethod` 装饰器
- [ ] 3.3 实现 `get_global_data()` 方法：调用 `get_cache(return_result=True)`，检查 `result.is_hit`
- [ ] 3.4 实现 `get_global_data()` 的cache miss逻辑：调用 `data_fetcher` 回调，使用 `set_cache()` 存储结果
- [ ] 3.5 实现 `get_global_data()` 的返回值：返回 `(data, is_cache_hit)` 元组
- [ ] 3.6 实现 `get_user_status()` 方法：生成包含 `user_id` 的key，调用 `get_cache(return_result=True)`
- [ ] 3.7 实现 `get_user_status()` 的cache miss逻辑：调用 `status_fetcher` 回调，使用 `set_cache()` 存储结果
- [ ] 3.8 实现 `invalidate_global()` 方法：调用 `delete_cache()` 删除全局数据缓存
- [ ] 3.9 实现 `invalidate_user_status()` 方法：构造用户状态key，调用 `delete_cache()` 删除
- [ ] 3.10 为所有公共方法添加完整的docstring，包含参数说明、返回值和使用示例

## 4. 实现 BusinessCacheService

- [ ] 4.1 创建 `backend/common/services/business_cache.py` 文件
- [ ] 4.2 实现 `BusinessCacheService` 类骨架，使用 `@staticmethod` 装饰器
- [ ] 4.3 实现 `cache_result()` 通用方法：接受 `cache_key`, `fetcher`, `timeout` 参数
- [ ] 4.4 实现 `cache_result()` 的cache hit逻辑：调用 `get_cache(return_result=True)`，检查 `result.is_hit`
- [ ] 4.5 实现 `cache_result()` 的cache miss逻辑：调用 `fetcher` 回调，使用 `set_cache()` 存储结果
- [ ] 4.6 实现 `cache_snapshot()` 便利方法：使用 `get_standard_cache_key()` 生成key，默认timeout=300
- [ ] 4.7 实现 `cache_execution_result()` 便利方法：使用 `get_standard_cache_key()` 生成key
- [ ] 4.8 为所有公共方法添加完整的docstring，包含参数说明和返回值

## 5. 实现 CacheInvalidator

- [ ] 5.1 在 `utils/cache.py` 中添加 `CacheInvalidator` 类骨架
- [ ] 5.2 实现 `invalidate_viewset()` 方法：使用 `get_standard_cache_key()` 生成key，调用 `delete_cache()`
- [ ] 5.3 实现 `invalidate_viewset_list()` 方法：生成基础key，添加 `:*` 通配符，调用 `delete_cache_pattern()`
- [ ] 5.4 实现 `invalidate_separated_cache_global()` 方法：使用 `is_separated=True` 生成key，调用 `delete_cache()`
- [ ] 5.5 实现 `invalidate_separated_cache_user_status()` 方法：添加 `user_id` 和 `is_separated=True`，调用 `delete_cache()`
- [ ] 5.6 为所有失效方法添加异常处理：捕获 `delete_cache()` 和 `delete_cache_pattern()` 的异常，记录debug日志
- [ ] 5.7 为所有公共方法添加完整的docstring，包含参数说明和使用示例

## 6. SeparatedCacheService 单元测试

- [ ] 6.1 创建 `backend/common/tests/test_separated_cache.py` 文件
- [ ] 6.2 编写测试用例：`test_get_global_data_cache_miss` - mock cache miss，验证 `data_fetcher` 被调用
- [ ] 6.3 编写测试用例：`test_get_global_data_cache_hit` - mock cache hit，验证 `data_fetcher` 未被调用
- [ ] 6.4 编写测试用例：`test_get_global_data_returns_tuple` - 验证返回 `(data, is_cache_hit)` 格式
- [ ] 6.5 编写测试用例：`test_get_user_status_with_user_id` - 验证user_id包含在cache key中
- [ ] 6.6 编写测试用例：`test_invalidate_global_deletes_cache` - mock `delete_cache()`，验证调用正确
- [ ] 6.7 编写测试用例：`test_invalidate_user_status_deletes_cache` - mock `delete_cache()`，验证key包含user_id
- [ ] 6.8 运行测试，确保覆盖率 > 90%（使用 `pytest --cov=common.services.separated_cache`）

## 7. BusinessCacheService 单元测试

- [ ] 7.1 创建 `backend/common/tests/test_business_cache.py` 文件
- [ ] 7.2 编写测试用例：`test_cache_result_cache_miss` - mock cache miss，验证 `fetcher` 被调用
- [ ] 7.3 编写测试用例：`test_cache_result_cache_hit` - mock cache hit，验证 `fetcher` 未被调用
- [ ] 7.4 编写测试用例：`test_cache_snapshot_generates_correct_key` - 验证key格式包含 "business:UnlockSnapshot"
- [ ] 7.5 编写测试用例：`test_cache_snapshot_default_timeout` - 验证默认timeout=300传递给 `set_cache()`
- [ ] 7.6 编写测试用例：`test_cache_execution_result_generates_correct_key` - 验证key格式包含 "business:CodeExecution"
- [ ] 7.7 编写测试用例：`test_custom_timeout_override` - 验证自定义timeout参数正确传递
- [ ] 7.8 运行测试，确保覆盖率 > 90%（使用 `pytest --cov=common.services.business_cache`）

## 8. CacheInvalidator 单元测试

- [ ] 8.1 创建 `backend/common/tests/test_cache_invalidator.py` 文件（或添加到现有的 `test_cache.py`）
- [ ] 8.2 编写测试用例：`test_invalidate_viewset_generates_correct_key` - 验证调用 `get_standard_cache_key()` 参数正确
- [ ] 8.3 编写测试用例：`test_invalidate_viewset_calls_delete_cache` - mock `delete_cache()`，验证调用一次
- [ ] 8.4 编写测试用例：`test_invalidate_viewset_list_uses_pattern` - 验证key以 `:*` 结尾
- [ ] 8.5 编写测试用例：`test_invalidate_viewset_list_calls_delete_pattern` - mock `delete_cache_pattern()`，验证调用
- [ ] 8.6 编写测试用例：`test_invalidate_separated_cache_global_flag` - 验证 `is_separated=True` 传递给key生成
- [ ] 8.7 编写测试用例：`test_invalidate_separated_cache_user_status_includes_user_id` - 验证user_id在key中
- [ ] 8.8 编写测试用例：`test_invalidate_handles_missing_cache_gracefully` - mock `delete_cache()` 抛出异常，验证不抛出
- [ ] 8.9 运行测试，确保覆盖率 > 90%

## 9. 集成测试

- [ ] 9.1 创建 `backend/common/tests/test_cache_services_integration.py` 文件
- [ ] 9.2 编写集成测试：`test_separated_cache_end_to_end` - 使用Redis，验证完整流程（写入、读取、失效）
- [ ] 9.3 编写集成测试：`test_business_cache_end_to_end` - 使用Redis，验证缓存结果和metrics记录
- [ ] 9.4 编写集成测试：`test_invalidation_removes_keys` - 使用Redis，验证失效操作真实删除key
- [ ] 9.5 编写集成测试：`test_null_value_caching` - 验证 `is_null=True` 时缓存穿透保护生效
- [ ] 9.6 运行集成测试，确保与真实Redis交互正常（使用 `pytest --redis` 标记）

## 10. 性能测试

- [ ] 10.1 创建 `backend/common/tests/test_cache_performance.py` 文件
- [ ] 10.2 编写基准测试：`test_service_layer_overhead` - 对比直接 `cache.get()` 和 `SeparatedCacheService.get_global_data()` 的性能
- [ ] 10.3 编写基准测试：`test_key_generation_performance` - 测试 `get_standard_cache_key()` 10,000次调用耗时
- [ ] 10.4 验证性能目标：服务层开销 < 1μs（使用 `time.perf_counter()` 精确测量）
- [ ] 10.5 如果性能不达标，优化代码（内联简单逻辑，减少函数调用）
- [ ] 10.6 记录基准测试结果到文档（在design.md或单独的PERFORMANCE.md中）

## 11. 文档和最佳实践

- [ ] 11.1 为每个服务类添加详细的模块docstring，说明用途和使用场景
- [ ] 11.2 创建 `backend/docs/cache_best_practices.md`（或在现有docs中添加章节）
- [ ] 11.3 编写决策树：何时使用CacheMixin vs SeparatedCacheService vs BusinessCacheService
- [ ] 11.4 添加代码示例：展示如何在实际代码中使用每个服务类
- [ ] 11.5 在 `backend/common/services/__init__.py` 中添加使用说明的注释

## 12. 代码质量检查

- [ ] 12.1 运行 `ruff check common/services/` 修复linting错误
- [ ] 12.2 运行 `ruff format common/services/` 确保代码格式一致
- [ ] 12.3 运行 `mypy common/services/` 检查类型注解（确保所有函数有类型提示）
- [ ] 12.4 确保所有新代码符合项目风格指南（参考现有代码）
- [ ] 12.5 运行全部测试套件，确保没有破坏现有功能（`pytest backend/common/tests/`）

## 13. 验收和发布准备

- [ ] 13.1 运行完整测试套件，确保所有测试通过（单元、集成、性能）
- [ ] 13.2 检查测试覆盖率报告，确保新增代码覆盖率 > 90%
- [ ] 13.3 验证 `openspec status` 显示所有artifacts完成
- [ ] 13.4 创建git commit：`git add backend/common/services backend/common/utils/cache.py backend/common/tests/`
- [ ] 13.5 编写commit message：遵循约定式提交格式，如 "feat: add unified cache service layer (SeparatedCacheService, BusinessCacheService, CacheInvalidator)"
