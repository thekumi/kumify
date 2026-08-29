import logging

from django.dispatch import receiver

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
