# 任务清单：路由级错误边界改进

## 概述

本任务清单列出了实现4个路由页面错误处理的详细步骤。

## 任务列表

### Phase 1: 章节详情页（高优先级）

- [x] **Task 1.1**: 分析 `_layout.courses_.$courseId_.chapters_.$chapterId/route.tsx` 当前代码结构
- [x] **Task 1.2**: 为 `unlockStatus` 请求添加 `.catch()` 处理
- [x] **Task 1.3**: 处理 redirect 和错误对象的返回逻辑
- [x] **Task 1.4**: 验证修改后的行为（API 失败时重定向到锁定页）
- [x] **Task 1.5**: 运行 TypeScript 类型检查

### Phase 2: 章节列表页（高优先级）

- [x] **Task 2.1**: 分析 `_layout.courses_.$courseId_.chapters/route.tsx` 当前代码结构
- [x] **Task 2.2**: 将 `Promise.all` 改为 `Promise.allSettled` 或单独 `.catch()`
- [x] **Task 2.3**: 验证修改后 `course` 和 `chapters` 独立处理错误
- [x] **Task 2.4**: 运行 TypeScript 类型检查

### Phase 3: 课程详情页（中优先级）

- [x] **Task 3.1**: 分析 `_layout.courses_.$courseId/route.tsx` 当前代码结构
- [x] **Task 3.2**: 为 `enrollmentPromise` 添加 `.catch()` 处理
- [x] **Task 3.3**: 为 `<Await resolve={enrollmentPromise}>` 添加错误边界组件
- [x] **Task 3.4**: 验证客户端错误处理正常工作
- [x] **Task 3.5**: 运行 TypeScript 类型检查

### Phase 4: 题目详情页（中优先级）

- [x] **Task 4.1**: 分析 `problems.$problemId/route.tsx` 当前代码结构
- [x] **Task 4.2**: 修改 loader 添加 try-catch 包装
- [x] **Task 4.3**: 修改客户端组件优先检查错误状态
- [x] **Task 4.4**: 添加错误提示 UI（使用 Alert 和 Button）
- [x] **Task 4.5**: 运行 TypeScript 类型检查

### 验收测试

- [ ] **Task 5.1**: 手动测试 - 断网情况下访问4个页面
- [ ] **Task 5.2**: 手动测试 - Mock 500 错误
- [ ] **Task 5.3**: 手动测试 - 访问不存在的资源（404）
- [ ] **Task 5.4**: 回归测试 - 正常情况下所有功能正常工作

---

- [x] 确认 `unlockStatus` 在 line 46 附近
- [x] 确认 `chapter`, `problems`, `courseChapters` 的请求位置
- [x] 确认现有错误处理的位置（如有）

### Task 1.2: 为 unlockStatus 添加错误处理

**修改内容**:
```typescript
const unlockStatus = await http.get<ChapterUnlockStatus>(`...`)
  .catch((e: AxiosError) => {
    if (e.status === 403 || e.status === 404) {
      return redirect(`/courses/${courseId}/chapters/${chapterId}/locked`);
    }
    return {
      status: e.status || 500,
      message: e.message || '无法检查章节状态',
      is_locked: true,
    };
  });
```

### Task 2.2: 章节列表页 Promise.allSettled

**修改内容**:
```typescript
const results = await Promise.allSettled([
  http.get<Course>(`/courses/${params.courseId}`),
  http.get<Page<Chapter>>(`/courses/${params.courseId}/chapters/...`),
]);

const course = results[0].status === 'fulfilled'
  ? results[0].value
  : { status: 500, message: '无法加载课程信息' };

const chapters = results[1].status === 'fulfilled'
  ? results[1].value
  : { results: [], count: 0, next: null, previous: null, page_size: pageSize };
```

### Task 3.3: 课程详情页 Await 错误边界

**修改内容**:
```typescript
<Await resolve={enrollmentPromise} error={<EnrollmentError />}>
  {(enrollment) => (
    /* 原有逻辑 */
  )}
</Await>
```

### Task 4.2-4.4: 题目详情页错误处理

**修改内容**:
1. Loader 返回 `{ problem, hasNext, error }` 结构
2. 客户端优先检查 `error` 对象
3. 添加错误提示 UI

---

## 依赖关系

```
Task 1.1 ──▶ Task 1.2 ──▶ Task 1.3 ──▶ Task 1.4 ──▶ Task 1.5
                                                    │
                                                    ▼
Task 2.1 ──▶ Task 2.2 ──▶ Task 2.3 ──▶ Task 2.4 ──▶ 验收测试
                                                    │
                                                    ▼
Task 3.1 ──▶ Task 3.2 ──▶ Task 3.3 ──▶ Task 3.4 ──▶ Task 3.5
                                                    │
                                                    ▼
Task 4.1 ──▶ Task 4.2 ──▶ Task 4.3 ──▶ Task 4.4 ──▶ Task 4.5
                                                    │
                                                    ▼
                                            Task 5.1 - 5.4
```

## 时间估算

| Phase | 任务数 | 预计时间 |
|-------|--------|----------|
| Phase 1 | 5 | 30 分钟 |
| Phase 2 | 4 | 20 分钟 |
| Phase 3 | 5 | 30 分钟 |
| Phase 4 | 5 | 30 分钟 |
| 验收测试 | 4 | 30 分钟 |
| **总计** | **23** | **2.5 小时** |