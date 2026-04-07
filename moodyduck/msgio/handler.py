import logging

from django.dispatch import receiver
from django.utils.timezone import localtime, now

from moodyduck.cronhandler.signals import cron

from .models import Notification
from .registry import get_all_gateways
from .signals import send_message

logger = logging.getLogger(__name__)


@receiver(send_message)
def outbound_dispatch(sender, **kwargs):
    """Route outbound notifications to the appropriate gateway via registry."""
    gateway_name = kwargs.get("dispatcher")
    notification = kwargs.get("notification")

    gateways = get_all_gateways()
    gateway = gateways.get(gateway_name)
    if gateway is None:
        logger.warning("outbound_dispatch: no gateway registered for %r", gateway_name)
        return

    try:
        gateway.send_notification(notification)
    except Exception:
        logger.exception("Error dispatching notification via gateway %r", gateway_name)


@receiver(cron)
def send_notifications(sender, **kwargs):
    returns = []
    for notification in Notification.objects.all():
        for schedule in notification.notificationdatetimeschedule_set.all():
            if not schedule.sent and schedule.datetime <= localtime(now()):
                try:
                    returns.append(notification.send())
                    schedule.sent = True
                    schedule.save()
                except Exception:
                    logger.exception(
                        "Failed to send scheduled notification %d", notification.pk
                    )
        for daily in notification.notificationdailyschedule_set.all():
            if (
                (not daily.last_sent) or daily.last_sent < localtime(now()).date()
            ) and daily.time <= localtime(now()).time():
                try:
                    returns.append(notification.send())
                    daily.last_sent = localtime(now()).date()
                    daily.save()
                except Exception:
                    logger.exception(
                        "Failed to send daily notification %d", notification.pk
                    )
    return returns
