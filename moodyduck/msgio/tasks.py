import logging

from celery import shared_task
from django.utils.timezone import localtime, now

logger = logging.getLogger(__name__)


@shared_task
def send_notifications():
    from .models import Notification

    for notification in Notification.objects.all():
        for schedule in notification.notificationdatetimeschedule_set.all():
            if not schedule.sent and schedule.datetime <= localtime(now()):
                try:
                    notification.send()
                    schedule.sent = True
                    schedule.save()
                except Exception:
                    logger.exception(
                        "Failed to send scheduled notification %d", notification.pk
                    )

        for daily in notification.notificationdailyschedule_set.all():
            if (
                not daily.last_sent or daily.last_sent < localtime(now()).date()
            ) and daily.time <= localtime(now()).time():
                try:
                    notification.send()
                    daily.last_sent = localtime(now()).date()
                    daily.save()
                except Exception:
                    logger.exception(
                        "Failed to send daily notification %d", notification.pk
                    )
