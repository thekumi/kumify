from django.db import models
from django.contrib.auth import get_user_model

from annoying.fields import AutoOneToOneField


class UserProfile(models.Model):
    user = AutoOneToOneField(get_user_model(), on_delete=models.CASCADE)
    pgp_key = models.TextField(blank=True)

    display_name = models.CharField(max_length=128, blank=True, null=True)
    timezone = models.CharField(max_length=64, blank=True, null=True)
    legal_name = models.CharField(max_length=128, blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.display_name or self.user.username


class EmergencyAccessLog(models.Model):
    class Meta:
        ordering = ["-accessed_at"]

    user = models.ForeignKey(get_user_model(), models.CASCADE)
    accessed_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=32, default="android")
    method = models.CharField(max_length=32, default="emergency_screen")
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Emergency access for {self.user} at {self.accessed_at:%Y-%m-%d %H:%M}"
