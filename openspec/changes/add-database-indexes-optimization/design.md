## Context

当前 `backend/courses` 应用的数据模型缺少针对高频查询场景的索引支持。通过对代码分析，发现以下关键查询瓶颈：

1. **N+1 查询**：ChapterUnlockService.is_unlocked 中对 ChapterProgress 的查询
2. **复合查询缺乏索引**：Submission.objects.filter(user=X, problem=Y, status='Z')
3. **排序性能问题**：Course.objects.all().order_by('title') 在大数据量下性能差
4. **JOIN 查询优化**：ProblemProgress.objects.filter(enrollment__user=X)

## Goals / Non-Goals

**Goals:**
- 提升高频查询性能 10-100 倍
- 减少数据库负载和响应时间
- 优化 N+1 查询场景
- 保持现有 API 和业务逻辑不变

**Non-Goals:**
- 修改任何 API 接口或序列化器
- 改变业务逻辑或数据结构
- 前端性能优化
- 缓存策略变更

## Decisions

### 1. 使用 Django ORM 的 Index 类而非单独的 SQL 语句

**Rationale**：
- Django Index 类自动处理迁移创建
- 支持数据库特定优化（如 PostgreSQL CONCURRENTLY）
- 代码可维护性更好

**Alternative 考虑**：直接执行原生 SQL CREATE INDEX，但难以管理跨数据库兼容性

### 2. 复合索引的字段顺序优化

**Rationale**：
- 等值查询字段放在前面：`(user, problem, status)` 而非 `(status, user, problem)`
- 时间字段使用 -created_at 支持倒序排序

**示例**：
```python
models.Index(fields=['enrollment', 'completed', 'chapter']),  # completed 常用于过滤
models.Index(fields=['user', 'problem', 'status']),        # user/problem 常用于等值查询
models.Index(fields=['type', '-created_at', 'id']),        # type 等值查询 + 时间排序
```

### 3. 生产环境使用 CONCURRENTLY 选项

**Rationale**：
- 避免锁表导致应用不可用
- PostgreSQL 特有语法，需要在迁移中处理

**Implementation**：
```python
# 在迁移文件中
if connection.vendor == 'postgresql':
    # PostgreSQL 支持 CONCURRENTLY
    migrations.RunSQL(
        "CREATE INDEX CONCURRENTLY idx_name ON table_name (col1, col2)",
        reverse_sql=migrations.RunSQL(
            "DROP INDEX CONCURRENTLY idx_name"
        )
    )
```

### 4. 保留 unique_together 的索引约束

**Rationale**：
- unique_together 自动创建唯一索引
- 不要再重复创建相同索引避免浪费
- 但要确保索引顺序与查询模式匹配

## Risks / Trade-offs

### [风险 1] 索引创建导致数据库锁表
**Mitigation**：
- 在非高峰时段执行迁移
- 使用 `CONCURRENTLY` 选项（PostgreSQL）
- 分批创建索引

### [风险 2] 索引增加写入开销
**Mitigation**：
- 只为高频查询场景创建索引
- 避免过度索引（每个索引增加 10-15% 写入开销）
- 监控写入性能变化

### [风险 3] 索引顺序不当导致优化器未使用
**Mitigation**：
- 使用 `EXPLAIN ANALYZE` 验证索引使用情况
- 测试不同字段组合
- 必要时创建多个覆盖相同查询的不同索引

### [风险 4] 大表索引创建时间过长
**Mitigation**：
- 先在测试环境评估索引创建时间
- 对超过 100 万行的表考虑使用 `CREATE INDEX ... CONCURRENTLY`
- 预估大表索引创建可能需要几分钟到几小时

## Migration Plan

### Phase 1: 开发环境
1. 生成迁移文件：`python manage.py makemigrations`
2. 应用迁移：`python manage.py migrate`
3. 验证索引：`python manage.py shell` → 执行 `EXPLAIN ANALYZE`

### Phase 2: 测试环境
1. 导入测试数据（建议至少 10 万条测试数据）
2. 执行性能基准测试
3. 验证查询响应时间改善

### Phase 3: 生产环境
1. 选择低峰时段（凌晨 2-4 点）
2. 使用 `--fake-initial` 预先检查迁移
3. 分批执行迁移
4. 监控数据库性能

### Rollback Strategy
```bash
# 回滚迁移
python manage.py migrate courses/migration_name

# 手动删除索引（如果迁移失败）
DROP INDEX CONCURRENTLY idx_name;
```

## Open Questions

1. 是否需要对 `enrollment__user` 这类跨表查询创建特殊索引？
   - 决定：不创建，因为可以通过 select_related 优化

2. 是否需要为 `unlock_condition__prerequisite_chapters` 的 ManyToMany 添加索引？
   - 决定：不需要，Django 自动处理中间表索引

3. 对 10 万级数据量，索引创建时间的预期？
   - 需要 PostgreSQL 和索引大小的具体数据进行评估