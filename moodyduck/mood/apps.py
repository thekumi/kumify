from django.apps import AppConfig


class MoodConfig(AppConfig):
    name = "moodyduck.mood"

    def ready(self):
        from django.db.models.signals import pre_delete  # noqa: PLC0415

        from moodyduck.common.models import DeletionLog  # noqa: PLC0415

        from .models import Activity, ActivityCategory, Mood, Status  # noqa: PLC0415

        def _log(resource_type):
            def handler(sender, instance, **kwargs):
                if instance.user_id:
                    DeletionLog.objects.create(
                        user_id=instance.user_id,
                        resource_type=resource_type,
                        resource_id=instance.pk,
                    )

            return handler

        pre_delete.connect(_log("moods"), sender=Mood)
        pre_delete.connect(_log("activity_categories"), sender=ActivityCategory)
        pre_delete.connect(_log("activities"), sender=Activity)
        pre_delete.connect(_log("statuses"), sender=Status)
