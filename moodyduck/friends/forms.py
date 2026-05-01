from django.forms import ModelForm

from moodyduck.frontend.mixins import BootstrapMixin
from .models import Person


class PersonForm(BootstrapMixin, ModelForm):
    class Meta:
        model = Person
        fields = [
            "name",
            "nickname",
            "birthday",
            "email",
            "phone",
            "relationship",
            "emergency_contact",
            "address",
            "notes",
            "last_contact",
        ]
