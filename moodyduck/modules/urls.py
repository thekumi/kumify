from django.urls import path

from . import views

# Plugin API routes are appended to this list dynamically in ModulesConfig.ready().
urlpatterns = [
    path("api/modules/", views.ModulesListView.as_view(), name="modules-list"),
    path(
        "api/modules/<slug:slug>/preference/",
        views.ModulePreferenceView.as_view(),
        name="module-preference",
    ),
    path("api/nav-order/", views.NavOrderView.as_view(), name="nav-order"),
    path(
        "api/admin/modules/",
        views.FeatureAdminView.as_view(),
        name="feature-admin-list",
    ),
    path(
        "api/admin/modules/<slug:slug>/",
        views.FeatureAdminView.as_view(),
        name="feature-admin-detail",
    ),
]
