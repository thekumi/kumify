from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from .models import UserProfile
from .forms import UserProfileForm


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = "profiles/profile_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        context["profile"] = profile
        context["title"] = _("Your Profile")
        context["subtitle"] = _("View your user profile information.")
        return context


class UserProfileEditView(LoginRequiredMixin, UpdateView):
    form_class = UserProfileForm
    template_name = "profiles/profile_edit.html"
    success_url = reverse_lazy("profiles:profile_view")

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Edit Profile")
        context["subtitle"] = _("Update your profile information.")
        return context


class TelegramPairingView(LoginRequiredMixin, TemplateView):
    template_name = "profiles/telegram_pairing.html"

    def _get_pairing(self):
        from moodyduck.msgio.models import TelegramPairingToken, GatewayUserSetting

        token, _ = TelegramPairingToken.objects.get_or_create(user=self.request.user)
        linked = GatewayUserSetting.objects.filter(
            gatewayuser__user=self.request.user,
            gatewayuser__gateway="telegram",
            key="chat_id",
        ).exists()
        return token, linked

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token, linked = self._get_pairing()
        context["pairing_token"] = token
        context["linked"] = linked
        context["title"] = _("Telegram")
        context["subtitle"] = _("Link your Telegram account to MoodyDuck.")
        return context

    def post(self, request, *args, **kwargs):
        from moodyduck.msgio.models import TelegramPairingToken

        action = request.POST.get("action")
        if action == "regenerate":
            TelegramPairingToken.objects.filter(user=request.user).delete()
        elif action == "unlink":
            from moodyduck.msgio.models import GatewayUser

            GatewayUser.objects.filter(user=request.user, gateway="telegram").delete()
        return redirect("profiles:telegram_pairing")


class IntegrationsView(LoginRequiredMixin, TemplateView):
    template_name = "profiles/integrations.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from moodyduck.msgio.models import GatewayUser

        connected = set(
            GatewayUser.objects.filter(user=self.request.user).values_list(
                "gateway", flat=True
            )
        )

        context["gateways"] = [
            {
                "id": "telegram",
                "name": "Telegram",
                "icon": "bi-telegram",
                "description": _(
                    "Log mood entries and habits via the MoodyDuck Telegram bot."
                ),
                "connected": "telegram" in connected,
                "settings_url": "profiles:telegram_pairing",
            },
            {
                "id": "matrix",
                "name": "Matrix",
                "icon": "bi-chat-dots",
                "description": _("Receive notifications in any Matrix room."),
                "connected": "matrix" in connected,
                "settings_url": "profiles:matrix_settings",
            },
            {
                "id": "ntfy",
                "name": "ntfy",
                "icon": "bi-bell",
                "description": _(
                    "Push notifications via ntfy.sh or a self-hosted ntfy server."
                ),
                "connected": "ntfy" in connected,
                "settings_url": "profiles:ntfy_settings",
            },
        ]
        context["title"] = _("Integrations")
        context["subtitle"] = _("Connect MoodyDuck to external services.")
        return context


class MatrixSettingsView(LoginRequiredMixin, TemplateView):
    template_name = "profiles/matrix_settings.html"

    def _get_room_id(self):
        from moodyduck.msgio.models import GatewayUserSetting

        try:
            return GatewayUserSetting.objects.get(
                gatewayuser__user=self.request.user,
                gatewayuser__gateway="matrix",
                key="room_id",
            ).value
        except GatewayUserSetting.DoesNotExist:
            return ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["room_id"] = self._get_room_id()
        context["connected"] = bool(context["room_id"])
        try:
            from dbsettings.functions import dbsettings

            context["bot_username"] = dbsettings.MATRIX_USERNAME
        except Exception:
            context["bot_username"] = ""
        context["title"] = _("Matrix Settings")
        context["subtitle"] = _("Connect your Matrix account to MoodyDuck.")
        return context

    def post(self, request, *args, **kwargs):
        from moodyduck.msgio.models import GatewayUser, GatewayUserSetting

        action = request.POST.get("action")
        if action == "save":
            room_id = request.POST.get("room_id", "").strip()
            if room_id:
                gw, _ = GatewayUser.objects.get_or_create(
                    user=request.user, gateway="matrix"
                )
                GatewayUserSetting.objects.update_or_create(
                    gatewayuser=gw, key="room_id", defaults={"value": room_id}
                )
        elif action == "unlink":
            from moodyduck.msgio.models import GatewayUser

            GatewayUser.objects.filter(user=request.user, gateway="matrix").delete()
        return redirect("profiles:matrix_settings")


class NtfySettingsView(LoginRequiredMixin, TemplateView):
    template_name = "profiles/ntfy_settings.html"

    def _get_topic_url(self):
        from moodyduck.msgio.models import GatewayUserSetting

        try:
            return GatewayUserSetting.objects.get(
                gatewayuser__user=self.request.user,
                gatewayuser__gateway="ntfy",
                key="topic_url",
            ).value
        except GatewayUserSetting.DoesNotExist:
            return ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["topic_url"] = self._get_topic_url()
        context["connected"] = bool(context["topic_url"])
        context["title"] = _("ntfy Settings")
        context["subtitle"] = _("Push notifications via ntfy.")
        return context

    def post(self, request, *args, **kwargs):
        from moodyduck.msgio.models import GatewayUser, GatewayUserSetting

        action = request.POST.get("action")
        if action == "save":
            topic_url = request.POST.get("topic_url", "").strip()
            if topic_url:
                gw, _ = GatewayUser.objects.get_or_create(
                    user=request.user, gateway="ntfy"
                )
                GatewayUserSetting.objects.update_or_create(
                    gatewayuser=gw, key="topic_url", defaults={"value": topic_url}
                )
        elif action == "unlink":
            from moodyduck.msgio.models import GatewayUser

            GatewayUser.objects.filter(user=request.user, gateway="ntfy").delete()
        return redirect("profiles:ntfy_settings")
