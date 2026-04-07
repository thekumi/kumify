from django.urls import path
from .views import (
    UserProfileView,
    UserProfileEditView,
    IntegrationsView,
    TelegramPairingView,
    MatrixSettingsView,
    NtfySettingsView,
)

app_name = "profiles"

urlpatterns = [
    path("", UserProfileView.as_view(), name="profile_view"),
    path("edit/", UserProfileEditView.as_view(), name="profile_edit"),
    path("integrations/", IntegrationsView.as_view(), name="integrations"),
    path(
        "integrations/telegram/", TelegramPairingView.as_view(), name="telegram_pairing"
    ),
    path("integrations/matrix/", MatrixSettingsView.as_view(), name="matrix_settings"),
    path("integrations/ntfy/", NtfySettingsView.as_view(), name="ntfy_settings"),
]
