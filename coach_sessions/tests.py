from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class SessionModelTest(TestCase):
    def test_session_creation(self):
        from .models import Session
        starts_at = timezone.now()
        session = Session.objects.create(
            starts_at=starts_at,
            duration=60,
            location="Gym",
            notes="Morning session",
            capacity=10,
            status="SCHEDULED"
        )
        self.assertEqual(session.location, "Gym")
        self.assertEqual(session.status, "SCHEDULED")

class SessionAttendeeModelTest(TestCase):
    def setUp(self):
        from .models import Session
        self.user = User.objects.create_user(username="attendee", password="password")
        self.session = Session.objects.create(
            starts_at=timezone.now(),
            duration=60,
            location="Gym"
        )

    def test_attendee_creation(self):
        from .models import SessionAttendee
        attendee = SessionAttendee.objects.create(
            session=self.session,
            user=self.user,
            intent_status="PLANNED",
            attendance_status="ARRIVED",
            payment_status="UNBILLED"
        )
        self.assertEqual(attendee.session, self.session)
        self.assertEqual(attendee.user, self.user)
        self.assertEqual(attendee.intent_status, "PLANNED")

    def test_session_cancellation_waives_payments(self):
        from .models import SessionAttendee
        attendee = SessionAttendee.objects.create(
            session=self.session,
            user=self.user,
            payment_status="UNBILLED"
        )
        self.session.cancel(reason="Bad weather", cancelled_by=self.user)
        attendee.refresh_from_db()
        self.assertEqual(self.session.status, "CANCELLED")
        self.assertEqual(self.session.cancel_reason, "Bad weather")
        self.assertEqual(attendee.payment_status, "WAIVED")

    def test_lateness_calculation(self):
        from datetime import timedelta
        from .models import SessionAttendee
        # Session starts now, attendee arrived 10 minutes later
        arrival_time = self.session.starts_at + timedelta(minutes=10)
        attendee = SessionAttendee.objects.create(
            session=self.session,
            user=self.user,
            arrived_at=arrival_time
        )
        self.assertEqual(attendee.lateness, timedelta(minutes=10))

    def test_lateness_calculation_early(self):
        from datetime import timedelta
        from .models import SessionAttendee
        # Session starts now, attendee arrived 5 minutes early
        arrival_time = self.session.starts_at - timedelta(minutes=5)
        attendee = SessionAttendee.objects.create(
            session=self.session,
            user=self.user,
            arrived_at=arrival_time
        )
        # Should be 0 or negative? Requirement 3.2 says "arrived_at - session.starts_at"
        self.assertEqual(attendee.lateness, timedelta(minutes=-5))

    def test_billing_candidates_filtering(self):
        from .models import Session, SessionAttendee
        self.session.status = 'COMPLETED'
        self.session.save()
        
        # Candidate: Attended, Unbilled
        c1 = SessionAttendee.objects.create(
            session=self.session, user=self.user, 
            attendance_status='ATTENDED', payment_status='UNBILLED'
        )
        # Candidate: No Show, Unbilled
        user2 = User.objects.create_user(username="user2", password="password")
        c2 = SessionAttendee.objects.create(
            session=self.session, user=user2, 
            attendance_status='NOSHOW', payment_status='UNBILLED'
        )
        # Not Candidate: Already Paid
        user3 = User.objects.create_user(username="user3", password="password")
        c3 = SessionAttendee.objects.create(
            session=self.session, user=user3, 
            attendance_status='ATTENDED', payment_status='PAID'
        )
        
        candidates = SessionAttendee.objects.billing_candidates()
        self.assertIn(c1, candidates)
        self.assertIn(c2, candidates)
        self.assertNotIn(c3, candidates)

    def test_awaiting_payment_filtering(self):
        from .models import Session, SessionAttendee
        self.session.status = 'COMPLETED'
        self.session.save()
        
        # Requested
        c1 = SessionAttendee.objects.create(
            session=self.session, user=self.user, 
            payment_status='REQUESTED'
        )
        # Paid (Not awaiting)
        user2 = User.objects.create_user(username="user2", password="password")
        c2 = SessionAttendee.objects.create(
            session=self.session, user=user2, 
            payment_status='PAID'
        )
        
        awaiting = SessionAttendee.objects.awaiting_payment()
        self.assertIn(c1, awaiting)
        self.assertNotIn(c2, awaiting)
