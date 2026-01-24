# backend-testing Specification

## Purpose
TBD - created by archiving change add-accounts-tests. Update Purpose after archive.
## Requirements
### Requirement: accounts App Must Have Comprehensive Test Coverage

The `accounts` app MUST have comprehensive test coverage for all models, serializers, permissions, and views. Tests MUST use factory_boy for test data management and MUST be organized by functional feature.

#### Scenario: Factory Boy Setup

**GIVEN** the project has factory-boy installed
**WHEN** a developer writes tests for the accounts app
**THEN** factories MUST exist for:
- `UserFactory` - creates test User instances with optional admin/st_number/avatar traits
- `MembershipTypeFactory` - creates test MembershipType instances
- `SubscriptionFactory` - creates test Subscription instances with auto-calculated end_date

#### Scenario: User Model Tests

**GIVEN** a User instance created via UserFactory
**WHEN** accessing the user's string representation
**THEN** it MUST return the format `{st_number}-{username}`
**AND** st_number MUST be unique across users
**AND** avatar field MUST accept text data (base64 or URL)

#### Scenario: MembershipType Model Tests

**GIVEN** a MembershipType instance
**WHEN** accessing string representation
**THEN** it MUST return the membership name
**AND** is_active MUST default to True

#### Scenario: Subscription Model Tests

**GIVEN** a Subscription instance
**WHEN** created without an end_date
**THEN** end_date MUST be auto-calculated as start_date + membership_type.duration_days
**AND** string representation MUST return `{user.username} - {membership_type.name}`

#### Scenario: RegisterUserSerializer Validation

**GIVEN** a registration request with valid data
**WHEN** the serializer is validated and saved
**THEN** a User MUST be created with a hashed password
**AND** duplicate st_number MUST raise a ValidationError with message "该学号已被注册"
**AND** password validation MUST be enforced via Django's password validators

#### Scenario: Login Serializer Accepts Username or Student Number

**GIVEN** a user with username "testuser" and st_number "2024000001"
**WHEN** logging in with username="testuser" or username="2024000001"
**THEN** both attempts MUST succeed with correct password
**AND** the response token MUST contain custom claims for username and st_number
**AND** an inactive user MUST NOT be able to login

#### Scenario: Logout Serializer Validation

**GIVEN** a valid refresh token
**WHEN** the logout serializer is validated
**THEN** the refresh token MUST be accepted
**AND** a missing refresh token MUST be rejected

#### Scenario: UserSerializer Subscription Fields

**GIVEN** a user with an active subscription
**WHEN** the user is serialized
**THEN** has_active_subscription MUST return True
**AND** current_subscription MUST contain the subscription details
**AND** id and st_number MUST be read-only fields

#### Scenario: Change Password Serializer

**GIVEN** an authenticated user
**WHEN** changing password with correct old_password
**THEN** the new password MUST be hashed and saved
**AND** the old password MUST no longer work for authentication
**AND** incorrect old_password MUST raise ValidationError

#### Scenario: IsSubscriptionActive Permission

**GIVEN** a permission check for IsSubscriptionActive
**WHEN** the user is unauthenticated
**THEN** permission MUST be denied
**WHEN** the user has no subscription
**THEN** permission MUST be denied
**WHEN** the user has an expired subscription
**THEN** permission MUST be denied
**WHEN** the user has an active subscription (end_date > now)
**THEN** permission MUST be granted

#### Scenario: Login View Success and Failure

**GIVEN** a registered user
**WHEN** posting to /auth/auth/login with correct credentials
**THEN** response status MUST be 200
**AND** response MUST contain access and refresh tokens
**AND** response MUST contain user_id, username, st_number
**WHEN** posting with incorrect credentials
**THEN** response status MUST be 401
**AND** IP address MUST be logged

#### Scenario: Register View Success and Validation

