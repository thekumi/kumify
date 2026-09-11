import base64
import json
import os

from cryptography.hazmat.primitives.asymmetric.ec import (
    ECDH,
    SECP256R1,
    generate_private_key,
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    load_der_public_key,
)


def encrypt_for_user(public_key_spki_b64: str, fields: dict) -> dict:
    """ECIES-encrypt a fields dict for the user's ECDH P-256 public key.

    Returns a dict for storing directly in a JSONField:
      {"v": 2, "epk": <spki-b64>, "iv": <b64>, "wrapped": <b64>}

    The "wrapped" ciphertext decrypts — using the user's private key and the
    ephemeral public key via ECDH + AES-256-GCM — to a JSON-encoded fields dict.

    The AES key is the raw ECDH shared secret (X coordinate, 32 bytes for P-256),
    matching Web Crypto's ECDH deriveKey behaviour so the browser can decrypt
    without any additional KDF.
    """
    spki_bytes = base64.b64decode(public_key_spki_b64)
    user_public_key = load_der_public_key(spki_bytes)

    ephemeral_private = generate_private_key(SECP256R1())
    ephemeral_public = ephemeral_private.public_key()

    shared_secret = ephemeral_private.exchange(ECDH(), user_public_key)

    iv = os.urandom(12)
    ciphertext = AESGCM(shared_secret).encrypt(iv, json.dumps(fields).encode(), None)

    epk_bytes = ephemeral_public.public_bytes(
        Encoding.DER, PublicFormat.SubjectPublicKeyInfo
    )

    return {
        "v": 2,
        "epk": base64.b64encode(epk_bytes).decode(),
        "iv": base64.b64encode(iv).decode(),
        "wrapped": base64.b64encode(ciphertext).decode(),
    }
