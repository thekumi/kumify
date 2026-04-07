from moodyduck.frontend.classes import NavSection, NavItem
from django.urls import reverse_lazy

section = NavSection("Friends")
section.add_item(NavItem("People", reverse_lazy("friends:person_list")))

NAV_SECTIONS = [section]
DASHBOARD_SECTIONS = []
