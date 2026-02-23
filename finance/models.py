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
