from django.apps import AppConfig


class HabitsConfig(AppConfig):
    name = "moodyduck.habits"

    def ready(self):
        from django.db.models.signals import pre_delete  # noqa: PLC0415

        from moodyduck.common.models import DeletionLog  # noqa: PLC0415
        from moodyduck.planner.registry import (  # noqa: PLC0415
            register_virtual_task_list,
        )

        from .models import Habit, HabitLog  # noqa: PLC0415

        register_virtual_task_list("habits", color="#7C3AED")

        def _log_habit(sender, instance, **kwargs):
            if instance.user_id:
                DeletionLog.objects.create(
                    user_id=instance.user_id,
                    resource_type="habits",
                    resource_id=instance.pk,
                )

        def _log_habit_log(sender, instance, **kwargs):
            user_id = instance.habit.user_id if instance.habit_id else None
            if user_id:
                DeletionLog.objects.create(
                    user_id=user_id,
                    resource_type="habit_logs",
                    resource_id=instance.pk,
                )

        pre_delete.connect(_log_habit, sender=Habit)
        pre_delete.connect(_log_habit_log, sender=HabitLog)
