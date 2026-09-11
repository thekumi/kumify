from django.urls import reverse_lazy

from moodyduck.frontend.classes import NavItem, NavSection

section = NavSection("Friends")
section.add_item(NavItem("People", reverse_lazy("friends:person_list")))

NAV_SECTIONS = [section]
DASHBOARD_SECTIONS = []
