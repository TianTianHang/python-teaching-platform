## 1. Modify Server-side Loader

- [x] 1.1 Simplify `_layout.tsx` server loader to only check session authentication
- [x] 1.2 Return user data from session cache if valid
- [x] 1.3 Return `needsRefresh: true` if cache expired or missing

## 2. Add Client-side Loader

- [x] 2.1 Add `clientLoader` function to `_layout.tsx`
- [x] 2.2 Read server response (user + needsRefresh)
- [x] 2.3 If `needsRefresh=true`, call auth/me API
- [x] 2.4 If auth/me succeeds, call auth.set-session to update session
- [x] 2.5 Return user data
- [x] 2.6 Set `clientLoader.hydrate = true`

## 3. Update Type Definitions

- [x] 3.1 Update Route.ComponentProps to handle new loader return type

## 4. Verify

- [x] 4.1 Run typecheck: `cd frontend/web-student && pnpm run typecheck`
- [ ] 4.2 Test page load in browser, check network for reduced API calls (需要手动测试)