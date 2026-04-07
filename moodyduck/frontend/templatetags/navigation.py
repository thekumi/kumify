import logging

from django import template
from django.conf import settings

from ..classes import NavSection

from importlib import import_module

logger = logging.getLogger(__name__)
register = template.Library()


@register.simple_tag
def sidebar_nav():
    sections: list[NavSection] = []

    for module in settings.CORE_MODULES + settings.ENABLED_MODULES:
        try:
            features = import_module(f"moodyduck.{module}.features")
            try:
                sections += features.NAV_SECTIONS
            except Exception:
                logger.exception(
                    "Error loading NAV_SECTIONS from moodyduck.%s.features", module
                )
        except ImportError:
            pass  # App has no features.py — that's fine
        except Exception:
            logger.exception("Error importing moodyduck.%s.features", module)

    return '<div class="md-nav-divider"></div>'.join(
        [section.get_html() for section in sections]
    )
