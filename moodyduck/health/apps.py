from django.apps import AppConfig


class HealthConfig(AppConfig):
    name = "moodyduck.health"

    def ready(self):
        from django.db.models.signals import pre_delete  # noqa: PLC0415

        from moodyduck.common.models import DeletionLog  # noqa: PLC0415
        from moodyduck.planner.registry import (  # noqa: PLC0415
            register_virtual_calendar,
        )

        from .models import HealthLog  # noqa: PLC0415

        register_virtual_calendar("health.medications", color="#059669")
        register_virtual_calendar("health.vaccinations", color="#DC2626")

        def _log_health_log(sender, instance, **kwargs):
            if instance.user_id:
                DeletionLog.objects.create(
                    user_id=instance.user_id,
                    resource_type="health_logs",
                    resource_id=instance.pk,
                )

        pre_delete.connect(_log_health_log, sender=HealthLog)
