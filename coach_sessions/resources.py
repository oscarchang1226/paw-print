from import_export import resources, fields, widgets
from import_export.results import RowResult
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Session, SessionAttendee

User = get_user_model()

class SessionResource(resources.ModelResource):
    # ... (existing SessionResource code remains same)
    coach = fields.Field(
        column_name='coach_username',
        attribute='coach',
        widget=widgets.ForeignKeyWidget(User, 'username')
    )
    cancelled_by = fields.Field(
        column_name='cancelled_by',
        attribute='cancelled_by',
        widget=widgets.ForeignKeyWidget(User, 'username')
    )

    class Meta:
        model = Session
        fields = (
            'id', 'starts_at', 'duration', 'capacity', 'status', 'location', 
            'notes', 'cancel_reason', 'cancelled_at', 'coach', 'cancelled_by'
        )
        import_id_fields = ('starts_at', 'coach')
        skip_unchanged = True
        report_skipped = True

    def skip_row(self, instance, original, row, import_validation_errors=None):
        if original.pk:
            return True
        return super().skip_row(instance, original, row, import_validation_errors)

    def before_import_row(self, row, **kwargs):
        if not row.get('location'):
            row['location'] = 'Carrot Park'
        
    def import_row(self, row, instance_loader, **kwargs):
        kwargs['validate_unique'] = True
        
        # Manually validate Coach username if provided
        coach_username = row.get('coach_username')
        errors = {}
        if coach_username:
            try:
                User.objects.get(username=coach_username)
            except User.DoesNotExist:
                errors['coach'] = ValidationError(f"Coach with username '{coach_username}' does not exist.")

        # Manually validate Cancelled By username if provided
        cb_username = row.get('cancelled_by')
        if cb_username:
            try:
                User.objects.get(username=cb_username)
            except User.DoesNotExist:
                errors['cancelled_by'] = ValidationError(f"User with username '{cb_username}' (cancelled_by) does not exist.")

        # Status and Cancellation logic directly on row
        status = row.get('status')
        if status == 'CANCELLED':
            if not row.get('cancel_reason'):
                errors['cancel_reason'] = ValidationError("cancel_reason is required for CANCELLED sessions.")
            if not row.get('cancelled_at'):
                errors['cancelled_at'] = ValidationError("cancelled_at is required for CANCELLED sessions.")
            if not row.get('cancelled_by'):
                errors['cancelled_by'] = ValidationError("cancelled_by is required for CANCELLED sessions.")

        if errors:
            from import_export.results import RowResult, Error
            res = RowResult()
            res.import_type = RowResult.IMPORT_TYPE_ERROR
            for field, error in errors.items():
                res.errors.append(Error(error, number=kwargs.get('row_number')))
            return res

        try:
            res = super().import_row(row, instance_loader, **kwargs)
            return res
        except Exception as e:
            from import_export.results import RowResult, Error
            res = RowResult()
            res.import_type = RowResult.IMPORT_TYPE_ERROR
            res.errors.append(Error(e))
            return res

    def validate_instance(self, instance, import_validation_errors=None, validate_unique=True):
        if import_validation_errors is None:
            import_validation_errors = {}
        
        if not getattr(instance, 'coach', None):
            import_validation_errors['coach'] = ValidationError("Coach is required.", code='required')

        if instance.status == 'CANCELLED':
            if not instance.cancel_reason:
                import_validation_errors['cancel_reason'] = ValidationError("cancel_reason is required for CANCELLED sessions.", code='required')
            if not instance.cancelled_at:
                import_validation_errors['cancelled_at'] = ValidationError("cancelled_at is recommended/required for CANCELLED sessions.", code='required')
            if not instance.cancelled_by:
                import_validation_errors['cancelled_by'] = ValidationError("cancelled_by is recommended for CANCELLED sessions.", code='required')

        if import_validation_errors:
            raise ValidationError(import_validation_errors)

        super().validate_instance(instance, import_validation_errors, validate_unique)

