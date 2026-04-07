import json
import logging

from django.http import HttpResponse
from django.views import View

from .commands import dispatch
from .models import GatewayUser, GatewayUserSetting, TelegramPairingToken
from .registry import send_via_gateway

logger = logging.getLogger(__name__)


def _get_user(gateway: str, sender_id: str):
    """Return the MoodyDuck user linked to this gateway/sender_id pair, or None."""
    try:
        setting = GatewayUserSetting.objects.get(
            gatewayuser__gateway=gateway,
            key="chat_id",
            value=str(sender_id),
        )
        return setting.gatewayuser.user
    except GatewayUserSetting.DoesNotExist:
        return None


def _handle_start(gateway: str, sender_id, token_str: str, username: str = "") -> None:
    """Pair a gateway user via a one-time pairing token."""
    token_str = token_str.strip()
    if not token_str:
        send_via_gateway(
            gateway,
            sender_id,
            "Hi! Send /start <pairing_token> to link your MoodyDuck account.",
        )
        return

    try:
        pairing = TelegramPairingToken.objects.get(token=token_str)
    except (TelegramPairingToken.DoesNotExist, Exception):
        send_via_gateway(
            gateway,
            sender_id,
            "❌ Invalid or expired token. Generate a new one in your MoodyDuck profile.",
        )
        return

    user = pairing.user
    gw, _created = GatewayUser.objects.get_or_create(user=user, gateway=gateway)
    GatewayUserSetting.objects.update_or_create(
        gatewayuser=gw,
        key="chat_id",
        defaults={"value": str(sender_id)},
    )
    pairing.delete()
    send_via_gateway(
        gateway,
        sender_id,
        f"✅ Linked to MoodyDuck as {user.username}! Use /help to see available commands.",
    )


class TelegramWebhookView(View):
    gateway = "telegram"

    def post(self, request, *args, **kwargs):
        try:
            update = json.loads(request.body)
        except Exception:
            return HttpResponse(status=200)

        message = update.get("message") or update.get("edited_message") or {}
        if not message:
            return HttpResponse(status=200)

        chat_id = message.get("chat", {}).get("id")
        text = (message.get("text") or "").strip()

        if not chat_id or not text or not text.startswith("/"):
            return HttpResponse(status=200)

        parts = text.split(maxsplit=1)
        command = parts[0].split("@")[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if command == "/start":
            # Pairing is handled here because it doesn't require an authenticated user
            _handle_start(self.gateway, chat_id, args)
        else:
            user = _get_user(self.gateway, str(chat_id))
            try:
                dispatch(user=user, gateway=self.gateway, sender_id=chat_id, text=text)
            except Exception:
                logger.exception(
                    "Error dispatching command %s from %s/%s",
                    command,
                    self.gateway,
                    chat_id,
                )

        return HttpResponse(status=200)
