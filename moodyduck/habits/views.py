from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from .models import Habit, HabitLog
from .forms import HabitForm, HabitLogForm


class HabitListView(LoginRequiredMixin, ListView):
    template_name = "habits/habit_list.html"
    model = Habit

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Habits")
        context["subtitle"] = _("Your habits and their schedules.")
        context["buttons"] = [
            (reverse_lazy("habits:habit_create"), _("New Habit"), "plus")
        ]
        return context

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)


class HabitCreateView(LoginRequiredMixin, CreateView):
    template_name = "habits/habit_edit.html"
    form_class = HabitForm
    model = Habit

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("New Habit")
        context["subtitle"] = _("Define a new habit to track.")
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("habits:habit_list")


class HabitEditView(LoginRequiredMixin, UpdateView):
    template_name = "habits/habit_edit.html"
    form_class = HabitForm
    model = Habit

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Edit Habit")
        context["subtitle"] = self.object.name
        context["buttons"] = [
            (
                reverse_lazy("habits:habit_delete", kwargs={"id": self.kwargs["id"]}),
                _("Delete"),
                "trash",
            ),
            (
                reverse_lazy(
                    "habits:log_create", kwargs={"habit_id": self.kwargs["id"]}
                ),
                _("Log Now"),
                "check",
            ),
        ]
        return context

    def get_object(self):
        return get_object_or_404(Habit, user=self.request.user, id=self.kwargs["id"])

    def get_success_url(self):
        return reverse_lazy("habits:habit_list")


class HabitDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "habits/habit_delete.html"
    model = Habit

    def get_object(self):
        return get_object_or_404(Habit, user=self.request.user, id=self.kwargs["id"])

    def get_success_url(self):
        return reverse_lazy("habits:habit_list")


class HabitLogListView(LoginRequiredMixin, ListView):
    template_name = "habits/log_list.html"
    model = HabitLog

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Habit Log")
        context["subtitle"] = _("A record of your completed habits.")
        return context

    def get_queryset(self):
        return HabitLog.objects.filter(habit__user=self.request.user).select_related(
            "habit"
        )


class HabitLogCreateView(LoginRequiredMixin, CreateView):
    template_name = "habits/log_edit.html"
    form_class = HabitLogForm
    model = HabitLog

    def get_habit(self):
        return get_object_or_404(
            Habit, user=self.request.user, id=self.kwargs["habit_id"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        habit = self.get_habit()
        context["title"] = _("Log Habit")
        context["subtitle"] = f"Record a completion of: {habit.name}"
        context["habit"] = habit
        return context

    def form_valid(self, form):
        form.instance.habit = self.get_habit()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("habits:log_list")


class HabitLogEditView(LoginRequiredMixin, UpdateView):
    template_name = "habits/log_edit.html"
    form_class = HabitLogForm
    model = HabitLog

    def get_object(self):
        return get_object_or_404(
            HabitLog, habit__user=self.request.user, id=self.kwargs["id"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Edit Log Entry")
        context["subtitle"] = f"Edit log for: {self.object.habit.name}"
        context["habit"] = self.object.habit
        return context

    def get_success_url(self):
        return reverse_lazy("habits:log_list")


class HabitLogDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "habits/log_delete.html"
    model = HabitLog

    def get_object(self):
        return get_object_or_404(
            HabitLog, habit__user=self.request.user, id=self.kwargs["id"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Delete Log Entry")
        context["subtitle"] = f"Delete log for: {self.object.habit.name}"
        return context

    def get_success_url(self):
        return reverse_lazy("habits:log_list")
