from django.views.generic import (
    ListView,
    UpdateView,
    DetailView,
    CreateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

from .models import Dream, DreamTheme, DreamMedia, Theme
from .forms import DreamForm

from moodyduck.common.helpers import get_upload_path

class DreamListView(LoginRequiredMixin, ListView):
    template_name = "dreams/dream_list.html"
    model = Dream

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Dream List")
        context["subtitle"] = _("A list of the dreams you have entered so far.")
        context["buttons"] = [
            (reverse_lazy("dreams:dream_create"), _("New Dream"), "plus")
        ]
        return context

    def get_queryset(self):
        return Dream.objects.filter(user=self.request.user).order_by("timestamp")


class DreamViewView(LoginRequiredMixin, DetailView):
    template_name = "dreams/dream_view.html"
    model = Dream

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("View Dream")
        context["subtitle"] = _("View the details of your dream.")
        context["buttons"] = [
            (
                reverse_lazy("dreams:dream_edit", kwargs={"id": self.kwargs["id"]}),
                _("Edit Dream"),
                "pencil-simple",
            )
        ]
        return context

    def get_object(self):
        return get_object_or_404(Dream, user=self.request.user, id=self.kwargs["id"])


class DreamCreateView(LoginRequiredMixin, CreateView):
    template_name = "dreams/dream_edit.html"
    form_class = DreamForm
    model = Dream

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Create Dream")
        context["subtitle"] = _("What did you dream?")
        context["scripts"] = [static("frontend/js/dropdown-to-buttons.js")]
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user

        ret = super().form_valid(form)

        for theme in form.cleaned_data["themes"]:
            if theme.user == self.request.user:
                DreamTheme.objects.create(theme=theme, dream=form.instance)

        for attachment in form.cleaned_data["uploads"]:
            dba = DreamMedia(dream=form.instance)
            dba.media.save(get_upload_path(form.instance, attachment.name), attachment)
            dba.save()

        return ret

    def get_success_url(self):
        return reverse_lazy("dreams:dream_view", kwargs={"id": self.object.id})


class DreamEditView(LoginRequiredMixin, UpdateView):
    template_name = "dreams/dream_edit.html"
    form_class = DreamForm
    model = Dream

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Update Dream")
        context["subtitle"] = _("Change details of a dream you entered before.")
        context["scripts"] = [static("frontend/js/dropdown-to-buttons.js")]
        context["buttons"] = [
            (
                reverse_lazy("dreams:dream_delete", kwargs={"id": self.kwargs["id"]}),
                _("Delete Dream"),
                "trash",
            )
        ]
        return context

    def get_object(self):
        return get_object_or_404(Dream, user=self.request.user, id=self.kwargs["id"])

    def form_valid(self, form):
        for theme in form.cleaned_data["themes"]:
            if theme.user == self.request.user:
                if theme not in form.instance.theme_set:
                    DreamTheme.objects.create(theme=theme, dream=form.instance)

        for dreamtheme in form.instance.dreamtheme_set.all():
            if dreamtheme.theme not in form.cleaned_data["themes"]:
                dreamtheme.delete()

        for attachment in form.cleaned_data["uploads"]:
            dba = DreamMedia(dream=form.instance)
            dba.media.save(get_upload_path(form.instance, attachment.name), attachment)
            dba.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("dreams:dream_view", kwargs={"id": self.object.id})


class DreamDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "dreams/dream_delete.html"
    model = Dream

    def get_object(self):
        return get_object_or_404(Dream, user=self.request.user, id=self.kwargs["id"])

    def get_success_url(self):
        return reverse_lazy("dreams:dream_list")


class ThemeListView(LoginRequiredMixin, ListView):
    template_name = "dreams/theme_list.html"
    model = Theme

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Themes")
        context["subtitle"] = _("The themes you have defined for your dreams.")
        context["buttons"] = [
            (reverse_lazy("dreams:theme_create"), _("Create Theme"), "pencil-simple")
        ]
        return context

    def get_queryset(self):
        return Theme.objects.filter(user=self.request.user)


class ThemeEditView(LoginRequiredMixin, UpdateView):
    template_name = "dreams/theme_edit.html"
    model = Theme
    fields = ["name", "icon", "color"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Edit Theme")
        context["subtitle"] = _("Make changes to the theme.")
        context["scripts"] = [
            static("colorfield/jscolor/jscolor.js"),
            static("colorfield/colorfield.js"),
        ]
        context["buttons"] = [
            (
                reverse_lazy("dreams:theme_delete", kwargs={"id": self.kwargs["id"]}),
                _("Delete Theme"),
                "trash",
            )
        ]
        return context

    def get_object(self):
        return get_object_or_404(Theme, user=self.request.user, id=self.kwargs["id"])

    def get_success_url(self):
        return reverse_lazy("dreams:theme_list")


class ThemeCreateView(LoginRequiredMixin, CreateView):
    template_name = "dreams/theme_edit.html"
    model = Theme
    fields = ["name", "icon", "color"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Create Theme")
        context["subtitle"] = _("Add a new theme for your dreams.")
        context["scripts"] = [
            static("colorfield/jscolor/jscolor.js"),
            static("colorfield/colorfield.js"),
        ]
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("dreams:theme_list")


class ThemeDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "dreams/theme_delete.html"
    model = Theme

    def get_object(self):
        return get_object_or_404(Theme, user=self.request.user, id=self.kwargs["id"])

    def get_success_url(self):
        return reverse_lazy("dreams:theme_list")


