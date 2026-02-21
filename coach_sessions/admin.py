from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Session, SessionAttendee
from .resources import SessionResource, SessionAttendeeResource

class SessionAttendeeInline(admin.TabularInline):
    model = SessionAttendee
    extra = 1

@admin.register(Session)
class SessionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = SessionResource
    list_display = ('starts_at', 'location', 'status', 'capacity', 'coach')
    list_filter = ('status', 'location', 'coach')
    inlines = [SessionAttendeeInline]
    actions = ['cancel_sessions']

    def cancel_sessions(self, request, queryset):
        for session in queryset:
            session.cancel(reason="Cancelled via admin")
    cancel_sessions.short_description = "Cancel selected sessions"

@admin.register(SessionAttendee)
class SessionAttendeeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = SessionAttendeeResource
    list_display = ('user', 'session', 'intent_status', 'attendance_status', 'payment_status', 'get_lateness')
    list_filter = ('intent_status', 'attendance_status', 'payment_status', 'session__starts_at')
    search_fields = ('user__username', 'session__location')

    def get_lateness(self, obj):
        return obj.lateness
    get_lateness.short_description = 'Lateness'
