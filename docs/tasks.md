# Technical Tasks

## Phase 1: Custom User Model (PWPT-1)
1. [x] Create the `users` app skeleton.
   - *Plan Item*: Item 2
   - *Requirement*: PWPT-1.1
2. [x] Write unit tests for the custom User model in `users/tests.py`.
   - *Plan Item*: Item 1
   - *Requirement*: PWPT-1.2
3. [x] Run tests and verify they fail (TDD).
   - *Plan Item*: Item 1
   - *Requirement*: PWPT-1.2
4. [x] Implement the custom `User` model in `users/models.py`.
   - *Plan Item*: Item 2
   - *Requirement*: PWPT-1.1
5. [x] Update `paw_print/settings.py` with `AUTH_USER_MODEL = 'users.User'` and add `users` to `INSTALLED_APPS`.
   - *Plan Item*: Item 3
   - *Requirement*: PWPT-1.1
6. [x] Create and run migrations for the `users` app.
   - *Plan Item*: Item 2
   - *Requirement*: PWPT-1.1
7. [x] Run tests and verify they pass.
   - *Plan Item*: Item 1
   - *Requirement*: PWPT-1.2
