# Context 覆盖 Bug 修复

## 问题描述

`optimize-problems-api-dynamic-fields` 实现中存在一个严重的 bug：在 `ProblemViewSet` 的 `list()` 和 `retrieve()` 方法中，直接传递 `context={'exclude_fields': exclude_fields}` 参数，这会**覆盖整个 context 字典**，导致 Django REST Framework 默认提供的关键字段（`request`、`view`、`format`）丢失。

## 影响

### 核心问题

所有题目的 `is_unlocked` 字段都返回 `False`，用户看到所有题目都是锁定状态。

### 根本原因

```python
# backend/courses/views.py:683, 697 (错误实现)
serializer = self.get_serializer(page, many=True, context={'exclude_fields': exclude_fields})
```

DRF 的 `get_serializer()` 方法使用 `setdefault` 设置 context：

```python
# DRF 源码
kwargs.setdefault('context', self.get_serializer_context())
```

当手动传递 `context` 参数时，`setdefault` 不会执行，导致 serializer 收到的 context 只有：

```python
{
    'exclude_fields': {...}  # 只有这一个字段
}
```

缺少了：
- `request` - 当前请求对象
- `view` - 当前视图实例
- `format` - 响应格式

### 连锁反应

在 `ProblemSerializer.get_is_unlocked()` 方法中：

```python
# backend/courses/serializers.py:300-302
request = self.context.get('request')  # → None
if not request or not request.user.is_authenticated:
    return False  # 所有题目都返回 False！
```

由于 `request` 为 `None`，所有题目的 `is_unlocked` 都返回 `False`。

## 解决方案

### 方案：在 get_serializer_context() 中添加 exclude_fields

修改 `ProblemViewSet`：

1. **在 `get_serializer_context()` 中安全地添加 `exclude_fields`**
   - 捕获 `ValidationError` 异常，避免影响其他 action

2. **移除 `list()` 和 `retrieve()` 中的手动 context 传递**

## 修复代码

```python
def get_serializer_context(self):
    """
    向序列化器传递额外的上下文
    """
    context = super().get_serializer_context()

    # 传递缓存的 enrollment 到 serializer context
    if hasattr(self, '_enrollment'):
        context['enrollment'] = self._enrollment

    # 传递快照相关变量
    if hasattr(self, '_use_snapshot'):
        context['use_snapshot'] = self._use_snapshot
    if hasattr(self, '_unlock_states'):
        context['unlock_states'] = self._unlock_states

    # 安全地添加 exclude_fields（捕获验证异常）
    try:
        context['exclude_fields'] = self.get_exclude_fields()
    except Exception:
        # 验证失败时使用空集合（list/retrieve 会单独处理错误）
        context['exclude_fields'] = set()

    return context

def list(self, request, *args, **kwargs):
    """
    列表方法：支持字段排除
    """
    # 获取并验证排除字段（可能抛出 ValidationError）
    exclude_fields = self.get_exclude_fields()  # 保留验证逻辑

    queryset = self.filter_queryset(self.get_queryset())
    page = self.paginate_queryset(queryset)

    if page is not None:
        serializer = self.get_serializer(page, many=True)  # 不再手动传递 context
        return self.get_paginated_response(serializer.data)

    serializer = self.get_serializer(queryset, many=True)  # 不再手动传递 context
    return Response(serializer.data)

def retrieve(self, request, *args, **kwargs):
    """
    详情方法：支持字段排除
    """
    # 获取并验证排除字段（可能抛出 ValidationError）
    exclude_fields = self.get_exclude_fields()  # 保留验证逻辑

    instance = self.get_object()
    serializer = self.get_serializer(instance)  # 不再手动传递 context
    return Response(serializer.data)
```

## 测试验证

修复后需要验证：

1. **题目解锁状态正确显示**
   - 已解锁题目显示为解锁
   - 未解锁题目显示为锁定

2. **字段排除功能正常**
   - `?exclude=content,recent_threads` 正确排除指定字段
   - 无效字段名返回 400 错误

3. **快照机制正常工作**
   - `is_unlocked` 使用快照数据
   - 快照过期时回退到实时查询

## 相关文件

- `backend/courses/views.py` - ProblemViewSet 类
- `backend/courses/serializers.py` - ProblemSerializer 类
- `openspec/changes/optimize-problems-api-dynamic-fields/` - 变更文档