# backend-testing Specification Delta: Courses Admin Tests

## ADDED Requirements

### Requirement: courses App Admin Interface Must Have Comprehensive Test Coverage

All admin customizations and import/export functionality in the `courses` app MUST have comprehensive test coverage with at least 80 test cases covering all admin functionality.

#### Scenario: Course Admin Coverage

**GIVEN** CourseAdmin in courses/admin.py
**WHEN** admin tests are written
**THEN** tests MUST cover:
- **Git Repository Import**:
  - Valid repository import with URL validation
  - Invalid URL handling (malformed, unreachable)
  - Branch error handling (non-existent branch)
  - Import conflict resolution
  - Statistics tracking during import
  - Repository access permission verification
  - Large repository handling
  - Network timeout handling

#### Scenario: Problem Admin Coverage

**GIVEN** ProblemAdmin in courses/admin.py
**WHEN** admin tests are written
**THEN** tests MUST cover:
- **Excel Import with Multiple Sheets**:
  - Valid Excel file with proper format
  - Sheet validation and data extraction
  - Duplicate title prevention
  - Invalid JSON parsing in fill-blank problems
  - Missing required field handling
  - Data type validation
  - Large file performance
  - Batch creation integrity
- **Excel Export**:
  - Export format validation
  - Data integrity verification
  - Export with relationships
  - Export filtering options
  - File encoding handling

#### Scenario: Chapter Admin Coverage

**GIVEN** ChapterAdmin in courses/admin.py
**WHEN** admin tests are written
**THEN** tests MUST cover:
- **Excel Import**:
  - Order conflict detection
  - Chapter order uniqueness
  - Course association validation
  - Bulk chapter operations
- **Excel Export**:
  - Export with ordering preservation
  - Chapter inclusion in course export

#### Scenario: Exam Admin Coverage

**GIVEN** ExamProblemAdmin, ExamSubmissionAdmin, and ExamAnswerAdmin
**WHEN** admin tests are written
**THEN** tests MUST cover:
- **ExamProblemAdmin**:
  - Problem assignment to exams
  - Problem type validation (choice/fillblank only)
  - Score minimum validation (must be > 0)
  - Order validation within exam
  - Duplicate problem prevention
- **ExamSubmissionAdmin**:
  - Submission review functionality
  - Status filtering in admin list
  - Score calculations display
  - One-submission enforcement
- **ExamAnswerAdmin**:
  - Answer review interface
  - Correctness display logic
  - Score breakdown visualization
  - Percentage-based scoring

#### Scenario: Admin Form Validation Testing

**GIVEN** all admin forms
**WHEN** admin tests are written
**THEN** tests MUST cover:
- **Field Validation**:
  - Required field validation
  - Field length constraints
  - Data type validation
  - Choice field validation
  - Unique constraint validation
- **Custom Clean Methods**:
  - Business rule validation
  - Cross-field validation
  - Data transformation validation
- **Model Integration**:
  - Model clean method execution
  - Database constraint enforcement
  - Cascade behavior validation

#### Scenario: Custom Admin Actions Testing

**GIVEN** all custom admin actions
**WHEN** admin tests are written
**THEN** tests MUST cover:
- **Bulk Operations**:
  - Bulk delete with cascade behavior
  - Bulk publish/unpublish
  - Bulk archive
  - Permission validation for bulk actions
- **Custom Actions**:
  - Action execution logic
  - Action parameter validation
  - Action success feedback
  - Action error handling
  - Action performance with large datasets

#### Scenario: Admin Template Testing

**GIVEN** admin template customization
**WHEN** admin tests are written
**THEN** tests MUST cover:
- **List View Customization**:
  - Custom column display
  - Filtering functionality
  - Search functionality
  - Pagination
  - Actions column
- **Detail View Customization**:
  - Field display order
  - Read-only field handling
  - Inline formsets
  - Related objects display
- **Filter Functionality**:
  - Date range filters
  - Status filters
  - Type filters
  - Custom filters

#### Scenario: Admin Performance Testing

**GIVEN** admin interface performance concerns
**WHEN** admin tests are written
**THEN** tests MUST cover:
- **Large Dataset Handling**:
  - List view pagination performance
  - Search performance with large datasets
  - Filter performance
- **Complex Operations**:
  - Bulk operation performance
  - Export performance
  - Import performance
  - File upload handling

#### Scenario: Admin Security Testing

**GIVEN** admin interface security
**WHEN** admin tests are written
**THEN** tests MUST cover:
- **Permission Enforcement**:
  - Staff-only access
  - Object-level permissions
  - Action-level permissions
- **Input Sanitization**:
  - XSS prevention in forms
  - SQL injection prevention
  - CSRF protection
- **Data Exposure**:
  - Sensitive field handling
  - Field-level permissions
  - Audit logging

## Success Metrics

1. All admin customizations have test coverage
2. Total test count ≥ 80
3. All import/export functionality is tested
4. All form validations work correctly
5. All custom actions work as expected
6. Admin templates render correctly
7. Performance requirements are met
8. Security requirements are enforced
9. Run `manage.py test courses.tests.test_admin` with no failures

### Requirement: Admin Tests Must Test Real Admin Functionality

Admin tests MUST test actual Django admin functionality rather than just model methods.

#### Scenario: Admin Client Usage

**GIVEN** the admin test suite
**WHEN** running tests
**THEN** all tests MUST use:
- `django.contrib.admin.site` for direct testing
- Admin URL testing (e.g., `/admin/courses/course/`)
- Admin form submission testing
- Admin view testing with test client
- Admin template rendering verification

#### Scenario: File Upload Testing

**GIVEN** admin file upload functionality
**WHEN** admin tests are written
**THEN** tests MUST cover:
- **Excel File Upload**:
  - Valid file upload with proper format
  - Invalid file format handling
  - Large file handling
  - Corrupted file handling
- **Git Repository Import**:
  - URL validation
  - Repository access testing
  - Branch specification testing

#### Scenario: Admin Permission Testing

**GIVEN** admin permission system
**WHEN** admin tests are written
**THEN** tests MUST cover:
- **Staff Access**:
  - Non-staff access denial
  - Staff access verification
  - Superuser vs staff permissions
- **Object-Level Permissions**:
  - Object ownership verification
  - Change permission verification
  - Delete permission verification