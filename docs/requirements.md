# Requirements Document

## Introduction
Paw-print is a foundational Django project. This requirements document is driven by GitHub issues to ensure traceability.

## Requirements from Issues

### [PWPT-5] Coach Sessions with Attendee Status, Attendance, and Billing Workflow
**Source**: GitHub Issue #5

1. **User Story**: As a coach, I want to create and edit sessions so that I can plan my schedule and locations.
   - **Acceptance Criteria**: WHEN creating or editing a session THEN the system SHALL persist date/time, duration, location, notes, and optional capacity.

2. **User Story**: As a coach, I want to cancel a session so that I can handle schedule changes.
   - **Acceptance Criteria**: WHEN a session is cancelled THEN the system SHALL require a `cancel_reason` and record `cancelled_at` and `cancelled_by`.

3. **User Story**: As a coach, I want cancelled sessions to automatically waive payments so that I don't bill for cancelled work.
   - **Acceptance Criteria**: WHEN a session status is set to `CANCELLED` THEN the system SHALL automatically set all associated attendee `payment_status` to `WAIVED`.

4. **User Story**: As a coach, I want to mark a session as completed so that I can proceed to billing.
   - **Acceptance Criteria**: WHEN a session is finished THEN the coach SHALL be able to mark the session status as `COMPLETED`.

5. **User Story**: As a coach, I want to manage attendees for a session so that I know who is expected to attend.
   - **Acceptance Criteria**: WHEN managing a session THEN the system SHALL allow adding and removing attendees.

6. **User Story**: As a coach, I want to track attendee intent so that I can see who is confirmed.
   - **Acceptance Criteria**: WHEN an attendee is added to a session THEN they SHALL have an `intent_status` of `PLANNED`, `INVITED`, `CONFIRMED`, or `DECLINED`.

7. **User Story**: As a coach, I want to override a declined status so that I can manually confirm attendees who change their minds.
   - **Acceptance Criteria**: WHEN an attendee is `DECLINED` THEN the coach SHALL be able to move them to `CONFIRMED`.

8. **User Story**: As a coach, I want to record when an attendee arrives so that I can track punctuality.
   - **Acceptance Criteria**: WHEN an attendee arrives THEN the coach SHALL mark them as `ARRIVED` and the system SHALL record the `arrived_at` timestamp.

9. **User Story**: As a coach, I want to see how late an attendee was so that I can address it with them.
   - **Acceptance Criteria**: WHEN an attendee has an `arrived_at` time THEN the system SHALL compute lateness as `arrived_at - session.starts_at`.

10. **User Story**: As a coach, I want to record final attendance status so that I have a record of who was there.
    - **Acceptance Criteria**: WHEN a session is in progress or finished THEN the coach SHALL be able to mark an attendee as `ATTENDED` or `NOSHOW`.

11. **User Story**: As a coach, I want to manage payment statuses for attendees so that I can track my revenue.
    - **Acceptance Criteria**: WHEN a session is COMPLETED THEN the coach SHALL be able to set attendee `payment_status` to `UNBILLED`, `REQUESTED`, `PAID`, or `WAIVED`.

12. **User Story**: As a coach, I want to bill for no-shows so that I can enforce my cancellation policy.
    - **Acceptance Criteria**: WHEN an attendee is marked as `ATTENDED` or `NOSHOW` and the session is `COMPLETED` THEN the system SHALL list them as candidates for billing (`payment_status` = `UNBILLED`).

13. **User Story**: As a coach, I want to record when a payment was received so that I have financial records.
    - **Acceptance Criteria**: WHEN `payment_status` is set to `PAID` THEN the system SHALL store the `paid_at` timestamp.

14. **User Story**: As a coach, I want to see which payments are pending so that I can follow up.
    - **Acceptance Criteria**: WHEN `payment_status` is `REQUESTED` and session is `COMPLETED` THEN the system SHALL display these in an "Awaiting Payment" list.
