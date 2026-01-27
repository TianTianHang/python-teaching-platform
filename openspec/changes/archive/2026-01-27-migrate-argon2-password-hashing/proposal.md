# Proposal: Migrate Django Password Hashing to Argon2

## Summary

Migrate Django's password hashing algorithm from the default PBKDF2-SHA256 to Argon2, which is the current industry standard recommended by OWASP and NIST for password hashing. This change will improve security and potentially reduce login endpoint latency.

## Motivation

### Current State
Django 5.2.7 uses PBKDF2-SHA256 as the default password hasher with 600,000 iterations. This is secure but computationally expensive, contributing to the known login endpoint performance issue (4s+ latency under high load).

### Problems
1. **Performance**: PBKDF2 is CPU-intensive and can cause slow login times under load
2. **Security**: While PBKDF2 is secure, Argon2 is the current OWASP recommendation (winner of Password Hashing Competition 2015)
3. **GPU/ASIC Resistance**: Argon2 is designed to be memory-hard, making it more resistant against GPU/ASIC attacks

### Benefits
- Better resistance against parallel attacks (GPU/ASIC)
- Potentially faster authentication under high load
- Alignment with current security best practices
- Still backward compatible with existing PBKDF2 hashes

## Proposed Solution

### High-Level Approach
1. Configure Django to use Argon2 as the preferred password hasher
2. Keep PBKDF2 as a fallback for existing password hashes
3. Implement automatic migration: users' passwords will be rehashed with Argon2 on next successful login
4. Add comprehensive tests to ensure backward compatibility

### Implementation Scope
- **In Scope**:
  - Update Django settings to use Argon2 as the default hasher
  - Add `argon2-cffi` dependency
  - Add tests for password hashing and migration
  - Update documentation

- **Out of Scope**:
  - Forced password rehash for all users (automatic migration on login is sufficient)
  - Changes to password validation rules
  - Frontend changes (this is a backend-only change)

## Affected Capabilities

This change modifies the **authentication** capability by upgrading the password hashing algorithm.

### New Capabilities
None - this is a security enhancement to existing functionality

### Modified Capabilities
- `authentication`: Password hashing will use Argon2 instead of PBKDF2

## Dependencies

- **Package Dependency**: `argon2-cffi` (Python binding for Argon2)
- **Django Version**: Django 5.2.7 (already supports Argon2 out of the box)

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Argon2 not available in production environment | Low | High | Add check for argon2-cffi availability, fallback to PBKDF2 |
| Existing users unable to login | Low | Critical | Keep PBKDF2 in PASSWORD_HASHERS list for backward compatibility |
| Performance regression (Argon2 slower than expected) | Low | Medium | Configurable time cost parameter; can tune after testing |

## Open Questions

1. **Argon2 variant**: Should we use Argon2i (optimized against side-channel attacks) or Argon2id (hybrid approach, recommended by OWASP)?
   - **Recommendation**: Argon2id (OWASP recommendation)

2. **Time cost parameter**: What value should we use for the time cost?
   - **Recommendation**: Start with Django's default (2), adjust based on load testing

3. **Memory cost**: How much memory should Argon2 use per hash?
   - **Recommendation**: Django default (512 KB) is reasonable for most applications

## Success Criteria

1. New user registrations use Argon2 password hashing
2. Existing users with PBKDF2 hashes can still login successfully
3. After successful login, user's password is automatically rehashed with Argon2
4. All existing tests pass
5. New tests verify Argon2 hashing behavior
6. Login endpoint performance is not degraded

## Related Changes

None - this is a standalone security enhancement.
