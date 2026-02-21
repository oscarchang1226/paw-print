from django.test import TestCase
from django.contrib.auth import get_user_model
from tablib import Dataset
from coach_sessions.models import Session, SessionAttendee
from .resources import SessionAttendeeResource
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class SessionAttendeeImportExportTest(TestCase):
    def setUp(self):
        self.coach = User.objects.create_user(username='coach1', first_name='Coach')
        self.attendee = User.objects.create_user(username='user1', first_name='User')
        self.session_time = (timezone.now() + timedelta(days=1)).replace(microsecond=0)
        self.session = Session.objects.create(
            coach=self.coach,
            starts_at=self.session_time,
            duration=60,
            location='Carrot Park'
        )
        self.resource = SessionAttendeeResource()
        self.dataset = Dataset()
        self.dataset.headers = [
            'session_datetime', 'coach_username', 'user_username', 
            'intent_status', 'attendance_status', 'payment_status', 
            'arrived_at', 'paid_at'
        ]

    def test_import_attendee_basic(self):
        """Test basic session attendee import."""
        self.dataset.append([
            self.session_time.strftime('%Y-%m-%d %H:%M:%S'), 'coach1', 'user1',
            'CONFIRMED', 'ATTENDED', 'PAID', '', self.session_time.strftime('%Y-%m-%d %H:%M:%S')
        ])
        result = self.resource.import_data(self.dataset, dry_run=False)
        
        if result.has_errors():
            for row in result.rows:
                print(f"Row errors: {row.errors}")
            for error in result.base_errors:
                print(f"Base error: {error.error}")

        self.assertFalse(result.has_errors())
        self.assertEqual(SessionAttendee.objects.count(), 1)
        attendee = SessionAttendee.objects.first()
        self.assertEqual(attendee.user, self.attendee)
        self.assertEqual(attendee.session, self.session)
        self.assertEqual(attendee.payment_status, 'PAID')

    def test_import_attendee_session_not_found(self):
        """Test that non-existent session blocks import."""
        self.dataset.append([
            '2026-01-01 00:00:00', 'coach1', 'user1',
            'CONFIRMED', 'ATTENDED', 'PAID', '', ''
        ])
        result = self.resource.import_data(self.dataset, dry_run=True)
        self.assertTrue(result.has_errors() or any(row.errors for row in result.rows))

    def test_import_attendee_user_not_found(self):
        """Test that non-existent user blocks import."""
        self.dataset.append([
            self.session_time.strftime('%Y-%m-%d %H:%M:%S'), 'coach1', 'nonexistent',
            'CONFIRMED', 'ATTENDED', 'PAID', '', ''
        ])
        result = self.resource.import_data(self.dataset, dry_run=True)
        self.assertTrue(result.has_errors() or any(row.errors for row in result.rows))

    def test_import_attendee_arrived_at_required(self):
        """Test that arrived_at is required if attendance_status is ARRIVED."""
        self.dataset.append([
            self.session_time.strftime('%Y-%m-%d %H:%M:%S'), 'coach1', 'user1',
            'CONFIRMED', 'ARRIVED', 'UNBILLED', '', ''
        ])
        result = self.resource.import_data(self.dataset, dry_run=True)
        self.assertTrue(result.has_errors() or any(row.errors for row in result.rows))

    def test_import_attendee_paid_at_required(self):
        """Test that paid_at is required if payment_status is PAID."""
        self.dataset.append([
            self.session_time.strftime('%Y-%m-%d %H:%M:%S'), 'coach1', 'user1',
            'CONFIRMED', 'ATTENDED', 'PAID', '', ''
        ])
        result = self.resource.import_data(self.dataset, dry_run=True)
        self.assertTrue(result.has_errors() or any(row.errors for row in result.rows))
