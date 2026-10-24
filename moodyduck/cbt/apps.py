from django.apps import AppConfig


class CbtConfig(AppConfig):
    name = "moodyduck.cbt"

    def ready(self):
        from django.db.models.signals import pre_delete  # noqa: PLC0415

        from moodyduck.common.models import DeletionLog  # noqa: PLC0415

        from .models import ThoughtRecord  # noqa: PLC0415

        def handler(sender, instance, **kwargs):
            if instance.user_id:
                DeletionLog.objects.create(
                    user_id=instance.user_id,
                    resource_type="cbt_records",
                    resource_id=instance.pk,
                )

        pre_delete.connect(handler, sender=ThoughtRecord)
