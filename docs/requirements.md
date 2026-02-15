# Requirements Document

## Introduction
Paw-print is a foundational Django project. This requirements document is driven by GitHub issues to ensure traceability.

## Requirements from Issues

### [PWPT-1] Initial Users App and Custom User Model
**Source**: GitHub Issue #1

1. **User Story**: As a developer, I want a custom User model from the start so that I can easily extend user attributes in the future without complex migrations.
- **Acceptance Criteria**:
  - WHEN the application is initialized THEN a custom `User` model inheriting from `AbstractUser` SHALL be present in a `users` app.
  - WHEN `AUTH_USER_MODEL` is checked THEN it SHALL point to `users.User`.
  - WHEN migrations are run THEN the database SHALL correctly create the `users_user` table.

2. **User Story**: As a developer, I want unit tests for the User model so that I can ensure core authentication identity remains stable.
- **Acceptance Criteria**:
  - WHEN tests are run THEN the system SHALL verify `User` model creation.
  - WHEN tests are run THEN the system SHALL verify basic fields (username, email, is_active).
  - WHEN tests are run THEN the system SHALL verify `AUTH_USER_MODEL` configuration.
