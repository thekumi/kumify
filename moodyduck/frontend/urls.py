from django.urls import path

from .views import DashboardView, UserRegistrationView

app_name = "frontend"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("accounts/register/", UserRegistrationView.as_view(), name="register"),
]
