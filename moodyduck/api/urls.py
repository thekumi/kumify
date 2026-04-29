from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ActivityViewSet,
    CBTRecordViewSet,
    CurrentProfileView,
    DreamViewSet,
    HabitLogViewSet,
    HabitViewSet,
    HealthLogViewSet,
    HealthParameterViewSet,
    MoodViewSet,
    StatusCheckView,
    StatusViewSet,
    VaccinationViewSet,
)

router = DefaultRouter()
router.register("moods", MoodViewSet, basename="mood")
router.register("activities", ActivityViewSet, basename="activity")
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
router.register("cbt/records", CBTRecordViewSet, basename="cbt-record")
router.register("dreams", DreamViewSet, basename="dream")

urlpatterns = [
    path("", include(router.urls)),
    path("profile/", CurrentProfileView.as_view(), name="profile"),
    path("status/", StatusCheckView.as_view(), name="status"),
    path("auth/", include("rest_framework.urls")),
]
