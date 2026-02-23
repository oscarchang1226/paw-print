from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path
from .models import Account, TransactionImportSource, ImportBatch, RawTransaction
from .importer import CSVImporter

@admin.register(ImportBatch)
class ImportBatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'source', 'status', 'total_rows', 'uploaded_at')
    readonly_fields = ('id', 'uploaded_at', 'uploaded_by', 'status', 'total_rows', 'imported_rows', 'forced_duplicate_count')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv_view), name='finance_import_csv'),
        ]
        return custom_urls + urls

    def import_csv_view(self, request):
        if request.method == 'POST':
            account_id = request.POST.get('account')
            source_id = request.POST.get('source')
            csv_file = request.FILES.get('csv_file')
            dry_run = request.POST.get('dry_run') == 'on'
            force = request.POST.get('force') == 'on'
            force_reason = request.POST.get('force_reason')

            if not account_id or not source_id or not csv_file:
                messages.error(request, "Account, Source, and CSV File are required.")
            elif force and not force_reason:
                messages.error(request, "Force Reason is required when forcing import.")
            else:
                try:
                    account = Account.objects.get(id=account_id)
                    source = TransactionImportSource.objects.get(id=source_id)
                    batch = ImportBatch.objects.create(
                        account=account,
                        source=source,
                        uploaded_by=request.user,
                        status='DRY_RUN'
                    )
                    importer = CSVImporter(batch)
                    result = importer.run_import(
                        csv_file, 
                        dry_run=dry_run, 
                        force=force, 
                        force_reason=force_reason,
                        user=request.user
                    )

                    if result['status'] == 'FAILED':
                        messages.error(request, f"Import failed: {result['errors']}")
                        batch.status = 'FAILED'
                        batch.save()
                    elif result['status'] == 'BLOCKED_BY_DUPLICATES':
                        messages.warning(request, "Import blocked by duplicates. Use 'Force Import' and provide a reason to proceed.")
                    elif result['status'] == 'SUCCESS':
                        messages.success(request, f"Imported {result['total']} rows successfully.")
                        return redirect('admin:finance_importbatch_changelist')
                    
                    context = {
                        **self.admin_site.each_context(request),
                        'result': result,
                        'batch': batch,
                        'accounts': Account.objects.all(),
                        'sources': TransactionImportSource.objects.all(),
                        'dry_run': dry_run,
                    }
                    return render(request, 'admin/finance/import_csv.html', context)
                except Exception as e:
                    messages.error(request, f"System error: {str(e)}")

        context = {
            **self.admin_site.each_context(request),
            'accounts': Account.objects.all(),
            'sources': TransactionImportSource.objects.all(),
        }
        return render(request, 'admin/finance/import_csv.html', context)

@admin.register(RawTransaction)
class RawTransactionAdmin(admin.ModelAdmin):
    list_display = ('txn_at_utc', 'account', 'description', 'amount', 'is_forced_duplicate')
    readonly_fields = [f.name for f in RawTransaction._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

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
