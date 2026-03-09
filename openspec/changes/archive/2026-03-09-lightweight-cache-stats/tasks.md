## 1. 修改 cache.py 热路径

- [x] 1.1 在 `get_cache()` 中移除 `AdaptiveTTLCalculator.record_hit()` 调用（第176行）
- [x] 1.2 在 `get_cache()` 中添加阈值判断，仅在 duration > 0.1 时才执行统计

## 2. 修改 cache_metrics.py 轻量化日志

- [x] 2.1 修改 `record_cache_hit()` - 添加阈值判断，仅在慢操作时执行完整逻辑
- [x] 2.2 修改 `record_cache_miss()` - 同样添加阈值判断
- [x] 2.3 保留 Prometheus counter.inc() - 始终执行（内存操作）

## 3. 验证与测试

- [x] 3.1 运行单元测试 `uv run python manage.py test common.tests.test_cache`
- [x] 3.2 检查 cache.log 确认不再每条都是 WARNING
- [x] 3.3 手动测试正常缓存操作延迟是否下降