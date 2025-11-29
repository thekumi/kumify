from django.forms import ModelForm, ModelMultipleChoiceField

from multiupload.fields import MultiFileField

from .models import Dream, Theme


class DreamForm(ModelForm):
    uploads = MultiFileField(required=False)
    themes = ModelMultipleChoiceField(
        queryset=Theme.objects.none(),
        required=False,
    )

    class Meta:
        model = Dream
        fields = ["timestamp", "mood", "title", "content", "type", "wet", "lucid"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["mood"].required = False

        if user is not None:
            self.fields["themes"].queryset = Theme.objects.filter(user=user)
        else:
            self.fields["themes"].queryset = Theme.objects.none()
