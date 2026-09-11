from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, UpdateView

from moodyduck.health.models import BasicMedicalInfo

from .forms import UserProfileForm
from .models import EmergencyAccessLog, UserProfile


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = "profiles/profile_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, _profile_created = UserProfile.objects.get_or_create(
            user=self.request.user
        )
        medical_info, _medical_created = BasicMedicalInfo.objects.get_or_create(
            user=self.request.user
        )
        context["profile"] = profile
        context["medical_info"] = medical_info
        context["recent_emergency_access_logs"] = EmergencyAccessLog.objects.filter(
            user=self.request.user
        )[:10]
        context["title"] = _("Your Profile")
        context["subtitle"] = _("View your user profile information.")
        return context


class UserProfileEditView(LoginRequiredMixin, UpdateView):
    form_class = UserProfileForm
    template_name = "profiles/profile_edit.html"
    success_url = reverse_lazy("profiles:profile_view")

    def get_object(self):
        profile, _profile_created = UserProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Edit Profile")
        context["subtitle"] = _("Update your profile information.")
        return context
