from moodyduck.frontend.classes import NavSection, NavItem

from django.urls import reverse_lazy

cbt_section = NavSection("CBT")
cbt_section.add_item(
    NavItem("Thought Records", reverse_lazy("cbt:record_list"), icon="ph ph-brain")
)

NAV_SECTIONS = [cbt_section]
DASHBOARD_SECTIONS = []
