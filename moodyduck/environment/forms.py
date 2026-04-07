from django.forms import ModelForm

from moodyduck.frontend.mixins import BootstrapMixin
from .models import CO2Category, CO2Entry, CO2Offset


class CO2CategoryForm(BootstrapMixin, ModelForm):
    class Meta:
        model = CO2Category
        fields = ["name", "icon"]


class CO2EntryForm(BootstrapMixin, ModelForm):
    class Meta:
        model = CO2Entry
        fields = ["date", "category", "description", "amount_kg", "notes"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["category"].queryset = CO2Category.objects.filter(user=user)
        else:
            self.fields["category"].queryset = CO2Category.objects.none()


class CO2OffsetForm(BootstrapMixin, ModelForm):
    class Meta:
        model = CO2Offset
        fields = ["date", "description", "amount_kg", "provider", "notes"]
