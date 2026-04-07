"""
Abstract base class for MoodyDuck messaging gateways.

Third-party gateways can be installed as Python packages and registered
via the ``moodyduck.gateways`` entry-point group in their ``pyproject.toml``:

    [project.entry-points."moodyduck.gateways"]
    mygateway = "mypackage.gateway:MyGateway"

The class must subclass BaseGateway and implement at minimum:
  - ``name``: a unique lowercase string identifier
  - ``recipient_id_key``: the GatewayUserSetting key that holds the
    gateway-specific recipient address (e.g. "chat_id", "room_id")
  - ``send_message_to(recipient_id, text)``: deliver a plain-text message

For gateways that support inbound bot commands, also register a webhook view
in the project's URL config and call ``msgio.commands.dispatch()`` from it.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseGateway(ABC):
    """Abstract base class for all messaging gateways."""

    #: Unique lowercase identifier used as the ``gateway`` field in GatewayUser
    name: str

    #: Key in GatewayUserSetting that stores the per-user recipient address
    recipient_id_key: str

    @abstractmethod
    def send_message_to(self, recipient_id: str, text: str) -> None:
        """Send a plain-text message to the given gateway-specific recipient."""

    def send_reply(self, sender_id: str, text: str) -> None:
        """
        Send a reply to an inbound message originator.
        Defaults to send_message_to; override if replies differ from regular sends.
        """
        self.send_message_to(sender_id, text)

    def send_notification(self, notification) -> None:
        """
        Deliver a Notification object to its recipient on this gateway.
        Looks up the recipient's gateway address from GatewayUserSetting.
        """
        from .models import GatewayUser
        from .helpers import run_filters

        settings = GatewayUser.objects.get(
            user=notification.recipient, gateway=self.name
        )
        recipient_id = settings.gatewayusersetting_set.get(
            key=self.recipient_id_key
        ).value
        text = run_filters(notification)
        self.send_message_to(recipient_id, text)
