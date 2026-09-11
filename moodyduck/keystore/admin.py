from django.contrib import admin

from .models import UserDevice, UserKeyBackup


@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "label",
        "device_id",
        "has_data_key",
        "created_at",
        "last_seen",
    ]
    list_filter = ["user"]
    readonly_fields = ["device_id", "created_at", "last_seen"]

    @admin.display(boolean=True)
    def has_data_key(self, obj):
        return obj.encrypted_data_key is not None


@admin.register(UserKeyBackup)
class UserKeyBackupAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at", "updated_at"]
    readonly_fields = ["created_at", "updated_at"]
