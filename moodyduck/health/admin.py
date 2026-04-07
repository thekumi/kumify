from django.contrib import admin

from .models import (
    HealthLog,
    HealthParameter,
    HealthRecord,
    Medication,
    MedicationCalendar,
    MedicationSchedule,
    MedicationSettings,
)


@admin.register(MedicationSettings)
class MedicationSettingsAdmin(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user__username",)
    raw_id_fields = ("user",)


class MedicationScheduleInline(admin.TabularInline):
    model = MedicationSchedule
    extra = 0


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "supply", "prn", "icon")
    list_filter = ("user", "prn")
    search_fields = ("name", "user__username")
    inlines = (MedicationScheduleInline,)
    raw_id_fields = ("user",)


@admin.register(MedicationSchedule)
class MedicationScheduleAdmin(admin.ModelAdmin):
    list_display = ("medication", "cycle_type", "cycle_count", "first", "last")
    list_filter = ("cycle_type",)
    raw_id_fields = ("medication",)


@admin.register(MedicationCalendar)
class MedicationCalendarAdmin(admin.ModelAdmin):
    list_display = ("medication", "date", "taken")
    list_filter = ("taken",)
    date_hierarchy = "date"
    raw_id_fields = ("medication",)


@admin.register(HealthParameter)
class HealthParameterAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "unit", "icon")
    list_filter = ("user",)
    search_fields = ("name", "user__username")
    raw_id_fields = ("user",)


class HealthRecordInline(admin.TabularInline):
    model = HealthRecord
    extra = 0
    raw_id_fields = ("parameter",)


@admin.register(HealthLog)
class HealthLogAdmin(admin.ModelAdmin):
    list_display = ("user", "recorded_at", "notes_short")
    list_filter = ("user",)
    search_fields = ("user__username", "notes")
    date_hierarchy = "recorded_at"
    inlines = (HealthRecordInline,)
    raw_id_fields = ("user",)

    @admin.display(description="Notes")
    def notes_short(self, obj):
        if not obj.notes:
            return ""
        return obj.notes[:60] + ("…" if len(obj.notes) > 60 else "")


@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ("log", "parameter", "value", "comment")
    search_fields = ("parameter__name", "comment")
    raw_id_fields = ("log", "parameter")
