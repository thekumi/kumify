"""
Gateway registry for MoodyDuck messaging.

Gateways are discovered via the ``moodyduck.gateways`` entry-point group.
Built-in gateways are registered in pyproject.toml alongside any third-party
ones installed in the same Python environment.
"""

from __future__ import annotations

import logging
from importlib.metadata import entry_points

from .base import BaseGateway

logger = logging.getLogger(__name__)

_registry: dict[str, BaseGateway] = {}


def build_registry() -> None:
    """
    Discover and instantiate all registered gateways.
    Called once from MsgioConfig.ready().
    """
    global _registry
    _registry = {}

    for ep in entry_points(group="moodyduck.gateways"):
        try:
            gateway_cls = ep.load()
            instance = gateway_cls()
            _registry[instance.name] = instance
            logger.debug("Registered gateway: %s (%s)", instance.name, ep.value)
        except Exception:
            logger.exception("Failed to load gateway entry point %r", ep.name)


def get_gateway(name: str) -> BaseGateway:
    """Return the gateway instance for the given name, or raise KeyError."""
    return _registry[name]


def get_all_gateways() -> dict[str, BaseGateway]:
    """Return a copy of the full gateway registry."""
    return dict(_registry)


def send_via_gateway(gateway: str, sender_id: str, text: str) -> None:
    """Send a plain-text message through the named gateway."""
    try:
        gw = _registry[gateway]
    except KeyError:
        logger.warning("send_via_gateway: no gateway registered for %r", gateway)
        return
    gw.send_reply(sender_id, text)
