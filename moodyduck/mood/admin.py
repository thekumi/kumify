from django.contrib import admin

from .models import (
    Activity,
    ActivityCategory,
    Aspect,
    AspectRating,
    Mood,
    Status,
    StatusActivity,
    StatusAspectRating,
    StatusMedia,
)


@admin.register(Mood)
class MoodAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "value", "icon")
    list_filter = ("user",)
    search_fields = ("name", "user__username")


@admin.register(ActivityCategory)
class ActivityCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "icon")
    list_filter = ("user",)
    search_fields = ("name", "user__username")


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "category", "icon")
    list_filter = ("user", "category")
    search_fields = ("name", "user__username")


class StatusActivityInline(admin.TabularInline):
    model = StatusActivity
    extra = 0
    raw_id_fields = ("activity",)


class StatusAspectRatingInline(admin.TabularInline):
    model = StatusAspectRating
    extra = 0
    raw_id_fields = ("aspect_rating",)


class StatusMediaInline(admin.TabularInline):
    model = StatusMedia
    extra = 0


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user", "mood", "short_text", "is_encrypted_display")
    list_filter = ("user", "mood")
    search_fields = ("user__username", "text", "title")
    date_hierarchy = "timestamp"
    inlines = (StatusActivityInline, StatusAspectRatingInline, StatusMediaInline)
    raw_id_fields = ("user", "mood")

    @admin.display(description="Encrypted", boolean=True)
    def is_encrypted_display(self, obj):
        return obj.is_encrypted


@admin.register(Aspect)
class AspectAdmin(admin.ModelAdmin):
    list_display = ("name", "user")
    list_filter = ("user",)
    search_fields = ("name", "user__username")


@admin.register(AspectRating)
class AspectRatingAdmin(admin.ModelAdmin):
    list_display = ("name", "aspect", "value", "icon")
    list_filter = ("aspect",)
    search_fields = ("name",)


admin.site.register(StatusMedia)
admin.site.register(StatusActivity)
admin.site.register(StatusAspectRating)
