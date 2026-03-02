# 增强缓存日志记录 - 阶段 1：实施任务

## 1. 配置缓存日志系统

- [x] 1.1 在 `core/settings.py` 的 LOGGING 配置中添加 `cache_file` handler，使用 RotatingFileHandler 写入 `logs/cache.log`，最大 10MB，保留 10 个文件
- [x] 1.2 在 `core/settings.py` 中添加 `teaching_platform.cache` logger，使用 `cache_file` 和 `console` handlers，级别为 INFO
- [x] 1.3 为 `cache_file` handler 配置 JSON 格式化器（使用现有的 `pythonjsonlogger.jsonlogger.JsonFormatter`）

## 2. 增强缓存指标记录函数

- [x] 2.1 在 `common/metrics/cache_metrics.py` 顶部添加 `logger = logging.getLogger('teaching_platform.cache')`
- [x] 2.2 修改 `record_cache_hit()` 函数，添加日志记录（INFO 级别），包含 event、endpoint、status、duration_ms、hit_rate 字段
- [x] 2.3 修改 `record_cache_miss()` 函数，添加日志记录（INFO 级别），包含 event、endpoint、status、duration_ms 字段
- [x] 2.4 修改 `record_cache_null_value()` 函数，添加日志记录（INFO 级别），包含 event、endpoint、status、duration_ms 字段
- [x] 2.5 在 `record_cache_hit()` 和 `record_cache_miss()` 中添加慢操作检测：当 duration > 0.1 秒时，记录 WARNING 级别日志

## 3. 增强 Cache Mixin 日志

- [x] 3.1 修改 `common/mixins/cache_mixin.py` 中的 `CacheListMixin.list()` 方法，在缓存命中时添加 TTL、duration_ms 到日志 extra 字段
- [x] 3.2 修改 `CacheListMixin.list()` 方法，在缓存未命中时记录 INFO 日志，包含 cache_key、view_name、adaptive_ttl
- [x] 3.3 同样修改 `CacheRetrieveMixin.retrieve()` 方法，添加相同的性能元数据到日志
- [x] 3.4 确保所有缓存日志使用 `get_logger('teaching_platform.cache')` 而不是 `logging.getLogger(__name__)`

## 4. 错误处理和兼容性

- [x] 4.1 在所有新增的日志记录调用外添加 try-except 块，防止日志写入失败影响缓存操作
- [x] 4.2 确保日志记录失败不会影响 Prometheus 指标的更新（保持两者独立性）
- [x] 4.3 为 `record_penetration_attempt()` 函数添加异常处理，确保穿透检测失败不影响系统运行

## 5. 测试和验证

- [x] 5.1 启动开发服务器，触发缓存操作，验证 `logs/cache.log` 文件创建和内容正确
- [x] 5.2 检查日志格式是否为有效的 JSON，包含所有必需字段（event、endpoint、status、duration_ms）
- [x] 5.3 运行性能测试 `test/locustfile.py`，对比启用日志前后的缓存操作耗时，确保额外延迟 < 0.5ms
- [x] 5.4 验证 Prometheus 指标仍正常工作（访问 `/metrics` 端点）
- [x] 5.5 测试慢操作告警：临时修改慢操作阈值为 0.001 秒，验证 WARNING 日志正确生成

## 6. 文档和清理

- [x] 6.1 在 `backend/common/metrics/cache_metrics.py` 中添加 docstring，说明新增的日志记录功能
- [x] 6.2 更新 `backend/logs/.gitkeep`，添加 cache.log 的说明
- [x] 6.3 清理测试过程中产生的日志文件，确保只保留必要的示例
