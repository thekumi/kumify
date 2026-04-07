from django.forms import (
    ModelForm,
    ModelMultipleChoiceField,
    BooleanField,
)

from multiupload.fields import MultiFileField

from moodyduck.frontend.mixins import BootstrapMixin
from .models import Status, Activity


class StatusForm(BootstrapMixin, ModelForm):
    uploads = MultiFileField(required=False)
    activities = ModelMultipleChoiceField(
        queryset=Activity.objects.none(),
        required=False,
    )
    encrypt = BooleanField(required=False)

    class Meta:
        model = Status
        fields = ["timestamp", "mood", "title", "text"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["mood"].required = False

        if user is not None:
            self.fields["activities"].queryset = Activity.objects.filter(user=user)
        else:
            self.fields["activities"].queryset = Activity.objects.none()
