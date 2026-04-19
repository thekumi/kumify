from rest_framework import serializers

from moodyduck.mood.models import Mood, Status
from moodyduck.habits.models import Habit, HabitLog
from moodyduck.health.models import (
    HealthParameter,
    HealthLog,
    HealthRecord,
    Vaccination,
)
from moodyduck.cbt.models import ThoughtRecord
from moodyduck.dreams.models import Dream


class MoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mood
        fields = ["id", "name", "value", "icon", "color"]
        read_only_fields = ["id"]


class StatusSerializer(serializers.ModelSerializer):
    mood = serializers.PrimaryKeyRelatedField(
        queryset=Mood.objects.none(), allow_null=True
    )

    class Meta:
        model = Status
        fields = ["id", "mood", "title", "text", "timestamp"]
        read_only_fields = ["id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            self.fields["mood"].queryset = Mood.objects.filter(user=request.user)


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = ["id", "name", "icon", "description"]
        read_only_fields = ["id"]


class HabitLogSerializer(serializers.ModelSerializer):
    habit = serializers.PrimaryKeyRelatedField(queryset=Habit.objects.none())

    class Meta:
        model = HabitLog
        fields = ["id", "habit", "date", "note"]
        read_only_fields = ["id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            self.fields["habit"].queryset = Habit.objects.filter(user=request.user)


class HealthParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthParameter
        fields = ["id", "name", "unit", "icon"]
        read_only_fields = ["id"]


class HealthRecordSerializer(serializers.ModelSerializer):
    parameter = HealthParameterSerializer(read_only=True)

    class Meta:
        model = HealthRecord
        fields = ["id", "parameter", "value"]
        read_only_fields = ["id"]


class HealthLogSerializer(serializers.ModelSerializer):
    records = HealthRecordSerializer(many=True, read_only=True)

    class Meta:
        model = HealthLog
        fields = ["id", "recorded_at", "notes", "records"]
        read_only_fields = ["id"]


class VaccinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vaccination
        fields = [
            "id",
            "name",
            "target_disease",
            "administered_on",
            "provider",
            "batch_number",
            "next_due",
            "notes",
        ]
        read_only_fields = ["id"]


class CBTRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThoughtRecord
        fields = "__all__"
        read_only_fields = ["id", "user"]


class DreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dream
        fields = "__all__"
        read_only_fields = ["id", "user"]
