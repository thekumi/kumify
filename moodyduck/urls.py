from django.contrib import admin
from django.urls import include, path, re_path

from moodyduck.frontend.views import ServiceWorkerView, SpaView

admin.site.site_header = "MoodyDuck Administration"
admin.site.site_title = "MoodyDuck Admin"
admin.site.index_title = "MoodyDuck"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("api/", include("moodyduck.api.urls")),
    path("sw.js", ServiceWorkerView.as_view(), name="service-worker"),
    re_path(r"^.*$", SpaView.as_view(), name="spa"),
]
