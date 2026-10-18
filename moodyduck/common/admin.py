from django.contrib import admin

from .models import ErrorLog


@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ["timestamp", "method", "path", "exception_type", "user", "resolved"]
    list_filter = ["resolved", "method", "exception_type"]
    search_fields = ["path", "exception_type", "exception_value", "traceback"]
    readonly_fields = [
        "timestamp",
        "path",
        "method",
        "user",
        "exception_type",
        "exception_value",
        "traceback",
    ]
    list_per_page = 50

    def has_add_permission(self, request):
        return False
