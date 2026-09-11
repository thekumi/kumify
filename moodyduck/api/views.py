import contextlib
import json
import uuid
from collections import Counter

from django.db.models import Prefetch
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
from moodyduck.health.models import (
    BasicMedicalInfo,
    HealthLog,
    HealthParameter,
    Medication,
    Vaccination,
)
from moodyduck.keystore.models import UserDevice, UserKeyBackup, UserKeyPair
from moodyduck.mood.models import Activity, Mood, Status, StatusActivity, StatusMedia
from moodyduck.profiles.models import EmergencyAccessLog

from .serializers import (
    ActivitySerializer,
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


_STAGING_MODELS = {
    "statuses": (Status, "user", StatusSerializer),
    "moods": (Mood, "user", MoodSerializer),
    "activities": (Activity, "user", ActivitySerializer),
    "dreams": (Dream, "user", DreamSerializer),
    "cbt_records": (ThoughtRecord, "user", CBTRecordSerializer),
    "health_logs": (HealthLog, "user", HealthLogSerializer),
    "vaccinations": (Vaccination, "user", VaccinationSerializer),
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
        resp = {"updated": updated}
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
        latest_vaccinations = []
        seen_targets = set()
        for vaccination in Vaccination.objects.filter(user=request.user).order_by(
            "target_disease", "-administered_on", "name"
        ):
            target = (vaccination.target_disease or vaccination.name).strip()
            if target in seen_targets:
                continue
            seen_targets.add(target)
            latest_vaccinations.append(vaccination)

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
                    latest_vaccinations,
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
        uploads = request.FILES.getlist("file") or request.FILES.getlist("uploads")
        if not uploads:
            return Response(
                {"file": ["Upload at least one attachment."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        attachments = []
        for upload in uploads:
            attachment = StatusMedia(status=status_obj)
            attachment.file.save(get_upload_path(status_obj, upload.name), upload)
            attachment.save()
            attachments.append(attachment)

        serializer = StatusMediaSerializer(
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
