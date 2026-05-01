import logging
import tempfile

import gnupg
from rest_framework import serializers

from moodyduck.mood.models import Activity, Mood, Status, StatusActivity, StatusMedia
from moodyduck.habits.models import Habit, HabitLog
from moodyduck.health.models import (
    BasicMedicalInfo,
    HealthParameter,
    HealthLog,
    HealthRecord,
    Vaccination,
)
from moodyduck.cbt.models import ThoughtRecord
from moodyduck.dreams.models import Dream, DreamMedia
from moodyduck.friends.models import Person
from moodyduck.profiles.models import EmergencyAccessLog, UserProfile


def encrypt_text_for_user(user, plaintext, object_label):
    pgp_key = getattr(user.userprofile, "pgp_key", "").strip()
    if not pgp_key:
        raise serializers.ValidationError(
            {"encrypt": "Add a PGP public key to your profile before encrypting."}
        )

    with tempfile.TemporaryDirectory() as gnupghome:
        gpg = gnupg.GPG(gnupghome=gnupghome)
        gpg.encoding = "utf-8"
        imported = gpg.import_keys(pgp_key)
        if imported.count == 0:
            logging.error("No public keys imported for user %s", user.pk)
            raise serializers.ValidationError(
                {"encrypt": "Your saved PGP key could not be imported."}
            )

        encrypted = gpg.encrypt(
            plaintext,
            recipients=[imported.fingerprints[0]],
            always_trust=True,
        )
        if not encrypted.ok:
            logging.error(
                "Error encrypting %s for user %s: %s",
                object_label,
                user.pk,
                encrypted.status,
            )
            raise serializers.ValidationError(
                {"encrypt": f"Error encrypting {object_label}: {encrypted.status}"}
            )

        return str(encrypted)


def habit_queryset_for_request(request):
    return Habit.objects.filter(user=request.user)


def habit_log_queryset_for_request(request):
    return HabitLog.objects.select_related("habit").filter(habit__user=request.user)


class StatusMediaSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = StatusMedia
        fields = ["id", "name", "url"]
        read_only_fields = ["id", "name", "url"]

    def get_name(self, obj):
        return obj.basename

    def get_url(self, obj):
        request = self.context.get("request")
        if not obj.file:
            return None
        url = obj.file.url
        return request.build_absolute_uri(url) if request else url


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
    attachments = StatusMediaSerializer(
        source="statusmedia_set",
        many=True,
        read_only=True,
    )

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
            "attachments",
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
        status.text = encrypt_text_for_user(status.user, status.text, "note")
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


class DreamMediaSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = DreamMedia
        fields = ["id", "name", "url"]
        read_only_fields = ["id", "name", "url"]

    def get_name(self, obj):
        return obj.basename

    def get_url(self, obj):
        request = self.context.get("request")
        if not obj.media:
            return None
        url = obj.media.url
        return request.build_absolute_uri(url) if request else url


class DreamSerializer(serializers.ModelSerializer):
    mood = serializers.PrimaryKeyRelatedField(
        queryset=Mood.objects.none(), allow_null=True, required=False
    )
    encrypt = serializers.BooleanField(required=False, write_only=True, default=False)
    attachments = DreamMediaSerializer(
        source="dreammedia_set",
        many=True,
        read_only=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            self.fields["mood"].queryset = Mood.objects.filter(user=request.user)

    def create(self, validated_data):
        encrypt = validated_data.pop("encrypt", False)
        dream = Dream.objects.create(**validated_data)
        self._maybe_encrypt(dream, encrypt)
        return dream

    def update(self, instance, validated_data):
        encrypt = validated_data.pop("encrypt", False)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        self._maybe_encrypt(instance, encrypt)
        return instance

    def _maybe_encrypt(self, dream, encrypt):
        if not encrypt or not dream.content or dream.content.startswith(
            "-----BEGIN PGP MESSAGE-----"
        ):
            return
        dream.content = encrypt_text_for_user(dream.user, dream.content, "dream")
        dream.save(update_fields=["content"])

    class Meta:
        model = Dream
        fields = [
            "id",
            "title",
            "content",
            "timestamp",
            "type",
            "mood",
            "lucid",
            "wet",
            "encrypt",
            "attachments",
        ]
        read_only_fields = ["id", "user"]


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "display_name",
            "timezone",
            "pgp_key",
            "legal_name",
            "phone",
            "address",
            "date_of_birth",
        ]


class BasicMedicalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasicMedicalInfo
        fields = ["blood_type", "allergies", "medical_notes"]


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = [
            "id",
            "name",
            "nickname",
            "phone",
            "email",
            "relationship",
            "notes",
        ]
        read_only_fields = ["id"]


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = [
            "id",
            "name",
            "nickname",
            "birthday",
            "email",
            "phone",
            "relationship",
            "address",
            "notes",
            "emergency_contact",
            "last_contact",
        ]
        read_only_fields = ["id"]


class EmergencyVaccinationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    target_disease = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    administered_on = serializers.DateField()
    provider = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    next_due = serializers.DateField(allow_null=True, required=False)
    batch_number = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    notes = serializers.CharField(allow_blank=True, allow_null=True, required=False)


class EmergencyProfileSerializer(serializers.Serializer):
    display_name = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    legal_name = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    phone = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    address = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    date_of_birth = serializers.DateField(allow_null=True, required=False)
    blood_type = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    allergies = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    medical_notes = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    contacts = EmergencyContactSerializer(many=True, read_only=True)
    vaccinations = EmergencyVaccinationSerializer(many=True, read_only=True)


class EmergencyAccessLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyAccessLog
        fields = ["id", "accessed_at", "source", "method", "details"]
        read_only_fields = ["id", "accessed_at"]
