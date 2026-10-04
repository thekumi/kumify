import base64

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Generate VAPID key pair for Web Push notifications"

    def handle(self, *args, **options):
        private_key = ec.generate_private_key(ec.SECP256R1())

        private_pem = private_key.private_bytes(
            Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption()
        ).decode()

        public_bytes = private_key.public_key().public_bytes(
            Encoding.X962, PublicFormat.UncompressedPoint
        )
        public_b64 = base64.urlsafe_b64encode(public_bytes).rstrip(b"=").decode()

        self.stdout.write(self.style.SUCCESS("Add to settings.ini:"))
        self.stdout.write("")
        self.stdout.write("[Push]")
        self.stdout.write("Subject = mailto:you@example.com")
        self.stdout.write(f"PublicKey = {public_b64}")
        self.stdout.write("PrivateKey =")
        for line in private_pem.strip().splitlines():
            self.stdout.write(f"    {line}")
