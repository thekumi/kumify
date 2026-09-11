import uuid

from django.contrib.auth import get_user_model
from django.db import models


class UserDevice(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    device_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    label = models.CharField(max_length=255, blank=True)
    # SPKI base64-encoded ECDH P-256 public key
    public_key = models.TextField()
    # Data key wrapped with this device's public key; null until distributed
    encrypted_data_key = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        label = self.label or str(self.device_id)
        return f"{self.user} — {label}"


class UserKeyPair(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    # Stored plaintext — the server uses this to ECIES-encrypt incoming data for this user
    public_key = models.TextField()
    # PKCS8 private key wrapped with the user's AES data key (AES-GCM): {iv, wrapped}
    encrypted_private_key = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"User key pair for {self.user}"


class UserKeyBackup(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    # Data key wrapped with a PBKDF2-derived key from the user's recovery passphrase
    encrypted_data_key = models.TextField()
    # Base64 PBKDF2 salt — stored so the client can re-derive the same wrapping key
    kdf_salt = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Key backup for {self.user}"
