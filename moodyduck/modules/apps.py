import warnings

from django.apps import AppConfig


class ModulesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "moodyduck.modules"
    verbose_name = "Modules"

    def ready(self):
        from importlib.metadata import entry_points  # noqa: PLC0415

        from django.db.models.signals import post_migrate  # noqa: PLC0415
        from django.urls import clear_url_caches, include, path  # noqa: PLC0415

        from .registry import registry  # noqa: PLC0415

        for ep in entry_points(group="moodyduck.plugins"):
            try:
                app_config_cls = ep.load()
            except Exception as exc:  # noqa: BLE001
                warnings.warn(f"moodyduck.plugins: failed to load {ep.name!r}: {exc}")
                continue

            cfg = getattr(app_config_cls, "moodyduck_plugin", None)
            if not isinstance(cfg, dict):
                continue

            registry[ep.name] = cfg

        if not registry:
            return

        from . import urls as modules_urls  # noqa: PLC0415

        for slug, cfg in registry.items():
            if "api_urls" in cfg:
                modules_urls.urlpatterns.append(
                    path(f"api/plugins/{slug}/", include(cfg["api_urls"]))
                )

        clear_url_caches()

        post_migrate.connect(_sync_features, sender=self)


def _sync_features(sender, **kwargs):
    from .models import Feature  # noqa: PLC0415
    from .registry import registry  # noqa: PLC0415

    for slug, cfg in registry.items():
        Feature.objects.update_or_create(
            slug=slug,
            defaults={
                "name": cfg.get("name", slug),
                "icon": cfg.get("icon", ""),
            },
        )
