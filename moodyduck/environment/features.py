from moodyduck.frontend.classes import NavSection, NavItem, NavCollapse

from django.urls import reverse_lazy

env_section = NavSection("Environment")
env_settings = NavCollapse("Details", icon="ph ph-list-bullets")
env_settings.add_item(
    NavItem("Entries", reverse_lazy("environment:entry_list"), icon="ph ph-cloud-fog")
)
env_settings.add_item(
    NavItem("Offsets", reverse_lazy("environment:offset_list"), icon="ph ph-leaf")
)
env_settings.add_item(
    NavItem(
        "Categories",
        reverse_lazy("environment:category_list"),
        icon="ph ph-tag",
    )
)
env_section.add_item(
    NavItem("Overview", reverse_lazy("environment:dashboard"), icon="ph ph-globe")
)
env_section.add_item(env_settings)

NAV_SECTIONS = [env_section]
DASHBOARD_SECTIONS = []
