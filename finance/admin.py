from django.contrib import admin
from .models import Account, TransactionImportSource

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'currency', 'institution', 'last4')
    readonly_fields = ('created_at', 'created_by')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(TransactionImportSource)
class TransactionImportSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'delimiter', 'has_header', 'date_format')
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        column_help = "Column name (if header exists) or numeric index as string (e.g., '3')."
        form.base_fields['date_column'].help_text = column_help
        form.base_fields['description_column'].help_text = column_help
        form.base_fields['amount_column'].help_text = column_help
        form.base_fields['category_column'].help_text = f"{column_help} Optional."
        form.base_fields['date_format'].help_text = (
            "Python strftime format (e.g., '%m/%d/%Y' for 01/31/2024, "
            "'%Y-%m-%d' for 2024-01-31)."
        )
        return form
