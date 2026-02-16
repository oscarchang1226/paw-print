from django.contrib import admin
from .models import Session, SessionAttendee

class SessionAttendeeInline(admin.TabularInline):
    model = SessionAttendee
    extra = 1

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('starts_at', 'location', 'status', 'capacity')
    list_filter = ('status', 'location')
    inlines = [SessionAttendeeInline]
    actions = ['cancel_sessions']

    def cancel_sessions(self, request, queryset):
        for session in queryset:
            session.cancel(reason="Cancelled via admin")
    cancel_sessions.short_description = "Cancel selected sessions"

@admin.register(SessionAttendee)
class SessionAttendeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'session', 'intent_status', 'attendance_status', 'payment_status', 'get_lateness')
    list_filter = ('intent_status', 'attendance_status', 'payment_status', 'session__starts_at')
    search_fields = ('user__username', 'session__location')

    def get_lateness(self, obj):
        return obj.lateness
    get_lateness.short_description = 'Lateness'
