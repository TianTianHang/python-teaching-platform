## Overview

This change is a technical migration (implementation refactoring) with no changes to functional requirements. The pages being migrated (homepage, course list, course detail) will continue to provide the same functionality - only the data fetching mechanism changes from server-side SSR to client-side.

## ADDED Requirements

（无新增需求）

## MODIFIED Requirements

（无需求变更 - 仅有实现方式改变）

## REMOVED Requirements

（无移除需求）

## Technical Implementation Note

This migration follows the established pattern in `client-side-backend-migration-guide`:
- Replace `loader` + `createHttp` with `useEffect` + `clientHttp`
- Replace `action` with client-side `clientHttp.post()`
- Handle 401 errors with automatic token refresh via `clientHttp` interceptor
- Display loading states via existing Skeleton components

The user-facing behavior remains identical to the current SSR implementation.