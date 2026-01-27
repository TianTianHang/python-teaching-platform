# Design: Argon2 Password Hashing Migration

## Overview

This document describes the technical design for migrating Django's password hashing from PBKDF2-SHA256 to Argon2id.

## Architecture

### Current Architecture

```
User Registration/Login Request
         |
         v
Django Auth System
         |
         v
PBKDF2SHA256PasswordHasher (600,000 iterations)
         |
         v
Password Hash (stored in database)
```

### Target Architecture

```
User Registration/Login Request
         |
         v
Django Auth System
         |
         +-> Argon2PasswordHasher (preferred, new users)
         |
         +-> PBKDF2SHA256PasswordHasher (fallback, existing users)
         |
         v
Password Hash (stored in database)
         |
         v
Automatic rehash on next successful login (if using old hasher)
```

## Technical Details

### Django Password Hasher Configuration

Django supports multiple password hashers simultaneously through the `PASSWORD_HASHERS` setting. The first hasher in the list is used for new passwords, while all hashers in the list can verify existing passwords.

**Current (implicit) Configuration:**
```python
# Django default (not explicitly set in settings.py)
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2SHA256PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]
```

**New Configuration:**
```python
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # First = preferred
    'django.contrib.auth.hashers.PBKDF2SHA256PasswordHasher',  # Keep for existing hashes
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]
```

### Argon2 Variant Selection

| Variant | Description | Recommendation |
|---------|-------------|----------------|
| Argon2d | Data-dependent, faster but vulnerable to side-channel attacks | No |
| Argon2i | Data-independent, optimized against side-channel attacks | No |
| Argon2id | Hybrid approach (default in Django) | **Yes (OWASP recommended)** |

Django's `Argon2PasswordHasher` uses Argon2id by default with sensible defaults:
- **time_cost**: 2 (number of iterations)
- **memory_cost**: 512 (memory in KB)
- **parallelism**: 2 (number of threads)

### Automatic Password Migration

Django provides built-in automatic password migration:

1. User logs in with old PBKDF2 hash
2. Django verifies password using PBKDF2 hasher
3. If verification succeeds and a "better" hasher is available (Argon2 is first in list), Django automatically:
   - Rehashes the password with Argon2
   - Updates the database with new hash

This happens transparently - no code changes needed beyond the `PASSWORD_HASHERS` setting.

### Database Schema

**No changes required.** The password field stores the hash as a string prefixed with the algorithm identifier:

```
# PBKDF2 hash format
pbkdf2_sha256$600000$salt$hash

# Argon2 hash format
argon2$argon2id$v=19$m=512,t=2,p=2$salt$hash
```

### Dependency Management

**New dependency to add to `pyproject.toml`:**

```toml
[project]
dependencies = [
    # ... existing dependencies
    "argon2-cffi>=23.1.0",  # Argon2 password hashing
]
```

## Testing Strategy

### Test Scenarios

1. **New User Registration**
   - Verify new users' passwords are hashed with Argon2
   - Check hash format starts with `argon2$argon2id`

2. **Existing User Login (PBKDF2 hash)**
   - Verify users with old PBKDF2 hashes can still login
   - Verify password is rehashed to Argon2 after successful login
   - Verify database is updated with new Argon2 hash

3. **Password Change**
   - Verify password changes use Argon2 hashing

4. **Backward Compatibility**
   - Verify PBKDF2 hashes still validate correctly
   - Verify no user is locked out during migration

5. **Performance**
   - Measure login time with Argon2
   - Compare with PBKDF2 baseline

### Test Files to Update

- `backend/accounts/tests/test_auth_views.py` - Add tests for Argon2 hashing
- `backend/accounts/tests/test_password_views.py` - Verify password change uses Argon2

## Security Considerations

### Threat Model

| Threat | PBKDF2 | Argon2id | Notes |
|--------|--------|----------|-------|
| Brute force (CPU) | Moderate protection | Better protection | Argon2 more efficient per security unit |
| Brute force (GPU) | Vulnerable | Resistant | Memory-hard design |
| Brute force (ASIC) | Vulnerable | Resistant | Memory-hard design |
| Side-channel attacks | Resistant | Resistant | Argon2id specifically designed for this |

### Parameter Selection

The default Django parameters provide good security for most applications:

```python
# Django Argon2PasswordHasher defaults
time_cost = 2        # Iterations (adjust based on server CPU)
memory_cost = 512    # KB of RAM (512 KB = 0.5 MB)
parallelism = 2      # Threads (should match typical CPU core count)
```

For production, consider:
- **Increase time_cost** if login latency is acceptable (e.g., to 3 or 4)
- **Increase memory_cost** if server has sufficient RAM (e.g., to 1024 KB)
- Monitor login performance and adjust accordingly

## Rollout Plan

### Phase 1: Development
1. Add `argon2-cffi` dependency
2. Configure `PASSWORD_HASHERS` in settings
3. Add tests for Argon2 behavior
4. Verify all tests pass

### Phase 2: Testing
1. Run load tests on login endpoint
2. Compare performance metrics
3. Verify backward compatibility with existing user database

### Phase 3: Deployment
1. Deploy to staging environment
2. Monitor login success rates
3. Deploy to production
4. Monitor metrics for 48 hours

### Phase 4: Verification
1. Check that new users get Argon2 hashes
2. Monitor automatic migration rate (hashes updated on login)
3. Consider forced password reset for inactive users (optional)

## Rollback Plan

If issues occur:

1. **Revert `PASSWORD_HASHERS` setting** - Remove Argon2 from first position
2. **Keep `argon2-cffi` dependency** - Needed to verify existing Argon2 hashes
3. **No data migration needed** - PBKDF2 hashes remain valid

The rollback is safe because Django maintains support for all configured hashers.

## Monitoring

### Key Metrics to Track

1. **Login success rate** - Should remain at ~100%
2. **Login latency (p50, p95, p99)** - Should not increase significantly
3. **Hash algorithm distribution** - Track migration from PBKDF2 to Argon2
4. **Error rate in authentication logs** - Should not increase

### Dashboard Queries

```sql
-- Count users by password hash algorithm
SELECT
    SUBSTRING(password FROM 1 FOR POSITION('$' IN password)) AS algorithm,
    COUNT(*) AS user_count
FROM accounts_user
GROUP BY algorithm;
```

## Open Questions

See [proposal.md](proposal.md) for open questions and recommendations.
