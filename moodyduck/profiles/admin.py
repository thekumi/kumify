from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import UserProfile

User = get_user_model()


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fields = ("display_name", "timezone", "pgp_key")


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = (
        "username",
        "email",
        "get_display_name",
        "is_active",
        "is_staff",
        "date_joined",
        "last_login",
    )
    list_filter = ("is_active", "is_staff", "is_superuser")

    @admin.display(description="Display name")
    def get_display_name(self, obj):
        try:
            return obj.userprofile.display_name or ""
        except UserProfile.DoesNotExist:
            return ""


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "timezone")
    search_fields = ("user__username", "user__email", "display_name")
    raw_id_fields = ("user",)
