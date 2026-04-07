from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from multiselectfield import MultiSelectField


class WeekdayChoices(models.IntegerChoices):
    MONDAY = 0, _("Monday")
    TUESDAY = 1, _("Tuesday")
    WEDNESDAY = 2, _("Wednesday")
    THURSDAY = 3, _("Thursday")
    FRIDAY = 4, _("Friday")
    SATURDAY = 5, _("Saturday")
    SUNDAY = 6, _("Sunday")


class PercentageField(models.FloatField):
    default_validators = [MaxValueValidator(100), MinValueValidator(0)]


class WeekdayField(MultiSelectField):
    def __init__(self, *args, **kwargs):
        self.choices = WeekdayChoices.choices
        super().__init__(*args, **kwargs)


class DayOfMonthField(models.PositiveIntegerField):
    default_validators = [MinValueValidator(1), MaxValueValidator(31)]
