from django.urls import path
from . import views

app_name = "environment"

urlpatterns = [
    path("", views.CO2DashboardView.as_view(), name="dashboard"),
    path("entries/", views.CO2EntryListView.as_view(), name="entry_list"),
    path("entries/new/", views.CO2EntryCreateView.as_view(), name="entry_create"),
    path("entries/<int:id>/edit/", views.CO2EntryEditView.as_view(), name="entry_edit"),
    path(
        "entries/<int:id>/delete/",
        views.CO2EntryDeleteView.as_view(),
        name="entry_delete",
    ),
    path("offsets/", views.CO2OffsetListView.as_view(), name="offset_list"),
    path("offsets/new/", views.CO2OffsetCreateView.as_view(), name="offset_create"),
    path(
        "offsets/<int:id>/edit/", views.CO2OffsetEditView.as_view(), name="offset_edit"
    ),
    path(
        "offsets/<int:id>/delete/",
        views.CO2OffsetDeleteView.as_view(),
        name="offset_delete",
    ),
    path("categories/", views.CO2CategoryListView.as_view(), name="category_list"),
    path(
        "categories/new/", views.CO2CategoryCreateView.as_view(), name="category_create"
    ),
    path(
        "categories/<int:id>/edit/",
        views.CO2CategoryEditView.as_view(),
        name="category_edit",
    ),
    path(
        "categories/<int:id>/delete/",
        views.CO2CategoryDeleteView.as_view(),
        name="category_delete",
    ),
]
