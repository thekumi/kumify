from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from moodyduck.frontend.mixins import BootstrapMixin
from .models import ThoughtRecord


class ThoughtRecordForm(BootstrapMixin, ModelForm):
    class Meta:
        model = ThoughtRecord
        fields = [
            "title",
            "situation",
            "thoughts",
            "pro_facts",
            "con_facts",
            "realistic",
            "outcome",
        ]
        labels = {
            "pro_facts": _("Supporting Evidence"),
            "con_facts": _("Contradicting Evidence"),
            "realistic": _("Balanced Thought"),
        }
