## Context

### Current State
章节相关页面目前采用服务端渲染架构：

**章节列表页** (`_layout.courses_.$courseId_.chapters/route.tsx`):
- 使用 `withAuth` 包装器进行服务端认证
- 服务端 `loader` 通过 `createHttp(request)` 获取数据
- 并行请求课程信息和章节列表（已优化）
- 支持无限滚动分页

**章节详情页** (`_layout.courses_.$courseId_.chapters_.$chapterId/route.tsx`):
- 使用 `withAuth` 包装器
- 服务端 `loader` 检查 `unlock_status`，根据结果进行服务端重定向（`redirect()`）
- 已有 `clientAction` 用于标记章节完成（客户端执行）
- 返回 Promises 用于 SSR streaming
- 副作用：自动标记章节为"进行中"状态

**章节 locked 页** (`_layout.courses_.$courseId_.chapters_.$chapterId_.locked.tsx`):
- 当前实现未确认（需检查）

### Dependencies
- **认证**: `withAuth` 包装器依赖服务端 session（HTTP-only cookies）
- **HTTP 客户端**: 服务端使用 `createHttp(request)`，客户端已有 `clientHttp`
- **其他已客户端化的页面**: home.tsx, problems.tsx, courses.tsx 等提供了参考模式

## Goals / Non-Goals

**Goals:**
1. 将所有章节相关页面迁移到 `clientLoader` + `hydrate` 架构
2. 移除对 `withAuth` 包装器的依赖，实现完全客户端认证
3. 在 clientLoader 中检查权限，返回状态信息，在组件中进行客户端重定向
4. 保持现有功能不变（解锁状态检查、进度跟踪、无限滚动等）
5. 提升客户端导航性能和用户体验

**Non-Goals:**
1. 不修改后端 API（所有 API 调用保持不变）
2. 不影响其他认证相关页面（login, register, set-session 等保持服务端）
3. 不改变业务逻辑（章节解锁规则、进度跟踪等保持不变）
4. 不涉及其他未迁移的页面（exams, membership, jupyter, performance 等）

## Decisions

### Decision 1: Use clientLoader with hydrate = true
**Choice**: 所有章节页面使用 `clientLoader` 并启用 `hydrate = true`

**Rationale**:
- **首次访问性能**: `hydrate = true` 确保首次访问时进行 SSR，首屏显示快
- **后续导航性能**: 客户端导航时直接使用 clientLoader，无需服务器渲染
- **一致性**: 与已迁移的页面（home, problems, courses）保持一致
- **渐进式增强**: 即使 JavaScript 失败，SSR 内容仍可显示

**Alternatives Considered**:
1. **仅 clientLoader (不 hydrate)**: 首次访问也需要客户端渲染，首屏慢，用户体验差 ❌
2. **保持服务端 loader**: 无法享受客户端导航优势，服务器负担重 ❌

### Decision 2: Mixed redirect strategy (check in loader, redirect in component)
**Choice**: 在 `clientLoader` 中检查 `unlock_status`，返回状态信息；在组件中使用 `useNavigate()` 进行客户端重定向

**Rationale**:
- **避免服务端重定向**: 不依赖服务端 `redirect()`，完全客户端控制
- **更好的用户体验**: 客户端重定向更快，无页面闪烁
- **灵活性**: 可以根据状态显示过渡动画或确认对话框
- **错误处理**: 可以捕获重定向失败的情况并提供备选方案

**Implementation Pattern**:
```typescript
// clientLoader
export async function clientLoader({ params }) {
  const unlockStatus = await clientHttp.get(`/courses/${courseId}/chapters/${chapterId}/unlock_status`);
  return { isLocked: unlockStatus.is_locked, ...otherData };
}

// Component
export default function ChapterDetailPage() {
  const { isLocked } = useLoaderData<typeof clientLoader>();
  const navigate = useNavigate();
  
  useEffect(() => {
    if (isLocked) {
      navigate(`/courses/${courseId}/chapters/${chapterId}/locked`, { replace: true });
    }
  }, [isLocked, navigate, courseId, chapterId]);
  
  if (isLocked) return null; // 或显示 loading
  // render chapter content
}
```

**Alternatives Considered**:
1. **在 clientLoader 中使用 redirect()**: 会导致客户端路由异常，破坏 SPA 体验 ❌
2. **保持服务端重定向**: 无法完全客户端化，违背迁移目标 ❌

### Decision 3: Complete client-side authentication (remove withAuth)
**Choice**: 移除 `withAuth` 包装器，使用 `clientHttp` + JWT token 完全在客户端进行认证

**Rationale**:
- **简化架构**: 移除服务端认证依赖，架构更清晰
- **性能提升**: 减少服务器计算负担
- **一致性**: 与其他已客户端化的页面保持一致
- **JWT 已可用**: 登录时已将 JWT 存储在 localStorage/cookie，可直接使用

**Token Management**:
- `clientHttp` 已从 localStorage/cookie 读取 token 并添加到 Authorization header
- 401 错误时在 clientLoader 中捕获并重定向到 `/auth/login`
- 无需额外的 token 管理逻辑

**Alternatives Considered**:
1. **保留 withAuth**: 无法实现完全客户端化，服务端负担仍存在 ❌
2. **使用 serverLoader → clientLoader 模式**: 增加复杂度，性能提升有限 ❌

### Decision 4: Keep side-effects as non-blocking fire-and-forget
**Choice**: 保留标记章节为"进行中"的副作用逻辑，但作为非阻塞的 fire-and-forget 请求

**Rationale**:
- **不影响性能**: 不阻塞页面渲染
- **用户体验好**: 页面立即显示，无需等待副作用完成
- **错误容忍**: 副作用失败不影响页面显示
- **现有模式**: 章节详情页已采用此模式，效果良好

