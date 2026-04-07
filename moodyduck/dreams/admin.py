from django.contrib import admin

from .models import Dream, DreamMedia, DreamTheme, DreamThemeRating, Theme, ThemeRating


class ThemeRatingInline(admin.TabularInline):
    model = ThemeRating
    extra = 0


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "icon")
    list_filter = ("user",)
    search_fields = ("name", "user__username")
    inlines = (ThemeRatingInline,)
    raw_id_fields = ("user",)


@admin.register(ThemeRating)
class ThemeRatingAdmin(admin.ModelAdmin):
    list_display = ("name", "theme", "value", "icon")
    list_filter = ("theme",)
    search_fields = ("name",)


class DreamThemeInline(admin.TabularInline):
    model = DreamTheme
    extra = 0
    raw_id_fields = ("theme",)


class DreamThemeRatingInline(admin.TabularInline):
    model = DreamThemeRating
    extra = 0
    raw_id_fields = ("theme_rating",)


class DreamMediaInline(admin.TabularInline):
    model = DreamMedia
    extra = 0


@admin.register(Dream)
class DreamAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "timestamp", "lucid", "wet", "type")
    list_filter = ("user", "lucid", "wet", "type")
    search_fields = ("title", "content", "user__username")
    date_hierarchy = "timestamp"
    inlines = (DreamThemeInline, DreamThemeRatingInline, DreamMediaInline)
    raw_id_fields = ("user", "mood")


admin.site.register(DreamMedia)
admin.site.register(DreamTheme)
admin.site.register(DreamThemeRating)
