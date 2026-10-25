from django.apps import AppConfig


class HealthConfig(AppConfig):
    name = "moodyduck.health"

    def ready(self):
        from django.db.models.signals import pre_delete  # noqa: PLC0415

        from moodyduck.common.models import DeletionLog  # noqa: PLC0415
        from moodyduck.planner.registry import (  # noqa: PLC0415
            register_virtual_calendar,
        )

        from .models import (  # noqa: PLC0415
            HealthLog,
            HealthParameter,
            Medication,
            Vaccination,
        )

        register_virtual_calendar("health.medications", color="#059669")
        register_virtual_calendar("health.vaccinations", color="#DC2626")

        def _log(resource_type):
            def handler(sender, instance, **kwargs):
                user_id = getattr(instance, "user_id", None)
                if user_id:
                    DeletionLog.objects.create(
                        user_id=user_id,
                        resource_type=resource_type,
                        resource_id=instance.pk,
                    )

            return handler

        pre_delete.connect(_log("health_logs"), sender=HealthLog)
        pre_delete.connect(_log("health_parameters"), sender=HealthParameter)
        pre_delete.connect(_log("medications"), sender=Medication)
        pre_delete.connect(_log("vaccinations"), sender=Vaccination)
