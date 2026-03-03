## Overview

修复章节详情页的流式渲染问题，让 Sidebar 组件能够立即渲染而不需要等待 chapter 数据。

## Current State

当前路由组件中，Sidebar 的渲染逻辑如下：

```tsx
<Await resolve={courseChapters}>
  {(resolved) => {
    // ...错误处理
    return (
      <Await resolve={chapter}>  {/* ❌ 嵌套等待 */}
        {(resolvedChapter) => (
          <ChapterSidebar
            initialData={resolved}
            courseId={params.courseId}
            currentChapterId={resolvedChapter.id}  {/* 从 chapter 获取 */}
            onChapterSelect={handleChapterSelect}
          />
        )}
      </Await>
    );
  }}
</Await>
```

问题：Sidebar 必须等待 `courseChapters` **和** `chapter` 都完成后才能渲染。

## Target State

修改后的渲染逻辑：

```tsx
<Await resolve={courseChapters}>
  {(resolved) => {
    // ...错误处理
    return (
      <ChapterSidebar
        initialData={resolved}
        courseId={params.courseId}
        currentChapterId={Number(params.chapterId)}  {/* ✅ 直接从 URL 获取 */}
        onChapterSelect={handleChapterSelect}
      />
    );
  }}
</Await>
```

改进：Sidebar 只需等待 `courseChapters` 即可立即渲染。

## Changes

### 文件修改

**`frontend/web-student/app/routes/_layout.courses_.$courseId_.chapters_.$chapterId/route.tsx`**

两处 Sidebar 渲染（mobile 和 desktop）都需要修改：

1. **Mobile Sidebar** (Line 116-149): 移除嵌套的 `<Await resolve={chapter}>`
2. **Desktop Sidebar** (Line 158-191): 移除嵌套的 `<Await resolve={chapter}>`

两处修改相同：
- 删除内层的 `<Await resolve={chapter}>` 组件
- 将 `currentChapterId={resolvedChapter.id}` 改为 `currentChapterId={Number(params.chapterId)}`
- 直接渲染 `<ChapterSidebar />` 而不是在 Await 回调中渲染

## Performance Impact

修改前后的数据流对比：

```
Before:
┌─────────────────────────────────────────────┐
│  Server Response Stream                     │
│  ├─ unlockStatus (blocking)                 │
│  ├─ courseChapters ─────────┐              │
│  ├─ chapter ────────────────┼──▶ Sidebar   │
│  └─ problems                │   waits for   │
│                             │   both        │
└─────────────────────────────┴───────────────┘

After:
┌─────────────────────────────────────────────┐
│  Server Response Stream                     │
│  ├─ unlockStatus (blocking)                 │
│  ├─ courseChapters ─────────▶ Sidebar       │
│  ├─ chapter ────────────────▶ Title/Content │
│  └─ problems ───────────────▶ Problems      │
│                                             │
│  Sidebar 不再依赖 chapter 数据              │
└─────────────────────────────────────────────┘
```

## Testing

1. 访问任意章节详情页
2. 验证 Sidebar 在 chapter 数据返回前即可显示
3. 验证当前章节在 Sidebar 中高亮正确
4. 验证章节切换功能正常
5. 验证移动端和桌面端表现一致

## Risk Assessment

| 风险项 | 等级 | 缓解措施 |
|--------|------|----------|
| `params.chapterId` 类型问题 | 低 | 使用 `Number()` 显式转换 |
| `ChapterSidebar` 其他依赖 | 低 | 已确认只需 `currentChapterId` |

## Rollback

如有问题，恢复原始文件的嵌套 Await 结构即可。
