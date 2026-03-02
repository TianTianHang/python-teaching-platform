# 增强缓存日志记录 - 阶段 3：实施任务

## 1. 创建 Django Model 存储报告数据

- [ ] 1.1 在 `common/models.py` 中创建 `CacheDailyReport` 模型，包含 date、hit_rate、total_requests、avg_duration_ms 等字段
- [ ] 1.2 创建 `CacheCapacitySnapshot` 模型，包含 date、used_memory、max_memory、total_keys 等字段
- [ ] 1.3 添加 JSONField 用于存储 hot_keys、cold_keys、alerts 等复杂数据
- [ ] 1.4 为 date 字段添加数据库索引，加速查询
- [ ] 1.5 运行 `makemigrations` 和 `migrate` 创建数据库表

## 2. 实现缓存键分析器

- [ ] 2.1 创建 `common/analytics/key_analyzer.py`，实现 `CacheKeyAnalyzer` 类
- [ ] 2.2 实现 `analyze_hot_keys()` 方法，扫描日志统计访问频率，返回 Top 100
- [ ] 2.3 实现 `analyze_cold_keys()` 方法，识别访问次数 < 10 且存在 > 7 天的 key
- [ ] 2.4 实现 `analyze_key_patterns()` 方法，按前缀分组统计
- [ ] 2.5 实现 `calculate_churn_rate()` 方法，计算新增和失效 key 的比率
- [ ] 2.6 添加流式处理逻辑，逐行读取日志避免内存溢出

## 3. 实现容量分析器

- [ ] 3.1 创建 `common/analytics/capacity_analyzer.py`，实现 `CacheCapacityAnalyzer` 类
- [ ] 3.2 实现 `collect_memory_metrics()` 方法，使用 Redis INFO 命令获取内存数据
- [ ] 3.3 实现 `calculate_memory_trend()` 方法，对比昨日数据计算趋势
- [ ] 3.4 实现 `project_exhaustion_date()` 方法，预测内存耗尽时间
- [ ] 3.5 实现 `generate_recommendations()` 方法，根据使用率生成扩容/缩容建议
- [ ] 3.6 实现 `analyze_by_data_type()` 方法，按数据类型（string/hash/list）分析内存分布

## 4. 实现趋势分析器

- [ ] 4.1 创建 `common/analytics/trend_analyzer.py`，实现 `CacheTrendAnalyzer` 类
- [ ] 4.2 实现 `calculate_hit_rate_trend()` 方法，计算 7 天和 30 天命中率趋势
- [ ] 4.3 实现 `detect_weekly_pattern()` 方法，识别每周周期性模式
- [ ] 4.4 实现 `compare_period_over_period()` 方法，计算环比/同比变化
- [ ] 4.5 实现 `detect_long_term_degradation()` 方法，检测长期性能下降
- [ ] 4.6 实现 `generate_ascii_chart()` 方法，生成文本图表

## 5. 实现日报生成器

- [ ] 5.1 创建 `common/analytics/report_generator.py`，实现 `CacheReportGenerator` 类
- [ ] 5.2 实现 `generate_daily_report()` 方法，协调各分析器生成完整报告
- [ ] 5.3 实现 `_generate_markdown_report()` 方法，生成 Markdown 格式报告
- [ ] 5.4 实现 `_generate_json_report()` 方法，生成 JSON 格式报告
- [ ] 5.5 实现报告数据持久化，将数据保存到 `CacheDailyReport` 模型
- [ ] 5.6 在报告中包含异常检测（命中率下降、请求激增等）

## 6. 创建 Celery 周期性任务

- [ ] 6.1 在 `common/cache_warming/tasks.py` 中创建 `generate_daily_cache_report` 任务
- [ ] 6.2 配置 Celery Beat，每天 02:00 执行该任务
- [ ] 6.3 在任务中调用 `CacheReportGenerator.generate_daily_report()`
- [ ] 6.4 添加任务重试机制，失败时最多重试 3 次
- [ ] 6.5 添加任务超时控制，超时时间设为 10 分钟
- [ ] 6.6 实现任务失败告警，发送邮件或记录 ERROR 日志

## 7. 创建 Django 管理命令

- [ ] 7.1 创建 `backend/common/management/commands/generate_cache_report.py`
- [ ] 7.2 实现基本功能：生成今日报告
- [ ] 7.3 添加 `--date` 参数，支持生成指定日期报告
- [ ] 7.4 添加 `--start` 和 `--end` 参数，支持生成日期范围报告
- [ ] 7.5 添加 `--analytics-only` 参数，只生成键分析不生成完整报告
- [ ] 7.6 添加 `--export` 参数，支持导出 CSV 格式

- [ ] 7.7 创建 `backend/common/management/commands/analyze_cache_keys.py`
- [ ] 7.8 实现键分析功能，支持按日期、端点过滤
- [ ] 7.9 添加 `--endpoint` 参数，过滤特定端点的键
- [ ] 7.10 添加 `--export` 参数，导出键统计到 CSV

- [ ] 7.11 创建 `backend/common/management/commands/cache_trend_report.py`
- [ ] 7.12 实现趋势报告功能，支持 `--days` 参数（7/30/90）
- [ ] 7.13 添加 `--export` 参数，导出趋势数据到 CSV

## 8. 配置和优化

- [ ] 8.1 在 `core/settings.py` 中添加 `CACHE_REPORT` 配置项，包含报告时间、保留天数等
- [ ] 8.2 配置报告文件路径：`CACHE_REPORT_PATH = 'logs/cache_daily_report.log'`
- [ ] 8.3 添加告警阈值配置：`CACHE_CAPACITY_ALERT_THRESHOLD = 0.9`
- [ ] 8.4 优化日志扫描性能，使用时间范围过滤避免扫描全部日志
- [ ] 8.5 添加任务监控，记录任务执行耗时到日志

## 9. 测试和验证

- [ ] 9.1 手动运行 `python manage.py generate_cache_report`，验证报告生成
- [ ] 9.2 检查生成的 Markdown 和 JSON 文件格式正确
- [ ] 9.3 验证数据库记录创建成功，包含所有字段
- [ ] 9.4 测试热点分析：创建模拟日志，验证 Top 100 正确识别
- [ ] 9.5 测试容量分析：模拟不同内存使用率，验证告警生成
- [ ] 9.6 测试趋势分析：生成 30 天历史数据，验证趋势计算
- [ ] 9.7 测试周期性任务：手动触发 Celery 任务，验证执行正常
- [ ] 9.8 性能测试：使用 1GB 日志文件测试，确保扫描时间 < 5 分钟

## 10. 文档和清理

- [ ] 10.1 为所有分析器类添加完整的 docstring
- [ ] 10.2 创建示例报告文件，展示日报格式
- [ ] 10.3 在 README 中添加报告使用说明
- [ ] 10.4 创建监控仪表板配置（可选）：Prometheus/Grafana 面板配置示例
