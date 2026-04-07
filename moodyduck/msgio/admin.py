from django.contrib import admin

from .models import (
    GatewayUser,
    GatewayUserSetting,
    Notification,
    NotificationDailySchedule,
    NotificationDatetimeSchedule,
    NotificationDispatcher,
    TelegramPairingToken,
)


class GatewayUserSettingInline(admin.TabularInline):
    model = GatewayUserSetting
    extra = 1
    fields = ("key", "value")


@admin.register(GatewayUser)
class GatewayUserAdmin(admin.ModelAdmin):
    list_display = ("user", "gateway")
    list_filter = ("gateway",)
    search_fields = ("user__username", "user__email")
    inlines = (GatewayUserSettingInline,)
    raw_id_fields = ("user",)


@admin.register(GatewayUserSetting)
class GatewayUserSettingAdmin(admin.ModelAdmin):
    list_display = ("gatewayuser", "key", "value")
    list_filter = ("key",)
    search_fields = ("gatewayuser__user__username", "key", "value")
    raw_id_fields = ("gatewayuser",)


class NotificationDispatcherInline(admin.TabularInline):
    model = NotificationDispatcher
    extra = 1
    fields = ("dispatcher",)


class NotificationDatetimeScheduleInline(admin.TabularInline):
    model = NotificationDatetimeSchedule
    extra = 0
    fields = ("datetime", "sent")
    readonly_fields = ("sent",)


class NotificationDailyScheduleInline(admin.TabularInline):
    model = NotificationDailySchedule
    extra = 0
    fields = ("time", "last_sent")
    readonly_fields = ("last_sent",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "app", "short_content")
    list_filter = ("app",)
    search_fields = ("recipient__username", "content", "app")
    inlines = (
        NotificationDispatcherInline,
        NotificationDatetimeScheduleInline,
        NotificationDailyScheduleInline,
    )
    raw_id_fields = ("recipient",)

    @admin.display(description="Content")
    def short_content(self, obj):
        return obj.content[:80] + ("…" if len(obj.content) > 80 else "")


@admin.register(NotificationDispatcher)
class NotificationDispatcherAdmin(admin.ModelAdmin):
    list_display = ("notification", "dispatcher")
    list_filter = ("dispatcher",)
    raw_id_fields = ("notification",)


@admin.register(NotificationDatetimeSchedule)
class NotificationDatetimeScheduleAdmin(admin.ModelAdmin):
    list_display = ("notification", "datetime", "sent")
    list_filter = ("sent",)
    raw_id_fields = ("notification",)


@admin.register(NotificationDailySchedule)
class NotificationDailyScheduleAdmin(admin.ModelAdmin):
    list_display = ("notification", "time", "last_sent")
    raw_id_fields = ("notification",)


@admin.register(TelegramPairingToken)
class TelegramPairingTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "created_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("token", "created_at")
    raw_id_fields = ("user",)

    def has_add_permission(self, request):
        return False
