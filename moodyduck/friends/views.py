from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from .models import Person
from .forms import PersonForm


class PersonListView(LoginRequiredMixin, ListView):
    template_name = "friends/person_list.html"
    model = Person

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Friends")
        context["subtitle"] = _("People you care about.")
        context["buttons"] = [
            (reverse_lazy("friends:person_create"), _("Add Person"), "plus")
        ]
        return context

    def get_queryset(self):
        return Person.objects.filter(user=self.request.user)


class PersonViewView(LoginRequiredMixin, DetailView):
    template_name = "friends/person_view.html"
    model = Person

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.object.display_name
        context["subtitle"] = _("Contact details")
        context["buttons"] = [
            (
                reverse_lazy("friends:person_edit", kwargs={"id": self.kwargs["id"]}),
                _("Edit"),
                "pencil-simple",
            )
        ]
        return context

    def get_object(self):
        return get_object_or_404(Person, user=self.request.user, id=self.kwargs["id"])


class PersonCreateView(LoginRequiredMixin, CreateView):
    template_name = "friends/person_edit.html"
    form_class = PersonForm
    model = Person

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Add Person")
        context["subtitle"] = _("Add someone to your contacts.")
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("friends:person_view", kwargs={"id": self.object.id})


class PersonEditView(LoginRequiredMixin, UpdateView):
    template_name = "friends/person_edit.html"
    form_class = PersonForm
    model = Person

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Edit Person")
        context["subtitle"] = self.object.display_name
        context["buttons"] = [
            (
                reverse_lazy("friends:person_delete", kwargs={"id": self.kwargs["id"]}),
                _("Delete"),
                "trash",
            )
        ]
        return context

    def get_object(self):
        return get_object_or_404(Person, user=self.request.user, id=self.kwargs["id"])

    def get_success_url(self):
        return reverse_lazy("friends:person_view", kwargs={"id": self.object.id})


class PersonDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "friends/person_delete.html"
    model = Person

    def get_object(self):
        return get_object_or_404(Person, user=self.request.user, id=self.kwargs["id"])

    def get_success_url(self):
        return reverse_lazy("friends:person_list")