**Implementation Pattern**:
```typescript
export async function clientLoader({ params }) {
  const chapter = await clientHttp.get(`/courses/${courseId}/chapters/${chapterId}`);
  
  // Fire-and-forget: mark as in-progress
  if (chapter.status === 'not_started') {
    clientHttp.post(`/courses/${courseId}/chapters/${chapterId}/mark_as_completed/`, { completed: false })
      .catch(() => {}); // Silently handle errors
  }
  
  return { chapter };
}
```

### Decision 5: Reuse existing HydrateFallback and ErrorBoundary patterns
**Choice**: 参考已客户端化的页面（home.tsx, problems.tsx）创建骨架屏和错误边界

**Rationale**:
- **一致性**: 整个应用的加载和错误体验保持一致
- **已有组件**: `SkeletonHome`, `SkeletonProblems` 等可复用或作为参考
- **用户友好**: 清晰的加载状态和错误提示

**Components to Create**:
- `SkeletonChapterList`: 章节列表页骨架屏
- `SkeletonChapterDetail`: 章节详情页骨架屏（包含侧边栏）
- ErrorBoundary 组件（可复用通用模式）

## Risks / Trade-offs

### Risk 1: First-page load performance degradation
**Risk**: 客户端渲染可能导致首次访问比 SSR 慢

**Mitigation**:
- 使用 `hydrate = true` 确保首次访问仍进行 SSR
- 提供高质量的 HydrateFallback 骨架屏
- 优化 clientLoader 性能（并行请求、数据缓存）

### Risk 2: Authentication security concerns
**Risk**: 客户端认证可能不如服务端安全（JWT 存储在 localStorage）

**Mitigation**:
- JWT 已在登录时存储，现有安全措施保持不变
- 后端 API 仍验证每个请求的 token
- 401 错误立即重定向到登录页
- 考虑未来将 JWT 存储在 HTTP-only cookie（需架构升级）

### Risk 3: Client-side redirect flicker
**Risk**: 客户端重定向可能导致短暂的内容闪烁（显示内容后再重定向）

**Mitigation**:
- 在 clientLoader 中返回 `isLocked` 状态
- 在组件中尽早检查状态并重定向
- 渲染前检查：`if (isLocked) return null;` 避免渲染内容
- 考虑使用 `useEffect` + `replace: true` 减少闪烁

### Risk 4: Breaking infinite scroll on chapter list
**Risk**: 章节列表页使用无限滚动，迁移可能破坏现有功能

**Mitigation**:
- 保留 `useInfiniteScroll` hook 的使用
- 确保 clientLoader 返回的数据格式与之前一致
- 测试无限滚动在不同场景下的表现

### Trade-off: Complexity vs. Performance
**Trade-off**: 混合重定向策略（loader 检查 + 组件重定向）增加了代码复杂度，但提供了更好的性能和用户体验

**Rationale**: 性能和用户体验的提升值得这额外的复杂度，且模式可在其他页面复用

## Migration Plan

### Phase 1: Preparation
1. **Review existing implementations**: 研究已客户端化的页面（home, problems, courses）
2. **Create skeleton components**: 实现 `SkeletonChapterList`, `SkeletonChapterDetail`
3. **Verify API compatibility**: 确认所有 API 端点支持客户端调用（无需特殊 headers）

### Phase 2: Migrate chapter list page
1. Replace `loader` with `clientLoader` in `_layout.courses_.$courseId_.chapters/route.tsx`
2. Remove `withAuth` wrapper
3. Switch to `clientHttp` for all API calls
4. Add `HydrateFallback` and `ErrorBoundary`
5. Test infinite scroll functionality
6. Verify error handling and redirects

### Phase 3: Migrate chapter detail page
1. Replace `loader` with `clientLoader` in `_layout.courses_.$courseId_.chapters_.$chapterId/route.tsx`
2. Modify `unlock_status` check to return status instead of server-side redirect
3. Add client-side redirect logic in component (using `useNavigate`)
4. Keep existing `clientAction` for marking completion
5. Add `HydrateFallback` and `ErrorBoundary`
6. Test locked/unlocked scenarios
7. Verify side-effects (mark as in-progress)

### Phase 4: Migrate locked page
1. Check current implementation of `_layout.courses_.$courseId_.chapters_.$chapterId_.locked.tsx`
2. Migrate to `clientLoader` if needed
3. Test redirect flow from detail page

### Phase 5: Testing and validation
1. **Manual testing**:
   - Test all user flows (unlocked chapter, locked chapter, redirect)
   - Test error scenarios (401, 403, 404, 500)
   - Test performance (client-side navigation speed)
2. **Automated testing**: Update existing tests to work with clientLoader
3. **Performance monitoring**: Compare before/after metrics

### Rollback Strategy
- 每个 phase 都可以独立回滚（通过 git revert）
- 保留服务端 loader 代码作为注释，方便快速回滚
- 灰度发布：先在测试环境验证，再上生产

## Open Questions

1. **Locked page implementation**: 当前 locked 页的实现未确认，是否需要迁移？
   - **Action**: 在 Phase 4 前检查 locked 页代码

2. **Token storage location**: JWT token 存储在 localStorage 还是 cookie？
   - **Assumption**: `clientHttp` 已处理此逻辑，无需额外改动
   - **Verification**: 检查 `~/utils/http/client.ts` 实现

3. **Infinite scroll caching**: 客户端导航时，无限滚动的历史数据是否需要保留？
   - **Decision**: 暂时不保留（简单实现），可根据用户反馈优化

4. **Error boundary granularity**: 是否需要为不同错误类型提供不同的错误提示？
   - **Decision**: 先实现通用错误处理，后续根据需要细化
