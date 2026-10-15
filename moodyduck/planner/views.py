from django.db.models import Q
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CalendarEvent, Task, TaskList, UserCalendar
from .registry import get_virtual_calendars, get_virtual_task_lists
from .serializers import (
    CalendarEventSerializer,
    TaskListSerializer,
    TaskSerializer,
    UserCalendarSerializer,
)


class UserCalendarViewSet(viewsets.ModelViewSet):
    serializer_class = UserCalendarSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserCalendar.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        for descriptor in get_virtual_calendars():
            UserCalendar.objects.get_or_create(
                user=request.user,
                virtual_key=descriptor.key,
                defaults={"color": descriptor.color},
            )
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CalendarEventViewSet(viewsets.ModelViewSet):
    serializer_class = CalendarEventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = CalendarEvent.objects.filter(calendar__user=self.request.user)
        calendar_id = self.request.query_params.get("calendar")
        if calendar_id:
            qs = qs.filter(calendar_id=calendar_id)
        from_date = self.request.query_params.get("from")
        to_date = self.request.query_params.get("to")
        if from_date and to_date:
            qs = qs.filter(
                Q(rrule__isnull=False)
                | Q(start__date__gte=from_date, start__date__lte=to_date)
            )
        return qs


class TaskListViewSet(viewsets.ModelViewSet):
    serializer_class = TaskListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TaskList.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        for descriptor in get_virtual_task_lists():
            TaskList.objects.get_or_create(
                user=request.user,
                virtual_key=descriptor.key,
                defaults={"color": descriptor.color},
            )
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Task.objects.filter(task_list__user=self.request.user)
        task_list_id = self.request.query_params.get("task_list")
        if task_list_id:
            qs = qs.filter(task_list_id=task_list_id)
        from_date = self.request.query_params.get("from")
        to_date = self.request.query_params.get("to")
        if from_date and to_date:
            qs = qs.filter(
                Q(rrule__isnull=False)
                | Q(due_date__gte=from_date, due_date__lte=to_date)
            )
        done = self.request.query_params.get("done")
        if done is not None:
            qs = qs.filter(done=done.lower() in ("true", "1"))
        return qs


class VirtualDescriptorsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "calendars": [
                    {"key": d.key, "color": d.color} for d in get_virtual_calendars()
                ],
                "task_lists": [
                    {"key": d.key, "color": d.color} for d in get_virtual_task_lists()
                ],
            }
        )
