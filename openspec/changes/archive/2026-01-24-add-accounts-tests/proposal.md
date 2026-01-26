# Add Comprehensive Tests for accounts App

## Summary

Add comprehensive test coverage for the `accounts` Django app using factory_boy for test data management. Tests will be organized by functional feature into separate files for better maintainability.

## Motivation

The `accounts` app currently has minimal test coverage (only a placeholder `tests.py` file). This is a critical security and authentication module that handles:
- User registration and authentication (JWT-based)
- Password management
- User profile management
- Subscription/membership tracking
- Admin user management

Comprehensive tests are essential to ensure:
- Security vulnerabilities are caught early
- Authentication flows work correctly
- Edge cases are handled properly
- Future changes don't break existing functionality

## Proposed Changes

### 1. Add Test Dependencies
- Add `factory-boy` to `pyproject.toml` dependencies
- Leverage existing `Faker` dependency for realistic test data

### 2. Create Test Factory Module
- `tests/factories.py` - Factory Boy definitions for:
  - `UserFactory` - for creating test users with various states
  - `MembershipTypeFactory` - for membership types
  - `SubscriptionFactory` - for user subscriptions

### 3. Organize Tests by Functional Feature

Create separate test files under `tests/` directory:

| File | Purpose |
|------|---------|
| `test_models.py` | Model logic, custom methods, constraints |
| `test_serializers.py` | Serializer validation, create/update logic |
| `test_permissions.py` | Permission class behavior |
| `test_auth_views.py` | Login, Register, Logout, Token operations |
| `test_user_views.py` | Me, UserUpdate, UserList, UserDelete |
| `test_membership_views.py` | MembershipTypeListView |
| `test_password_views.py` | ChangePasswordView |

### 4. Test Coverage Goals

- **Unit Tests**: Model methods, serializer validation, permission checks
- **Integration Tests**: API endpoint behavior with authentication
- **Edge Cases**: Invalid inputs, duplicate data, permission denied scenarios
- **Success Paths**: Happy path validation for all operations

## Impact

### Affected Components
- `backend/accounts/tests/` - New test directory structure
- `backend/accounts/tests.py` - Will be removed/replaced
- `backend/pyproject.toml` - Add factory-boy dependency

### Non-Breaking Changes
- This is a pure addition; no existing behavior changes
- Existing tests (if any) continue to work

### Performance Impact
- Test execution time will increase but remains acceptable
- CI/CD pipeline will include comprehensive test coverage

## Alternatives Considered

1. **Keep single `tests.py` file**: Rejected because accounts app has complex, multi-faceted functionality that benefits from separation of concerns.

2. **Use pytest over unittest**: Rejected to maintain consistency with Django's default test framework and existing project conventions.

3. **Use model mommies instead of factory_boy**: Rejected because factory_boy is more mature, better documented, and integrates better with Faker.

## Open Questions

None - requirements are clear based on existing codebase structure.

## Related Changes

- May inform testing patterns for other backend apps (courses, commerce, etc.)
- Could establish a project-wide testing convention for future work
