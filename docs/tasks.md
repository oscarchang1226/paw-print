# Technical Tasks

## Phase 3: Coach Sessions & Attendance (PWPT-5)

### Setup & Models
14. [x] Create a branch `PWPT-5` for the issue. - *Plan Item*: N/A - *Requirement*: N/A
15. [x] Create a new app `coach_sessions` to hold session-related logic. - *Plan Item*: Item 6 - *Requirement*: 1.1
16. [x] Define `Session` model with required fields and status choices. - *Plan Item*: Item 6 - *Requirement*: 1.1, 1.4
17. [x] Define `SessionAttendee` model with status fields (Intent, Attendance, Payment). - *Plan Item*: Item 8 - *Requirement*: 2.1, 2.2, 4.1
18. [x] Write unit tests for `Session` and `SessionAttendee` model definitions in `coach_sessions/tests.py`. - *Plan Item*: Item 6, 8 - *Requirement*: 1.1, 2.2
19. [x] Run tests and verify they fail (Red). - *Plan Item*: Item 6, 8 - *Requirement*: 1.1, 2.2
20. [x] Implement `Session` and `SessionAttendee` models. - *Plan Item*: Item 6, 8 - *Requirement*: 1.1, 2.2
21. [x] Run tests and verify they pass (Green). - *Plan Item*: Item 6, 8 - *Requirement*: 1.1, 2.2

### Session Logic
22. [x] Write tests for session cancellation logic (automatic status update for attendees). - *Plan Item*: Item 7 - *Requirement*: 1.2, 1.3
23. [x] Implement cancellation logic in `Session` model (e.g., in a `cancel()` method or `save()` override). - *Plan Item*: Item 7 - *Requirement*: 1.2, 1.3
24. [x] Verify cancellation tests pass. - *Plan Item*: Item 7 - *Requirement*: 1.2, 1.3

### Attendance & Lateness
25. [x] Write tests for attendance tracking and lateness property. - *Plan Item*: Item 9, 10 - *Requirement*: 3.1, 3.2, 3.3
26. [x] Implement `lateness` property on `SessionAttendee` model. - *Plan Item*: Item 10 - *Requirement*: 3.2
27. [x] Verify attendance tests pass. - *Plan Item*: Item 9, 10 - *Requirement*: 3.1, 3.3

### Billing Workflow
28. [x] Write tests for billing logic (filtering candidates for payment request). - *Plan Item*: Item 12 - *Requirement*: 4.2, 4.4
29. [x] Implement model managers or helper methods for billing status filtering. - *Plan Item*: Item 12 - *Requirement*: 4.2, 4.4
30. [x] Verify billing tests pass. - *Plan Item*: Item 12 - *Requirement*: 4.2, 4.4

### Admin Integration
31. [x] Register `Session` and `SessionAttendee` models in admin. - *Plan Item*: Item 6, 8 - *Requirement*: 1.1, 2.1
32. [x] Customize Admin UI to show lateness and billing status lists. - *Plan Item*: Item 12 - *Requirement*: 4.2, 4.4
