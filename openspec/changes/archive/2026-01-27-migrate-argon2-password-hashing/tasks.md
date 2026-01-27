# Tasks: Migrate Django Password Hashing to Argon2

## Phase 1: Implementation

### 1. Add argon2-cffi dependency
- [x] Add `argon2-cffi>=23.1.0` to `backend/pyproject.toml` dependencies
- [x] Run `uv sync` to install the new dependency
- [x] Verify installation with `uv pip list | grep argon2`

**Validation**: Package appears in installed packages list

### 2. Configure PASSWORD_HASHERS in Django settings
- [x] Add `PASSWORD_HASHERS` setting to `backend/core/settings.py`
- [x] Place `Argon2PasswordHasher` first in the list
- [x] Include `PBKDF2PasswordHasher` for backward compatibility

**Validation**: Setting is properly formatted and contains all required hashers

### 3. Create password hashing tests
- [x] Add test case for new user registration using Argon2id
- [x] Add test case for existing PBKDF2 user login (backward compatibility)
- [x] Add test case for automatic password migration on login
- [x] Add test case for password change using Argon2id

**Validation**: All new tests pass

## Phase 2: Testing

### 4. Run existing test suite
- [x] Run `uv run python manage.py test` to verify no regressions
- [x] Fix any test failures related to password hashing

**Validation**: All existing tests pass

### 5. Manual testing with test database
- [x] Create a test user with PBKDF2 hash (simulate existing user)
- [x] Verify login works with PBKDF2 hash
- [x] Verify password hash is updated to Argon2id after login
- [x] Create a new user and verify Argon2id is used
- [x] Change password and verify Argon2id is used

**Validation**: All manual tests pass

### 6. Performance testing (optional but recommended)
- [x] Run load test on login endpoint before change
- [x] Run load test on login endpoint after change
- [x] Compare p50, p95, p99 latencies

**Validation**: Performance is not significantly degraded

## Phase 3: Deployment

### 7. Update documentation
- [x] Update `CLAUDE.md` or project docs to reflect Argon2 usage
- [x] Document password hash migration behavior

**Validation**: Documentation is accurate

### 8. Deploy to development environment
- [x] Deploy changes to dev/staging environment
- [x] Verify new users get Argon2id hashes
- [x] Verify existing users can still login

**Validation**: No issues in staging

### 9. Deploy to production
- [x] Deploy changes to production
- [x] Monitor login success rate and latency
- [x] Monitor error logs for authentication failures

**Validation**: Production metrics are healthy

## Phase 4: Verification (Post-Deployment)

### 10. Monitor hash migration
- [x] Query database to check distribution of password hash algorithms
- [x] Track migration rate as users log in
- [x] Consider communication plan for inactive users (optional)

**Validation**: Migration is proceeding as expected

---

## Dependencies

- **Task 2 depends on Task 1**: PASSWORD_HASHERS configuration requires argon2-cffi to be installed
- **Task 4 depends on Task 2**: Tests need the configuration to be in place
- **Task 5 depends on Task 4**: Manual testing should come after automated tests pass
- **Task 6 can run in parallel with Task 5**: If you have a separate performance testing environment
- **Task 8 depends on all previous tasks**: Deployment requires completion of implementation and testing

## Parallelizable Work

- Tasks 1 and 2 (test writing) can be done in parallel with the implementation
- Documentation (Task 7) can be written anytime
- Performance testing (Task 6) can run in parallel with other testing if resources allow
