from django.template.loader import render_to_string

import random


class NavSection:
    def __init__(self, name, order=100):
        self.name = name
        self.order = order
        self.items: list[NavItem | NavCollapse] = []

    def add_item(self, item):
        self.items.append(item)

    def get_html(self, active=None) -> str:
        html = f'<div class="md-nav-section-heading">{self.name}</div>\n'
        self.items.sort(key=lambda x: x.order)
        for item in self.items:
            html += item.get_html()
        return html


class NavItem:
    def __init__(self, name, url, icon="ph ph-smiley", title=None, order=100):
        self.name = name
        self.url = url
        self.icon = icon
        self.title = title or name
        self.order = order

    def get_html(self, active=None) -> str:
        return (
            f'<a class="md-nav-item{" active" if self.name == active else ""}" href="{self.url}">'
            f'<i class="{self.icon}"></i>'
            f"<span>{self.name}</span>"
            f"</a>\n"
        )


class NavCollapse:
    def __init__(self, name, icon="ph ph-smiley", order=100):
        self.name = name
        self.icon = icon
        self.order = order
        self.items: list[NavItem] = []

    def add_item(self, item):
        self.items.append(item)

    def get_html(self, active=None) -> str:
        element_id = f"nc-{random.randint(100000, 999999)}"
        html = (
            f'<div class="md-nav-collapse-toggle" data-target="{element_id}" aria-expanded="false">'
            f'<i class="{self.icon}"></i>'
            f"<span>{self.name}</span>"
            f'<i class="ph ph-caret-right md-chevron"></i>'
            f"</div>"
            f'<div id="{element_id}" class="md-nav-collapse-inner">'
        )
        self.items.sort(key=lambda x: x.order)
        for item in self.items:
            html += item.get_html()
        html += "</div>\n"
        return html


class DashboardSection:
    def __init__(self, name, template, context=None):
        self.name = name
        self.template = template
        self.context = context or {}
        self.styles = []
        self.scripts = []

    def get_html(self, request):
        return render_to_string(self.template, self.context, request)

    def add_style(self, style):
        self.styles.append(style)

    def add_script(self, script):
        self.scripts.append(script)
