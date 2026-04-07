from django.urls import path
from . import views

app_name = "health"

urlpatterns = [
    path("", views.MedicationListView.as_view(), name="medication_list"),
    path(
        "medication/new/",
        views.MedicationCreateView.as_view(),
        name="medication_create",
    ),
    path(
        "medication/<int:id>/edit/",
        views.MedicationEditView.as_view(),
        name="medication_edit",
    ),
    path(
        "medication/<int:id>/delete/",
        views.MedicationDeleteView.as_view(),
        name="medication_delete",
    ),
    path("settings/", views.MedicationSettingsView.as_view(), name="settings"),
    path("parameter/", views.HealthParameterListView.as_view(), name="parameter_list"),
    path(
        "parameter/new/",
        views.HealthParameterCreateView.as_view(),
        name="parameter_create",
    ),
    path(
        "parameter/<int:id>/edit/",
        views.HealthParameterEditView.as_view(),
        name="parameter_edit",
    ),
    path(
        "parameter/<int:id>/delete/",
        views.HealthParameterDeleteView.as_view(),
        name="parameter_delete",
    ),
    path("log/", views.HealthLogListView.as_view(), name="log_list"),
    path("log/new/", views.HealthLogCreateView.as_view(), name="log_create"),
    path("log/<int:id>/edit/", views.HealthLogEditView.as_view(), name="log_edit"),
    path(
        "log/<int:id>/delete/", views.HealthLogDeleteView.as_view(), name="log_delete"
    ),
]
