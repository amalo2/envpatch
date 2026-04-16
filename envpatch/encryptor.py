"""Encrypt and decrypt .env values using Fernet symmetric encryption."""
from __future__ import annotations

import base64
import os
from dataclasses import dataclass, field
from typing import Dict, List

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:  # pragma: no cover
    Fernet = None  # type: ignore
    InvalidToken = Exception  # type: ignore


@dataclass
class EncryptResult:
    encrypted: Dict[str, str] = field(default_factory=dict)
    skipped: List[str] = field(default_factory=list)

    @property
    def encrypted_count(self) -> int:
        return len(self.encrypted)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)

    def to_summary(self) -> str:
        return f"Encrypted {self.encrypted_count} key(s), skipped {self.skipped_count}."


@dataclass
class DecryptResult:
    decrypted: Dict[str, str] = field(default_factory=dict)
    failed: List[str] = field(default_factory=list)

    @property
    def decrypted_count(self) -> int:
        return len(self.decrypted)

    def to_summary(self) -> str:
        return f"Decrypted {self.decrypted_count} key(s), {len(self.failed)} failed."


def generate_key() -> str:
    """Generate a new Fernet key as a string."""
    if Fernet is None:
        raise RuntimeError("cryptography package is required for encryption.")
    return Fernet.generate_key().decode()


def encrypt_env(env: Dict[str, str], key: str, keys: List[str] | None = None) -> EncryptResult:
    """Encrypt values in env dict. If keys is None, encrypt all."""
    if Fernet is None:
        raise RuntimeError("cryptography package is required for encryption.")
    f = Fernet(key.encode() if isinstance(key, str) else key)
    result = EncryptResult()
    targets = keys if keys is not None else list(env.keys())
    for k, v in env.items():
        if k in targets:
            result.encrypted[k] = f.encrypt(v.encode()).decode()
        else:
            result.skipped.append(k)
    return result


def decrypt_env(env: Dict[str, str], key: str) -> DecryptResult:
    """Attempt to decrypt all values in env dict."""
    if Fernet is None:
        raise RuntimeError("cryptography package is required for encryption.")
    f = Fernet(key.encode() if isinstance(key, str) else key)
    result = DecryptResult()
    for k, v in env.items():
        try:
            result.decrypted[k] = f.decrypt(v.encode()).decode()
        except Exception:
            result.failed.append(k)
    return result
