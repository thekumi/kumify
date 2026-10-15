from django.apps import AppConfig


class FriendsConfig(AppConfig):
    name = "moodyduck.friends"

    def ready(self):
        from moodyduck.planner.registry import (  # noqa: PLC0415
            register_virtual_calendar,
        )

        register_virtual_calendar("friends.birthdays", color="#D97706")
