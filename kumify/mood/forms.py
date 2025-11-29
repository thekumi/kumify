from django.forms import (
    ModelForm,
    ModelMultipleChoiceField,
    BooleanField,
    Form,
    CharField,
    Textarea,
)

from multiupload.fields import MultiFileField

from .models import Status, Activity


class StatusForm(ModelForm):
    uploads = MultiFileField(required=False)
    activities = ModelMultipleChoiceField(
        queryset=Activity.objects.none(),  # start with empty; fill in __init__
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


class EncryptorForm(Form):
    key = CharField(label="GPG Key", max_length=8192, required=True, widget=Textarea())
