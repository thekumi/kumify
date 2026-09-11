from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ActivityViewSet,
    CBTRecordViewSet,
    CurrentEmergencyProfileView,
    CurrentProfileView,
    DashboardStatsView,
    DreamMediaEncryptView,
    DreamViewSet,
    EmergencyAccessLogViewSet,
    HabitLogViewSet,
    HabitViewSet,
    HealthLogViewSet,
    HealthParameterViewSet,
    MedicationViewSet,
    MeView,
    MoodViewSet,
    PersonViewSet,
    StagingView,
    StatusCheckView,
    StatusMediaEncryptView,
    StatusViewSet,
    ThemeViewSet,
    TokenLoginView,
    UserDeviceViewSet,
    UserKeyBackupView,
    UserKeyPairView,
    VaccinationViewSet,
)

router = DefaultRouter()
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

urlpatterns = [
    path("", include(router.urls)),
    path("profile/", CurrentProfileView.as_view(), name="profile"),
    path(
        "emergency-profile/",
        CurrentEmergencyProfileView.as_view(),
        name="emergency-profile",
    ),
    path("status/", StatusCheckView.as_view(), name="status"),
    path("staging/", StagingView.as_view(), name="staging"),
    path(
        "media/status/<int:pk>/", StatusMediaEncryptView.as_view(), name="media-status"
    ),
    path("media/dream/<int:pk>/", DreamMediaEncryptView.as_view(), name="media-dream"),
    path("keybackup/", UserKeyBackupView.as_view(), name="keybackup"),
    path("userkeypair/", UserKeyPairView.as_view(), name="userkeypair"),
    path("me/", MeView.as_view(), name="me"),
    path("stats/dashboard/", DashboardStatsView.as_view(), name="stats-dashboard"),
    path("auth/token/", TokenLoginView.as_view(), name="api_token_auth"),
    path("auth/", include("rest_framework.urls")),
]
