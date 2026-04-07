from moodyduck.frontend.classes import (
    NavSection,
    NavItem,
    NavCollapse,
)
from django.urls import reverse_lazy

health_section = NavSection("Health")

health_settings_collapse = NavCollapse("Settings", icon="ph ph-gear")
health_settings_collapse.add_item(
    NavItem(
        "Parameters",
        reverse_lazy("health:parameter_list"),
        icon="ph ph-sliders-horizontal",
    )
)
health_settings_collapse.add_item(
    NavItem(
        "Medication Settings",
        reverse_lazy("health:settings"),
        icon="ph ph-clock",
    )
)

health_section.add_item(
    NavItem("Medications", reverse_lazy("health:medication_list"), icon="ph ph-pill")
)
health_section.add_item(
    NavItem("Health Log", reverse_lazy("health:log_list"), icon="ph ph-heartbeat")
)
health_section.add_item(health_settings_collapse)

NAV_SECTIONS = [health_section]
DASHBOARD_SECTIONS = []
