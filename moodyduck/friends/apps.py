from django.apps import AppConfig


class FriendsConfig(AppConfig):
    name = "moodyduck.friends"

    def ready(self):
        from django.db.models.signals import pre_delete  # noqa: PLC0415

        from moodyduck.common.models import DeletionLog  # noqa: PLC0415
        from moodyduck.planner.registry import (  # noqa: PLC0415
            register_virtual_calendar,
        )

        from .models import Person  # noqa: PLC0415

        register_virtual_calendar("friends.birthdays", color="#D97706")

        def _log_person(sender, instance, **kwargs):
            if instance.user_id:
                DeletionLog.objects.create(
                    user_id=instance.user_id,
                    resource_type="people",
                    resource_id=instance.pk,
                )

        pre_delete.connect(_log_person, sender=Person)
