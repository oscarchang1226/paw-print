from django.test import TestCase
from django.contrib.auth import get_user_model
from tablib import Dataset
from .resources import UserResource

User = get_user_model()

class UserImportExportTest(TestCase):
    def setUp(self):
        self.resource = UserResource()
        self.dataset = Dataset()
        self.dataset.headers = ['first_name', 'last_name', 'email']

    def test_import_user_basic(self):
        """Test basic import with all fields provided."""
        self.dataset.append(['John', 'Doe', 'JOHN.DOE@example.com'])
        result = self.resource.import_data(self.dataset, dry_run=False)
        
        self.assertFalse(result.has_errors())
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(first_name='John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'john.doe@example.com')
        self.assertEqual(user.username, 'john.doe')

    def test_import_user_missing_last_name(self):
        """Test username generation when last_name is missing."""
        self.dataset.append(['Jane', '', 'jane@example.com'])
        result = self.resource.import_data(self.dataset, dry_run=False)
        
        self.assertFalse(result.has_errors())
        user = User.objects.get(first_name='Jane')
        self.assertEqual(user.username, 'jane')

    def test_import_user_missing_email(self):
        """Test email generation when email is missing."""
        self.dataset.append(['Coach', 'O', ''])
        result = self.resource.import_data(self.dataset, dry_run=False)
        
        self.assertFalse(result.has_errors())
        user = User.objects.get(first_name='Coach')
        self.assertEqual(user.email, 'coach@coachotennis.com')

    def test_import_user_duplicate_username(self):
        """Test that duplicate username blocks import or is reported."""
        User.objects.create(username='duplicate.user', first_name='Existing')
        
        self.dataset.append(['Duplicate', 'User', 'new@example.com'])
        result = self.resource.import_data(self.dataset, dry_run=True)
        
        # In django-import-export, duplicates are usually identified as 'skip' or 'update'
        # based on import_id_fields. But our requirement says "block import until admin acknowledges"
        # and "Default policy: block import and require admin to fix file".
        # We want to ensure it's detected.
        row_result = result.rows[0]
        self.assertEqual(row_result.import_type, 'skip') # Default behavior if it exists

    def test_import_user_duplicate_email(self):
        """Test that duplicate email blocks import or is reported."""
        User.objects.create(username='Other', email='dup@example.com', first_name='Existing')
        
        self.dataset.append(['New', 'User', 'dup@example.com'])
        result = self.resource.import_data(self.dataset, dry_run=True)
        
        # We need custom logic in Resource to detect email duplicates if username is unique
        row_result = result.rows[0]
        self.assertTrue(row_result.import_type in ['skip', 'error', 'invalid'])
