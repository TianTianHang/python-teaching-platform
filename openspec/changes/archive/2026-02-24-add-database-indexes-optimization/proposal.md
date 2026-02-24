## Why

当前 `backend/courses` 应用中存在多个高频查询场景缺少合适的数据库索引支持，导致：
- N+1 查询问题（如章节解锁状态检查）
- 复杂条件的 WHERE 查询缺乏索引（如用户提交记录按状态筛选）
- 排序操作性能不佳（如按时间倒序获取列表）

随着用户量和数据量增长，这些查询会成为性能瓶颈。

## What Changes

为以下模型添加数据库索引：

1. **ChapterProgress** - 添加 `(enrollment, completed)` 复合索引
2. **Submission** - 添加 `(user, problem, status)` 复合索引
3. **ProblemProgress** - 为 `status` 字段添加 `db_index=True`，添加 `(enrollment, status)` 复合索引
4. **Problem** - 为 `chapter` 外键添加 `db_index=True`，添加 `(type, -created_at, id)` 复合索引
5. **ChapterUnlockCondition** - 为 `unlock_date` 字段添加 `db_index=True`
6. **Course** - 为 `title` 字段添加 `db_index=True`
7. **ExamSubmission** - 移除与 `unique_together` 重复的索引

## Capabilities

### New Capabilities

- `database-index-optimization`: 为课程相关数据模型添加数据库索引以提升查询性能

### Modified Capabilities

_None - 这是纯性能优化，不改变业务逻辑或 API 行为_

## Impact

**影响的代码模块：**
- `backend/courses/models.py` - 修改模型定义，添加索引配置
- `backend/courses/migrations/` - 生成新的数据库迁移文件

**不影响的组件：**
- API 接口（无变化）
- 前端代码（无变化）
- 业务逻辑（无变化）

**数据库影响：**
- 需要执行迁移创建索引
- 大表上的索引创建可能需要一定时间（建议在生产环境使用 `CONCURRENTLY` 选项）
- 每个索引会增加写入开销和存储空间（约 10-15% 存储）
