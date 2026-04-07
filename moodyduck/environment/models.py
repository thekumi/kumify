from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CO2Category(models.Model):
    class Meta:
        ordering = ["name"]
        verbose_name = _("CO2 Category")
        verbose_name_plural = _("CO2 Categories")

    user = models.ForeignKey(get_user_model(), models.CASCADE)
    name = models.CharField(max_length=64)
    icon = models.CharField(max_length=64, default="ph ph-cloud-fog")

    def __str__(self):
        return self.name


class CO2Entry(models.Model):
    class Meta:
        ordering = ["-date"]
        verbose_name = _("CO2 Entry")
        verbose_name_plural = _("CO2 Entries")

    user = models.ForeignKey(get_user_model(), models.CASCADE)
    date = models.DateField(default=timezone.now)
    category = models.ForeignKey(CO2Category, models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=256)
    amount_kg = models.DecimalField(
        max_digits=10, decimal_places=3, help_text=_("CO2 equivalent in kg")
    )
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.date}: {self.description} ({self.amount_kg} kg CO2e)"


class CO2Offset(models.Model):
    class Meta:
        ordering = ["-date"]
        verbose_name = _("CO2 Offset")
        verbose_name_plural = _("CO2 Offsets")

    user = models.ForeignKey(get_user_model(), models.CASCADE)
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=256)
    amount_kg = models.DecimalField(
        max_digits=10, decimal_places=3, help_text=_("CO2 offset in kg")
    )
    provider = models.CharField(max_length=128, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.date}: {self.description} ({self.amount_kg} kg CO2e offset)"
