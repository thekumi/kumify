from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ActivityCategoryViewSet,
    ActivityViewSet,
    CBTRecordViewSet,
    ChangePasswordView,
    CurrentEmergencyProfileView,
    CurrentProfileView,
    CustomPropertyViewSet,
    DashboardStatsView,
    DreamMediaEncryptView,
    DreamViewSet,
    EmergencyAccessLogViewSet,
    ErrorLogViewSet,
    HabitLogViewSet,
    HabitViewSet,
    HealthLogViewSet,
    HealthParameterViewSet,
    MedicationViewSet,
    MeView,
    MoodViewSet,
    NotificationSettingsView,
    PersonViewSet,
    PushSubscriptionViewSet,
    RegisterView,
    ScrubView,
    ServerInfoView,
    StagingView,
    StatusCheckView,
    StatusMediaEncryptView,
    StatusViewSet,
    SyncDeletionsView,
    TestPushView,
    ThemeViewSet,
    TokenLoginView,
    UnifiedPushSubscriptionView,
    UserDeviceViewSet,
    UserKeyBackupView,
    UserKeyPairView,
    VaccinationViewSet,
    VapidPublicKeyView,
)

router = DefaultRouter()
router.register(
    "activity-categories", ActivityCategoryViewSet, basename="activity-category"
)
router.register("properties", CustomPropertyViewSet, basename="property")
router.register("moods", MoodViewSet, basename="mood")
router.register("activities", ActivityViewSet, basename="activity")
router.register("friends", PersonViewSet, basename="friend")
router.register("statuses", StatusViewSet, basename="status")
router.register("habits", HabitViewSet, basename="habit")
router.register("habit-logs", HabitLogViewSet, basename="habit-log")
router.register(
    "health/parameters", HealthParameterViewSet, basename="health-parameter"
)
router.register("health/logs", HealthLogViewSet, basename="health-log")
router.register(
    "health/vaccinations", VaccinationViewSet, basename="health-vaccination"
)
router.register("health/medications", MedicationViewSet, basename="health-medication")
router.register("cbt/records", CBTRecordViewSet, basename="cbt-record")
router.register("dreams", DreamViewSet, basename="dream")
router.register("dream-themes", ThemeViewSet, basename="dream-theme")
router.register(
    "emergency-access-logs", EmergencyAccessLogViewSet, basename="emergency-access-log"
)
router.register("devices", UserDeviceViewSet, basename="device")
router.register(
    "push-subscriptions", PushSubscriptionViewSet, basename="push-subscription"
)
router.register("error-logs", ErrorLogViewSet, basename="error-log")

urlpatterns = [
    path("planner/", include("moodyduck.planner.urls")),
    path("", include(router.urls)),
    path("profile/", CurrentProfileView.as_view(), name="profile"),
    path(
        "emergency-profile/",
        CurrentEmergencyProfileView.as_view(),
        name="emergency-profile",
    ),
    path("status/", StatusCheckView.as_view(), name="status"),
    path("staging/", StagingView.as_view(), name="staging"),
    path("scrub/", ScrubView.as_view(), name="scrub"),
    path(
        "media/status/<int:pk>/", StatusMediaEncryptView.as_view(), name="media-status"
    ),
    path("media/dream/<int:pk>/", DreamMediaEncryptView.as_view(), name="media-dream"),
    path("keybackup/", UserKeyBackupView.as_view(), name="keybackup"),
    path("userkeypair/", UserKeyPairView.as_view(), name="userkeypair"),
    path("me/", MeView.as_view(), name="me"),
    path("stats/dashboard/", DashboardStatsView.as_view(), name="stats-dashboard"),
    path("sync/deletions/", SyncDeletionsView.as_view(), name="sync-deletions"),
    path("auth/token/", TokenLoginView.as_view(), name="api_token_auth"),
    path("auth/register/", RegisterView.as_view(), name="api_register"),
    path("auth/server-info/", ServerInfoView.as_view(), name="api_server_info"),
    path(
        "auth/password/change/",
        ChangePasswordView.as_view(),
        name="api_password_change",
    ),
    path("auth/", include("rest_framework.urls")),
    path(
        "notification-settings/",
        NotificationSettingsView.as_view(),
        name="notification-settings",
    ),
    path("vapid-public-key/", VapidPublicKeyView.as_view(), name="vapid-public-key"),
    path(
        "push/unifiedpush/", UnifiedPushSubscriptionView.as_view(), name="unifiedpush"
    ),
    path("push/test/", TestPushView.as_view(), name="push-test"),
]
