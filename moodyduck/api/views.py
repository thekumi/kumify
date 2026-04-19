from django.http import JsonResponse
from django.views import View

from rest_framework import permissions, viewsets
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from moodyduck.mood.models import Mood, Status
from moodyduck.habits.models import Habit, HabitLog
from moodyduck.health.models import HealthLog, HealthParameter, Vaccination
from moodyduck.cbt.models import ThoughtRecord
from moodyduck.dreams.models import Dream

from .serializers import (
    CBTRecordSerializer,
    DreamSerializer,
    HabitLogSerializer,
    HabitSerializer,
    HealthLogSerializer,
    HealthParameterSerializer,
    MoodSerializer,
    StatusSerializer,
    VaccinationSerializer,
)


class StatusCheckView(View):
    def get(self, request):
        return JsonResponse({"status": "OK"})


class MoodViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = MoodSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Mood.objects.filter(user=self.request.user)


class StatusViewSet(viewsets.ModelViewSet):
    serializer_class = StatusSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Status.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HabitViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)


class HabitLogViewSet(viewsets.ModelViewSet):
    serializer_class = HabitLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return HabitLog.objects.filter(habit__user=self.request.user)


class HealthParameterViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = HealthParameterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return HealthParameter.objects.filter(user=self.request.user)


class HealthLogViewSet(viewsets.ModelViewSet):
    serializer_class = HealthLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return HealthLog.objects.filter(user=self.request.user)

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
