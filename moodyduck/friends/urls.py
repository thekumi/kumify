from django.urls import path

from .views import (
    PersonListView,
    PersonViewView,
    PersonCreateView,
    PersonEditView,
    PersonDeleteView,
)

app_name = "friends"

urlpatterns = [
    path("", PersonListView.as_view(), name="person_list"),
    path("person/<int:id>/view/", PersonViewView.as_view(), name="person_view"),
    path("person/<int:id>/edit/", PersonEditView.as_view(), name="person_edit"),
    path("person/<int:id>/delete/", PersonDeleteView.as_view(), name="person_delete"),
    path("person/new/", PersonCreateView.as_view(), name="person_create"),
]
