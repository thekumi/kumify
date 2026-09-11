from django.urls import path

from .views import GPSLogView

app_name = "gpslog"

urlpatterns = [
    path("<uuid:track>/<uuid:token>/", GPSLogView.as_view(), name="gpslog"),
]
