from django.forms import ModelForm

from moodyduck.frontend.mixins import BootstrapMixin
from .models import Habit, HabitLog


class HabitForm(BootstrapMixin, ModelForm):
    class Meta:
        model = Habit
        fields = ["name", "icon", "color", "description"]


class HabitLogForm(BootstrapMixin, ModelForm):
    class Meta:
        model = HabitLog
        fields = ["date", "note"]