class SessionAttendeeResource(resources.ModelResource):
    class Meta:
        model = SessionAttendee
        fields = (
            'id', 'intent_status', 'attendance_status', 
            'payment_status', 'arrived_at', 'paid_at'
        )
        # identification is handled manually in get_or_init_instance
        import_id_fields = () 
        skip_unchanged = True
        report_skipped = True

    def get_or_init_instance(self, instance_loader, row):
        """Manually find SessionAttendee based on session and user usernames."""
        from django.utils.dateparse import parse_datetime
        from django.utils import timezone
        import datetime
        dt_str = row.get('session_datetime')
        coach_un = row.get('coach_username')
        user_un = row.get('user_username')
        
        # Parse datetime and ensure it's aware
        dt = parse_datetime(dt_str)
        if dt and timezone.is_naive(dt):
            dt = timezone.make_aware(dt)

        try:
            session = Session.objects.get(starts_at=dt, coach__username=coach_un)
            user = User.objects.get(username=user_un)
            instance = SessionAttendee.objects.get(session=session, user=user)
            return instance, False
        except (Session.DoesNotExist, User.DoesNotExist, SessionAttendee.DoesNotExist):
            # If it doesn't exist, create it (init only)
            instance = SessionAttendee()
            if 'session' in locals(): instance.session = session
            if 'user' in locals(): instance.user = user
            return instance, True
        except Exception:
            return SessionAttendee(), True

    def import_row(self, row, instance_loader, **kwargs):
        kwargs['validate_unique'] = True
        
        # Resolve instance early to catch errors if it fails
        instance, created = self.get_or_init_instance(instance_loader, row)
        
        # Perform custom validation on row data since instance might be empty/None
        errors = {}
        if not getattr(instance, 'session', None):
            errors['session'] = ValidationError("Session not found.", code='invalid')
        if not getattr(instance, 'user', None):
            errors['user'] = ValidationError("User not found.", code='invalid')
        
        att_status = row.get('attendance_status')
        arr_at = row.get('arrived_at')
        if att_status == 'ARRIVED' and not arr_at:
            errors['arrived_at'] = ValidationError("arrived_at required if attendance_status is ARRIVED")

        pay_status = row.get('payment_status')
        p_at = row.get('paid_at')
        if pay_status == 'PAID' and not p_at:
            errors['paid_at'] = ValidationError("paid_at required if payment_status is PAID")

        if errors:
            from import_export.results import RowResult, Error
            res = RowResult()
            res.import_type = RowResult.IMPORT_TYPE_ERROR
            for field, error in errors.items():
                res.errors.append(Error(error, number=kwargs.get('row_number')))
            return res

        return super().import_row(row, instance_loader, **kwargs)

    def validate_instance(self, instance, import_validation_errors=None, validate_unique=True):
        if import_validation_errors is None:
            import_validation_errors = {}

        if not getattr(instance, 'session_id', None) and not getattr(instance, 'session', None):
            import_validation_errors['session'] = ValidationError(
                "Session not found for provided datetime and coach.",
                code='invalid'
            )

        if not getattr(instance, 'user_id', None) and not getattr(instance, 'user', None):
            import_validation_errors['user'] = ValidationError(
                "Attendee user not found.",
                code='invalid'
            )

        attendance_status = getattr(instance, 'attendance_status', None)
        arrived_at = getattr(instance, 'arrived_at', None)
        if attendance_status == 'ARRIVED' and not arrived_at:
            import_validation_errors['arrived_at'] = ValidationError(
                "arrived_at required if attendance_status is ARRIVED",
                code='required'
            )

        payment_status = getattr(instance, 'payment_status', None)
        paid_at = getattr(instance, 'paid_at', None)
        if payment_status == 'PAID' and not paid_at:
            import_validation_errors['paid_at'] = ValidationError(
                "paid_at required if payment_status is PAID",
                code='required'
            )
        
        # Also call model validation
        try:
            instance.clean()
        except ValidationError as e:
            import_validation_errors.update(e.message_dict if hasattr(e, 'message_dict') else {'__all__': e.messages})
