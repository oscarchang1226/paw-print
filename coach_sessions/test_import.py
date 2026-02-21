from django.test import TestCase
from django.contrib.auth import get_user_model
from tablib import Dataset
from coach_sessions.models import Session
from .resources import SessionResource
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class SessionImportExportTest(TestCase):
    def setUp(self):
        self.coach = User.objects.create_user(username='coach1', first_name='Coach', last_name='One')
        self.resource = SessionResource()
        self.dataset = Dataset()
        self.dataset.headers = [
            'starts_at', 'duration', 'capacity', 'status', 'coach_username', 
            'location', 'notes', 'cancel_reason', 'cancelled_at', 'cancelled_by'
        ]

    def test_import_session_basic(self):
        """Test basic session import."""
        starts_at = timezone.now() + timedelta(days=1)
        self.dataset.append([
            starts_at.strftime('%Y-%m-%d %H:%M:%S'), 60, 10, 'SCHEDULED', 'coach1',
            'Carrot Park', 'Some notes', '', '', ''
        ])
        result = self.resource.import_data(self.dataset, dry_run=False)
        
        if result.has_errors():
            for row in result.rows:
                print(f"Row errors: {row.errors}")
            for error in result.base_errors:
                print(f"Base error: {error.error}")

        self.assertFalse(result.has_errors())
        self.assertEqual(Session.objects.count(), 1)
        session = Session.objects.first()
        self.assertEqual(session.coach, self.coach)
        self.assertEqual(session.duration, 60)
        self.assertEqual(session.location, 'Carrot Park')

    def test_import_session_cancelled_missing_reason(self):
        """Test that cancelled session requires a reason."""
        starts_at = timezone.now() + timedelta(days=1)
        self.dataset.append([
            starts_at.strftime('%Y-%m-%d %H:%M:%S'), 60, 10, 'CANCELLED', 'coach1',
            'Carrot Park', 'Some notes', '', '', ''
        ])
        
        result = self.resource.import_data(self.dataset, dry_run=True)
        self.assertTrue(result.has_errors())
        
        row_result = result.rows[0]
        self.assertTrue(any('cancel_reason' in str(e.error) for e in row_result.errors))

    def test_import_session_coach_not_found(self):
        """Test that non-existent coach blocks import."""
        starts_at = timezone.now() + timedelta(days=1)
        self.dataset.append([
            starts_at.strftime('%Y-%m-%d %H:%M:%S'), 60, 10, 'SCHEDULED', 'nonexistent',
            'Carrot Park', '', '', '', ''
        ])
        result = self.resource.import_data(self.dataset, dry_run=True)
        
        self.assertTrue(result.has_errors())
        row_result = result.rows[0]
        self.assertTrue(any('coach' in str(e.error).lower() for e in row_result.errors))

    def test_import_session_duplicate(self):
        """Test duplicate session detection (coach_username, starts_at)."""
        starts_at = (timezone.now() + timedelta(days=1)).replace(microsecond=0)
        Session.objects.create(
            coach=self.coach,
            starts_at=starts_at,
            duration=60,
            location='Original'
        )
        
        self.dataset.append([
            starts_at.strftime('%Y-%m-%d %H:%M:%S'), 60, 10, 'SCHEDULED', 'coach1',
            'New Location', '', '', '', ''
        ])
        result = self.resource.import_data(self.dataset, dry_run=True)
        
        # Policy says block/skip duplicates
        row_result = result.rows[0]
        self.assertEqual(row_result.import_type, 'skip')
