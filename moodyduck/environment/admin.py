from django.contrib import admin

from .models import CO2Category, CO2Entry, CO2Offset


@admin.register(CO2Category)
class CO2CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "icon")
    list_filter = ("user",)
    search_fields = ("name", "user__username")
    raw_id_fields = ("user",)


@admin.register(CO2Entry)
class CO2EntryAdmin(admin.ModelAdmin):
    list_display = ("description", "user", "date", "amount_kg", "category")
    list_filter = ("user", "category")
    search_fields = ("description", "user__username")
    date_hierarchy = "date"
    raw_id_fields = ("user", "category")


@admin.register(CO2Offset)
class CO2OffsetAdmin(admin.ModelAdmin):
    list_display = ("description", "user", "date", "amount_kg", "provider")
    list_filter = ("user",)
    search_fields = ("description", "user__username", "provider")
    date_hierarchy = "date"
    raw_id_fields = ("user",)
