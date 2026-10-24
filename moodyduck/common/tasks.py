from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from moodyduck.common.models import DeletionLog


@shared_task
def prune_deletion_log():
    cutoff = timezone.now() - timedelta(days=30)
    deleted, _ = DeletionLog.objects.filter(deleted_at__lt=cutoff).delete()
    return deleted
