from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _

from .models import CO2Category, CO2Entry, CO2Offset
from .forms import CO2CategoryForm, CO2EntryForm, CO2OffsetForm


class CO2DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "environment/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Environment")
        context["subtitle"] = _("Your CO2 footprint overview.")
        total_emissions = (
            CO2Entry.objects.filter(user=self.request.user).aggregate(
                total=Sum("amount_kg")
            )["total"]
            or 0
        )
        total_offsets = (
            CO2Offset.objects.filter(user=self.request.user).aggregate(
                total=Sum("amount_kg")
            )["total"]
            or 0
        )
        context["total_emissions"] = total_emissions
        context["total_offsets"] = total_offsets
        context["net_balance"] = total_emissions - total_offsets
        context["recent_entries"] = CO2Entry.objects.filter(user=self.request.user)[:5]
        context["recent_offsets"] = CO2Offset.objects.filter(user=self.request.user)[:5]
        return context


class CO2EntryListView(LoginRequiredMixin, ListView):
    template_name = "environment/entry_list.html"
    model = CO2Entry

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("CO2 Entries")
        context["subtitle"] = _("Your recorded CO2 emissions.")
        context["buttons"] = [
            (reverse_lazy("environment:entry_create"), _("New Entry"), "plus")
        ]
        context["total"] = (
            self.get_queryset().aggregate(total=Sum("amount_kg"))["total"] or 0
        )
        return context

    def get_queryset(self):
        return CO2Entry.objects.filter(user=self.request.user)


class CO2EntryCreateView(LoginRequiredMixin, CreateView):
    template_name = "environment/entry_edit.html"
    form_class = CO2EntryForm
    model = CO2Entry

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("New CO2 Entry")
        context["subtitle"] = _("Record a CO2 emission.")
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("environment:entry_list")


class CO2EntryEditView(LoginRequiredMixin, UpdateView):
    template_name = "environment/entry_edit.html"
    form_class = CO2EntryForm
    model = CO2Entry

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Edit CO2 Entry")
        context["subtitle"] = str(self.object.description)
        context["buttons"] = [
            (
                reverse_lazy(
                    "environment:entry_delete", kwargs={"id": self.kwargs["id"]}
                ),
                _("Delete"),
                "trash",
            )
        ]
        return context

    def get_object(self):
        return get_object_or_404(CO2Entry, user=self.request.user, id=self.kwargs["id"])

    def get_success_url(self):
        return reverse_lazy("environment:entry_list")


class CO2EntryDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "environment/entry_delete.html"
    model = CO2Entry

    def get_object(self):
        return get_object_or_404(CO2Entry, user=self.request.user, id=self.kwargs["id"])

    def get_success_url(self):
        return reverse_lazy("environment:entry_list")


class CO2OffsetListView(LoginRequiredMixin, ListView):
    template_name = "environment/offset_list.html"
    model = CO2Offset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("CO2 Offsets")
        context["subtitle"] = _("Your recorded CO2 offsets.")
        context["buttons"] = [
            (reverse_lazy("environment:offset_create"), _("New Offset"), "plus")
        ]
        context["total"] = (
            self.get_queryset().aggregate(total=Sum("amount_kg"))["total"] or 0
        )
        return context

    def get_queryset(self):
        return CO2Offset.objects.filter(user=self.request.user)


class CO2OffsetCreateView(LoginRequiredMixin, CreateView):
    template_name = "environment/offset_edit.html"
    form_class = CO2OffsetForm
    model = CO2Offset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("New CO2 Offset")
        context["subtitle"] = _("Record a CO2 offset.")
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("environment:offset_list")


class CO2OffsetEditView(LoginRequiredMixin, UpdateView):
    template_name = "environment/offset_edit.html"
    form_class = CO2OffsetForm
    model = CO2Offset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Edit CO2 Offset")
        context["subtitle"] = str(self.object.description)
        context["buttons"] = [
            (
                reverse_lazy(
                    "environment:offset_delete", kwargs={"id": self.kwargs["id"]}
                ),
                _("Delete"),
                "trash",
            )
        ]
        return context

    def get_object(self):
        return get_object_or_404(
            CO2Offset, user=self.request.user, id=self.kwargs["id"]
        )

    def get_success_url(self):
        return reverse_lazy("environment:offset_list")


class CO2OffsetDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "environment/offset_delete.html"
    model = CO2Offset

    def get_object(self):
        return get_object_or_404(
            CO2Offset, user=self.request.user, id=self.kwargs["id"]
        )

    def get_success_url(self):
        return reverse_lazy("environment:offset_list")


class CO2CategoryListView(LoginRequiredMixin, ListView):
    template_name = "environment/category_list.html"
    model = CO2Category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("CO2 Categories")
        context["subtitle"] = _("Categories for your emissions.")
        context["buttons"] = [
            (reverse_lazy("environment:category_create"), _("New Category"), "plus")
        ]
        return context

    def get_queryset(self):
        return CO2Category.objects.filter(user=self.request.user)


class CO2CategoryCreateView(LoginRequiredMixin, CreateView):
    template_name = "environment/category_edit.html"
    form_class = CO2CategoryForm
    model = CO2Category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("New Category")
        context["subtitle"] = _("Add an emission category.")
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("environment:category_list")


class CO2CategoryEditView(LoginRequiredMixin, UpdateView):
    template_name = "environment/category_edit.html"
    form_class = CO2CategoryForm
    model = CO2Category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Edit Category")
        context["subtitle"] = str(self.object.name)
        context["buttons"] = [
            (
                reverse_lazy(
                    "environment:category_delete", kwargs={"id": self.kwargs["id"]}
                ),
                "Delete",
                "trash",
            )
        ]
        return context

    def get_object(self):
        return get_object_or_404(
            CO2Category, user=self.request.user, id=self.kwargs["id"]
        )

    def get_success_url(self):
        return reverse_lazy("environment:category_list")


class CO2CategoryDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "environment/category_delete.html"
    model = CO2Category

    def get_object(self):
        return get_object_or_404(
            CO2Category, user=self.request.user, id=self.kwargs["id"]
        )

    def get_success_url(self):
        return reverse_lazy("environment:category_list")
