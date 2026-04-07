from django.apps import AppConfig


class MsgioConfig(AppConfig):
    name = "moodyduck.msgio"

    def ready(self):
        # Build the gateway registry from entry points
        from .registry import build_registry

        build_registry()

        # Register the unified outbound signal handler
        from . import handler  # noqa: F401

        # Auto-discover command handlers from all installed apps
        from .commands import load_app_commands

        load_app_commands()
