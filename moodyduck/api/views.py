from django.http import JsonResponse
from django.views import View

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from django.shortcuts import get_object_or_404

from moodyduck.common.helpers import get_upload_path
from moodyduck.mood.models import Activity, Mood, Status, StatusMedia
from moodyduck.habits.models import Habit, HabitLog
from moodyduck.health.models import BasicMedicalInfo, HealthLog, HealthParameter, Vaccination
from moodyduck.cbt.models import ThoughtRecord
from moodyduck.dreams.models import Dream, DreamMedia
from moodyduck.friends.models import Person
from moodyduck.profiles.models import EmergencyAccessLog

from .serializers import (
    CBTRecordSerializer,
    DreamSerializer,
    ActivitySerializer,
    BasicMedicalInfoSerializer,
    DreamMediaSerializer,
    EmergencyAccessLogSerializer,
    EmergencyContactSerializer,
    EmergencyProfileSerializer,
    EmergencyVaccinationSerializer,
    habit_log_queryset_for_request,
    habit_queryset_for_request,
    HabitLogSerializer,
    HabitSerializer,
    HealthLogSerializer,
    HealthLogWriteSerializer,
    HealthParameterSerializer,
    MoodSerializer,
    PersonSerializer,
    StatusMediaSerializer,
    StatusSerializer,
    UserProfileSerializer,
    VaccinationSerializer,
)


class StatusCheckView(View):
    def get(self, request):
        return JsonResponse({"status": "OK"})


class CurrentProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserProfileSerializer(request.user.userprofile).data)

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user.userprofile,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


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

        payload = {
            "display_name": profile.display_name,
            "legal_name": profile.legal_name,
            "phone": profile.phone,
            "address": profile.address,
            "date_of_birth": profile.date_of_birth,
            "blood_type": medical_info.blood_type,
            "allergies": medical_info.allergies,
            "medical_notes": medical_info.medical_notes,
            "contacts": EmergencyContactSerializer(
                request.user.person_set.filter(emergency_contact=True),
                many=True,
            ).data,
            "vaccinations": EmergencyVaccinationSerializer(
                latest_vaccinations,
                many=True,
            ).data,
        }
        return Response(EmergencyProfileSerializer(payload).data)

    def patch(self, request):
        profile_serializer = UserProfileSerializer(
            request.user.userprofile,
            data=request.data,
            partial=True,
        )
        profile_serializer.is_valid(raise_exception=True)
        profile_serializer.save()

        medical_info, _ = BasicMedicalInfo.objects.get_or_create(user=request.user)
        medical_serializer = BasicMedicalInfoSerializer(
            medical_info,
            data=request.data,
            partial=True,
        )
        medical_serializer.is_valid(raise_exception=True)
        medical_serializer.save()
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
        return Status.objects.filter(user=self.request.user)

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
        return Dream.objects.filter(user=self.request.user)

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
