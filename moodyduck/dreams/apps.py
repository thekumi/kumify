from django.apps import AppConfig


class DreamsConfig(AppConfig):
    name = "moodyduck.dreams"

    def ready(self):
        from django.db.models.signals import pre_delete  # noqa: PLC0415

        from moodyduck.common.models import DeletionLog  # noqa: PLC0415

        from .models import Dream  # noqa: PLC0415

        def handler(sender, instance, **kwargs):
            if instance.user_id:
                DeletionLog.objects.create(
                    user_id=instance.user_id,
                    resource_type="dreams",
                    resource_id=instance.pk,
                )

        pre_delete.connect(handler, sender=Dream)
