from rest_framework import serializers

from .models import CalendarEvent, Task, TaskList, UserCalendar


class UserCalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCalendar
        fields = [
            "id",
            "color",
            "is_visible",
            "order",
            "virtual_key",
            "encrypted_payload",
        ]
        read_only_fields = ["id", "virtual_key"]


class CalendarEventSerializer(serializers.ModelSerializer):
    calendar = serializers.PrimaryKeyRelatedField(queryset=UserCalendar.objects.none())

    class Meta:
        model = CalendarEvent
        fields = [
            "id",
            "calendar",
            "start",
            "end",
            "all_day",
            "rrule",
            "encrypted_payload",
        ]
        read_only_fields = ["id"]
        extra_kwargs = {
            "end": {"required": False, "allow_null": True},
            "rrule": {"required": False, "allow_null": True, "allow_blank": True},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            self.fields["calendar"].queryset = UserCalendar.objects.filter(
                user=request.user
            )


class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskList
        fields = [
            "id",
            "color",
            "is_visible",
            "order",
            "virtual_key",
            "encrypted_payload",
        ]
        read_only_fields = ["id", "virtual_key"]


class TaskSerializer(serializers.ModelSerializer):
    task_list = serializers.PrimaryKeyRelatedField(queryset=TaskList.objects.none())

    class Meta:
        model = Task
        fields = [
            "id",
            "task_list",
            "due_date",
            "reminder_at",
            "rrule",
            "done",
            "done_at",
            "encrypted_payload",
        ]
        read_only_fields = ["id"]
        extra_kwargs = {
            "due_date": {"required": False, "allow_null": True},
            "reminder_at": {"required": False, "allow_null": True},
            "rrule": {"required": False, "allow_null": True, "allow_blank": True},
            "done_at": {"required": False, "allow_null": True},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            self.fields["task_list"].queryset = TaskList.objects.filter(
                user=request.user
            )
