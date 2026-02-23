import csv
import hashlib
import json
from datetime import datetime
from decimal import Decimal
import zoneinfo
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from .models import RawTransaction, ImportBatch

class CSVImporter:
    def __init__(self, batch: ImportBatch):
        self.batch = batch
        self.source = batch.source
        self.account = batch.account
        self.tz = zoneinfo.ZoneInfo(getattr(settings, 'TIME_ZONE', 'UTC'))

    def normalize_amount(self, amount_str):
        # Handle signs and common separators
        clean_amount = amount_str.replace(',', '').strip()
        return int(Decimal(clean_amount) * 100)

    def normalize_date(self, date_str):
        dt = datetime.strptime(date_str, self.source.date_format)
        if dt.tzinfo is None:
            # Assume it's in the application's local timezone
            dt = dt.replace(tzinfo=self.tz)
        return dt.astimezone(timezone.UTC)

    def generate_fingerprint(self, txn_at_utc, description, amount, category_raw):
        # sha256(account_id + source_id + normalized_datetime + normalized_description + normalized_amount + category_raw)
        payload = f"{self.account.id}{self.source.id}{txn_at_utc.isoformat()}{description}{amount}{category_raw or ''}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    def process_row(self, row):
        # Extract data using mapper
        date_val = self._get_col(row, self.source.date_column)
        desc_val = self._get_col(row, self.source.description_column)
        amount_val = self._get_col(row, self.source.amount_column)
        category_val = self._get_col(row, self.source.category_column) if self.source.category_column else None

        normalized_date = self.normalize_date(date_val)
        normalized_amount = self.normalize_amount(amount_val)
        fingerprint = self.generate_fingerprint(normalized_date, desc_val, normalized_amount, category_val)

        return {
            'txn_at_utc': normalized_date,
            'description': desc_val,
            'amount': normalized_amount,
            'category_raw': category_val,
            'fingerprint_hash': fingerprint,
            'raw_payload': row
        }

    def _get_col(self, row, col_def):
        if self.source.has_header:
            if col_def in row:
                return row[col_def]
            # Try numeric index if header name fails? Requirement says "accept either string (header name) or numeric index as string"
            # In DictReader, we only have names.
        
        # If numeric index as string
        if col_def.isdigit():
            idx = int(col_def)
            # row might be a dict (from DictReader) or list (from reader)
            if isinstance(row, dict):
                # DictReader values
                vals = list(row.values())
                if 0 <= idx < len(vals):
                    return vals[idx]
            elif isinstance(row, list):
                if 0 <= idx < len(row):
                    return row[idx]
        
        raise KeyError(f"Column '{col_def}' not found in row.")

    def run_import(self, file_handle, dry_run=True, force=False, force_reason=None, user=None):
        decoded_file = file_handle.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file, delimiter=self.source.delimiter)
        
        results = []
        duplicates = []
        errors = []
        
        file_fingerprints = set()

        for i, row in enumerate(reader):
            try:
                processed = self.process_row(row)
                fp = processed['fingerprint_hash']
                
                # Check for file-local duplicates
                if fp in file_fingerprints:
                    duplicates.append({'row': i+1, 'data': processed, 'reason': 'Duplicate in file'})
                file_fingerprints.add(fp)

                # Check for DB duplicates
                if not force and RawTransaction.objects.filter(fingerprint_hash=fp, is_forced_duplicate=False).exists():
                    duplicates.append({'row': i+1, 'data': processed, 'reason': 'Duplicate in database'})
                
                processed['is_forced_duplicate'] = force if fp in [d['data']['fingerprint_hash'] for d in duplicates] else False
                if processed['is_forced_duplicate']:
                    processed['force_reason'] = force_reason
                    processed['forced_by'] = user
                    processed['forced_at'] = timezone.now()

                results.append(processed)
            except Exception as e:
                errors.append({'row': i+1, 'error': str(e)})

        if errors:
            return {
                'status': 'FAILED', 
                'errors': errors, 
                'total': len(results),
                'duplicates': duplicates,
                'results': []
            }

        if duplicates and not force and not dry_run:
             return {
                 'status': 'BLOCKED_BY_DUPLICATES', 
                 'duplicates': duplicates,
                 'total': len(results),
                 'results': results
             }

        if not dry_run:
            with transaction.atomic():
                for res in results:
                    RawTransaction.objects.create(
                        import_batch=self.batch,
                        account=self.account,
                        source=self.source,
                        **res
                    )
                self.batch.status = 'COMPLETED'
                self.batch.total_rows = len(results)
                self.batch.imported_rows = len(results)
                self.batch.forced_duplicate_count = len(duplicates) if force else 0
                self.batch.save()
        
        return {
            'status': 'SUCCESS' if not dry_run else 'DRY_RUN',
            'total': len(results),
            'duplicates': duplicates,
            'results': results
        }
