from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


class Medication(models.Model):
    class Meta:
        ordering = ["pk"]

    user = models.ForeignKey(get_user_model(), models.CASCADE)
    encrypted_payload = models.JSONField(null=True, blank=True)

    def __str__(self):
        return str(self.pk)


class HealthParameter(models.Model):
    class Meta:
        ordering = ["name"]

    user = models.ForeignKey(get_user_model(), models.CASCADE)
    name = models.CharField(max_length=128, null=True, blank=True)
    icon = models.CharField(max_length=64, default="ph ph-heart", null=True, blank=True)
    unit = models.CharField(max_length=12, null=True, blank=True)
    encrypted_payload = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name or str(self.pk)


class BasicMedicalInfo(models.Model):
    user = models.OneToOneField(get_user_model(), models.CASCADE)
    blood_type = models.CharField(max_length=8, blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    medical_notes = models.TextField(blank=True, null=True)
    encrypted_payload = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Basic medical info for {self.user}"


class HealthLog(models.Model):
    """A single health check-in containing values for multiple parameters."""

    class Meta:
        ordering = ["-recorded_at"]

    user = models.ForeignKey(get_user_model(), models.CASCADE)
    recorded_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(null=True, blank=True)
    encrypted_payload = models.JSONField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Health log — {self.recorded_at:%Y-%m-%d %H:%M}"


class HealthRecord(models.Model):
    """A single parameter value within a HealthLog check-in."""

    log = models.ForeignKey(HealthLog, models.CASCADE, related_name="records")
    parameter = models.ForeignKey(HealthParameter, models.CASCADE)
    value = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    encrypted_payload = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.parameter.name}: {self.value}"


class Vaccination(models.Model):
    class Meta:
        ordering = ["-pk"]

    user = models.ForeignKey(get_user_model(), models.CASCADE)
    name = models.CharField(max_length=128, null=True, blank=True)
    target_disease = models.CharField(max_length=128, null=True, blank=True)
    administered_on = models.DateField(null=True, blank=True)
    provider = models.CharField(max_length=128, null=True, blank=True)
    batch_number = models.CharField(max_length=64, null=True, blank=True)
    next_due = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    encrypted_payload = models.JSONField(null=True, blank=True)

    def __str__(self):
        if self.administered_on:
            return f"{self.name} on {self.administered_on:%Y-%m-%d}"
        return self.name or str(self.pk)
