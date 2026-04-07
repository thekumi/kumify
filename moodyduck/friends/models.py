from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date


class Person(models.Model):
    class Meta:
        ordering = ["name"]

    user = models.ForeignKey(get_user_model(), models.CASCADE)
    name = models.CharField(max_length=128)
    nickname = models.CharField(max_length=64, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=32, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    last_contact = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    @property
    def display_name(self):
        if self.nickname:
            return f"{self.name} ({self.nickname})"
        return self.name

    @property
    def days_since_contact(self):
        if self.last_contact:
            return (date.today() - self.last_contact).days
        return None

    @property
    def days_until_birthday(self):
        if not self.birthday:
            return None
        today = date.today()
        next_bday = self.birthday.replace(year=today.year)
        if next_bday < today:
            next_bday = self.birthday.replace(year=today.year + 1)
        return (next_bday - today).days
