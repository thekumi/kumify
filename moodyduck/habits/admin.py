from django.contrib import admin

from .models import (
    DailyHabitSchedule,
    DateHabitSchedule,
    Habit,
    HabitLog,
    HabitSchedule,
    MonthlyHabitSchedule,
    WeeklyHabitSchedule,
)


class HabitScheduleInline(admin.TabularInline):
    model = HabitSchedule
    extra = 0
    show_full_result_count = False


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "icon", "color")
    list_filter = ("user",)
    search_fields = ("name", "user__username")
    raw_id_fields = ("user",)


@admin.register(HabitLog)
class HabitLogAdmin(admin.ModelAdmin):
    list_display = ("habit", "date")
    list_filter = ("habit__user", "habit")
    date_hierarchy = "date"
    raw_id_fields = ("habit",)


@admin.register(MonthlyHabitSchedule)
class MonthlyHabitScheduleAdmin(admin.ModelAdmin):
    list_display = ("habit", "day", "active")
    list_filter = ("active",)
    raw_id_fields = ("habit",)


@admin.register(WeeklyHabitSchedule)
class WeeklyHabitScheduleAdmin(admin.ModelAdmin):
    list_display = ("habit", "weekdays", "active")
    list_filter = ("active",)
    raw_id_fields = ("habit",)


@admin.register(DailyHabitSchedule)
class DailyHabitScheduleAdmin(admin.ModelAdmin):
    list_display = ("habit", "active")
    list_filter = ("active",)
    raw_id_fields = ("habit",)


@admin.register(DateHabitSchedule)
class DateHabitScheduleAdmin(admin.ModelAdmin):
    list_display = ("habit", "date", "active")
    list_filter = ("active",)
    date_hierarchy = "date"
    raw_id_fields = ("habit",)
