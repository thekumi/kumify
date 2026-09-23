import contextlib
import json
import uuid
from collections import Counter

from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views import View
from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from moodyduck.cbt.models import ThoughtRecord
from moodyduck.common.helpers import get_upload_path
from moodyduck.dreams.models import Dream, DreamMedia, Theme
from moodyduck.friends.models import Person
from moodyduck.gpslog.models import GPSPoint
from moodyduck.habits.models import Habit, HabitLog
from moodyduck.health.models import (
    BasicMedicalInfo,
    HealthLog,
    HealthParameter,
    HealthRecord,
    Medication,
    Vaccination,
)
from moodyduck.keystore.crypto import encrypt_for_user
from moodyduck.keystore.models import UserDevice, UserKeyBackup, UserKeyPair
from moodyduck.mood.models import Activity, Mood, Status, StatusActivity, StatusMedia
from moodyduck.profiles.models import EmergencyAccessLog, UserProfile

from .serializers import (
    ActivitySerializer,
    BasicMedicalInfoSerializer,
    CBTRecordSerializer,
    DreamMediaSerializer,
    DreamSerializer,
    EmergencyAccessLogSerializer,
    EmergencyContactSerializer,
    EmergencyVaccinationSerializer,
    HabitLogSerializer,
    HabitSerializer,
    HealthLogSerializer,
    HealthLogWriteSerializer,
    HealthParameterSerializer,
    MedicationSerializer,
    MoodSerializer,
    PersonSerializer,
    StatusMediaSerializer,
    StatusSerializer,
    ThemeSerializer,
    UserDeviceKeySerializer,
    UserDeviceRegisterSerializer,
    UserDeviceSerializer,
    UserKeyBackupSerializer,
    UserKeyPairSerializer,
    UserProfileSerializer,
    VaccinationSerializer,
    habit_log_queryset_for_request,
    habit_queryset_for_request,
)


class StatusCheckView(View):
    def get(self, request):
        return JsonResponse({"status": "OK"})


