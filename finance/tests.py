import uuid
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from finance.models import Account, TransactionImportSource, ImportBatch, RawTransaction
from finance.importer import CSVImporter

User = get_user_model()

class CSVImporterTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.account = Account.objects.create(name='Test Bank', type='BANK', created_by=self.user)
        self.source = TransactionImportSource.objects.create(
            name='Chase', 
            delimiter=',',
            has_header=True,
            date_column='Date', 
            description_column='Description', 
            amount_column='Amount', 
            date_format='%m/%d/%Y'
        )
        self.batch = ImportBatch.objects.create(
            account=self.account,
            source=self.source,
            uploaded_by=self.user
        )
        self.importer = CSVImporter(self.batch)

    def test_normalize_amount(self):
        self.assertEqual(self.importer.normalize_amount('10.00'), 1000)
        self.assertEqual(self.importer.normalize_amount('-5.50'), -550)
        self.assertEqual(self.importer.normalize_amount('1,234.56'), 123456)

    def test_normalize_date(self):
        from datetime import datetime
        import zoneinfo
        dt = self.importer.normalize_date('01/31/2024')
        # Defaults to midnight America/Chicago if not specified.
        # 2024-01-31 00:00:00 Chicago is 2024-01-31 06:00:00 UTC (CST is UTC-6)
        self.assertEqual(dt.year, 2024)
        self.assertEqual(dt.month, 1)
        self.assertEqual(dt.day, 31)
        self.assertEqual(dt.hour, 6) # UTC

    def test_run_import_success(self):
        import io
        csv_content = "Date,Description,Amount\n01/01/2024,Lunch,-15.00\n01/02/2024,Salary,1000.00"
        file = io.BytesIO(csv_content.encode('utf-8'))
        
        result = self.importer.run_import(file, dry_run=False)
        self.assertEqual(result['status'], 'SUCCESS')
        self.assertEqual(RawTransaction.objects.count(), 2)
        
        batch = ImportBatch.objects.get(id=self.batch.id)
        self.assertEqual(batch.status, 'COMPLETED')
        self.assertEqual(batch.total_rows, 2)

    def test_duplicate_detection(self):
        import io
        csv_content = "Date,Description,Amount\n01/01/2024,Lunch,-15.00\n01/01/2024,Lunch,-15.00"
        file = io.BytesIO(csv_content.encode('utf-8'))
        
        # Dry run should detect 1 duplicate
        result = self.importer.run_import(file, dry_run=True)
        self.assertEqual(len(result['duplicates']), 1)
        self.assertEqual(result['duplicates'][0]['reason'], 'Duplicate in file')

class ImportBatchModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.account = Account.objects.create(name='Test Bank', type='BANK', created_by=self.user)
        self.source = TransactionImportSource.objects.create(
            name='Chase', date_column='d', description_column='desc', amount_column='amt', date_format='%Y'
        )

    def test_batch_creation(self):
        batch = ImportBatch.objects.create(
            account=self.account,
            source=self.source,
            uploaded_by=self.user,
            status='COMPLETED',
            total_rows=10,
            imported_rows=10
        )
        self.assertIsInstance(batch.id, uuid.UUID)
        self.assertEqual(batch.status, 'COMPLETED')

class RawTransactionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.account = Account.objects.create(name='Test Bank', type='BANK', created_by=self.user)
        self.source = TransactionImportSource.objects.create(
            name='Chase', date_column='d', description_column='desc', amount_column='amt', date_format='%Y'
        )
        self.batch = ImportBatch.objects.create(
            account=self.account,
            source=self.source,
            uploaded_by=self.user,
            status='COMPLETED'
        )

    def test_transaction_creation(self):
        from django.utils import timezone
        txn = RawTransaction.objects.create(
            import_batch=self.batch,
            account=self.account,
            source=self.source,
            txn_at_utc=timezone.now(),
            description='Test Transaction',
            amount=-1000, # -$10.00
            fingerprint_hash='fakehash',
            raw_payload={'Date': '2024-01-01', 'Amount': '-10.00'}
        )
        self.assertIsInstance(txn.id, uuid.UUID)
        self.assertEqual(txn.amount, -1000)

    def test_immutability_update(self):
        from django.utils import timezone
        txn = RawTransaction.objects.create(
            import_batch=self.batch,
            account=self.account,
            source=self.source,
            txn_at_utc=timezone.now(),
            description='Immutable',
            amount=500,
            fingerprint_hash='hash1',
            raw_payload={}
        )
        txn.description = 'Changed'
        with self.assertRaises(ValidationError) as cm:
            txn.save()
        self.assertIn("RawTransaction is immutable", str(cm.exception))

    def test_immutability_delete(self):
        from django.utils import timezone
        txn = RawTransaction.objects.create(
            import_batch=self.batch,
            account=self.account,
            source=self.source,
            txn_at_utc=timezone.now(),
            description='Immutable',
            amount=500,
            fingerprint_hash='hash1',
            raw_payload={}
        )
        with self.assertRaises(ValidationError) as cm:
            txn.delete()
        self.assertIn("RawTransaction is immutable", str(cm.exception))
        self.assertTrue(RawTransaction.objects.filter(id=txn.id).exists())

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

class ImportAdminTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username='admin', password='password')
        self.client.login(username='admin', password='password')
        self.account = Account.objects.create(name='Test Bank', type='BANK', created_by=self.user)
        self.source = TransactionImportSource.objects.create(
            name='Chase', 
            delimiter=',',
            has_header=True,
            date_column='Date', 
            description_column='Description', 
            amount_column='Amount', 
            date_format='%m/%d/%Y'
        )

    def test_import_csv_view_get(self):
        from django.urls import reverse
        url = reverse('admin:finance_import_csv')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Import Transactions CSV")

    def test_import_csv_view_dry_run(self):
        from django.urls import reverse
        import io
        url = reverse('admin:finance_import_csv')
        csv_content = "Date,Description,Amount\n01/01/2024,Lunch,-15.00"
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        csv_file.name = 'test.csv'
        
        data = {
            'account': str(self.account.id),
            'source': str(self.source.id),
            'csv_file': csv_file,
            'dry_run': 'on'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dry Run Results: DRY_RUN")
        # Ensure no transactions created
        self.assertEqual(RawTransaction.objects.count(), 0)
