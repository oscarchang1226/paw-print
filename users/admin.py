from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export.admin import ImportExportModelAdmin
from .models import User
from .resources import UserResource

@admin.register(User)
class CustomUserAdmin(ImportExportModelAdmin, UserAdmin):
    resource_class = UserResource
    pass