class UserDeviceViewSet(viewsets.ModelViewSet):
    serializer_class = UserDeviceSerializer
    lookup_field = "device_id"

    def get_queryset(self):
        return UserDevice.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return UserDeviceRegisterSerializer
        if self.action == "set_key":
            return UserDeviceKeySerializer
        return UserDeviceSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        device = serializer.save(user=request.user)
        return Response(
            UserDeviceSerializer(device, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["patch"], url_path="key")
    def set_key(self, request, device_id=None):
        device = self.get_object()
        serializer = UserDeviceKeySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        device.encrypted_data_key = serializer.validated_data["encrypted_data_key"]
        device.save(update_fields=["encrypted_data_key"])
        return Response(UserDeviceSerializer(device, context={"request": request}).data)


class UserKeyBackupView(APIView):
    def get(self, request):
        try:
            backup = UserKeyBackup.objects.get(user=request.user)
        except UserKeyBackup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(UserKeyBackupSerializer(backup).data)

    def post(self, request):
        serializer = UserKeyBackupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        backup, _ = UserKeyBackup.objects.update_or_create(
            user=request.user,
            defaults={
                "encrypted_data_key": serializer.validated_data["encrypted_data_key"],
                "kdf_salt": serializer.validated_data["kdf_salt"],
            },
        )
        return Response(UserKeyBackupSerializer(backup).data)


_SCRUB_FIELDS = {
    "statuses": (Status, "user", ["mood", "title", "text"]),
    "moods": (Mood, "user", ["name", "value", "color", "icon"]),
    "activities": (Activity, "user", ["name", "icon"]),
    "dreams": (Dream, "user", ["title", "content"]),
    "cbt_records": (
        ThoughtRecord,
        "user",
        [
            "title",
            "situation",
            "thoughts",
            "pro_facts",
            "con_facts",
            "realistic",
            "outcome",
        ],
    ),
    "health_logs": (HealthLog, "user", ["notes"]),
    "vaccinations": (
        Vaccination,
        "user",
        [
            "name",
            "target_disease",
            "administered_on",
            "provider",
            "batch_number",
            "next_due",
            "notes",
        ],
    ),
    "people": (
        Person,
        "user",
        [
            "name",
            "nickname",
            "birthday",
            "email",
            "phone",
            "relationship",
            "address",
            "notes",
            "last_contact",
        ],
    ),
    "medications": (Medication, "user", ["name", "remarks"]),
    "health_parameters": (HealthParameter, "user", ["name", "unit", "icon"]),
    "habits": (Habit, "user", ["name", "description"]),
    "habit_logs": (HabitLog, "habit__user", ["note"]),
    "health_records": (HealthRecord, "log__user", ["value"]),
    "user_profile": (
        UserProfile,
        "user",
        ["legal_name", "phone", "address", "date_of_birth"],
    ),
    "basic_medical_info": (
        BasicMedicalInfo,
        "user",
        ["blood_type", "allergies", "medical_notes"],
    ),
}


def _any_plaintext_q(fields):
    q = Q()
    for f in fields:
        q |= Q(**{f"{f}__isnull": False})
    return q


_STAGING_MODELS = {
    "moods": (Mood, "user", MoodSerializer),
    "activities": (Activity, "user", ActivitySerializer),
    "dreams": (Dream, "user", DreamSerializer),
    "cbt_records": (ThoughtRecord, "user", CBTRecordSerializer),
    "health_logs": (HealthLog, "user", HealthLogSerializer),
    "vaccinations": (Vaccination, "user", VaccinationSerializer),
    "people": (Person, "user", PersonSerializer),
    "medications": (Medication, "user", MedicationSerializer),
    "health_parameters": (HealthParameter, "user", HealthParameterSerializer),
    "habits": (Habit, "user", HabitSerializer),
    "habit_logs": (HabitLog, "habit__user", HabitLogSerializer),
}


_STAGING_BATCH = 200


class StagingView(APIView):
    """Return records with no encrypted_payload (GET) or bulk-update them (PATCH)."""

    def get(self, request):
        result = {}
        for key, (model, user_field, serializer_cls) in _STAGING_MODELS.items():
            qs = model.objects.filter(
                **{user_field: request.user},
                encrypted_payload__isnull=True,
            )
            if model is Status:
                qs = qs.select_related("mood").prefetch_related(
                    Prefetch(
                        "statusactivity_set",
                        queryset=StatusActivity.objects.select_related("activity"),
                    ),
                    "statusmedia_set",
                )
            result[key] = serializer_cls(
                qs[:_STAGING_BATCH], many=True, context={"request": request}
            ).data
        result["status_upgrades"] = StatusSerializer(
            Status.objects.filter(user=request.user)
            .filter(
                Q(encrypted_payload__isnull=True)
                | Q(mood__isnull=False)
                | Q(statusactivity__isnull=False)
            )
            .distinct()
            .select_related("mood")
            .prefetch_related(
                Prefetch(
                    "statusactivity_set",
                    queryset=StatusActivity.objects.select_related("activity"),
                ),
            )[:_STAGING_BATCH],
            many=True,
            context={"request": request},
        ).data
        result["vaccination_upgrades"] = VaccinationSerializer(
            Vaccination.objects.filter(
                user=request.user,
                encrypted_payload__isnull=False,
            ).filter(Q(administered_on__isnull=False) | Q(next_due__isnull=False))[
                :_STAGING_BATCH
            ],
            many=True,
        ).data
        result["gps_pending"] = GPSPoint.objects.filter(
            track__user=request.user,
            encrypted_payload__isnull=True,
            latitude__isnull=False,
        ).count()
        result["health_records"] = list(
            HealthRecord.objects.filter(
                log__user=request.user,
                encrypted_payload__isnull=True,
                value__isnull=False,
            ).values("id", "value")[:_STAGING_BATCH]
        )
        result["status_media"] = [
            {"id": m.pk, "url": m.file.url}
            for m in StatusMedia.objects.filter(
                status__user=request.user, encrypted_payload__isnull=True
            )
        ]
        result["dream_media"] = [
            {"id": m.pk, "url": m.media.url}
            for m in DreamMedia.objects.filter(
                dream__user=request.user, encrypted_payload__isnull=True
            )
        ]
        profile = request.user.userprofile
        if not profile.encrypted_payload and any(
            [profile.legal_name, profile.phone, profile.address, profile.date_of_birth]
        ):
            result["profile_upgrade"] = UserProfileSerializer(profile).data
        else:
            result["profile_upgrade"] = None
        medical_info = BasicMedicalInfo.objects.filter(
            user=request.user, encrypted_payload__isnull=True
        ).first()
        if medical_info and any(
            [
                medical_info.blood_type,
                medical_info.allergies,
                medical_info.medical_notes,
            ]
        ):
            result["medical_info_upgrade"] = BasicMedicalInfoSerializer(
                medical_info
            ).data
        else:
            result["medical_info_upgrade"] = None
        return Response(result)

    def patch(self, request):
        updated = 0
        errors = []
        for key, (model, user_field, _) in _STAGING_MODELS.items():
            for item in request.data.get(key, []):
                pk = item.get("id")
                payload = item.get("encrypted_payload")
                if not pk or not payload:
                    continue
                rows = model.objects.filter(
                    **{user_field: request.user, "pk": pk}
                ).update(encrypted_payload=payload)
                if rows:
                    updated += rows
                else:
                    errors.append({"model": key, "id": pk, "error": "Not found"})
        for item in request.data.get("status_upgrades", []):
            pk = item.get("id")
            payload = item.get("encrypted_payload")
            if not pk or not payload:
                continue
            rows = Status.objects.filter(user=request.user, pk=pk).update(
                encrypted_payload=payload, mood=None, title=None, text=None
            )
            if rows:
                StatusActivity.objects.filter(status_id=pk).delete()
                updated += rows
            else:
                errors.append(
                    {"model": "status_upgrades", "id": pk, "error": "Not found"}
                )

        for item in request.data.get("vaccination_upgrades", []):
            pk = item.get("id")
            payload = item.get("encrypted_payload")
            if not pk or not payload:
                continue
            rows = Vaccination.objects.filter(user=request.user, pk=pk).update(
                encrypted_payload=payload, administered_on=None, next_due=None
            )
            if rows:
                updated += rows
            else:
                errors.append(
                    {"model": "vaccination_upgrades", "id": pk, "error": "Not found"}
                )

        for item in request.data.get("health_records", []):
            pk = item.get("id")
            payload = item.get("encrypted_payload")
            if not pk or not payload:
                continue
            rows = HealthRecord.objects.filter(log__user=request.user, pk=pk).update(
                encrypted_payload=payload, value=None
            )
            if rows:
                updated += rows
            else:
                errors.append(
                    {"model": "health_records", "id": pk, "error": "Not found"}
                )

        if request.data.get("encrypt_gps"):
            key_pair = UserKeyPair.objects.filter(user=request.user).first()
            if key_pair:
                _GPS_FIELDS = ("latitude", "longitude", "altitude", "speed", "bearing")
                points = GPSPoint.objects.filter(
                    track__user=request.user,
                    encrypted_payload__isnull=True,
                    latitude__isnull=False,
                )[:_STAGING_BATCH]
                for point in points:
                    fields = {
                        f: getattr(point, f)
                        for f in _GPS_FIELDS
                        if getattr(point, f) is not None
                    }
                    point.encrypted_payload = encrypt_for_user(
                        key_pair.public_key, fields
                    )
                    point.latitude = None
                    point.longitude = None
                    point.altitude = None
                    point.speed = None
                    point.bearing = None
                    point.save()
                    updated += 1

        profile_upgrade = request.data.get("profile_upgrade")
        if profile_upgrade:
            pk = profile_upgrade.get("id")
            payload = profile_upgrade.get("encrypted_payload")
            if pk and payload:
                rows = UserProfile.objects.filter(user=request.user, pk=pk).update(
                    encrypted_payload=payload,
                    legal_name=None,
                    date_of_birth=None,
                    phone=None,
                    address=None,
                )
                updated += rows

        medical_info_upgrade = request.data.get("medical_info_upgrade")
        if medical_info_upgrade:
            pk = medical_info_upgrade.get("id")
            payload = medical_info_upgrade.get("encrypted_payload")
            if pk and payload:
                rows = BasicMedicalInfo.objects.filter(user=request.user, pk=pk).update(
                    encrypted_payload=payload,
                    blood_type=None,
                    allergies=None,
                    medical_notes=None,
                )
                updated += rows

        resp = {"updated": updated}
        if errors:
            resp["errors"] = errors
        return Response(
            resp, status=status.HTTP_207_MULTI_STATUS if errors else status.HTTP_200_OK
        )


class ScrubView(APIView):
    """
    GET  — returns records that are encrypted but still have plaintext fields, grouped by
           model key. Each record includes id, encrypted_payload, and the non-null plaintext
           fields so the client can decrypt, merge, and re-encrypt.
    PATCH — accepts {model_key: [{id, encrypted_payload}]} from the client after it has
            merged any missing plaintext into the payload; updates encrypted_payload and
            nulls the plaintext fields atomically.
    """

    def get(self, request):
        result = {}
        for key, (model, user_field, fields) in _SCRUB_FIELDS.items():
            q = (
                Q(**{user_field: request.user})
                & Q(encrypted_payload__isnull=False)
                & _any_plaintext_q(fields)
            )
            records = list(
                model.objects.filter(q).values("id", "encrypted_payload", *fields)
            )
            if records:
                result[key] = records
        return Response(result)

    def patch(self, request):
        total = 0
        errors = []
        for key, records in request.data.items():
            if key not in _SCRUB_FIELDS:
                continue
            model, user_field, fields = _SCRUB_FIELDS[key]
            null_kwargs = {f: None for f in fields}
            for record in records:
                pk = record.get("id")
                payload = record.get("encrypted_payload")
                if not pk or not payload:
                    continue
                try:
                    rows = model.objects.filter(
                        pk=pk, **{user_field: request.user}
                    ).update(encrypted_payload=payload, **null_kwargs)
                    total += rows
                except (ValueError, TypeError) as e:
                    errors.append({"id": pk, "model": key, "error": str(e)})
        resp = {"scrubbed": total}
        if errors:
            resp["errors"] = errors
        return Response(
            resp, status=status.HTTP_207_MULTI_STATUS if errors else status.HTTP_200_OK
        )


class UserKeyPairView(APIView):
    def get(self, request):
        try:
            kp = UserKeyPair.objects.get(user=request.user)
        except UserKeyPair.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(UserKeyPairSerializer(kp).data)

    def post(self, request):
        if UserKeyPair.objects.filter(user=request.user).exists():
            return Response(
                {"detail": "Key pair already exists."},
                status=status.HTTP_409_CONFLICT,
            )
        serializer = UserKeyPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        kp = serializer.save(user=request.user)
        return Response(UserKeyPairSerializer(kp).data, status=status.HTTP_201_CREATED)


class CurrentProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = UserProfileSerializer(request.user.userprofile).data
        data["email"] = request.user.email
        return Response(data)

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user.userprofile,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if "email" in request.data:
            request.user.email = request.data["email"]
            request.user.save(update_fields=["email"])
        data = serializer.data
        data["email"] = request.user.email
        return Response(data)


class CurrentEmergencyProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = request.user.userprofile
        medical_info, _ = BasicMedicalInfo.objects.get_or_create(user=request.user)
        vaccinations = Vaccination.objects.filter(user=request.user).order_by("-pk")

        return Response(
            {
                "display_name": profile.display_name,
                "profile_encrypted_payload": profile.encrypted_payload,
                "medical_encrypted_payload": medical_info.encrypted_payload,
                "contacts": EmergencyContactSerializer(
                    request.user.person_set.filter(emergency_contact=True),
                    many=True,
                ).data,
                "vaccinations": EmergencyVaccinationSerializer(
                    vaccinations,
                    many=True,
                ).data,
            }
        )

    def patch(self, request):
        profile = request.user.userprofile
        if "profile_encrypted_payload" in request.data:
            profile.encrypted_payload = request.data["profile_encrypted_payload"]
            profile.save(update_fields=["encrypted_payload"])

        medical_info, _ = BasicMedicalInfo.objects.get_or_create(user=request.user)
        if "medical_encrypted_payload" in request.data:
            medical_info.encrypted_payload = request.data["medical_encrypted_payload"]
            medical_info.save(update_fields=["encrypted_payload"])

        return self.get(request)


class EmergencyAccessLogViewSet(viewsets.ModelViewSet):
    serializer_class = EmergencyAccessLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EmergencyAccessLog.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PersonViewSet(viewsets.ModelViewSet):
    serializer_class = PersonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Person.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MoodViewSet(viewsets.ModelViewSet):
    serializer_class = MoodSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Mood.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ActivityViewSet(viewsets.ModelViewSet):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StatusViewSet(viewsets.ModelViewSet):
    serializer_class = StatusSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Status.objects.filter(user=self.request.user).order_by("-timestamp")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        detail=True,
        methods=["post"],
        parser_classes=[MultiPartParser, FormParser],
        url_path="attachments",
        url_name="attachments",
    )
    def upload_attachments(self, request, pk=None):
        status_obj = self.get_object()
        upload = request.FILES.get("file")
        if not upload:
            return Response(
                {"file": ["No file provided."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ep_raw = request.data.get("encrypted_payload")
        ep = json.loads(ep_raw) if ep_raw else None

        attachment = StatusMedia(status=status_obj, encrypted_payload=ep)
        attachment.file.save(get_upload_path(status_obj, upload.name), upload)
        attachment.save()

        return Response(
            StatusMediaSerializer(attachment, context={"request": request}).data,
            status=201,
        )

    @action(
        detail=True,
        methods=["delete"],
        url_path=r"attachments/(?P<attachment_id>[^/.]+)",
        url_name="delete-attachment",
    )
    def delete_attachment(self, request, pk=None, attachment_id=None):
        attachment = get_object_or_404(
            StatusMedia,
            status=self.get_object(),
            pk=attachment_id,
        )
        attachment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return habit_queryset_for_request(self.request)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HabitLogViewSet(viewsets.ModelViewSet):
    serializer_class = HabitLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return habit_log_queryset_for_request(self.request)


class HealthParameterViewSet(viewsets.ModelViewSet):
    serializer_class = HealthParameterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return HealthParameter.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HealthLogViewSet(viewsets.ModelViewSet):
    serializer_class = HealthLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return HealthLog.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return HealthLogWriteSerializer
        return HealthLogSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class VaccinationViewSet(viewsets.ModelViewSet):
    serializer_class = VaccinationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Vaccination.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CBTRecordViewSet(viewsets.ModelViewSet):
    serializer_class = CBTRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ThoughtRecord.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DreamViewSet(viewsets.ModelViewSet):
    serializer_class = DreamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Dream.objects.filter(user=self.request.user)
            .prefetch_related("dreamtheme_set__theme")
            .order_by("-timestamp")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        detail=True,
        methods=["post"],
        parser_classes=[MultiPartParser, FormParser],
        url_path="attachments",
        url_name="attachments",
    )
    def upload_attachments(self, request, pk=None):
        dream = self.get_object()
        uploads = request.FILES.getlist("file") or request.FILES.getlist("uploads")
        if not uploads:
            return Response(
                {"file": ["Upload at least one attachment."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        attachments = []
        for upload in uploads:
            attachment = DreamMedia(dream=dream)
            attachment.media.save(get_upload_path(dream, upload.name), upload)
            attachment.save()
            attachments.append(attachment)

        serializer = DreamMediaSerializer(
            attachments,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=201)

    @action(
        detail=True,
        methods=["delete"],
        url_path=r"attachments/(?P<attachment_id>[^/.]+)",
        url_name="delete-attachment",
    )
    def delete_attachment(self, request, pk=None, attachment_id=None):
        attachment = get_object_or_404(
            DreamMedia,
            dream=self.get_object(),
            pk=attachment_id,
        )
        attachment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ThemeViewSet(viewsets.ModelViewSet):
    serializer_class = ThemeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Theme.objects.filter(user=self.request.user).order_by("name")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StatusMediaEncryptView(APIView):
    """Replace a StatusMedia file with its client-encrypted version."""

    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, pk):
        media = get_object_or_404(StatusMedia, pk=pk, status__user=request.user)
        new_file = request.FILES.get("file")
        ep_raw = request.data.get("encrypted_payload")
        if not new_file or not ep_raw:
            return Response(
                {"detail": "file and encrypted_payload required."}, status=400
            )
        ep = json.loads(ep_raw) if isinstance(ep_raw, str) else ep_raw
        path = f"usermedia/{request.user.id}/{uuid.uuid4()}/{new_file.name}"
        media.file.delete(save=False)
        media.file.save(path, new_file, save=False)
        media.encrypted_payload = ep
        media.save(update_fields=["file", "encrypted_payload"])
        return Response({"id": media.pk})


class DreamMediaEncryptView(APIView):
    """Replace a DreamMedia file with its client-encrypted version."""

    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, pk):
        media = get_object_or_404(DreamMedia, pk=pk, dream__user=request.user)
        new_file = request.FILES.get("file")
        ep_raw = request.data.get("encrypted_payload")
        if not new_file or not ep_raw:
            return Response(
                {"detail": "file and encrypted_payload required."}, status=400
            )
        ep = json.loads(ep_raw) if isinstance(ep_raw, str) else ep_raw
        path = f"usermedia/{request.user.id}/{uuid.uuid4()}/{new_file.name}"
        media.media.delete(save=False)
        media.media.save(path, new_file, save=False)
        media.encrypted_payload = ep
        media.save(update_fields=["media", "encrypted_payload"])
        return Response({"id": media.pk})


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = request.user.userprofile
        return Response(
            {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
                "display_name": profile.display_name or "",
            }
        )


class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        week_start = now - timezone.timedelta(days=7)

        total = Status.objects.filter(user=request.user).count()

        streak = 0
        last_date = None
        for s in Status.objects.filter(user=request.user).order_by("-timestamp"):
            d = s.timestamp.date()
            today = now.date()
            if last_date is None:
                if d != today and d != today - timezone.timedelta(days=1):
                    break
                last_date = d
                streak += 1
                continue
            if d == last_date:
                continue
            if d == last_date - timezone.timedelta(days=1):
                last_date = d
                streak += 1
                continue
            break

        weekly = list(
            Status.objects.filter(
                user=request.user,
                timestamp__gte=week_start,
                timestamp__lte=now,
            )
            .select_related("mood")
            .prefetch_related("statusactivity_set__activity")
        )

        mood_values = [
            s.mood.value for s in weekly if s.mood and s.mood.value is not None
        ]
        weekly_avg = sum(mood_values) / len(mood_values) if mood_values else None

        closest = None
        if weekly_avg is not None:
            for mood in Mood.objects.filter(user=request.user):
                if mood.value is None:
                    continue
                if closest is None or abs(mood.value - weekly_avg) < abs(
                    closest.value - weekly_avg
                ):
                    closest = mood

        activity_counts = Counter()
        for s in weekly:
            for sa in s.statusactivity_set.all():
                if sa.activity_id:
                    activity_counts[sa.activity_id] += 1

        top_activity = None
        top_count = 0
        if activity_counts:
            top_id, top_count = activity_counts.most_common(1)[0]
            with contextlib.suppress(Activity.DoesNotExist):
                top_activity = Activity.objects.get(id=top_id, user=request.user)

        return Response(
            {
                "total": total,
                "streak": streak,
                "weekly_avg": weekly_avg,
                "closest_mood": {
                    "id": closest.id,
                    "name": closest.name or "",
                    "icon": closest.icon or "",
                    "color": closest.color or "",
                }
                if closest
                else None,
                "top_activity": {
                    "id": top_activity.id,
                    "name": top_activity.name or "",
                    "icon": top_activity.icon or "",
                    "color": top_activity.color or "",
                    "count": top_count,
                }
                if top_activity
                else None,
            }
        )


class MedicationViewSet(viewsets.ModelViewSet):
    serializer_class = MedicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Medication.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TokenLoginView(ObtainAuthToken):
    # The installed DRF version omits authentication_classes = (), so
    # SessionAuthentication from DEFAULT_AUTHENTICATION_CLASSES would run and
    # enforce CSRF on any request that carries a session cookie. Clearing it
    # here means no authentication runs at all on this endpoint — only the
    # username/password in the request body is checked.
    authentication_classes = []
