from django import forms

from moodyduck.frontend.mixins import BootstrapMixin
from .models import (
    Medication,
    MedicationSchedule,
    MedicationSettings,
    HealthParameter,
    HealthLog,
    HealthRecord,
)


class MedicationForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Medication
        fields = ["name", "icon", "supply", "default_refill", "prn", "remarks"]


class MedicationScheduleForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = MedicationSchedule
        fields = [
            "cycle_type",
            "cycle_count",
            "first",
            "last",
            "morning",
            "noon",
            "evening",
            "night",
        ]


class MedicationSettingsForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = MedicationSettings
        fields = [
            "morning_from",
            "morning_till",
            "noon_from",
            "noon_till",
            "evening_from",
            "evening_till",
            "night_from",
            "night_till",
            "notifications",
            "refill_reminder",
        ]


class HealthParameterForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = HealthParameter
        fields = ["name", "icon", "unit"]


class HealthLogForm(BootstrapMixin, forms.ModelForm):
    """
    A form for a single health check-in.

    Dynamic fields named `param_<id>` are added for every HealthParameter
    belonging to the current user.  On save, ``save_records()`` must be
    called to persist the individual HealthRecord values.
    """

    class Meta:
        model = HealthLog
        fields = ["recorded_at", "notes"]
        widgets = {
            "recorded_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, parameters=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parameters = parameters or []
        for param in self.parameters:
            field_name = f"param_{param.id}"
            self.fields[field_name] = forms.DecimalField(
                label=f"{param.name}" + (f" ({param.unit})" if param.unit else ""),
                required=False,
                max_digits=12,
                decimal_places=6,
            )
            # Pre-populate on edit
            if self.instance.pk:
                try:
                    record = self.instance.records.get(parameter=param)
                    self.initial[field_name] = record.value
                except HealthRecord.DoesNotExist:
                    pass

    def save_records(self):
        """Create or update one HealthRecord per parameter after the log is saved."""
        for param in self.parameters:
            value = self.cleaned_data.get(f"param_{param.id}")
            if value is not None:
                HealthRecord.objects.update_or_create(
                    log=self.instance,
                    parameter=param,
                    defaults={"value": value},
                )
            else:
                # Remove a previously-set value if the field was cleared
                HealthRecord.objects.filter(log=self.instance, parameter=param).delete()
