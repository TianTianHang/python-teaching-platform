# Authentication Specification

## ADDED Requirements

### Requirement: Password Hashing with Argon2id

New user passwords MUST be hashed using the Argon2id algorithm (OWASP recommended variant) with Django's default parameters:
- time_cost: 2
- memory_cost: 512 KB
- parallelism: 2

The password hash MUST be stored in the database using Django's standard format with the algorithm identifier prefix.

#### Scenario: New user registration uses Argon2id hashing

**Given** a new user registers with username "testuser" and password "SecurePass123!"
**When** the user account is created
**Then** the password field in the database MUST start with "argon2$argon2id"
**And** the password MUST be verifiable using Django's `check_password()` method

#### Scenario: Password change uses Argon2id hashing

**Given** an existing user with any password hash algorithm
**When** the user successfully changes their password
**Then** the new password MUST be hashed with Argon2id
**And** the password field in the database MUST start with "argon2$argon2id"

### Requirement: Backward Compatible Password Verification

The system MUST continue to accept passwords hashed with legacy algorithms (PBKDF2SHA256, PBKDF2) for existing users. These hashes MUST be verifiable without requiring users to reset their passwords.

#### Scenario: Existing user with PBKDF2 hash can login

**Given** an existing user whose password is hashed with PBKDF2SHA256
**When** the user logs in with correct credentials
**Then** the login MUST succeed
**And** the user MUST receive a valid JWT token

### Requirement: Automatic Password Migration

When a user with a legacy password hash (PBKDF2SHA256 or PBKDF2) successfully authenticates, the system MUST automatically rehash their password using Argon2id and update the database. This migration MUST happen transparently without requiring additional action from the user.

#### Scenario: PBKDF2 password auto-migrates to Argon2id on login

**Given** an existing user whose password is hashed with PBKDF2SHA256
**When** the user successfully logs in
**Then** the password field in the database MUST start with "argon2$argon2id" after login
**And** subsequent logins MUST verify using the new Argon2id hash

#### Scenario: Multiple legacy hash algorithms are supported

**Given** existing users with passwords hashed using different algorithms (PBKDF2SHA256, PBKDF2)
**When** these users successfully login
**Then** all users MUST be able to authenticate
**And** all passwords MUST be migrated to Argon2id after successful login

### Requirement: Password Hasher Configuration

The `PASSWORD_HASHERS` setting in Django settings MUST be configured with Argon2 as the preferred (first) hasher, followed by legacy hashers for backward compatibility.

#### Scenario: PASSWORD_HASHERS setting includes Argon2 first

**Given** the Django settings file
**When** reading the `PASSWORD_HASHERS` configuration
**Then** `django.contrib.auth.hashers.Argon2PasswordHasher` MUST be the first element
**And** `django.contrib.auth.hashers.PBKDF2SHA256PasswordHasher` MUST be included
**And** `django.contrib.auth.hashers.PBKDF2PasswordHasher` MUST be included

### Requirement: Argon2 Dependency Availability

The `argon2-cffi` package MUST be available in the runtime environment for Argon2 password hashing to function. The package version MUST be >= 23.1.0.

#### Scenario: Argon2 package is installed

**Given** the Python environment
**When** checking installed packages
**Then** `argon2-cffi` MUST be present in the dependency list
**And** the version MUST be >= 23.1.0

### Requirement: User Authentication Performance

Login endpoint performance MUST NOT degrade when using Argon2id password hashing. The target latency for login under normal load SHOULD remain below 500ms (p95).

#### Scenario: Login performance with Argon2 is acceptable

**Given** a system configured with Argon2 password hashing
**When** measuring login endpoint latency under normal load
**Then** the p95 latency SHOULD be below 500ms
**And** login success rate SHOULD be >= 99.9%

#### Scenario: Login performance with PBKDF2 legacy hash

**Given** a user with a PBKDF2 password hash
**When** measuring login endpoint latency including migration
**Then** the login SHOULD succeed within a reasonable time frame
**And** the p95 latency SHOULD be below 1000ms (includes rehashing overhead)
