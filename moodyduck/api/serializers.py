import logging
import tempfile

import gnupg
from rest_framework import serializers

from moodyduck.mood.models import Activity, Mood, Status, StatusActivity
from moodyduck.habits.models import Habit, HabitLog
from moodyduck.health.models import (
    HealthParameter,
    HealthLog,
    HealthRecord,
    Vaccination,
)
from moodyduck.cbt.models import ThoughtRecord
from moodyduck.dreams.models import Dream
from moodyduck.profiles.models import UserProfile

def habit_queryset_for_request(request):
    return Habit.objects.filter(user=request.user)


def habit_log_queryset_for_request(request):
    return HabitLog.objects.select_related("habit").filter(habit__user=request.user)


class MoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mood
        fields = ["id", "name", "value", "icon", "color"]
        read_only_fields = ["id"]


class StatusSerializer(serializers.ModelSerializer):
    mood = serializers.PrimaryKeyRelatedField(
        queryset=Mood.objects.none(), allow_null=True
    )
    activities = serializers.SerializerMethodField(read_only=True)
    activity_ids = serializers.PrimaryKeyRelatedField(
        queryset=Activity.objects.none(),
        many=True,
        required=False,
        write_only=True,
    )
    encrypt = serializers.BooleanField(required=False, write_only=True, default=False)

    class Meta:
        model = Status
        fields = [
            "id",
            "mood",
            "title",
            "text",
            "timestamp",
            "activities",
            "activity_ids",
            "encrypt",
        ]
        read_only_fields = ["id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            self.fields["mood"].queryset = Mood.objects.filter(user=request.user)
            self.fields["activity_ids"].child_relation.queryset = Activity.objects.filter(
                user=request.user
            )

    def get_activities(self, obj):
        return ActivitySerializer(obj.activity_set, many=True).data

    def create(self, validated_data):
        encrypt = validated_data.pop("encrypt", False)
        activity_ids = validated_data.pop("activity_ids", [])
        status = Status.objects.create(**validated_data)
        self._sync_activities(status, activity_ids)
        self._maybe_encrypt(status, encrypt)
        return status

    def update(self, instance, validated_data):
        encrypt = validated_data.pop("encrypt", False)
        activity_ids = validated_data.pop("activity_ids", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        if activity_ids is not None:
            self._sync_activities(instance, activity_ids)
        self._maybe_encrypt(instance, encrypt)
        return instance

    def _sync_activities(self, status, activities):
        StatusActivity.objects.filter(status=status).exclude(activity__in=activities).delete()
        existing_ids = set(
            StatusActivity.objects.filter(status=status, activity__in=activities).values_list(
                "activity_id", flat=True
            )
        )
        for activity in activities:
            if activity.pk not in existing_ids:
                StatusActivity.objects.create(status=status, activity=activity)

    def _maybe_encrypt(self, status, encrypt):
        if not encrypt or not status.text or status.is_encrypted:
            return

        pgp_key = getattr(status.user.userprofile, "pgp_key", "").strip()
        if not pgp_key:
            raise serializers.ValidationError(
                {"encrypt": "Add a PGP public key to your profile before encrypting."}
            )

        with tempfile.TemporaryDirectory() as gnupghome:
            gpg = gnupg.GPG(gnupghome=gnupghome)
            gpg.encoding = "utf-8"
            imported = gpg.import_keys(pgp_key)
            if imported.count == 0:
                logging.error("No public keys imported for user %s", status.user_id)
                raise serializers.ValidationError(
                    {"encrypt": "Your saved PGP key could not be imported."}
                )

            encrypted = gpg.encrypt(
                status.text,
                recipients=[imported.fingerprints[0]],
                always_trust=True,
            )
            if not encrypted.ok:
                logging.error("Error encrypting status %s: %s", status.pk, encrypted.status)
                raise serializers.ValidationError(
                    {"encrypt": f"Error encrypting note: {encrypted.status}"}
                )

            status.text = str(encrypted)
            status.save(update_fields=["text"])


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ["id", "name", "icon", "color"]
        read_only_fields = ["id"]


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = ["id", "name", "icon", "color", "description"]
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
            self.fields["habit"].queryset = habit_queryset_for_request(request)


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


class HealthRecordWriteSerializer(serializers.Serializer):
    parameter = serializers.PrimaryKeyRelatedField(queryset=HealthParameter.objects.none())
    value = serializers.DecimalField(max_digits=12, decimal_places=6)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            self.fields["parameter"].queryset = HealthParameter.objects.filter(
                user=request.user
            )


class HealthLogSerializer(serializers.ModelSerializer):
    records = HealthRecordSerializer(many=True, read_only=True)

    class Meta:
        model = HealthLog
        fields = ["id", "recorded_at", "notes", "records"]
        read_only_fields = ["id"]


class HealthLogWriteSerializer(serializers.ModelSerializer):
    records = HealthRecordWriteSerializer(many=True, required=False)

    class Meta:
        model = HealthLog
        fields = ["id", "recorded_at", "notes", "records"]
        read_only_fields = ["id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            self.fields["records"].child.fields[
                "parameter"
            ].queryset = HealthParameter.objects.filter(user=request.user)

    def create(self, validated_data):
        records_data = validated_data.pop("records", [])
        log = HealthLog.objects.create(**validated_data)
        self._replace_records(log, records_data)
        return log

    def update(self, instance, validated_data):
        records_data = validated_data.pop("records", None)

        for field in ["recorded_at", "notes"]:
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        instance.save()

        if records_data is not None:
            self._replace_records(instance, records_data)

        return instance

    def to_representation(self, instance):
        return HealthLogSerializer(instance, context=self.context).data

    def _replace_records(self, log, records_data):
        parameter_ids = []

        for record_data in records_data:
            parameter = record_data["parameter"]
            HealthRecord.objects.update_or_create(
                log=log,
                parameter=parameter,
                defaults={"value": record_data["value"]},
            )
            parameter_ids.append(parameter.pk)

        HealthRecord.objects.filter(log=log).exclude(
            parameter_id__in=parameter_ids
        ).delete()


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


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["display_name", "timezone", "pgp_key"]
