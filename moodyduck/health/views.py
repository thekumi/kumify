from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from .models import (
    Medication,
    MedicationSettings,
    HealthParameter,
    HealthLog,
    Vaccination,
)
from .forms import (
    MedicationForm,
    MedicationSettingsForm,
    HealthParameterForm,
    HealthLogForm,
    VaccinationForm,
)


class MedicationListView(LoginRequiredMixin, ListView):
    template_name = "health/medication_list.html"
    model = Medication

    def get_queryset(self):
        return Medication.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Medications")
        context["subtitle"] = _("Your medications and supply.")
        context["buttons"] = [
            (reverse_lazy("health:medication_create"), _("New Medication"), "plus"),
            (reverse_lazy("health:settings"), _("Settings"), "cog"),
        ]
        try:
            context["settings"] = MedicationSettings.objects.get(user=self.request.user)
        except MedicationSettings.DoesNotExist:
            context["settings"] = None
        return context


class MedicationCreateView(LoginRequiredMixin, CreateView):
    template_name = "health/medication_edit.html"
    model = Medication
    form_class = MedicationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Add Medication")
        context["buttons"] = [
            (reverse_lazy("health:medication_list"), _("Back"), "arrow-left")
        ]
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("health:medication_list")


class MedicationEditView(LoginRequiredMixin, UpdateView):
    template_name = "health/medication_edit.html"
    model = Medication
    form_class = MedicationForm

    def get_object(self, queryset=None):
        return get_object_or_404(
            Medication, user=self.request.user, id=self.kwargs["id"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Edit Medication")
        context["buttons"] = [
            (reverse_lazy("health:medication_list"), _("Back"), "arrow-left")
        ]
        return context

    def get_success_url(self):
        return reverse_lazy("health:medication_list")


class MedicationDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "health/medication_delete.html"
    model = Medication

    def get_object(self, queryset=None):
        return get_object_or_404(
            Medication, user=self.request.user, id=self.kwargs["id"]
        )

    def get_success_url(self):
        return reverse_lazy("health:medication_list")


class MedicationSettingsView(LoginRequiredMixin, UpdateView):
    template_name = "health/medication_settings.html"
    model = MedicationSettings
    form_class = MedicationSettingsForm

    def get_object(self, queryset=None):
        obj, _ = MedicationSettings.objects.get_or_create(user=self.request.user)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Medication Settings")
        context["buttons"] = [
            (reverse_lazy("health:medication_list"), _("Back"), "arrow-left")
        ]
        return context

    def get_success_url(self):
        return reverse_lazy("health:medication_list")


class HealthParameterListView(LoginRequiredMixin, ListView):
    template_name = "health/parameter_list.html"
    model = HealthParameter

    def get_queryset(self):
        return HealthParameter.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Health Parameters")
        context["subtitle"] = _("Define the metrics you want to track.")
        context["buttons"] = [
            (reverse_lazy("health:parameter_create"), _("New Parameter"), "plus"),
        ]
        return context


class HealthParameterCreateView(LoginRequiredMixin, CreateView):
    template_name = "health/parameter_edit.html"
    model = HealthParameter
    form_class = HealthParameterForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Add Parameter")
        context["buttons"] = [
            (reverse_lazy("health:parameter_list"), _("Back"), "arrow-left")
        ]
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("health:parameter_list")


class HealthParameterEditView(LoginRequiredMixin, UpdateView):
    template_name = "health/parameter_edit.html"
    model = HealthParameter
    form_class = HealthParameterForm

    def get_object(self, queryset=None):
        return get_object_or_404(
            HealthParameter, user=self.request.user, id=self.kwargs["id"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Edit Parameter")
        context["buttons"] = [
            (reverse_lazy("health:parameter_list"), _("Back"), "arrow-left")
        ]
        return context

    def get_success_url(self):
        return reverse_lazy("health:parameter_list")


class HealthParameterDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "health/parameter_delete.html"
    model = HealthParameter

    def get_object(self, queryset=None):
        return get_object_or_404(
            HealthParameter, user=self.request.user, id=self.kwargs["id"]
        )

    def get_success_url(self):
        return reverse_lazy("health:parameter_list")


class HealthLogListView(LoginRequiredMixin, ListView):
    template_name = "health/log_list.html"
    model = HealthLog

    def get_queryset(self):
        return HealthLog.objects.filter(user=self.request.user).prefetch_related(
            "records__parameter"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Health Log")
        context["subtitle"] = _("Your check-ins over time.")
        context["buttons"] = [
            (reverse_lazy("health:log_create"), _("New Check-in"), "plus"),
        ]
        return context


class HealthLogMixin(LoginRequiredMixin):
    """Common helpers for HealthLog create/edit views."""

    template_name = "health/log_edit.html"
    model = HealthLog
    form_class = HealthLogForm

    def get_parameters(self):
        return HealthParameter.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["parameters"] = self.get_parameters()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context["form"]
        # Build paired list so templates don't need a custom filter
        context["param_fields"] = [
            (param, form[f"param_{param.id}"]) for param in self.get_parameters()
        ]
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        form.save_records()
        return response

    def get_success_url(self):
        return reverse_lazy("health:log_list")


class HealthLogCreateView(HealthLogMixin, CreateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("New Health Check-in")
        context["subtitle"] = _("Record today's health measurements.")
        context["buttons"] = [
            (reverse_lazy("health:log_list"), _("Back"), "arrow-left")
        ]
        return context


class HealthLogEditView(HealthLogMixin, UpdateView):
    def get_object(self, queryset=None):
        return get_object_or_404(
            HealthLog, user=self.request.user, id=self.kwargs["id"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Edit Health Check-in")
        context["buttons"] = [
            (reverse_lazy("health:log_list"), _("Back"), "arrow-left"),
            (
                reverse_lazy("health:log_delete", kwargs={"id": self.kwargs["id"]}),
                _("Delete"),
                "trash",
            ),
        ]
        return context


class HealthLogDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "health/log_delete.html"
    model = HealthLog

    def get_object(self, queryset=None):
        return get_object_or_404(
            HealthLog, user=self.request.user, id=self.kwargs["id"]
        )

    def get_success_url(self):
        return reverse_lazy("health:log_list")


class VaccinationListView(LoginRequiredMixin, ListView):
    template_name = "health/vaccination_list.html"
    model = Vaccination

    def get_queryset(self):
        return Vaccination.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Vaccinations")
        context["subtitle"] = _("Keep a record of your immunizations and boosters.")
        context["buttons"] = [
            (reverse_lazy("health:vaccination_create"), _("Add Vaccination"), "plus"),
        ]
        return context


class VaccinationCreateView(LoginRequiredMixin, CreateView):
    template_name = "health/vaccination_edit.html"
    model = Vaccination
    form_class = VaccinationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Add Vaccination")
        context["buttons"] = [
            (reverse_lazy("health:vaccination_list"), _("Back"), "arrow-left")
        ]
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("health:vaccination_list")


class VaccinationEditView(LoginRequiredMixin, UpdateView):
    template_name = "health/vaccination_edit.html"
    model = Vaccination
    form_class = VaccinationForm

    def get_object(self, queryset=None):
        return get_object_or_404(
            Vaccination, user=self.request.user, id=self.kwargs["id"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Edit Vaccination")
        context["buttons"] = [
            (reverse_lazy("health:vaccination_list"), _("Back"), "arrow-left"),
            (
                reverse_lazy(
                    "health:vaccination_delete", kwargs={"id": self.kwargs["id"]}
                ),
                _("Delete"),
                "trash",
            ),
        ]
        return context

    def get_success_url(self):
        return reverse_lazy("health:vaccination_list")


class VaccinationDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "health/vaccination_delete.html"
    model = Vaccination

    def get_object(self, queryset=None):
        return get_object_or_404(
            Vaccination, user=self.request.user, id=self.kwargs["id"]
        )

    def get_success_url(self):
        return reverse_lazy("health:vaccination_list")
