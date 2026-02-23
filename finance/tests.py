import uuid
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from finance.models import Account

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
