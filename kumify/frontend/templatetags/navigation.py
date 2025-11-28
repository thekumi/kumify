from django import template
from django.conf import settings
from django.urls import reverse_lazy

from ..classes import NavSection

from importlib import import_module

register = template.Library()

@register.simple_tag
def sidebar_nav():
    sections: list[NavSection] = []

    for module in settings.CORE_MODULES + settings.ENABLED_MODULES:
        try:
            features = import_module(f"kumify.{module}.features")
            try:
                sections += features.NAV_SECTIONS
            except Exception as e:
                print(f"Error loading NAV_SECTIONS from kumify.{module}.features: {e}")
        except Exception as e:
            print(f"Error importing kumify.{module}.features: {e}")
            

    return """
            <li class="nav-item">
                <a class="nav-link" href=\"""" +  reverse_lazy("frontend:dashboard") + """\">
                    <i class="fas fa-fw fa-tachometer-alt"></i>
                    <span>Dashboard</span></a>
            </li>

            <!-- Divider -->
            <hr class="sidebar-divider">
    """ + """
            <!-- Divider -->
            <hr class="sidebar-divider">
    """.join([section.get_html() for section in sections])