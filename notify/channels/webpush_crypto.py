# Copyright (c) 2026 Zhambyl Yermagambet
"""Expose the optional cryptography dependency as one import boundary."""

from cryptography.hazmat.primitives import hashes as hashes
from cryptography.hazmat.primitives.asymmetric import ec as ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature as decode_dss_signature
from cryptography.hazmat.primitives.ciphers.aead import AESGCM as AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF as HKDF
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
    load_pem_private_key,
)


def load_private_key(private_key_pem: bytes) -> ec.EllipticCurvePrivateKey:
    """Load and validate one elliptic-curve private key.

    Returns:
        The elliptic-curve private key stored in the PEM document.

    Raises:
        TypeError: If the document contains another private key type.

    """
    private_key = load_pem_private_key(private_key_pem, password=None)
    if not isinstance(private_key, ec.EllipticCurvePrivateKey):
        message = "stored key is not an EC private key"
        raise TypeError(message)
    return private_key


def create_keypair_material() -> tuple[ec.EllipticCurvePrivateKey, bytes, bytes]:
    """Create one key and its public point and private PEM bytes.

    Returns:
        The private key, encoded public point, and private PEM document.

    """
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_point = private_key.public_key().public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
    private_pem = private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
    return private_key, public_point, private_pem


def create_exchange(browser_public: bytes) -> tuple[bytes, bytes]:
    """Create one temporary public key and shared secret.

    Returns:
        The encoded server public point and the shared secret.

    """
    browser_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), browser_public)
    server_private = ec.generate_private_key(ec.SECP256R1())
    server_public = server_private.public_key().public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
    return server_public, server_private.exchange(ec.ECDH(), browser_key)
