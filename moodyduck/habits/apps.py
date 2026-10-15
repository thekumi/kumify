from django.apps import AppConfig


class HabitsConfig(AppConfig):
    name = "moodyduck.habits"

    def ready(self):
        from moodyduck.planner.registry import (  # noqa: PLC0415
            register_virtual_task_list,
        )

        register_virtual_task_list("habits", color="#7C3AED")
