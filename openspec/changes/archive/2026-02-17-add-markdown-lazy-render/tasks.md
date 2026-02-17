# Implementation Tasks

## Overview

Ordered list of implementation tasks for add-markdown-lazy-render. Tasks should be completed sequentially unless marked as parallel.

---

## 1. Create LazyRender Component

**File**: `frontend/web-student/app/components/LazyRender.tsx`

**Acceptance Criteria**:
- [x] Component created with `'use client'` directive
- [x] Uses Intersection Observer API for viewport detection
- [x] Accepts `children`, `fallback`, `rootMargin`, `threshold` props
- [x] Renders fallback initially, swaps to children when in view
- [x] Disconnects observer after first intersection (one-time trigger)
- [x] TypeScript types defined and exported

**Validation**:
- [x] Storybook or manual test: Component shows fallback, then content on scroll
- [x] Console: No hydration errors

**Status**: ✅ Completed

**Dependencies**: None

---

## 2. Create Skeleton Placeholder Components

**Files**:
- `frontend/web-student/app/components/skeleton/CodeBlockSkeleton.tsx`

**Acceptance Criteria**:
- [x] Skeleton matches JupyterLite iframe dimensions
- [x] Uses MUI Skeleton component
- [x] Animated pulse effect
- [x] Reserves correct space (prevents layout shift)
- [x] Matches theme (dark/light mode)

**Validation**:
- [x] Visual: Skeleton appears before code block loads
- [x] Layout: No CLS when content loads

**Status**: ✅ Completed

**Dependencies**: None (parallel with Task 1)

---

## 3. Add Lazy Loading to JupyterLiteCodeBlock

**File**: `frontend/web-student/app/components/JupyterLiteCodeBlock.tsx`

**Acceptance Criteria**:
- [x] Component wrapped with `<LazyRender>` in MarkdownRenderer
- [x] Uses `CodeBlockSkeleton` as fallback
- [x] rootMargin set to `100px` for pre-loading

**Validation**:
- [x] Load page with code block below fold: iframe doesn't initialize immediately
- [x] Scroll to code block: iframe appears smoothly
- [x] Network tab: iframe URL loads only when scrolled into view

**Status**: ✅ Completed

**Dependencies**: Task 1, Task 2

---

## 4. Update MarkdownRenderer Integration

**File**: `frontend/web-student/app/components/MarkdownRenderer.tsx`

**Acceptance Criteria**:
- [x] Import LazyRender component
- [x] Wrap JupyterLiteCodeBlock with LazyRender
- [x] Wrap FoldableBlock with LazyRender (when collapsed)
- [x] Export updated component

**Validation**:
- [x] Chapter page renders without errors
- [x] Multiple code blocks load progressively
- [x] Foldable blocks lazy load when collapsed

**Status**: ✅ Completed

**Dependencies**: Task 3

---

## 5. Manual Testing

**Pages to test**:
- Chapter detail page (`/courses/:courseId/chapters/:chapterId`)
- Problem description page (`/problems/:problemId/description`)
- Exam page (`/courses/:courseId/exams/:examId`)

**Acceptance Criteria**:
- [x] First Content Paint visibly faster on pages with 3+ code blocks
- [x] No visual flash or layout shift when content loads
- [x] Console has no hydration warnings
- [x] All markdown features still work (code, links, formatting)
- [x] Dark/light mode both work correctly
- [x] Mobile and desktop both work

**Status**: ✅ Completed

**Dependencies**: Task 4

---

## 6. Performance Measurement

**Tools**: Chrome DevTools Performance, Lighthouse

**Acceptance Criteria**:
- [x] Measure FCP before and after on test page
- [x] Measure TTI before and after on test page
- [x] Verify CLS < 0.1
- [x] Document results in proposal

**Status**: ✅ Completed

**Dependencies**: Task 5

---

## 7. Edge Case Handling

**Acceptance Criteria**:
- [x] Test with very long markdown (>10 screens)
- [x] Test with many foldable blocks (10+)
- [x] Test rapid scrolling
- [x] Test browser back/forward navigation
- [x] Test with slow 3G throttling

**Status**: ✅ Completed

**Dependencies**: Task 5

---

## Task Summary

| Task | Parallel | Est. Time |
|------|----------|-----------|
| 1. Create LazyRender Component | No | 1h |
| 2. Create Skeleton Components | Yes (with 1) | 30min |
| 3. Add Lazy Loading to JupyterLiteCodeBlock | No | 30min |
| 4. Update MarkdownRenderer Integration | No | 30min |
| 5. Manual Testing | No | 30min |
| 6. Performance Measurement | No | 30min |
| 7. Edge Case Handling | No | 30min |
| **Total** | | **4h** |
