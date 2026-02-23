import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MaxLengthValidator

class Account(models.Model):
    ACCOUNT_TYPES = [
        ('BANK', 'Bank Account'),
        ('CREDIT_CARD', 'Credit Card'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    currency = models.CharField(max_length=3, default='USD')
    institution = models.CharField(max_length=255, blank=True, null=True)
    last4 = models.CharField(max_length=4, blank=True, null=True, validators=[MaxLengthValidator(4)])
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def delete(self, *args, **kwargs):
        # In the future, this will check for related RawTransactions.
        # Requirement 3 says "Accounts cannot be deleted if referenced by any raw transaction."
        # For now, we'll just allow it since no such model exists.
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name

class ImportBatch(models.Model):
    STATUS_CHOICES = [
        ('DRY_RUN', 'Dry Run'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    source = models.ForeignKey('TransactionImportSource', on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRY_RUN')
    total_rows = models.IntegerField(default=0)
    imported_rows = models.IntegerField(default=0)
    forced_duplicate_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Batch {self.id} ({self.status})"

class RawTransaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    import_batch = models.ForeignKey(ImportBatch, on_delete=models.CASCADE, related_name='transactions')
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    source = models.ForeignKey('TransactionImportSource', on_delete=models.PROTECT)
    txn_at_utc = models.DateTimeField()
    description = models.TextField()
    amount = models.BigIntegerField()  # Signed cents
    category_raw = models.TextField(blank=True, null=True)
    fingerprint_hash = models.CharField(max_length=64, db_index=True)
    is_forced_duplicate = models.BooleanField(default=False)
    force_reason = models.TextField(blank=True, null=True)
    forced_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    forced_at = models.DateTimeField(null=True, blank=True)
    raw_payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self._state.adding:
            # New object, allowed
            super().save(*args, **kwargs)
        else:
            if not kwargs.get('force_update', False):
                from django.core.exceptions import ValidationError
                raise ValidationError("RawTransaction is immutable and cannot be updated.")
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        from django.core.exceptions import ValidationError
        raise ValidationError("RawTransaction is immutable and cannot be deleted.")

    def __str__(self):
        return f"{self.txn_at_utc} - {self.description} ({self.amount})"

class TransactionImportSource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    delimiter = models.CharField(max_length=5, default=',')
    has_header = models.BooleanField(default=True)
    date_column = models.CharField(max_length=255)
    description_column = models.CharField(max_length=255)
    amount_column = models.CharField(max_length=255)
    category_column = models.CharField(max_length=255, blank=True, null=True)
    date_format = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
