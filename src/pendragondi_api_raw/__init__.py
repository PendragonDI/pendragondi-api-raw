"""
Pendragondi API Raw
-------------------

This package exposes the primary decorators used to instrument your Python
functions for API call logging.  Import ``log_api_call`` for synchronous
functions and ``log_api_call_async`` for asynchronous functions.  Both
decorators will record metadata about each invocation into a local SQLite
database so that later analysis can surface redundant calls, cache
misses and other wasteful patterns.

Example::

    from pendragondi_api_raw import log_api_call
    import requests

    @log_api_call(service="openai", cacheable=True)
    def call_openai():
        return requests.post("https://api.openai.com/v1/chat/completions",
                             json={"prompt": "Hello"})

    # run your code normally
    call_openai()

The decorators are intentionally minimal – they collect facts without
attempting to interpret them.  For higher level guidance and automatic
optimisations, see the companion ``pendragondi-api-pro`` package.
"""

from .decorator import log_api_call_decorator as log_api_call
from .decorator_async import log_api_call_async

__all__ = [
    "log_api_call",
    "log_api_call_async",
]