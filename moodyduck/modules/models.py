from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

ENABLED_FOR_CHOICES = [
    ("disabled", "Disabled"),
    ("staff", "Staff only"),
    ("all", "Everyone"),
]


class Feature(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    enabled_for = models.CharField(
        max_length=20, choices=ENABLED_FOR_CHOICES, default="all"
    )
    shown_by_default = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def is_enabled_for(self, user):
        if self.enabled_for == "disabled":
            return False
        if self.enabled_for == "staff":
            return user.is_staff
        return True


class UserFeaturePreference(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="feature_prefs"
    )
    feature = models.ForeignKey(
        Feature, on_delete=models.CASCADE, related_name="user_prefs"
    )
    visible = models.BooleanField(default=True)

    class Meta:
        unique_together = ("user", "feature")

    def __str__(self):
        return f"{self.user} / {self.feature} / {'shown' if self.visible else 'hidden'}"


class UserNavOrder(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="nav_order"
    )
    order = models.JSONField(default=list)

    def __str__(self):
        return f"{self.user} nav order"
