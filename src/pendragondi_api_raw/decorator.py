"""
Decorators for logging synchronous API calls.

Use ``@log_api_call`` on your HTTP wrapper functions to record metadata
about each invocation.  The decorator is designed to be as non‑intrusive
as possible: it measures duration, captures HTTP method and endpoint if
available, scrubs sensitive fields and computes a deterministic hash of
the request signature.  In the event of an exception, the call is still
recorded (with a status code of 0) before the exception is re‑raised.

The ``proxy`` parameter is reserved for future use and currently has no
effect.  The ``mask_keys``, ``method`` and ``path`` parameters allow you
to override detection behaviour on a per‑call basis.
"""

import time
import functools
from typing import Callable, Optional, List, Any

from .logger import log_api_call
from .utils import (
    get_default_mask_keys,
    scrub_payload,
    hash_request,
)


def log_api_call_decorator(
    proxy: bool = False,
    mask_keys: Optional[List[str]] = None,
    method: Optional[str] = None,
    path: Optional[str] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorate a synchronous function to log API call metadata.

    Args:
        proxy: Reserved for future proxy mode (currently unused).
        mask_keys: Additional payload keys to redact on top of the defaults.
        method: Override detection of the HTTP method.
        path: Override detection of the endpoint/path.

    Returns:
        A decorator which wraps the target function.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            used_mask_keys = get_default_mask_keys()
            if mask_keys:
                # Merge default masks with call‑specific ones, de‑duplicate
                used_mask_keys = list({*used_mask_keys, *mask_keys})

            try:
                response = func(*args, **kwargs)
                duration = time.time() - start_time
                # Try to extract method and endpoint from the response, if present
                extracted_method = method or getattr(getattr(response, "request", None), "method", None)
                extracted_path = path or getattr(response, "url", None)

                # Fallback values
                used_method = (extracted_method or "UNKNOWN").upper()
                used_path = extracted_path or func.__module__

                # Compose payload from kwargs only (args are opaque)
                payload = scrub_payload(kwargs.copy(), used_mask_keys)
                payload_hash = hash_request(used_method, used_path, payload)

                log_api_call(
                    {
                        "timestamp": start_time,
                        "service": kwargs.get("service") or "unknown",
                        "endpoint": used_path,
                        "duration": duration,
                        "cacheable": kwargs.get("cacheable", False),
                        "payload_hash": payload_hash,
                        "status_code": getattr(response, "status_code", 0),
                        "method": used_method,
                    }
                )

                return response
            except Exception as exc:
                # On failure still record the attempt
                duration = time.time() - start_time
                used_method = (method or "UNKNOWN").upper()
                used_path = path or func.__module__
                log_api_call(
                    {
                        "timestamp": start_time,
                        "service": kwargs.get("service") or "unknown",
                        "endpoint": used_path,
                        "duration": duration,
                        "cacheable": kwargs.get("cacheable", False),
                        "payload_hash": "error",
                        "status_code": 0,
                        "method": used_method,
                    }
                )
                raise
        return wrapper

    return decorator


__all__ = ["log_api_call_decorator"]