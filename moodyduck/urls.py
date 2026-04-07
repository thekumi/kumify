"""kumify URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include

from rest_framework.authtoken.views import obtain_auth_token

from moodyduck.msgio.views import TelegramWebhookView

admin.site.site_header = "MoodyDuck Administration"
admin.site.site_title = "MoodyDuck Admin"
admin.site.index_title = "MoodyDuck"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("profile/", include("moodyduck.profiles.urls", "profiles")),
    path("", include("moodyduck.frontend.urls", "frontend")),
    path("mood/", include("moodyduck.mood.urls", "mood")),
    path("cron/", include("moodyduck.cronhandler.urls", "cron")),
    path("webhooks/telegram/", TelegramWebhookView.as_view()),
    path("dreams/", include("moodyduck.dreams.urls", "dreams")),
    path("cbt/", include("moodyduck.cbt.urls", "cbt")),
    path("gpslog/", include("moodyduck.gpslog.urls")),
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("health/", include("moodyduck.health.urls", "health")),
    path("environment/", include("moodyduck.environment.urls", "environment")),
    path("habits/", include("moodyduck.habits.urls", "habits")),
    path("friends/", include("moodyduck.friends.urls", "friends")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("api/", include("moodyduck.api.urls")),
    path("api/auth/token/", obtain_auth_token, name="api_token_auth"),
]
