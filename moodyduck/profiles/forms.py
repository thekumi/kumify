from django import forms

from moodyduck.frontend.mixins import BootstrapMixin
from moodyduck.health.models import BasicMedicalInfo
from .models import UserProfile


class UserProfileForm(BootstrapMixin, forms.ModelForm):
    blood_type = forms.CharField(required=False, max_length=8)
    allergies = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
    medical_notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 4}))

    class Meta:
        model = UserProfile
        fields = [
            "display_name",
            "timezone",
            "legal_name",
            "phone",
            "address",
            "date_of_birth",
            "pgp_key",
        ]
        widgets = {
            "pgp_key": forms.Textarea(attrs={"rows": 6, "cols": 40}),
            "timezone": forms.TextInput(attrs={"placeholder": "e.g., Europe/Vienna"}),
            "address": forms.Textarea(attrs={"rows": 3}),
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            self.fields[name].required = False

        if self.instance and self.instance.pk:
            medical_info, _ = BasicMedicalInfo.objects.get_or_create(user=self.instance.user)
            self.fields["blood_type"].initial = medical_info.blood_type
            self.fields["allergies"].initial = medical_info.allergies
            self.fields["medical_notes"].initial = medical_info.medical_notes

    def save(self, commit=True):
        profile = super().save(commit=commit)
        medical_info, _ = BasicMedicalInfo.objects.get_or_create(user=profile.user)
        medical_info.blood_type = self.cleaned_data.get("blood_type")
        medical_info.allergies = self.cleaned_data.get("allergies")
        medical_info.medical_notes = self.cleaned_data.get("medical_notes")
        medical_info.save()
        return profile
