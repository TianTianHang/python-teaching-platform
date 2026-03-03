# 分离缓存机制 API 文档

## 概述

本系统实现了章节和问题数据的分离缓存机制，将全局数据（静态内容）和用户状态（动态数据）分开缓存，从而提高缓存命中率和降低内存占用。

## 架构

### 缓存层结构

```
┌─────────────────────────────────────────────────┐
│                   API 请求                      │
└─────────────────┬───────────────────────────────┘
                  │
        ┌─────────▼──────────┐
        │  ChapterViewSet    │
        │  ProblemViewSet    │
        └─────────┬──────────┘
                  │
    ┌─────────────┴─────────────┐
    │                           │
┌───▼───────────────┐  ┌──────▼──────────────┐
│  全局数据缓存层    │  │  用户状态缓存层      │
│  Global Data      │  │  User State         │
│                   │  │                     │
│ - 跨用户共享       │  │ - 按用户隔离        │
│ - 长TTL (30分钟)  │  │ - 短TTL (5分钟)    │
│ - 静态内容        │  │ - 动态状态          │
└───────────────────┘  └─────────────────────┘
         │                       │
         └───────────┬───────────┘
                     │
            ┌────────▼────────┐
            │   缓存合并层     │
            │   Merge Layer   │
            └────────┬────────┘
                     │
            ┌────────▼────────┐
            │  API Response    │
            └─────────────────┘
```

## 缓存键格式

### 全局数据缓存键

```python
# 章节全局数据（单个）
chapter:global:{chapter_id}

# 章节全局数据（列表）
chapter:global:list:{course_id}

# 问题全局数据（单个）
problem:global:{problem_id}

# 问题全局数据（列表）
problem:global:list:{chapter_id}
```

**特点：**
- 不包含 `user_id`，可跨用户共享
- TTL: 1800秒（30分钟）
- 存储静态字段：id, title, content, order, created_at, updated_at

### 用户状态缓存键

```python
# 章节用户状态
chapter:status:{course_id}:{user_id}

# 问题用户状态
problem:status:{chapter_id}:{user_id}
```

**特点：**
- 包含 `user_id`，按用户隔离
- TTL: 300秒（5分钟）
- 存储动态字段：status, is_locked, is_unlocked, prerequisite_progress

## API 端点

### 章节列表 API

```
GET /api/v1/courses/{course_id}/chapters/
```

**缓存行为：**
1. 查询全局缓存键 `chapter:global:list:{course_id}`
2. 查询用户状态缓存键 `chapter:status:{course_id}:{user_id}`
3. 合并两层缓存数据
4. 返回完整响应

**响应格式（无变化）：**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "第一章：变量",
      "content": "章节内容...",
      "order": 1,
      "status": "completed",
      "is_locked": false,
      "prerequisite_progress": {...}
    }
  ]
}
```

### 章节详情 API

```
GET /api/v1/courses/{course_id}/chapters/{chapter_id}/
```

**缓存行为：**
1. 查询全局缓存键 `chapter:global:{chapter_id}`
2. 查询用户状态缓存键 `chapter:status:{course_id}:{user_id}`
3. 合并两层缓存数据
4. 返回完整响应

**响应格式（无变化）：**
```json
{
  "id": 1,
  "title": "第一章：变量",
  "content": "章节内容...",
  "order": 1,
  "status": "completed",
  "is_locked": false,
  "prerequisite_progress": {...}
}
```

### 问题列表 API

```
GET /api/v1/courses/{course_id}/chapters/{chapter_id}/problems/
```

**缓存行为：**
1. 查询全局缓存键 `problem:global:list:{chapter_id}`
2. 查询用户状态缓存键 `problem:status:{chapter_id}:{user_id}`
3. 合并两层缓存数据
4. 返回完整响应

### 问题详情 API

```
GET /api/v1/courses/{course_id}/chapters/{chapter_id}/problems/{problem_id}/
```

**缓存行为：**
1. 查询全局缓存键 `problem:global:{problem_id}`
2. 查询用户状态缓存键 `problem:status:{chapter_id}:{user_id}`
3. 合并两层缓存数据
4. 返回完整响应

## 缓存失效机制

### 用户进度更新

当用户完成章节或解决问题时：

```python
# 信号处理器
on_chapter_progress_change(instance)
on_problem_progress_change(instance)
```

**失效操作：**
- 删除用户状态缓存键
- 不影响全局数据缓存

```python
# 示例：章节进度更新
cache.delete(f"chapter:status:{course_id}:{user_id}")
```

### 内容更新

当管理员修改章节或问题内容时：

```python
# 信号处理器
on_chapter_content_change(instance)
on_problem_content_change(instance)
```

**失效操作：**
- 删除全局数据缓存键
- 不影响用户状态缓存

```python
# 示例：章节内容更新
cache.delete(f"chapter:global:{chapter_id}")
cache.delete(f"chapter:global:list:{course_id}")
```

## 性能指标

### 缓存命中率提升

**旧缓存策略：**
- 100章节 × 1000用户 = 100,000缓存条目
- 每个用户独立缓存全局数据
- 缓存命中率低（数据重复）

**新分离缓存策略：**
- 全局数据：100条（跨用户共享）
- 用户状态：1000条（每用户1条）
- 总计：1,100缓存条目
- **内存节省：98.9%**

### 响应时间

- 缓存命中：<5ms
- 缓存未命中：<50ms
- 平均响应时间降低约30%（由于命中率提升）

## 兼容性

### 向后兼容

- API响应格式**完全不变**
- 前端无需任何修改
- 旧缓存键会自动过期

### 降级策略

当任一缓存层失效时：
1. 从数据库查询对应数据
2. 回填缓存
3. 返回完整响应
4. 不影响用户体验

## 错误处理

### 缓存未命中

系统自动从数据库查询并回填缓存，无需特殊处理。

### 缓存服务不可用

系统自动降级到直接查询数据库，保证服务可用性。

## 使用示例

### 客户端调用

```javascript
// 获取章节列表（自动使用分离缓存）
const response = await fetch('/api/v1/courses/1/chapters/');
const data = await response.json();

// 响应格式与之前完全相同
console.log(data.results[0].title);  // "第一章：变量"
console.log(data.results[0].status);  // "completed"
```

### 管理后台操作

```python
# 更新章节内容（会自动失效全局缓存）
chapter = Chapter.objects.get(id=1)
chapter.title = "新标题"
chapter.save()  # 触发 on_chapter_content_change 信号

# 用户进度更新（会自动失效用户状态缓存）
progress = ChapterProgress.objects.get(id=1)
progress.completed = True
progress.save()  # 触发 on_chapter_progress_change 信号
```

## 监控指标

### 缓存命中率

- 全局数据缓存命中率目标：>90%
- 用户状态缓存命中率目标：>80%

### 内存占用

- 缓存条目数量减少98%+
- Redis内存使用量显著降低

## 相关文档

- [缓存策略文档](./cache-strategy.md)
- [运维文档](./operations.md)
- [变更日志](./CHANGELOG.md)
