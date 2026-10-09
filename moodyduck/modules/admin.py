from django.contrib import admin

from .models import Feature, UserFeaturePreference, UserNavOrder


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ["slug", "name", "enabled_for", "shown_by_default"]
    list_editable = ["enabled_for", "shown_by_default"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(UserFeaturePreference)
class UserFeaturePreferenceAdmin(admin.ModelAdmin):
    list_display = ["user", "feature", "visible"]
    list_filter = ["feature", "visible"]


@admin.register(UserNavOrder)
class UserNavOrderAdmin(admin.ModelAdmin):
    list_display = ["user"]
    raw_id_fields = ["user"]
