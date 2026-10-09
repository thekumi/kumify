from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Feature, UserFeaturePreference, UserNavOrder
from .registry import registry


class ModulesListView(APIView):
    def get(self, request):
        user = request.user

        feature_map = {f.slug: f for f in Feature.objects.all()}
        pref_map = {
            p.feature.slug: p.visible
            for p in UserFeaturePreference.objects.filter(user=user).select_related(
                "feature"
            )
        }

        result = []
        for slug, cfg in registry.items():
            feature = feature_map.get(slug)
            if feature and not feature.is_enabled_for(user):
                continue

            shown_by_default = feature.shown_by_default if feature else True
            visible = pref_map.get(slug, shown_by_default)

            result.append(
                {
                    "slug": slug,
                    "name": cfg.get("name", slug),
                    "icon": cfg.get("icon", ""),
                    "nav_path": cfg.get("nav_path", f"/plugins/{slug}"),
                    "bundle_url": cfg.get("bundle_url"),
                    "visible": visible,
                }
            )

        return Response(result)


class ModulePreferenceView(APIView):
    def patch(self, request, slug):
        if slug not in registry:
            raise NotFound()

        cfg = registry[slug]
        feature, _ = Feature.objects.get_or_create(
            slug=slug,
            defaults={
                "name": cfg.get("name", slug),
                "icon": cfg.get("icon", ""),
            },
        )

        if not feature.is_enabled_for(request.user):
            raise PermissionDenied()

        visible = request.data.get("visible")
        if visible is None:
            raise ValidationError({"visible": "This field is required."})

        pref, _ = UserFeaturePreference.objects.get_or_create(
            user=request.user, feature=feature
        )
        pref.visible = bool(visible)
        pref.save()

        return Response({"slug": slug, "visible": pref.visible})


class NavOrderView(APIView):
    def get(self, request):
        try:
            order = UserNavOrder.objects.get(user=request.user).order
        except UserNavOrder.DoesNotExist:
            order = []
        return Response(order)

    def put(self, request):
        order = request.data
        if not isinstance(order, list) or not all(isinstance(k, str) for k in order):
            raise ValidationError("Expected a JSON array of strings.")
        UserNavOrder.objects.update_or_create(
            user=request.user, defaults={"order": order}
        )
        return Response(order)


ENABLED_FOR_VALUES = {"disabled", "staff", "all"}


class FeatureAdminView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        result = []
        for slug, cfg in registry.items():
            feature = Feature.objects.filter(slug=slug).first()
            result.append(
                {
                    "slug": slug,
                    "name": cfg.get("name", slug),
                    "icon": cfg.get("icon", ""),
                    "enabled_for": feature.enabled_for if feature else "all",
                    "shown_by_default": feature.shown_by_default if feature else True,
                }
            )
        return Response(result)

    def patch(self, request, slug):
        if slug not in registry:
            raise NotFound()

        cfg = registry[slug]
        feature, _ = Feature.objects.get_or_create(
            slug=slug,
            defaults={"name": cfg.get("name", slug), "icon": cfg.get("icon", "")},
        )

        enabled_for = request.data.get("enabled_for")
        shown_by_default = request.data.get("shown_by_default")

        if enabled_for is not None:
            if enabled_for not in ENABLED_FOR_VALUES:
                raise ValidationError(
                    {"enabled_for": f"Must be one of: {', '.join(ENABLED_FOR_VALUES)}."}
                )
            feature.enabled_for = enabled_for

        if shown_by_default is not None:
            feature.shown_by_default = bool(shown_by_default)

        feature.save()
        return Response(
            {
                "slug": feature.slug,
                "enabled_for": feature.enabled_for,
                "shown_by_default": feature.shown_by_default,
            }
        )
