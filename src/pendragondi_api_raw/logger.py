"""
SQLite logging backend for Pendragondi API Raw.

This module persists API call metadata into a local SQLite database.  It
ensures the required table and indices exist, honours the sampling rate
configuration and retries when the database is temporarily locked.
"""

import sqlite3
import time
import random
import os
from typing import Dict, Any

from .constants import DEFAULT_DB_PATH, DEFAULT_SAMPLE_RATE


DEBUG_MODE = os.getenv("PENDRAGONDI_DEBUG", "0") == "1"


def init_db() -> None:
    """
    Ensure the SQLite DB and table exist, creating indices for performance.
    This function is safe to call multiple times and will not recreate existing tables or indices.
    """
    with sqlite3.connect(DEFAULT_DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS api_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                service TEXT,
                endpoint TEXT,
                duration REAL,
                cacheable BOOLEAN,
                payload_hash TEXT,
                status_code INTEGER,
                method TEXT
            )
        """
        )
        # Add useful indices for query speed in analyzer
        conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON api_calls(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_endpoint ON api_calls(endpoint)")


def log_api_call(entry: Dict[str, Any]) -> None:
    """
    Insert an API call entry into the database with retry-on-lock safety.

    Args:
        entry: Dictionary containing:
            timestamp (float): Unix timestamp of the API call.
            service (str): Service name (e.g., 'openai').
            endpoint (str): Endpoint URL or path.
            duration (float): Duration of the call in seconds.
            cacheable (bool): Whether this call could be cached.
            payload_hash (str): Hash of the request signature.
            status_code (int): HTTP status code.
            method (str): HTTP method (e.g., 'GET', 'POST').

    Notes:
        - Respects DEFAULT_SAMPLE_RATE to allow sampling large volumes.
        - Retries up to 3 times if the SQLite database is locked.
    """
    # Sampling: drop some calls if configured to reduce overhead
    if random.random() > DEFAULT_SAMPLE_RATE:
        return

    init_db()

    max_retries = 3
    for attempt in range(max_retries):
        try:
            with sqlite3.connect(DEFAULT_DB_PATH) as conn:
                conn.execute(
                    """
                    INSERT INTO api_calls (
                        timestamp, service, endpoint, duration, cacheable,
                        payload_hash, status_code, method
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        entry.get("timestamp"),
                        entry.get("service", "unknown"),
                        entry.get("endpoint", "unknown"),
                        entry.get("duration", 0.0),
                        bool(entry.get("cacheable", False)),
                        entry.get("payload_hash", ""),
                        int(entry.get("status_code", 0)),
                        entry.get("method", "UNKNOWN"),
                    ),
                )
            return
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                # Sleep briefly then retry
                time.sleep(random.uniform(0.01, 0.05))
            else:
                if DEBUG_MODE:
                    print(f"[Pendragondi.API] Logging failed: {e}")
                return


__all__ = ["init_db", "log_api_call"]