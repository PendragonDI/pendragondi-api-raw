"""
Utility helpers for Pendragondi API Raw.

This module provides functions for safely redacting sensitive information
from request payloads, normalising data for deterministic hashing and
formatting timestamps.  It is deliberately small and free of external
dependencies.
"""

import json
import hashlib
from typing import Any, Dict, List, Set

from .constants import MASK_FIELDS


def get_default_mask_keys() -> List[str]:
    """Return a list of default keys that should be redacted from payloads."""
    return list(MASK_FIELDS)


def scrub_payload(data: Any, mask_keys: List[str]) -> Any:
    """
    Recursively remove sensitive values from a payload.

    This function will walk nested dictionaries and lists and replace the
    value of any key present in ``mask_keys`` (case–insensitive) with the
    literal string ``"<redacted>"``.  Non–container types are returned
    unchanged.

    Args:
        data: Arbitrary JSON–serialisable data structure (dict/list/scalars).
        mask_keys: List of keys (case–insensitive) to redact.

    Returns:
        A copy of the original data with sensitive values replaced.
    """
    mask_set: Set[str] = {k.lower() for k in mask_keys}
    if isinstance(data, dict):
        return {
            key: (
                "<redacted>" if key.lower() in mask_set else scrub_payload(value, mask_keys)
            )
            for key, value in data.items()
        }
    if isinstance(data, list):
        return [scrub_payload(item, mask_keys) for item in data]
    # Primitive types are returned as–is
    return data


def normalize_json(data: Any) -> str:
    """
    Canonicalise JSON data for hashing.

    Converts a Python object into a JSON string with sorted keys and no
    extraneous whitespace.  If serialization fails (e.g. object is not
    JSON–serialisable), returns the string "<unserializable>" instead.

    Args:
        data: A JSON–serialisable Python object.

    Returns:
        A stable JSON string representation.
    """
    try:
        return json.dumps(data, sort_keys=True, separators=(",", ":"))
    except Exception:
        return "<unserializable>"


def hash_request(method: str, path: str, payload: Any) -> str:
    """
    Compute a SHA‑256 hash of an API request.

    The hash incorporates the HTTP method, endpoint/path and the
    canonicalised payload.  This ensures that semantically identical
    requests produce the same fingerprint regardless of whitespace or
    key ordering.  Sensitive fields should be scrubbed from the payload
    before calling this function.

    Args:
        method: HTTP method (e.g. 'GET', 'POST').
        path: Endpoint path or URL.
        payload: JSON–serialisable body or parameters of the request.

    Returns:
        A 64‑character hexadecimal SHA‑256 hash string.
    """
    canonical_payload = normalize_json(payload)
    signature = f"{method.upper()}:{path}:{canonical_payload}"
    return hashlib.sha256(signature.encode()).hexdigest()


def iso_timestamp(ts: float) -> str:
    """
    Convert a Unix timestamp to an ISO 8601 string in UTC.

    Args:
        ts: Unix timestamp (seconds since epoch).

    Returns:
        An ISO 8601 formatted timestamp ending with 'Z'.
    """
    import datetime

    return datetime.datetime.utcfromtimestamp(ts).isoformat() + "Z"


__all__ = [
    "get_default_mask_keys",
    "scrub_payload",
    "normalize_json",
    "hash_request",
    "iso_timestamp",
]