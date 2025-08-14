"""
Constant definitions for Pendragondi API Raw.

This module centralises configuration defaults and environment variable
handling.  All paths, sampling rates and masking rules live here so that
other parts of the system can reference them without duplicating logic.

Environment variables (optional):

``PENDRAGONDI_DB_PATH``
    Override the location of the SQLite database used to log API calls.

``PENDRAGONDI_SAMPLE_RATE``
    A float between 0 and 1.0 indicating the fraction of calls to record.
    Useful in high‐throughput systems where logging every call would be
    prohibitive.  Defaults to 1.0 (log everything).

``PENDRAGONDI_MASK_FIELDS``
    Comma–separated list of payload keys to redact before hashing or
    storage.  Entries are case–insensitive.  The defaults include a
    variety of common API keys, tokens and personal data fields.
"""

import os
from pathlib import Path
from typing import Set

def _float_env(name: str, default: float) -> float:
    """Parse a floating point environment variable with fallback."""
    val = os.getenv(name, str(default))
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _mask_set(raw: str) -> Set[str]:
    """Split a comma–separated string into a set of lower‑case tokens."""
    parts = [p.strip() for p in raw.split(",")]
    return {p.lower() for p in parts if p}


# --- Default masking keys ----------------------------------------------------

# These keys are redacted from payloads by default.  You can add more keys
# via the ``PENDRAGONDI_MASK_FIELDS`` environment variable.  All matches
# are case–insensitive.
DEFAULT_MASK_FIELDS: Set[str] = {
    "authorization", "api_key", "token", "email", "ssn", "password",
    "access_token", "secret", "session", "cookie", "set-cookie",
    "refresh_token", "id_token", "card_number", "cvv", "account_number",
    "iban", "swift", "phone", "address", "user", "username", "user_id",
}

# Merge user–supplied mask keys from environment
ENV_MASK_FIELDS = _mask_set(os.getenv("PENDRAGONDI_MASK_FIELDS", ""))

# Final mask set used by utils.scrub_payload
MASK_FIELDS = DEFAULT_MASK_FIELDS | ENV_MASK_FIELDS


# --- Database and sampling configuration ------------------------------------

# Path to the SQLite database.  Defaults to a hidden file in the user's
# home directory.  You can override this path with the environment variable
# ``PENDRAGONDI_DB_PATH``.  Relative paths are resolved relative to the
# current working directory.
DEFAULT_DB_PATH: Path = Path(
    os.getenv("PENDRAGONDI_DB_PATH", Path.home() / ".pendragondi_api_log.db")
)

# Fraction of calls to record.  1.0 means log everything.  Setting this
# lower can reduce overhead in high throughput environments.  Values
# outside the range [0.0, 1.0] are coerced.
DEFAULT_SAMPLE_RATE: float = max(0.0, min(1.0, _float_env("PENDRAGONDI_SAMPLE_RATE", 1.0)))


__all__ = [
    "MASK_FIELDS",
    "DEFAULT_DB_PATH",
    "DEFAULT_SAMPLE_RATE",
]