from django.contrib import admin

from .models import EmotionRecord, ThoughtRecord


class EmotionInline(admin.TabularInline):
    model = ThoughtRecord.emotions.through
    extra = 0
    verbose_name = "Emotion (before)"


class EmotionNowInline(admin.TabularInline):
    model = ThoughtRecord.emotions_now.through
    extra = 0
    verbose_name = "Emotion (after)"


@admin.register(ThoughtRecord)
class ThoughtRecordAdmin(admin.ModelAdmin):
    list_display = ("title_or_situation", "user", "complete")
    list_filter = ("user", "complete")
    search_fields = ("title", "situation", "user__username")
    raw_id_fields = ("user",)
    exclude = ("emotions", "emotions_now")
    inlines = (EmotionInline, EmotionNowInline)

    @admin.display(description="Record")
    def title_or_situation(self, obj):
        return obj.title or (obj.situation[:60] if obj.situation else "—")


@admin.register(EmotionRecord)
class EmotionRecordAdmin(admin.ModelAdmin):
    list_display = ("emotion", "percentage")
    search_fields = ("emotion",)
