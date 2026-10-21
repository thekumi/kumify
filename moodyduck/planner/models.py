from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class UserCalendar(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, models.CASCADE, related_name="calendars")
    color = models.CharField(max_length=7, default="#4A90D9")
    is_visible = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)
    # Non-null for auto-created virtual calendars; null for user-created ones.
    virtual_key = models.CharField(max_length=64, null=True, blank=True)
    encrypted_payload = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["order", "pk"]
        unique_together = [("user", "virtual_key")]

    def __str__(self):
        return str(self.pk)


class CalendarEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    calendar = models.ForeignKey(UserCalendar, models.CASCADE, related_name="events")
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)
    all_day = models.BooleanField(default=False)
    # iCalendar RRULE string for recurring events; expanded by the API within
    # the requested date window.
    rrule = models.CharField(max_length=256, null=True, blank=True)
    encrypted_payload = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["start"]

    def __str__(self):
        return str(self.pk)


class TaskList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, models.CASCADE, related_name="task_lists")
    color = models.CharField(max_length=7, default="#4A90D9")
    is_visible = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)
    virtual_key = models.CharField(max_length=64, null=True, blank=True)
    encrypted_payload = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["order", "pk"]
        unique_together = [("user", "virtual_key")]

    def __str__(self):
        return str(self.pk)


class Medication(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, models.CASCADE, related_name="medications")
    encrypted_payload = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return str(self.pk)


class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    task_list = models.ForeignKey(TaskList, models.CASCADE, related_name="tasks")
    due_date = models.DateField(null=True, blank=True)
    reminder_at = models.DateTimeField(null=True, blank=True)
    rrule = models.CharField(max_length=256, null=True, blank=True)
    done = models.BooleanField(default=False)
    done_at = models.DateTimeField(null=True, blank=True)
    encrypted_payload = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["due_date", "pk"]

    def __str__(self):
        return str(self.pk)
