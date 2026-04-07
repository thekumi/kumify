from django.urls import path

from .views import (
    HabitListView,
    HabitCreateView,
    HabitEditView,
    HabitDeleteView,
    HabitLogListView,
    HabitLogCreateView,
    HabitLogEditView,
    HabitLogDeleteView,
)

app_name = "habits"

urlpatterns = [
    path("", HabitListView.as_view(), name="habit_list"),
    path("habit/<int:id>/edit/", HabitEditView.as_view(), name="habit_edit"),
    path("habit/<int:id>/delete/", HabitDeleteView.as_view(), name="habit_delete"),
    path("habit/new/", HabitCreateView.as_view(), name="habit_create"),
    path("log/", HabitLogListView.as_view(), name="log_list"),
    path("log/new/<int:habit_id>/", HabitLogCreateView.as_view(), name="log_create"),
    path("log/<int:id>/edit/", HabitLogEditView.as_view(), name="log_edit"),
    path("log/<int:id>/delete/", HabitLogDeleteView.as_view(), name="log_delete"),
]
