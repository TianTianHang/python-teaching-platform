## Tasks

- [x] 1. 修改章节详情页流式渲染 - 移除 Sidebar 嵌套 Await
  - **文件**: `frontend/web-student/app/routes/_layout.courses_.$courseId_.chapters_.$chapterId/route.tsx`
  - **修改内容**:
    1. ✅ 找到 mobile Sidebar 渲染部分（约 Line 116-149）
    2. ✅ 移除内层的 `<Await resolve={chapter}>` 嵌套
    3. ✅ 将 `currentChapterId={resolvedChapter.id}` 改为 `currentChapterId={Number(params.chapterId)}`
    4. ✅ 对 desktop Sidebar（约 Line 158-191）重复相同修改
  - **验证**:
    - TypeScript 编译通过
    - Sidebar 在 chapter 数据返回前即可渲染
    - 当前章节高亮正确

- [x] 2. 测试验证
  - **测试场景**:
    1. ✅ TypeScript 编译通过
    2. [ ] 访问任意课程章节详情页 - 需手动验证
    3. [ ] 验证 Sidebar 立即显示（在 chapter 内容加载前）- 需手动验证
    4. [ ] 验证当前章节在 Sidebar 中高亮正确 - 需手动验证
    5. [ ] 验证点击章节切换正常 - 需手动验证
  - **性能检查**:
    - [ ] 网络面板中确认流式渲染正常（多个请求并行）- 需手动验证

## Implementation Notes

### 修改前代码结构（mobile Sidebar）
```tsx
<Await resolve={courseChapters}>
  {(resolved) => {
    if ('status' in resolved) { /* 错误处理 */ }
    return (
      <Await resolve={chapter}>  {/* 嵌套等待 - 需要移除 */}
        {(resolvedChapter) => (
          <ChapterSidebar
            initialData={resolved}
            courseId={params.courseId}
            currentChapterId={resolvedChapter.id}
            onChapterSelect={handleChapterSelect}
          />
        )}
      </Await>
    );
  }}
</Await>
```

### 修改后代码结构
```tsx
<Await resolve={courseChapters}>
  {(resolved) => {
    if ('status' in resolved) { /* 错误处理 */ }
    return (
      <ChapterSidebar
        initialData={resolved}
        courseId={params.courseId}
        currentChapterId={Number(params.chapterId)}  {/* 直接使用 URL 参数 */}
        onChapterSelect={handleChapterSelect}
      />
    );
  }}
</Await>
```

### Desktop Sidebar 修改相同
两处（mobile 和 desktop）的修改完全一致。
