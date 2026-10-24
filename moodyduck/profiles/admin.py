from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import RegistrationReason, UserProfile

User = get_user_model()


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fields = ("display_name", "timezone", "pgp_key")


class RegistrationReasonInline(admin.StackedInline):
    model = RegistrationReason
    can_delete = False
    verbose_name_plural = "Registration reason"
    readonly_fields = ("reason", "requested_at")
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, RegistrationReasonInline)
    list_display = (
        "username",
        "email",
        "get_display_name",
        "is_active",
        "is_staff",
        "get_registration_reason",
        "date_joined",
        "last_login",
    )
    list_filter = ("is_active", "is_staff", "is_superuser")
    actions = ["approve_users"]

    @admin.display(description="Display name")
    def get_display_name(self, obj):
        try:
            return obj.userprofile.display_name or ""
        except UserProfile.DoesNotExist:
            return ""

    @admin.display(description="Registration reason")
    def get_registration_reason(self, obj):
        try:
            r = obj.registration_reason.reason
            return r[:60] + "…" if len(r) > 60 else r
        except RegistrationReason.DoesNotExist:
            return ""

    @admin.action(description="Approve selected users (set active)")
    def approve_users(self, request, queryset):
        updated = queryset.filter(is_active=False).update(is_active=True)
        self.message_user(request, f"{updated} user(s) approved.")


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "timezone")
    search_fields = ("user__username", "user__email", "display_name")
    raw_id_fields = ("user",)
