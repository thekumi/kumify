import logging
from importlib import import_module

from django import template
from django.conf import settings

register = template.Library()
logger = logging.getLogger(__name__)


def _dashboard_sections():
    sections = []

    for module in settings.CORE_MODULES + settings.ENABLED_MODULES:
        try:
            features = import_module(f"moodyduck.{module}.features")
        except ImportError:
            continue
        except Exception:
            logger.exception("Error importing moodyduck.%s.features", module)
            continue

        try:
            sections.extend(features.DASHBOARD_SECTIONS)
        except AttributeError:
            continue
        except Exception:
            logger.exception(
                "Error loading DASHBOARD_SECTIONS from moodyduck.%s.features", module
            )

    return sections


@register.simple_tag(takes_context=True)
def dashboard(context):
    sections = _dashboard_sections()

    dashboard_html = ""

    for section in sections:
        dashboard_html += f"<h3>{section.name}</h3>"

        dashboard_html += section.get_html(context["request"])

        if section != sections[-1]:
            dashboard_html += '<hr class="dashboard-divider">'

    return dashboard_html


@register.simple_tag
def dashboard_styles():
    styles = []

    for section in _dashboard_sections():
        styles.extend(section.styles)

    return styles


@register.simple_tag
def dashboard_scripts():
    scripts = []

    for section in _dashboard_sections():
        scripts.extend(section.scripts)

    return scripts
