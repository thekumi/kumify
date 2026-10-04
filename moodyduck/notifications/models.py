from django.contrib.auth import get_user_model
from django.db import models


class PushSubscription(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="push_subscriptions"
    )
    endpoint = models.URLField(max_length=2048)
    p256dh = models.TextField()
    auth = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "endpoint")]

    def __str__(self):
        return f"{self.user} — {self.endpoint[:60]}"


class NotificationSettings(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="notification_settings",
    )
    daily_reminder = models.BooleanField(default=False)
    # Stored as "HH:MM" in the user's local time (best-effort; server uses UTC)
    daily_reminder_time = models.TimeField(default="20:00")
    habits_reminder = models.BooleanField(default=False)
    last_daily_sent = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "notification settings"

    def __str__(self):
        return f"Notification settings for {self.user}"
