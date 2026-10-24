from django.contrib.auth import get_user_model
from django.db import models


class DeletionLog(models.Model):
    class Meta:
        ordering = ["-deleted_at"]
        indexes = [models.Index(fields=["user", "deleted_at"])]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    resource_type = models.CharField(max_length=64)
    resource_id = models.IntegerField()
    deleted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resource_type}#{self.resource_id} deleted at {self.deleted_at}"


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
