from django.contrib import admin

from .models import (
    HealthLog,
    HealthParameter,
    HealthRecord,
    Medication,
    Vaccination,
)


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ("pk", "user")
    list_filter = ("user",)
    search_fields = ("user__username",)
    raw_id_fields = ("user",)


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


@admin.register(Vaccination)
class VaccinationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "target_disease",
        "user",
        "administered_on",
        "next_due",
        "provider",
    )
    list_filter = ("user", "administered_on", "next_due")
    search_fields = ("name", "target_disease", "provider", "batch_number", "notes")
    date_hierarchy = "administered_on"
    raw_id_fields = ("user",)
