## Context

当前缓存系统存在两套策略并存的问题：

```
┌─────────────────────────────────────────────────────────────────────────┐
│  旧策略 (CacheListMixin)                  新策略 (分离缓存)              │
├─────────────────────────────────────────────────────────────────────────┤
│  api:ChapterViewSet:user_123:page=1      chapter:global:list:5          │
│  api:ProblemViewSet:user_456:page=2      chapter:status:5:123           │
│                                          problem:global:list:10         │
│  每用户独立缓存，内存浪费                  problem:status:10:456         │
│                                          跨用户共享全局数据             │
└─────────────────────────────────────────────────────────────────────────┘
```

**核心问题**：
1. 信号处理器重复注册：`ChapterProgress` 有 `invalidate_chapter_progress_cache()` 和 `on_chapter_progress_change()` 两个处理器
2. ViewSet 继承混乱：重写了 list/retrieve 但仍继承 Mixin
3. Key 空间分裂：Redis 中存在冗余数据

**约束条件**：
- 迁移期间不能影响生产环境正常运行
- 必须保持 API 行为不变（仅改内部实现）
- 需要清理 Redis 中的旧缓存数据

## Goals / Non-Goals

**Goals:**
- 完全移除旧缓存策略（CacheListMixin 等）在 courses 应用中的使用
- 统一到分离缓存策略（全局数据 + 用户状态）
- 清理重复的信号处理器
- 清理 Redis 中的旧缓存 Key

**Non-Goals:**
- 不修改 file_management 应用的缓存（它使用独立的 FolderViewSet/FileEntryViewSet）
- 不改变 API 响应格式或行为
- 不引入新的缓存机制（如缓存预热策略变更）

## Decisions

### 1. 迁移策略：直接替换，不保留旧代码

**选择**：直接删除旧策略代码，不保留兼容层

**理由**：
- 新策略已在 ChapterViewSet/ProblemViewSet 的 list/retrieve 方法中实现
- 旧策略代码会造成混淆和维护负担
- 缓存 Key 空间已分离，无需兼容

**替代方案**：保留旧策略作为 fallback
- **缺点**：增加代码复杂度，两套逻辑并存

### 2. ViewSet 继承调整：移除旧 Mixin，保留方法重写

**选择**：从 ViewSet 继承链中移除 `CacheListMixin`、`CacheRetrieveMixin`、`InvalidateCacheMixin`

**修改前**：
```python
class ChapterViewSet(
    DynamicFieldsMixin,
    CacheListMixin,        # 移除
    CacheRetrieveMixin,    # 移除
    InvalidateCacheMixin,  # 移除
    viewsets.ModelViewSet,
):
    def list(self, ...):  # 已重写，使用新策略
        ...
```

**修改后**：
```python
class ChapterViewSet(
    DynamicFieldsMixin,
    viewsets.ModelViewSet,
):
    def list(self, ...):  # 保持不变
        ...
```

**理由**：
- list/retrieve 方法已重写，Mixin 的方法不会被调用
- 移除后代码意图更清晰

### 3. 信号处理器：删除旧处理器，保留新处理器

**选择**：删除以下旧信号处理器：
- `invalidate_problem_progress_cache` (signals.py:32)
- `invalidate_chapter_progress_cache` (signals.py:46)

保留以下新信号处理器：
- `on_chapter_progress_change` (signals.py:324)
- `on_problem_progress_change` (signals.py:346)
- `on_chapter_content_change` (signals.py:368)
- `on_problem_content_change` (signals.py:393)

**理由**：
- 新处理器实现细粒度失效，仅清除受影响用户的缓存
- 旧处理器使用 `delete_cache_pattern("api:*")` 清除所有用户的缓存

### 4. 其他 ViewSet：暂不迁移

**选择**：以下 ViewSet 保持使用 CacheListMixin：
- `CourseViewSet`
- `EnrollmentViewSet`
- `ExamViewSet`
- `DiscussionThreadViewSet`
- `DiscussionReplyViewSet`
- `SubmissionViewSet`
- `CodeDraftViewSet`
- `file_management` 应用中的 ViewSet

**理由**：
- 这些 ViewSet 的数据不涉及复杂的用户状态分离
- 可在后续迭代中按需迁移
- 本次迁移聚焦于核心问题（Chapter/Problem 的重复信号处理器）

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|----------|
| 升级期间缓存未命中增加 | 可接受，新缓存会在请求时自动填充 |
| 旧缓存 Key 残留在 Redis 中 | 提供清理脚本，可手动或定时清理 |
| search/ordering 参数走父类方法时无缓存 | 已有设计：这些参数会 fallback 到父类，不做缓存（符合预期） |

## Migration Plan

**Phase 1: 代码修改**
1. 从 ChapterViewSet/ProblemViewSet 移除旧 Mixin 继承
2. 删除旧的信号处理器
3. 清理相关的 import 语句

**Phase 2: 测试验证**
1. 运行现有缓存相关测试
2. 验证缓存 Key 格式正确
3. 验证信号处理器触发正确的缓存失效

**Phase 3: Redis 清理**
1. 提供清理脚本删除 `api:ChapterViewSet:*` 和 `api:ProblemViewSet:*` 的旧 Key
2. 可选：在低峰期执行

**Rollback Plan**：
- Git revert 代码变更
- 旧缓存 Key 会在 TTL 过期后自动清理（不影响功能）

## Open Questions

（无 - 设计已明确）