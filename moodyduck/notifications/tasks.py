import json
import logging
import urllib.error
import urllib.request

from celery import shared_task
from django.conf import settings
from django.utils import timezone

try:
    from pywebpush import WebPushException, webpush
except ImportError:
    webpush = None
    WebPushException = Exception

from .models import NotificationSettings, UnifiedPushSubscription

logger = logging.getLogger(__name__)


def _send_up(endpoint, payload: dict) -> None:
    """POST a JSON payload to a UnifiedPush endpoint."""
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10):
            pass
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            UnifiedPushSubscription.objects.filter(endpoint=endpoint).delete()
        else:
            logger.warning("UP push failed for %s: HTTP %s", endpoint[:60], e.code)
    except OSError as e:
        logger.warning("UP push failed for %s: %s", endpoint[:60], e)


def send_push_to_user(user, payload: dict) -> None:
    """Send a push notification to all of a user's subscriptions."""
    vapid_private_key = getattr(settings, "VAPID_PRIVATE_KEY", "")
    vapid_claims = {
        "sub": getattr(settings, "VAPID_CLAIMS_SUB", "mailto:admin@example.com")
    }

    if webpush and vapid_private_key:
        for sub in user.push_subscriptions.all():
            try:
                webpush(
                    subscription_info={
                        "endpoint": sub.endpoint,
                        "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
                    },
                    data=json.dumps(payload),
                    vapid_private_key=vapid_private_key,
                    vapid_claims=vapid_claims,
                )
            except WebPushException as e:
                logger.warning("Web Push failed for %s: %s", sub.endpoint[:60], e)
                if e.response and e.response.status_code in (404, 410):
                    sub.delete()

    for sub in user.up_subscriptions.all():
        _send_up(sub.endpoint, payload)


@shared_task
def send_scheduled_notifications():
    """Send wake-up push to users whose reminder time has just passed."""
    now = timezone.localtime()
    current_time = now.time().replace(second=0, microsecond=0)
    today = now.date()

    for ns in NotificationSettings.objects.filter(daily_reminder=True).select_related(
        "user"
    ):
        reminder = ns.daily_reminder_time.replace(second=0, microsecond=0)
        delta = (current_time.hour * 60 + current_time.minute) - (
            reminder.hour * 60 + reminder.minute
        )
        if not (0 <= delta < 15):
            continue
        if ns.last_daily_sent == today:
            continue

        send_push_to_user(
            ns.user, {"title": "MoodyDuck", "body": "Time to log your mood!"}
        )
        ns.last_daily_sent = today
        ns.save(update_fields=["last_daily_sent"])
