from django.db import models
from django.conf import settings

class SessionAttendeeManager(models.Manager):
    def billing_candidates(self):
        return self.filter(
            session__status='COMPLETED',
            attendance_status__in=['ATTENDED', 'NOSHOW'],
            payment_status='UNBILLED'
        )

    def awaiting_payment(self):
        return self.filter(
            session__status='COMPLETED',
            payment_status='REQUESTED'
        )

class Session(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]

    starts_at = models.DateTimeField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    location = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    
    cancel_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_sessions'
    )

    def __str__(self):
        return f"Session at {self.location} on {self.starts_at}"

    def cancel(self, reason, cancelled_by=None):
        from django.utils import timezone
        self.status = 'CANCELLED'
        self.cancel_reason = reason
        self.cancelled_at = timezone.now()
        self.cancelled_by = cancelled_by
        self.save()
        self.attendees.all().update(payment_status='WAIVED')

class SessionAttendee(models.Model):
    INTENT_CHOICES = [
        ('PLANNED', 'Planned'),
        ('INVITED', 'Invited'),
        ('CONFIRMED', 'Confirmed'),
        ('DECLINED', 'Declined'),
    ]
    
    ATTENDANCE_CHOICES = [
        ('ARRIVED', 'Arrived'),
        ('ATTENDED', 'Attended'),
        ('NOSHOW', 'No Show'),
    ]
    
    PAYMENT_CHOICES = [
        ('UNBILLED', 'Unbilled'),
        ('REQUESTED', 'Requested'),
        ('PAID', 'Paid'),
        ('WAIVED', 'Waived'),
    ]

    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='attendees')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='session_attendances')
    
    intent_status = models.CharField(max_length=20, choices=INTENT_CHOICES, default='PLANNED')
    attendance_status = models.CharField(max_length=20, choices=ATTENDANCE_CHOICES, null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='UNBILLED')
    
    arrived_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    objects = SessionAttendeeManager()

    class Meta:
        unique_together = ('session', 'user')

    def __str__(self):
        return f"{self.user} for {self.session}"

    @property
    def lateness(self):
        if self.arrived_at and self.session.starts_at:
            return self.arrived_at - self.session.starts_at
        return None
