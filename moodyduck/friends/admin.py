from django.contrib import admin

from .models import Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "nickname",
        "user",
        "birthday",
        "days_until_birthday",
        "last_contact",
        "days_since_contact",
    )
    list_filter = ("user",)
    search_fields = ("name", "nickname", "email", "user__username")
    raw_id_fields = ("user",)
    date_hierarchy = "created_at"
    fieldsets = (
        (None, {"fields": ("user", "name", "nickname")}),
        ("Contact", {"fields": ("email", "phone", "address", "last_contact")}),
        ("Personal", {"fields": ("birthday", "notes")}),
    )
