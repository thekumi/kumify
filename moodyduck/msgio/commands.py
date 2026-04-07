"""
Command registry for inbound messaging.

Any app can register bot commands that work across all supported messaging
gateways (Telegram, Matrix, future gateways).

Usage in an app's commands.py::

    from moodyduck.msgio.commands import register_command, reply

    @register_command("/mood")
    def cmd_mood(user, gateway, sender_id, args):
        ...
        reply(gateway, sender_id, "✅ Logged!")

The gateway layer is responsible for:
  1. Parsing the incoming message into (user, gateway, sender_id, text)
  2. Calling dispatch(user, gateway, sender_id, text)

Each command handler receives:
  - user:      Django User instance (or None if not yet paired)
  - gateway:   str gateway identifier, e.g. "telegram"
  - sender_id: gateway-specific identifier to reply to (chat_id, room_id, etc.)
  - args:      str, text after the command name (may be empty)
"""

from __future__ import annotations

import importlib
import logging
from typing import Callable

from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)

# Registry: command_name (lowercased, with leading /) → handler function
_registry: dict[str, Callable] = {}


def register_command(name: str):
    """Decorator that registers a command handler for the given command name."""
    if not name.startswith("/"):
        raise ValueError(f"Command name must start with '/': {name!r}")

    def decorator(fn: Callable) -> Callable:
        _registry[name.lower()] = fn
        return fn

    return decorator


def dispatch(user, gateway: str, sender_id, text: str) -> None:
    """Parse text as a bot command and invoke the matching registered handler."""
    if not text or not text.startswith("/"):
        return

    parts = text.split(maxsplit=1)
    # Strip @botname suffix (Telegram group chats send /command@BotName)
    command = parts[0].split("@")[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    handler = _registry.get(command)
    if handler:
        try:
            handler(user=user, gateway=gateway, sender_id=sender_id, args=args)
        except Exception:
            logger.exception(
                "Error in command handler %s (gateway=%s, sender=%s)",
                command,
                gateway,
                sender_id,
            )
    elif user is not None:
        reply(
            gateway,
            sender_id,
            _("Unknown command. Send /help for a list of available commands."),
        )


def reply(gateway: str, sender_id, text: str) -> None:
    """Send a reply back through the given gateway."""
    from .gateways import send_via_gateway

    send_via_gateway(gateway, sender_id, text)


def get_commands() -> dict[str, Callable]:
    """Return a copy of the registered command dict (for /help generation)."""
    return dict(_registry)


def load_app_commands() -> None:
    """
    Auto-discover command modules from all installed apps.

    Each Django app may expose a ``commands.py`` at its package root.
    Importing it triggers the @register_command decorators.
    Called once from MsgioConfig.ready().
    """
    from django.apps import apps

    for app_config in apps.get_app_configs():
        try:
            importlib.import_module(f"{app_config.name}.commands")
        except ImportError:
            pass  # App has no commands.py — that's fine
        except Exception:
            logger.exception("Error loading commands from %s", app_config.name)
