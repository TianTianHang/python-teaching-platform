# HTTP Connection Pool Specification

## ADDED Requirements

### Requirement: TCP Connection Reuse
The SSR service SHALL maintain a pool of reusable TCP connections to the backend API, enabling Keep-Alive to avoid repeated TCP handshakes for subsequent requests.

#### Scenario: Connection Reuse Across Multiple Requests
- **WHEN** the SSR service makes multiple HTTP requests to the same backend host
- **THEN** the system SHALL reuse existing TCP connections when available
- **AND** SHALL NOT create a new TCP connection for each request

#### Scenario: First Request Creates New Connection
- **WHEN** no idle connection is available in the pool
- **THEN** the system SHALL establish a new TCP connection
- **AND** SHALL add it to the connection pool for future reuse

### Requirement: Connection Pool Configuration
The system SHALL provide configurable connection pool parameters with sensible defaults for optimal performance in a PM2 cluster environment.

#### Scenario: Default Connection Pool Parameters
- **WHEN** the SSR service starts
- **THEN** the system SHALL configure `maxSockets` to 50
- **AND** SHALL configure `maxFreeSockets` to 10
- **AND** SHALL enable `keepAlive` to true
- **AND** SHALL configure `keepAliveMsecs` to 1000
- **AND** SHALL configure socket `timeout` to 30000

#### Scenario: Connection Limit Per Process
- **WHEN** concurrent requests exceed `maxSockets` limit
- **THEN** the system SHALL queue additional requests
- **AND** SHALL process them as connections become available
- **AND** SHALL NOT create more than `maxSockets` connections per target host

### Requirement: Server-Side Only
The HTTP connection pool SHALL be active only in the server-side SSR environment and MUST NOT affect client-side browser behavior.

#### Scenario: Agent Not Used in Browser
- **WHEN** code runs in the browser environment
- **THEN** the system SHALL NOT create HTTP Agent instances
- **AND** SHALL rely on the browser's built-in connection management

#### Scenario: Agent Created in SSR
- **WHEN** code runs in the SSR server environment
- **THEN** the system SHALL create global HTTP/HTTPS Agent instances
- **AND** SHALL apply them to all Axios requests

### Requirement: Automatic Connection Cleanup
The system SHALL automatically manage connection lifecycle, closing idle connections after timeout and handling stale connections.

#### Scenario: Idle Connection Timeout
- **WHEN** a connection remains idle longer than the configured timeout
- **THEN** the system SHALL close the connection
- **AND** SHALL remove it from the connection pool

#### Scenario: Stale Connection Detection
- **WHEN** a connection becomes stale (e.g., backend restart)
- **THEN** the system SHALL detect the failure via Keep-Alive probe
- **AND** SHALL close the stale connection
- **AND** SHALL establish a new connection for the next request

### Requirement: Backward Compatibility
The connection pool implementation SHALL NOT break existing functionality or require changes to loader code.

#### Scenario: Existing Loaders Work Without Modification
- **WHEN** existing loader functions use `createHttp(request)`
- **THEN** the system SHALL automatically use the connection pool
- **AND** SHALL NOT require any code changes in loaders

#### Scenario: Existing Auth Flow Unchanged
- **WHEN** HTTP requests include authentication headers
- **THEN** the connection pool SHALL NOT interfere with JWT token handling
- **AND** SHALL NOT affect the 401 refresh flow
