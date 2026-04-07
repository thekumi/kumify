from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from datetime import time, date

from dateutil.relativedelta import relativedelta


class MedicationSettings(models.Model):
    user = models.ForeignKey(get_user_model(), models.CASCADE)

    morning_from = models.TimeField(default=time(6))
    morning_till = models.TimeField(default=time(10))
    noon_from = models.TimeField(default=time(12))
    noon_till = models.TimeField(default=time(14))
    evening_from = models.TimeField(default=time(19))
    evening_till = models.TimeField(default=time(21))
    night_from = models.TimeField(default=time(22))
    night_till = models.TimeField(default=time(23))

    notifications = models.BooleanField(default=True)
    refill_reminder = models.PositiveSmallIntegerField(default=7)

    def __str__(self):
        return f"Medication settings for {self.user}"


class Medication(models.Model):
    class Meta:
        ordering = ["name"]

    user = models.ForeignKey(get_user_model(), models.CASCADE)
    name = models.CharField(max_length=128)
    icon = models.CharField(max_length=64, default="ph ph-pill")

    supply = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=2)
    default_refill = models.PositiveSmallIntegerField(default=1)

    prn = models.BooleanField(default=False, help_text=_("As needed (pro re nata)"))
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class ScheduleChoices(models.IntegerChoices):
    DAYS = 0, _("Days")
    WEEKS = 1, _("Weeks")
    MONTHS = 2, _("Months")


class MedicationSchedule(models.Model):
    medication = models.ForeignKey(Medication, models.CASCADE)

    cycle_type = models.IntegerField(choices=ScheduleChoices.choices)
    cycle_count = models.IntegerField(default=1)

    first = models.DateField(default=date.today)
    last = models.DateField(null=True, blank=True)

    morning = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=2)
    noon = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=2)
    evening = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=2)
    night = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.medication.name} schedule"

    def next(self, today=True):
        if self.last and timezone.now().date() > self.last:
            return False
        cur = self.first
        while True:
            if (timezone.now().date() < cur) or (
                today and timezone.now().date() == cur
            ):
                return cur
            cur += relativedelta(
                days=self.cycle_count if self.cycle_type == ScheduleChoices.DAYS else 0,
                weeks=(
                    self.cycle_count if self.cycle_type == ScheduleChoices.WEEKS else 0
                ),
                months=(
                    self.cycle_count if self.cycle_type == ScheduleChoices.MONTHS else 0
                ),
            )
            if self.last and cur > self.last:
                return False


class MedicationCalendar(models.Model):
    class TimeChoices(models.IntegerChoices):
        MORNING = 0, _("Morning")
        NOON = 1, _("Noon")
        EVENING = 2, _("Evening")
        NIGHT = 3, _("Night")

    date = models.DateField(default=date.today)
    time = models.IntegerField(choices=TimeChoices.choices)

    medication = models.ForeignKey(Medication, models.CASCADE)
    schedule = models.ForeignKey(MedicationSchedule, models.SET_NULL, null=True)

    count = models.DecimalField(max_digits=5, decimal_places=2)
    taken = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.medication.name} on {self.date}"


class HealthParameter(models.Model):
    class Meta:
        ordering = ["name"]

    user = models.ForeignKey(get_user_model(), models.CASCADE)
    name = models.CharField(max_length=128)
    icon = models.CharField(max_length=64, default="ph ph-heart")
    unit = models.CharField(max_length=12, null=True, blank=True)

    def __str__(self):
        return self.name


class HealthLog(models.Model):
    """A single health check-in containing values for multiple parameters."""

    class Meta:
        ordering = ["-recorded_at"]

    user = models.ForeignKey(get_user_model(), models.CASCADE)
    recorded_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Health log — {self.recorded_at:%Y-%m-%d %H:%M}"


class HealthRecord(models.Model):
    """A single parameter value within a HealthLog check-in."""

    log = models.ForeignKey(HealthLog, models.CASCADE, related_name="records")
    parameter = models.ForeignKey(HealthParameter, models.CASCADE)
    value = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.parameter.name}: {self.value}"
