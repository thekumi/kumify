from django.urls import path

from .views import (
    ThoughtRecordListView,
    ThoughtRecordViewView,
    ThoughtRecordCreateView,
    ThoughtRecordEditView,
    ThoughtRecordDeleteView,
)

app_name = "cbt"

urlpatterns = [
    path("", ThoughtRecordListView.as_view(), name="record_list"),
    path("record/new/", ThoughtRecordCreateView.as_view(), name="record_create"),
    path("record/<int:id>/view/", ThoughtRecordViewView.as_view(), name="record_view"),
    path("record/<int:id>/edit/", ThoughtRecordEditView.as_view(), name="record_edit"),
    path(
        "record/<int:id>/delete/",
        ThoughtRecordDeleteView.as_view(),
        name="record_delete",
    ),
]
