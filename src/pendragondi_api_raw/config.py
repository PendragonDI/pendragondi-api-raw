"""
Configuration loading utilities.

Pendragondi API Raw stores optional configuration files in the top‑level
``config/`` directory.  Currently, only a pricing file is supported
(``pricing.yaml``).  Higher level packages may extend this mechanism to
load additional user configuration.
"""

import yaml
from pathlib import Path
from typing import Dict, Any

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"
PRICING_PATH = CONFIG_DIR / "pricing.yaml"

def load_pricing_config() -> Dict[str, Any]:
    """
    Load the YAML pricing configuration.

    Returns a dictionary mapping service names to pricing metadata.  If
    the file does not exist or fails to parse, an empty dictionary is
    returned.  See the repository's ``config/pricing.yaml`` for an
    example schema.
    """
    if PRICING_PATH.exists():
        try:
            with open(PRICING_PATH, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}
    return {}


__all__ = ["load_pricing_config"]