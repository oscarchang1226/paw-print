# Implementation Plan

This plan is driven by GitHub issues and follows Test-Driven Development (TDD).

## Phase 3: Coach Sessions and Attendance (PWPT-5)
Enable coaches to manage sessions, attendees, and tracking.

- **Item 6: Session Model and CRUD**
  - Description: Implement `Session` model with fields for date/time, duration, location, notes, capacity, and status (SCHEDULED, CANCELLED, COMPLETED).
  - Priority: High
  - Linked Requirements: 1.1, 1.4
- **Item 7: Session Cancellation Logic**
  - Description: Implement session cancellation with `cancel_reason` and automatic waiving of attendee payments.
  - Priority: High
  - Linked Requirements: 1.2, 1.3
- **Item 8: SessionAttendee Model**
  - Description: Implement a join model for Session and User (attendee) with `intent_status` (PLANNED, INVITED, CONFIRMED, DECLINED).
  - Priority: High
  - Linked Requirements: 2.1, 2.2, 2.3
- **Item 9: Real-time Attendance**
  - Description: Add `attendance_status` (ARRIVED, ATTENDED, NOSHOW) and `arrived_at` field.
  - Priority: Medium
  - Linked Requirements: 3.1, 3.3
- **Item 10: Lateness Calculation**
  - Description: Implement property/logic to calculate lateness based on `arrived_at` and session start time.
  - Priority: Low
  - Linked Requirements: 3.2
- **Item 11: Payment Tracking**
  - Description: Add `payment_status` (UNBILLED, REQUESTED, PAID, WAIVED) and `paid_at`.
  - Priority: High
  - Linked Requirements: 4.1, 4.3
- **Item 12: Billing UI Logic**
  - Description: Implement logic to filter attendees for "To Request" and "Awaiting Payment" lists.
  - Priority: Medium
  - Linked Requirements: 4.2, 4.4
