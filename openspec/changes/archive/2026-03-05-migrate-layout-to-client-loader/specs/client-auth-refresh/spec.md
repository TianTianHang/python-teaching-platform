## ADDED Requirements

### Requirement: Client-side auth refresh
The system SHALL allow the client to check session cache validity and refresh user data when needed after hydration.

#### Scenario: Session cache valid
- **WHEN** user visits a page with valid session cache (within 15 minutes)
- **THEN** server returns cached user data without calling auth/me API
- **AND** client uses the cached data directly

#### Scenario: Session cache expired
- **WHEN** user visits a page with expired session cache (after 15 minutes)
- **THEN** server returns needsRefresh=true without user data
- **AND** client calls auth/me to get fresh user data
- **AND** client calls auth.set-session to update session cache
- **AND** client uses the fresh user data

#### Scenario: No session cache
- **WHEN** user visits a page with no session cache
- **THEN** server returns needsRefresh=true without user data
- **AND** client calls auth/me to get user data
- **AND** client calls auth.set-session to set session cache
- **AND** client uses the user data