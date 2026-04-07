from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date

from colorfield.fields import ColorField
from polymorphic.models import PolymorphicModel
from dateutil.relativedelta import relativedelta

from moodyduck.common.fields import WeekdayField, DayOfMonthField


class Habit(models.Model):
    class Meta:
        ordering = ["name"]

    user = models.ForeignKey(get_user_model(), models.CASCADE)
    name = models.CharField(max_length=64)
    icon = models.CharField(default="ph ph-user-gear", max_length=64)
    color = ColorField(default="#000000")
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class HabitSchedule(PolymorphicModel):
    habit = models.ForeignKey(Habit, models.CASCADE)
    active = models.BooleanField(default=True)

    def next_scheduled(self, today=True):
        raise NotImplementedError(
            "%s does not implement next_scheduled." % self.__class__
        )


class MonthlyHabitSchedule(HabitSchedule):
    day = DayOfMonthField()

    def next_scheduled(self, today=True):
        now = timezone.now()
        if self.day < now.day:
            return (now + relativedelta(months=1, day=self.day)).date()
        elif self.day == now.day:
            return (
                now.date()
                if today
                else (now + relativedelta(months=1, day=self.day)).date()
            )
        return (now + relativedelta(day=self.day)).date()


class WeeklyHabitSchedule(HabitSchedule):
    weekdays = WeekdayField()

    def next_scheduled(self, today=True):
        now = timezone.now()
        found = None
        for weekday in self.weekdays:
            on = now + relativedelta(weekday=weekday)
            if on.date() < now.date() or (on.date() == now.date() and not today):
                on += relativedelta(weeks=1)
            if found is None or on.date() < found.date():
                found = on
        return found.date() if found else None


class DailyHabitSchedule(HabitSchedule):
    def next_scheduled(self, today=True):
        if self.active:
            return (
                timezone.now().date()
                if today
                else (timezone.now() + relativedelta(days=1)).date()
            )
        return None


class DateHabitSchedule(HabitSchedule):
    date = models.DateField()

    def next_scheduled(self, today=True):
        now = timezone.now().date()
        if self.active and (self.date > now or (today and self.date == now)):
            return self.date
        return None


class HabitLog(models.Model):
    class Meta:
        ordering = ["-date"]

    habit = models.ForeignKey(Habit, models.CASCADE)
    date = models.DateField(default=date.today)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.habit.name} – {self.date}"
