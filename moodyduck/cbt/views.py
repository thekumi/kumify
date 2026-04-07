from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from .models import ThoughtRecord
from .forms import ThoughtRecordForm


class ThoughtRecordListView(LoginRequiredMixin, ListView):
    template_name = "cbt/record_list.html"
    model = ThoughtRecord

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Thought Records")
        context["subtitle"] = _("Your CBT thought records.")
        context["buttons"] = [
            (reverse_lazy("cbt:record_create"), _("New Record"), "plus")
        ]
        return context

    def get_queryset(self):
        return ThoughtRecord.objects.filter(user=self.request.user).order_by("-id")


class ThoughtRecordViewView(LoginRequiredMixin, DetailView):
    template_name = "cbt/record_view.html"
    model = ThoughtRecord

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Thought Record")
        context["subtitle"] = self.object.title or _("Thought Record")
        context["buttons"] = [
            (
                reverse_lazy("cbt:record_edit", kwargs={"id": self.kwargs["id"]}),
                _("Edit"),
                "pencil-simple",
            )
        ]
        return context

    def get_object(self):
        return get_object_or_404(
            ThoughtRecord, user=self.request.user, id=self.kwargs["id"]
        )


class ThoughtRecordCreateView(LoginRequiredMixin, CreateView):
    form_class = ThoughtRecordForm
    template_name = "cbt/record_edit.html"
    model = ThoughtRecord

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("New Thought Record")
        context["subtitle"] = _("Document a thought and examine the evidence.")
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("cbt:record_view", kwargs={"id": self.object.id})


class ThoughtRecordEditView(LoginRequiredMixin, UpdateView):
    form_class = ThoughtRecordForm
    template_name = "cbt/record_edit.html"
    model = ThoughtRecord

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Edit Thought Record")
        context["subtitle"] = self.object.title or _("Thought Record")
        context["buttons"] = [
            (
                reverse_lazy("cbt:record_delete", kwargs={"id": self.kwargs["id"]}),
                _("Delete"),
                "trash",
            )
        ]
        return context

    def get_object(self):
        return get_object_or_404(
            ThoughtRecord, user=self.request.user, id=self.kwargs["id"]
        )

    def get_success_url(self):
        return reverse_lazy("cbt:record_view", kwargs={"id": self.object.id})


class ThoughtRecordDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "cbt/record_delete.html"
    model = ThoughtRecord

    def get_object(self):
        return get_object_or_404(
            ThoughtRecord, user=self.request.user, id=self.kwargs["id"]
        )

    def get_success_url(self):
        return reverse_lazy("cbt:record_list")
