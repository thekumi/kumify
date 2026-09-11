from django.urls import reverse_lazy

from moodyduck.frontend.classes import NavItem, NavSection

section = NavSection("Habits")
section.add_item(NavItem("Habit List", reverse_lazy("habits:habit_list")))
section.add_item(NavItem("Log", reverse_lazy("habits:log_list")))

NAV_SECTIONS = [section]
DASHBOARD_SECTIONS = []
