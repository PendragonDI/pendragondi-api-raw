"""
Decorators for logging asynchronous API calls.

Use ``@log_api_call_async`` on your async functions to record metadata
about each invocation in the same way as the synchronous decorator.
"""

import time
import functools
from typing import Callable, Optional, List, Any, Awaitable

from .logger import log_api_call
from .utils import (
    get_default_mask_keys,
    scrub_payload,
    hash_request,
)


def log_api_call_async(
    proxy: bool = False,
    mask_keys: Optional[List[str]] = None,
    method: Optional[str] = None,
    path: Optional[str] = None,
) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
    """
    Decorate an asynchronous function to log API call metadata.

    Args:
        proxy: Reserved for future proxy mode (currently unused).
        mask_keys: Additional payload keys to redact on top of the defaults.
        method: Override detection of the HTTP method.
        path: Override detection of the endpoint/path.

    Returns:
        A decorator which wraps the target async function.
    """

    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            used_mask_keys = get_default_mask_keys()
            if mask_keys:
                used_mask_keys = list({*used_mask_keys, *mask_keys})
            try:
                response = await func(*args, **kwargs)
                duration = time.time() - start_time

                extracted_method = method or getattr(getattr(response, "request", None), "method", None)
                extracted_path = path or getattr(response, "url", None)

                used_method = (extracted_method or "UNKNOWN").upper()
                used_path = extracted_path or func.__module__

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
            except Exception:
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


__all__ = ["log_api_call_async"]