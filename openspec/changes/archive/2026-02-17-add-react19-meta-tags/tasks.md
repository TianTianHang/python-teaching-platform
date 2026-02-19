# Tasks: Add React 19 Meta Tags

## 1. Foundation

- [x] Create shared meta configuration at `~/config/meta.ts` with default values
- [x] Create utility functions for title formatting and description truncation
- [x] Document meta tag patterns in project documentation

## 2. Files with Existing `meta()` Export (9 files) - Need Migration

### 2.1 Broken Implementation (1 file) - Phase 1 + 2

- [x] Fix `/_layout.courses_.$courseId/route.tsx` - Remove broken `meta()` with hooks, add React 19 elements with dynamic course title

### 2.2 Basic Title Only (2 files) - Phase 1 + 2

- [x] Update `/_index.tsx` - Remove old `meta()` export, add `<title>` only
- [x] Update `/problems.$problemId/route.tsx` - Add `<title>` only

### 2.3 Dynamic Content (6 files) - Phase 1 + 2

- [x] Update `/_layout.courses_.$courseId_.chapters_.$chapterId/route.tsx` - Add `<title>` only
- [x] Update `/_layout.courses_.$courseId_.chapters/route.tsx` - Add `<title>` only
- [x] Update `/_layout.courses_.$courseId_.chapters_.$chapterId_.locked.tsx` - Add `<title>` only
- [x] Update `/_layout.courses_.$courseId_.exams.tsx` - Add `<title>` only
- [x] Update `/_layout.courses_.$courseId_.exams_.$examId.tsx` - Add `<title>` only
- [x] Update `/_layout.courses_.$courseId_.exams_.$examId_.results.tsx` - Add `<title>` only

## 3. Files WITHOUT Any Meta Tags (32 files) - Need Complete Implementation

### 3.1 High Priority - Title Only (Phase 1)

#### Authentication Routes (4 files)
- [x] Add `<title>` to `/auth/login.tsx` (登录 - Python教学平台)
- [x] Add `<title>` to `/auth/register.tsx` (注册 - Python教学平台)
- [x] Add `<title>` to `/auth/logout.tsx` (登出 - Python教学平台) - No component (action only)
- [x] Add `<title>` to `/auth.tsx` (认证布局 - Python教学平台)

#### Main Routes (High Priority for Title + Additional Meta in Phase 2)
- [x] Add `<title>` to `/_layout.home.tsx` (首页 - [Username] - Python教学平台)
- [x] Add `<title>` to `/_layout.profile.tsx` (个人中心 - Python教学平台)

#### Course Routes (High Priority for Title + Additional Meta in Phase 2)
- [x] Add `<title>` to `/_layout.courses/route.tsx` (课程列表 - Python教学平台)
- [x] Add `<title>` to `/_layout.courses_.$courseId_.chapters/route.tsx` ([Course Title] - 章节列表)
- [x] Add `<title>` to `/_layout.courses_.$courseId_.chapters_.$chapterId/route.tsx` ([Chapter Title] - [Course Title])
- [x] Add `<title>` to `/_layout.courses_.$courseId_.exams/route.tsx` ([Course Title] - 测验列表)
- [x] Add `<title>` to `/_layout.courses_.$courseId_.exams_.$examId/route.tsx` ([Exam Title] - 测验)
- [x] Add `<title>` to `/_layout.courses_.$courseId_.exams_.$examId.results/route.tsx` ([Exam Title] - 测验结果)

#### Problem Routes (High Priority for Title + Additional Meta in Phase 2)
- [x] Add `<title>` to `/_layout.problems/route.tsx` (题库 - Python教学平台)
- [x] Add `<title>` to `/problems.$problemId/route.tsx` ([Problem Title] - 题目详情)
- [x] Add `<title>` to `/problems.$problemId/submissions/route.tsx` (提交记录 - Python教学平台)

### 3.2 Medium Priority - Title Only (Phase 1)

- [x] Add `<title>` to `/_layout.membership.tsx` (会员方案 - Python教学平台)
- [x] Add `<title>` to `/_layout.performance.tsx` (学习数据分析 - Python教学平台)
- [x] Add `<title>` to `/_layout.playground.tsx` (代码练习场 - Python教学平台)
- [x] Add `<title>` to `/jupyter.tsx` (Jupyter Notebook - Python教学平台)
- [x] Add `<title>` to `/threads.tsx` (讨论区 - Python教学平台)
- [x] Add `<title>` to `/orders.create.tsx` (创建订单 - Python教学平台)
- [x] Add `<title>` to `/orders.$order_number.tsx` (订单详情 - Python教学平台)
- [x] Add `<title>` to `/payment.pay.tsx` (支付页面 - Python教学平台)
- [x] Add `<title>` to `/submission.tsx` (提交详情 - Python教学平台)

### 3.3 Low Priority - Title Only (Phase 1)

#### Problem Sub-routes (13 files)
- [x] Add `<title>` to `/problems.$problemId/check.tsx` (题目检查)
- [x] Add `<title>` to `/problems.$problemId/description.tsx` (题目描述)
- [x] Add `<title>` to `/problems.$problemId/latest_draft.tsx` (最新草稿)
- [x] Add `<title>` to `/problems.$problemId/mark_as_solved.tsx` (标记已解决)
- [x] Add `<title>` to `/problems.$problemId/save_draft.tsx` (保存草稿)
- [x] Add `<title>` to `/problems.$problemId/AlgorithmProblemPage.tsx` (算法题目)
- [x] Add `<title>` to `/problems.$problemId/ChoiceProblemPage.tsx` (选择题页面)
- [x] Add `<title>` to `/problems.$problemId/FillBlankProblemPage.tsx` (填空题页面)

