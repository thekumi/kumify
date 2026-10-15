from django.apps import AppConfig


class HealthConfig(AppConfig):
    name = "moodyduck.health"

    def ready(self):
        from moodyduck.planner.registry import (  # noqa: PLC0415
            register_virtual_calendar,
        )

        register_virtual_calendar("health.medications", color="#059669")
        register_virtual_calendar("health.vaccinations", color="#DC2626")
