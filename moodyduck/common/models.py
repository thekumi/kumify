from django.contrib.auth import get_user_model
from django.db import models


class ErrorLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    path = models.TextField()
    method = models.CharField(max_length=10)
    user = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="error_logs",
    )
    exception_type = models.CharField(max_length=255)
    exception_value = models.TextField()
    traceback = models.TextField()
    resolved = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.timestamp:%Y-%m-%d %H:%M} {self.exception_type}: {self.exception_value[:80]}"
