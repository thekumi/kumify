import json
import logging

from celery import shared_task
from django.conf import settings
from django.utils import timezone

try:
    from pywebpush import WebPushException, webpush
except ImportError:
    webpush = None
    WebPushException = Exception

from .models import NotificationSettings

logger = logging.getLogger(__name__)


@shared_task
def send_scheduled_notifications():
    """Send wake-up push to users whose reminder time has just passed."""
    if webpush is None:
        logger.warning("pywebpush not installed — push notifications disabled")
        return

    now = timezone.localtime()
    current_time = now.time().replace(second=0, microsecond=0)
    today = now.date()

    vapid_private_key = getattr(settings, "VAPID_PRIVATE_KEY", "")
    vapid_claims = {
        "sub": getattr(settings, "VAPID_CLAIMS_SUB", "mailto:admin@example.com")
    }

    if not vapid_private_key:
        logger.warning("VAPID_PRIVATE_KEY not configured — skipping push")
        return

    for ns in NotificationSettings.objects.filter(daily_reminder=True).select_related(
        "user"
    ):
        reminder = ns.daily_reminder_time.replace(second=0, microsecond=0)
        # Fire if within the last 15 minutes and not yet sent today
        delta = (current_time.hour * 60 + current_time.minute) - (
            reminder.hour * 60 + reminder.minute
        )
        if not (0 <= delta < 15):
            continue
        if ns.last_daily_sent == today:
            continue

        for sub in ns.user.push_subscriptions.all():
            try:
                webpush(
                    subscription_info={
                        "endpoint": sub.endpoint,
                        "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
                    },
                    data=json.dumps({}),
                    vapid_private_key=vapid_private_key,
                    vapid_claims=vapid_claims,
                )
            except WebPushException as e:
                logger.warning("Push failed for %s: %s", sub.endpoint[:60], e)
                if e.response and e.response.status_code in (404, 410):
                    sub.delete()

        ns.last_daily_sent = today
        ns.save(update_fields=["last_daily_sent"])
