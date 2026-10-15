from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CalendarEventViewSet,
    TaskListViewSet,
    TaskViewSet,
    UserCalendarViewSet,
    VirtualDescriptorsView,
)

router = DefaultRouter()
router.register("calendars", UserCalendarViewSet, basename="calendar")
router.register("events", CalendarEventViewSet, basename="calendar-event")
router.register("task-lists", TaskListViewSet, basename="task-list")
router.register("tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("", include(router.urls)),
    path("virtual/", VirtualDescriptorsView.as_view(), name="planner-virtual"),
]