**GIVEN** a registration request with unique username and st_number
**WHEN** posting to /auth/auth/register
**THEN** a new user MUST be created
**AND** response status MUST be 201
**AND** response MUST contain access and refresh tokens
**AND** transaction MUST be rolled back on validation error
**WHEN** st_number already exists
**THEN** response status MUST be 400
**AND** error message MUST indicate duplicate st_number

#### Scenario: Logout View Token Blacklisting

**GIVEN** an authenticated user with a valid refresh token
**WHEN** posting to /auth/auth/logout with the refresh token
**THEN** the refresh token MUST be blacklisted
**AND** response status MUST be 200
**AND** invalid/expired tokens MUST return 400

#### Scenario: Me View Authentication Required

**GIVEN** an authenticated user
**WHEN** getting /auth/auth/me
**THEN** response status MUST be 200
**AND** response MUST contain user profile data
**AND** response MUST include active subscription info if present
**WHEN** unauthenticated
**THEN** response status MUST be 401

#### Scenario: User Update View

**GIVEN** an authenticated user
**WHEN** patching /auth/users/me/update/ with valid data
**THEN** email, username, and avatar MAY be updated
**AND** st_number MUST NOT be updatable (read-only)
**AND** user MAY NOT update other users' profiles
**AND** unauthenticated requests MUST return 401

#### Scenario: User List View Admin Only

**GIVEN** an admin user
**WHEN** getting /auth/users
**THEN** response status MUST be 200
**AND** response MUST contain list of all users
**WHEN** requested by non-admin user
**THEN** response status MUST be 403

#### Scenario: User Delete View Admin Only

**GIVEN** an admin user
**WHEN** deleting /auth/users/{id}/delete/
**THEN** the user MUST be deleted
**AND** response status MUST be 204
**WHEN** requested by non-admin user
**THEN** response status MUST be 403

#### Scenario: Membership Type List View

**GIVEN** multiple membership types (active and inactive)
**WHEN** getting /auth/membership-types/
**THEN** response status MUST be 200
**AND** only active membership types (is_active=True) MUST be returned
**AND** results MUST be ordered by duration_days
**AND** no authentication MUST be required

#### Scenario: Change Password View

**GIVEN** an authenticated user
**WHEN** posting to /auth/users/me/change-password/ with correct old_password
**THEN** password MUST be updated
**AND** response status MUST be 200
**AND** user MUST be able to login with new password
**AND** user MUST NOT be able to login with old password
**WHEN** old_password is incorrect
**THEN** response status MUST be 400
**AND** error MUST indicate "旧密码错误"

### Requirement: Tests Must Be Organized by Functional Feature

Tests for the accounts app MUST be organized into separate files by functional area:

#### Scenario: Test File Organization

**GIVEN** the accounts/tests directory
**WHEN** browsing test files
**THEN** the following files MUST exist:
- `test_models.py` - Model behavior tests
- `test_serializers.py` - Serializer validation tests
- `test_permissions.py` - Permission class tests
- `test_auth_views.py` - Login, Register, Logout, Token endpoints
- `test_user_views.py` - Me, Update, List, Delete endpoints
- `test_membership_views.py` - Membership type endpoints
- `test_password_views.py` - Password change endpoint
**AND** `factories.py` MUST contain all factory definitions

### Requirement: Test Data Must Be Isolated

Each test MUST create its own test data and MUST NOT depend on data from other tests.

#### Scenario: Test Isolation

**GIVEN** multiple tests in the same test class
**WHEN** tests run in any order
**THEN** each test MUST use factory-created data
**AND** tests MUST NOT share database state
**AND** tests MUST pass when run individually or as a suite

### Requirement: Factory Boy Must Be Used for Test Data

All test data creation MUST use factory_boy factories instead of direct model instantiation or manual data creation.

#### Scenario: Factory Usage Pattern

**GIVEN** a test that requires a user
**WHEN** creating test data
**THEN** UserFactory() MUST be used instead of User.objects.create()
**AND** factory traits MAY be used for specific user types (admin, with_st_number, etc.)

