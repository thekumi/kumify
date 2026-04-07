"""
Gateway package — entry-point-discovered at startup.

Built-in gateways are listed in pyproject.toml under
[project.entry-points."moodyduck.gateways"]. Third-party gateways can be
installed as separate Python packages using the same entry-point group.
"""

# Re-export the helpers that the rest of msgio needs
from ..registry import build_registry, get_gateway, get_all_gateways, send_via_gateway

__all__ = ["build_registry", "get_gateway", "get_all_gateways", "send_via_gateway"]
