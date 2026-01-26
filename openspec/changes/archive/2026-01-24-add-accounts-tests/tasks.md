# Implementation Tasks

## Setup Phase

- [x] Add `factory-boy` to `backend/pyproject.toml` dependencies
- [x] Run `uv sync` to install new dependency
- [x] Create `backend/accounts/tests/` directory structure
- [x] Delete/remove placeholder `backend/accounts/tests.py` file
- [x] Create `backend/accounts/tests/__init__.py` file

## Factory Setup

- [x] Create `backend/accounts/tests/factories.py` module
- [x] Implement `UserFactory` with:
  - Default attributes for valid user
  - `admin_user` trait for admin users
  - `with_st_number` trait for users with student numbers
  - `with_avatar` trait for users with avatars
- [x] Implement `MembershipTypeFactory` with:
  - Default active membership type
  - `inactive` trait for disabled types
- [x] Implement `SubscriptionFactory` with:
  - Default active subscription
  - `expired` trait for expired subscriptions
  - Auto-computed end_date based on membership_type.duration_days

## Model Tests

- [x] Create `backend/accounts/tests/test_models.py`
- [x] Test `User` model:
  - String representation includes st_number and username
  - `st_number` uniqueness constraint
  - `avatar` field accepts valid data
- [x] Test `MembershipType` model:
  - String representation returns name
  - `is_active` field defaults to True
- [x] Test `Subscription` model:
  - String representation includes user and membership type
  - `end_date` auto-calculated from `membership_type.duration_days`
  - `is_active` field defaults to True

## Serializer Tests

- [x] Create `backend/accounts/tests/test_serializers.py`
- [x] Test `RegisterUserSerializer`:
  - Valid registration creates user with hashed password
  - Duplicate `st_number` raises validation error
  - Password validation enforced (length, complexity)
  - Missing required fields return errors
- [x] Test `CustomTokenObtainPairSerializer`:
  - Login with username works
  - Login with st_number works
  - Invalid credentials return appropriate error
  - Inactive user cannot login
  - Token contains custom claims (username, st_number)
- [x] Test `LogoutSerializer`:
  - Valid refresh token accepted
  - Missing refresh token rejected
- [x] Test `UserSerializer`:
  - Read-only fields enforced (id, st_number)
  - `has_active_subscription` returns correct boolean
  - `current_subscription` returns subscription details if active
  - Update allows email, username, avatar
- [x] Test `ChangePasswordSerializer`:
  - Valid old password required
  - New password validated
  - Password hash updated on save
- [x] Test `MembershipTypeSerializer`:
  - All fields are read-only

## Permission Tests

- [x] Create `backend/accounts/tests/test_permissions.py`
- [x] Test `IsSubscriptionActive` permission:
  - Returns False for unauthenticated users
  - Returns False for users without subscription
  - Returns False for users with expired subscription
  - Returns True for users with active subscription

## Authentication View Tests

- [x] Create `backend/accounts/tests/test_auth_views.py`
- [x] Test `LoginView`:
  - Successful login returns access and refresh tokens
  - Login with username works
  - Login with st_number works
  - Failed login returns 401
  - Inactive user cannot login
  - IP address logged correctly
- [x] Test `RegisterView`:
  - Successful registration creates user and returns tokens
  - Duplicate st_number returns 400 error
  - Duplicate username returns 400 error
  - Invalid password returns 400 error
  - Transaction rolled back on error
  - IP address logged correctly
- [x] Test `LogoutView`:
  - Valid refresh token blacklisted
  - Invalid refresh token returns 400 error
  - Expired refresh token handled correctly
- [x] Test `TokenRefreshView` (DRF SimpleJWT):
  - Valid refresh token returns new access token
- [x] Test `TokenVerifyView` (DRF SimpleJWT):
  - Valid access token passes verification

## User View Tests

- [x] Create `backend/accounts/tests/test_user_views.py`
- [x] Test `MeView`:
  - Authenticated user can retrieve own profile
  - Response includes subscription info if active
  - Unauthenticated request returns 401
- [x] Test `UserUpdateView`:
  - User can update own profile (email, username, avatar)
  - Cannot update st_number (read-only)
  - Cannot update other users
  - Unauthenticated request returns 401
- [x] Test `UserListView`:
  - Admin can list all users
  - Non-admin request returns 403
  - Response includes user count
- [x] Test `UserDeleteView`:
  - Admin can delete user
  - Non-admin request returns 403
  - Delete is transaction-wrapped

## Membership View Tests

- [x] Create `backend/accounts/tests/test_membership_views.py`
- [x] Test `MembershipTypeListView`:
  - Returns only active membership types
  - Ordered by duration_days
  - No authentication required
  - Response includes all fields

## Password View Tests

- [x] Create `backend/accounts/tests/test_password_views.py`
- [x] Test `ChangePasswordView`:
  - Successful password change returns 200
  - Old password incorrect returns 400
  - New password validation enforced
  - User can login with new password after change
  - Cannot login with old password after change
  - Unauthenticated request returns 401

## Test Configuration

- [x] Create `backend/accounts/tests/conftest.py` for shared fixtures
- [x] Configure test database settings if needed
- [x] Add test runner configuration to `pyproject.toml`

## Verification

- [x] Run all tests: `uv run python manage.py test accounts.tests`
- [x] Verify all tests pass
- [x] Check test coverage (optional): `uv run coverage run manage.py test accounts.tests`
- [x] Document any test data seeding requirements

## Documentation

- [x] Add testing notes to `backend/accounts/README.md` (create if doesn't exist)
- [x] Document factory usage examples for future tests
