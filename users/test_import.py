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
        """Test basic import with all fields provided. Username from email."""
        self.dataset.append(['John', 'Doe', 'JOHN.DOE@example.com'])
        result = self.resource.import_data(self.dataset, dry_run=False)
        
        self.assertFalse(result.has_errors())
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(first_name='John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'john.doe@example.com')
        self.assertEqual(user.username, 'john.doe')

    def test_import_user_username_from_email_prefix(self):
        """Test that username is extracted from the email prefix if provided."""
        self.dataset.append(['John', 'Doe', 'johnd@example.com'])
        result = self.resource.import_data(self.dataset, dry_run=False)
        
        self.assertFalse(result.has_errors())
        user = User.objects.get(first_name='John')
        self.assertEqual(user.username, 'johnd')

    def test_import_user_missing_last_name(self):
        """Test username generation when last_name and email are missing."""
        self.dataset.append(['Jane', '', ''])
        result = self.resource.import_data(self.dataset, dry_run=False)
        
        self.assertFalse(result.has_errors())
        user = User.objects.get(first_name='Jane')
        self.assertEqual(user.username, 'jane')
        self.assertEqual(user.email, 'jane@coachotennis.com')

    def test_import_user_missing_email_with_last_name(self):
        """Test email and username generation when email is missing but last_name exists."""
        self.dataset.append(['Coach', 'O', ''])
        result = self.resource.import_data(self.dataset, dry_run=False)
        
        self.assertFalse(result.has_errors())
        user = User.objects.get(first_name='Coach')
        self.assertEqual(user.username, 'coach.o')
        self.assertEqual(user.email, 'coach.o@coachotennis.com')

    def test_import_user_with_explicit_username(self):
        """Test that an explicit username is NOT overwritten by email-derived username."""
        self.dataset.append(['Oscar', 'Chang', 'oscarchang1226@gmail.com'])
        # Add username explicitly
        self.dataset.headers.append('username')
        # Since tablib Dataset objects are immutable in terms of row structure once appended,
        # we have to clear and rebuild or use a new one. 
        # But for the purpose of this test, let's just create a new dataset with correct headers.
        dataset = Dataset()
        dataset.headers = ['first_name', 'last_name', 'email', 'username']
        dataset.append(['Oscar', 'Chang', 'oscarchang1226@gmail.com', 'o_chang'])
        
        result = self.resource.import_data(dataset, dry_run=False)
        
        self.assertFalse(result.has_errors())
        user = User.objects.get(first_name='Oscar')
        self.assertEqual(user.username, 'o_chang')
        self.assertEqual(user.email, 'oscarchang1226@gmail.com')

    def test_import_user_duplicate_username(self):
        """Test that duplicate username blocks import or is reported."""
        User.objects.create(username='duplicate.user', first_name='Existing')
        
        # This will result in username 'duplicate.user' because of the email
        self.dataset.append(['Duplicate', 'User', 'duplicate.user@example.com'])
        result = self.resource.import_data(self.dataset, dry_run=True)
        
        # In django-import-export, duplicates are usually identified as 'skip' or 'update'
        # based on import_id_fields.
        row_result = result.rows[0]
        self.assertEqual(row_result.import_type, 'skip') # Default behavior if it exists

    def test_import_user_duplicate_email(self):
        """Test that duplicate email blocks import or is reported."""
        User.objects.create(username='Other', email='dup@example.com', first_name='Existing')
        
        # This will result in username 'new' but email 'dup@example.com' which is duplicate
        self.dataset.append(['New', 'User', 'dup@example.com'])
        result = self.resource.import_data(self.dataset, dry_run=True)
        
        # We have custom logic in Resource to detect email duplicates
        row_result = result.rows[0]
        self.assertTrue(row_result.import_type in ['skip', 'error', 'invalid'])
