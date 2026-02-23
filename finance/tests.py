import uuid
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from finance.models import Account, TransactionImportSource

User = get_user_model()

class AccountModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_account_creation(self):
        account = Account.objects.create(
            name='Test Bank',
            type='BANK',
            institution='Test Bank Inc',
            last4='1234',
            created_by=self.user
        )
        self.assertIsInstance(account.id, uuid.UUID)
        self.assertEqual(account.name, 'Test Bank')
        self.assertEqual(account.currency, 'USD')

    def test_unique_name(self):
        Account.objects.create(name='Unique Name', type='BANK', created_by=self.user)
        # Unique constraint is usually enforced at DB level, but we can test it with full_clean
        # and checking that a second create with same name fails (integrity error).
        # Django's full_clean also checks unique constraints.
        account2 = Account(name='Unique Name', type='BANK', created_by=self.user)
        with self.assertRaises(ValidationError):
            account2.full_clean()

    def test_last4_validation(self):
        # last4 should be max 4 characters
        # Using 5 chars should trigger validation error during full_clean
        account = Account(name='Long Last4', type='BANK', last4='12345', created_by=self.user)
        with self.assertRaises(ValidationError):
            account.full_clean()

    def test_default_currency(self):
        account = Account.objects.create(name='Default Currency', type='BANK', created_by=self.user)
        self.assertEqual(account.currency, 'USD')

class TransactionImportSourceModelTest(TestCase):
    def test_source_creation(self):
        source = TransactionImportSource.objects.create(
            name='Chase Checking',
            date_column='Date',
            description_column='Description',
            amount_column='Amount',
            date_format='%m/%d/%Y'
        )
        self.assertIsInstance(source.id, uuid.UUID)
        self.assertEqual(source.delimiter, ',')
        self.assertTrue(source.has_header)
        self.assertEqual(source.name, 'Chase Checking')

    def test_unique_name(self):
        TransactionImportSource.objects.create(
            name='Unique Source',
            date_column='Date',
            description_column='Description',
            amount_column='Amount',
            date_format='%m/%d/%Y'
        )
        source2 = TransactionImportSource(
            name='Unique Source',
            date_column='d',
            description_column='desc',
            amount_column='amt',
            date_format='%Y'
        )
        with self.assertRaises(ValidationError):
            source2.full_clean()

    def test_category_column_nullable(self):
        source = TransactionImportSource.objects.create(
            name='No Category Source',
            date_column='Date',
            description_column='Description',
            amount_column='Amount',
            date_format='%m/%d/%Y',
            category_column=None
        )
        self.assertIsNone(source.category_column)

class AccountAdminTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username='admin', password='password')
        self.client.login(username='admin', password='password')

    def test_admin_created_by_auto_fill(self):
        from django.urls import reverse
        url = reverse('admin:finance_account_add')
        data = {
            'name': 'Admin Account',
            'type': 'BANK',
            'currency': 'USD',
            'institution': 'Admin Bank',
            'last4': '9999',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) # Redirect after success
        account = Account.objects.get(name='Admin Account')
        self.assertEqual(account.created_by, self.user)