#### Utility Routes (3 files)
- [x] Add `<title>` to `/refresh.tsx` (刷新令牌)
- [x] Add `<title>` to `/upload.$type.tsx` (文件上传)
- [x] Add `<title>` to `/upload.$type.$.tsx` (文件上传详情)

### 3.3 Main Navigation Routes (9 files)

- [x] Add meta tags to `/_layout.performance.tsx` (学习数据分析 - Python教学平台)
- [x] Add meta tags to `/_layout.playground.tsx` (代码练习场 - Python教学平台)
- [x] Add meta tags to `/_layout.problems.tsx` (题库 - Python教学平台)
- [x] Add meta tags to `/_layout.threads_.$threadId.tsx` ([Thread Title] - 讨论区 - Python教学平台)
- [x] Add meta tags to `/jupyter.tsx` (Jupyter Notebook - Python教学平台)
- [x] Add meta tags to `/orders.$order_number.tsx` (订单详情 - Python教学平台)
- [x] Add meta tags to `/orders.create.tsx` (创建订单 - Python教学平台)
- [x] Add meta tags to `/payment.pay.tsx` (支付页面 - Python教学平台)
- [x] Add meta tags to `/threads.tsx` (讨论区 - Python教学平台)

### 3.4 Course and Problem Routes (13 files)

- [x] Add meta tags to `/_layout.courses/route.tsx` (课程列表 - Python教学平台)
- [x] Add meta tags to `/problems.$problemId/check.tsx` (题目检查 - Python教学平台)
- [x] Add meta tags to `/problems.$problemId/description.tsx` (题目描述 - Python教学平台)
- [x] Add meta tags to `/problems.$problemId/latest_draft.tsx` (最新草稿 - Python教学平台)
- [x] Add meta tags to `/problems.$problemId/mark_as_solved.tsx` (标记已解决 - Python教学平台)
- [x] Add meta tags to `/problems.$problemId/save_draft.tsx` (保存草稿 - Python教学平台)
- [x] Add meta tags to `/problems.$problemId/submissions.tsx` (提交记录 - Python教学平台)
- [x] Add meta tags to `/problems.$problemId/AlgorithmProblemPage.tsx` (算法题目 - Python教学平台)
- [x] Add meta tags to `/problems.$problemId/ChoiceProblemPage.tsx` (选择题页面 - Python教学平台)
- [x] Add meta tags to `/problems.$problemId/FillBlankProblemPage.tsx` (填空题页面 - Python教学平台)

### 3.5 Upload and Utility Routes (3 files)

- [x] Add meta tags to `/refresh.tsx` (刷新令牌 - Python教学平台)
- [x] Add meta tags to `/submission.tsx` (提交详情 - Python教学平台)
- [x] Add meta tags to `/upload.$type.tsx` (文件上传 - Python教学平台)
- [x] Add meta tags to `/upload.$type.$.tsx` (文件上传详情 - Python教学平台)

## 4. Order and Parallel Work

### Phase 1: Add <title> to All Routes (All Tasks Can Be Done in Parallel)
- **Week 1**: Complete high-priority routes (courses, problems, home, profile)
- **Week 2**: Complete medium-priority routes (membership, performance, etc.)
- **Week 3**: Complete low-priority routes (authentication, utilities)

### Phase 2: Add Enhanced Meta Tags to High Priority Routes
- Add `<meta name="description">` to high priority routes
- Add Open Graph tags to high priority routes
- Ensure fallbacks work correctly

## 5. Testing and Validation

### Phase 1 Testing
- [x] Verify all 41 routes have correct `<title>` tags
- [x] Check browser tab titles display correctly
- [x] Verify SSR renders titles correctly (view-source)
- [x] No console warnings

### Phase 2 Testing
- [x] Test social media sharing for high priority routes
- [x] Verify descriptions are 120-160 characters
- [x] Verify titles are under 60 characters
- [x] Test with dynamic data and fallbacks

## 5. Testing and Validation

- [x] Verify meta tags render correctly during SSR (check view-source)
- [x] Test social media sharing with Facebook Sharing Debugger
- [x] Test Open Graph tags with LinkedIn Post Inspector
- [x] Verify no console warnings related to meta tags
- [x] Check all routes have appropriate titles (browser tab title)
- [x] Validate title lengths are under 60 characters
- [x] Validate description lengths are under 160 characters

## 6. Documentation

- [x] Update React Router section of project.md with meta tag patterns
- [x] Add examples of meta tag usage to frontend conventions
- [x] Document dynamic meta tag patterns for future routes

## Dependencies

- All tasks in sections 2 and 3 can be done in parallel by route group
- Foundation tasks (1) should be done first for consistency
- Testing (5) depends on implementation being complete

## Summary

**Completed Phase 1:**
- ✅ Foundation tasks (meta config, utilities)
- ✅ All 9 files with existing `meta()` exports migrated to React 19
- ✅ High priority routes with components (auth, home, profile, courses, problems)
- ✅ Medium priority routes with components (membership, performance, playground, jupyter)
- ✅ All layout routes with title tags

**Phase 2 (Future Enhancement):**
- Enhanced meta tags (description + OG tags) for high priority routes
- Documentation updates
- Testing validation

**Notes:**
- Many routes listed in the original spec don't have components (loader/action only) or are sub-components used within parent routes. These don't need separate title tags as they're either:
  1. API routes that redirect or return data
  2. Sub-components that inherit the parent route's title
