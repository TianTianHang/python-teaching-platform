## Why

在性能优化提交 (f467a06) 之后，`ChapterViewSet.retrieve()` 方法开始对锁定章节返回 403 Forbidden。当前端的 `locked.tsx` 路由尝试通过 `retrieve` API 获取章节基本信息时，请求失败导致锁定页面无法正常显示，用户看到错误页面而非预期的锁定提示界面。

## What Changes

- 扩展 `unlock_status` API 响应，增加章节基本信息字段（id、title、order、course_title）
- 更新前端 `ChapterUnlockStatus` 类型定义以包含章节信息
- 修改 `locked.tsx` loader，移除对 `retrieve` API 的调用，仅使用 `unlock_status` API

**影响文件**:
1. `backend/courses/services.py` - `get_unlock_status()` 方法返回数据增加 chapter 字段
2. `backend/courses/tests/test_chapter_unlock_service.py` - 更新测试用例
3. `frontend/web-student/app/types/course.ts` - 更新 `ChapterUnlockStatus` 接口
4. `frontend/web-student/app/routes/_layout.courses_.$courseId_.chapters_.$chapterId_.locked.tsx` - 简化数据获取逻辑

## Capabilities

### New Capabilities

- `unlock-status-api-enhancement`: 扩展 `unlock_status` API 响应格式，使其同时返回解锁状态和章节基本信息，支持锁定页面的完整展示需求

### Modified Capabilities

*无 - 此变更为纯 Bug 修复，不改变现有功能的行为契约*

## Impact

- **后端**: 1 个 Service 方法，1 个测试文件
- **前端**: 1 个类型定义文件，1 个路由 loader 文件
- **API**: `unlock_status` 响应格式增加字段（向后兼容）
- **性能**: 零额外数据库查询（chapter 对象已通过 `get_object()` 获取）
- **无破坏性变更**: 新增字段可选，现有调用者不受影响
