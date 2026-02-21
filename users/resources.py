from import_export import resources, fields
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class UserResource(resources.ModelResource):
    # Map headers to model fields where they differ or need specific treatment
    # In this case, first_name, last_name, email match CSV headers.
    
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')
        import_id_fields = ('username',) 
        skip_unchanged = True
        report_skipped = True

    def skip_row(self, instance, original, row, import_validation_errors=None):
        """Skip the row if the user already exists (don't update)."""
        if original.pk:
            return True
        return super().skip_row(instance, original, row, import_validation_errors)

    def before_import(self, dataset, **kwargs):
        """Pre-populate username and email in the dataset if they are missing."""
        # Ensure 'username' and 'email' are in headers
        if 'username' not in dataset.headers:
            dataset.headers.append('username')
        if 'email' not in dataset.headers:
            dataset.headers.append('email')
        
        username_idx = dataset.headers.index('username')
        email_idx = dataset.headers.index('email')
        first_name_idx = dataset.headers.index('first_name')
        
        last_name_idx = None
        if 'last_name' in dataset.headers:
            last_name_idx = dataset.headers.index('last_name')

        # Create a NEW dataset to avoid InvalidDimensions error
        from tablib import Dataset
        new_dataset = Dataset()
        new_dataset.headers = dataset.headers

        for row in dataset:
            row_list = list(row)
            while len(row_list) < len(new_dataset.headers):
                row_list.append('')

            first_name = row_list[first_name_idx].strip()
            last_name = row_list[last_name_idx].strip() if last_name_idx is not None else ''
            
            if not row_list[username_idx]:
                if last_name:
                    row_list[username_idx] = f"{first_name}.{last_name}".lower()
                else:
                    row_list[username_idx] = first_name.lower()
            else:
                row_list[username_idx] = row_list[username_idx].lower()
            
            if not row_list[email_idx]:
                row_list[email_idx] = f"{first_name}@coachotennis.com".lower()
            else:
                row_list[email_idx] = row_list[email_idx].lower()
            
            new_dataset.append(row_list)
        
        # Clear the original dataset and copy from new_dataset
        headers = new_dataset.headers
        dataset.wipe()
        dataset.headers = headers
        for row in new_dataset:
            dataset.append(row)

    def before_import_row(self, row, **kwargs):
        """Handle missing data before validation (secondary check)."""
        pass

    def validate_instance(self, instance, import_validation_errors=None, validate_unique=True):
        """Custom validation to handle duplicate emails and other requirements."""
        if import_validation_errors is None:
            import_validation_errors = {}

        # Check for email duplicates specifically, since username is already handled by import_id_fields
        # We only check if the instance is new (no id)
        email = getattr(instance, 'email', None)
        if email:
            qs = User.objects.filter(email=email)
            if instance.pk:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                import_validation_errors['email'] = ValidationError(
                    f"A user with email {email} already exists.",
                    code='duplicate'
                )

        super().validate_instance(instance, import_validation_errors, validate_unique)
