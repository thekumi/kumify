import base64
import json
import logging
import urllib.error
import urllib.request

from celery import shared_task
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    load_pem_private_key,
)
from django.conf import settings
from django.utils import timezone

try:
    from pywebpush import WebPushException, webpush
except ImportError:
    webpush = None
    WebPushException = Exception

from .models import NotificationSettings, UnifiedPushSubscription

logger = logging.getLogger(__name__)


def _vapid_key(raw: str) -> str:
    if not raw.strip().startswith("-----"):
        return raw
    key = load_pem_private_key(raw.encode(), password=None)
    der = key.private_bytes(
        Encoding.DER, PrivateFormat.TraditionalOpenSSL, NoEncryption()
    )
    return base64.urlsafe_b64encode(der).rstrip(b"=").decode()


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
    vapid_private_key = _vapid_key(getattr(settings, "VAPID_PRIVATE_KEY", ""))
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
            except Exception as e:  # noqa: BLE001
                logger.warning("Web Push failed for %s: %s", sub.endpoint[:60], e)
                if (
                    isinstance(e, WebPushException)
                    and e.response
                    and e.response.status_code in (404, 410)
                ):
                    sub.delete()

    for sub in user.up_subscriptions.all():
        _send_up(sub.endpoint, payload)


@shared_task
def send_scheduled_notifications():
    """Send wake-up push to users for each configured reminder time."""
    now = timezone.localtime()
    current_minute = now.hour * 60 + now.minute
    today_str = str(now.date())

    for ns in NotificationSettings.objects.filter(daily_reminder=True).select_related(
        "user"
    ):
        times = ns.daily_reminder_times or []
        if not times:
            continue
        sent_today = set((ns.daily_reminder_sent or {}).get(today_str, []))
        fired = False
        for time_str in times:
            if time_str in sent_today:
                continue
            try:
                h, m = map(int, time_str.split(":"))
            except (ValueError, AttributeError):
                continue
            delta = current_minute - (h * 60 + m)
            if not (0 <= delta < 15):
                continue
            send_push_to_user(
                ns.user, {"title": "MoodyDuck", "body": "Time to log your mood!"}
            )
            sent_today.add(time_str)
            fired = True
        if fired:
            ns.daily_reminder_sent = {today_str: list(sent_today)}
            ns.save(update_fields=["daily_reminder_sent"])
