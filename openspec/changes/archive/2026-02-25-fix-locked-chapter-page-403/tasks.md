## 1. Backend Service Enhancement

- [x] 1.1 Update `ChapterUnlockService.get_unlock_status()` to return chapter information
- [x] 1.2 Modify response data structure to include `chapter` field
- [x] 1.3 Ensure no additional database queries are executed
- [x] 1.4 Verify existing caching mechanism still works

## 2. Backend Test Updates

- [x] 2.1 Update test cases for `get_unlock_status()` in `test_chapter_unlock_service.py`
- [x] 2.2 Add test scenarios for the new `chapter` field
- [x] 2.3 Run backend tests: `cd backend && uv run python manage.py test courses.tests.test_chapter_unlock_service`
- [x] 2.4 Verify no existing tests are broken

## 3. Frontend Type Definitions

- [x] 3.1 Update `ChapterUnlockStatus` interface in `frontend/web-student/app/types/course.ts`
- [x] 3.2 Add optional `chapter` field with correct TypeScript types
- [x] 3.3 Run type checking: `cd frontend/web-student && pnpm run typecheck`
- [x] 3.4 Verify type safety with existing code

## 4. Frontend Route Update

- [x] 4.1 Modify `locked.tsx` loader to use only `unlock_status` API
- [x] 4.2 Remove `retrieve` API call from locked route loader
- [x] 4.3 Update data fetching logic to use chapter info from response
- [ ] 4.4 Test both locked and unlocked chapter scenarios

## 5. Integration Testing

- [ ] 5.1 Test locked chapter page from user interface
- [ ] 5.2 Verify chapter information displays correctly
- [ ] 5.3 Check unlock status messages and prerequisites
- [ ] 5.4 Test with different unlock condition types

## 6. Performance Verification

- [ ] 6.1 Compare API response times before and after changes
- [ ] 6.2 Verify database query count remains the same
- [ ] 6.3 Test cache behavior with repeated calls
- [ ] 6.4 Check for any memory leaks or increased usage
