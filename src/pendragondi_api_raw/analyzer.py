"""
Analyze logged API call data.

The analyzer reads raw call logs from the SQLite database and derives
aggregate metrics such as total calls, duplicate groups, cacheable
misses, rate limit warnings and an estimate of potential cost savings.
All interpretation is deliberately minimal: we report what happened
without recommending how to fix it.  Pendragondi API Pro builds upon
these results to offer guidance and automation.
"""

import sqlite3
from collections import Counter, defaultdict
from typing import Any, Dict, List, Tuple

from .constants import DEFAULT_DB_PATH
from .config import load_pricing_config


def analyze_calls() -> Dict[str, Any]:
    """
    Read and summarise API calls from the database.

    Returns:
        dict: Contains analysis results:
            - total_requests (int)
            - total_duplicate_groups (int)
            - total_duplicate_calls (int)
            - cacheable_misses (int)
            - rate_limit_flags (int)
            - estimated_cost_reduction (float)
            - top_5_endpoints_by_waste (list[tuple[str, int]])
    """
    try:
        with sqlite3.connect(DEFAULT_DB_PATH) as conn:
            rows = conn.execute(
                "SELECT service, endpoint, payload_hash, cacheable, status_code FROM api_calls"
            ).fetchall()
    except sqlite3.Error:
        return _empty_stats()

    if not rows:
        return _empty_stats()

    total_requests = len(rows)
    endpoint_counter = Counter()
    duplicate_counter = Counter()  # number of duplicate calls per endpoint
    seen_hashes = defaultdict(list)  # map payload_hash -> list of (endpoint, cacheable, status_code)
    cacheable_misses = 0
    rate_limit_flags = 0

    # Load pricing for cost estimation (optional)
    pricing = load_pricing_config()

    # First pass: populate structures
    for service, endpoint, hsh, cacheable, status in rows:
        endpoint_counter[endpoint] += 1
        seen_hashes[hsh].append((endpoint, cacheable, status, service))

        if status == 429:
            rate_limit_flags += 1

    # Second pass: identify duplicates and cacheable misses
    total_duplicate_groups = 0
    total_duplicate_calls = 0
    estimated_savings = 0.0
    endpoint_waste = Counter()

    for hsh, calls in seen_hashes.items():
        if len(calls) > 1:
            total_duplicate_groups += 1
            # The first call is considered the original; duplicates are the rest
            duplicates = calls[1:]
            total_duplicate_calls += len(duplicates)
            for (endpoint, cacheable, status, service) in duplicates:
                duplicate_counter[endpoint] += 1
                # cost estimation: use pricing per service if available
                cost_entry = pricing.get(service, {}) if isinstance(pricing, dict) else {}
                cost_per_call = 0.0
                if isinstance(cost_entry, dict):
                    # try cost_per_call or fallback to cost_per_request
                    cost_per_call = cost_entry.get("cost_per_call") or cost_entry.get("cost") or 0.0
                estimated_savings += cost_per_call
                endpoint_waste[endpoint] += 1
                if cacheable:
                    cacheable_misses += 1

    # Top 5 endpoints by number of duplicate calls
    top_5_waste = endpoint_waste.most_common(5)

    return {
        "total_requests": total_requests,
        "total_duplicate_groups": total_duplicate_groups,
        "total_duplicate_calls": total_duplicate_calls,
        "cacheable_misses": cacheable_misses,
        "rate_limit_flags": rate_limit_flags,
        "estimated_cost_reduction": round(estimated_savings, 2),
        "top_5_endpoints_by_waste": top_5_waste,
    }


def _empty_stats() -> Dict[str, Any]:
    """Return an empty stats dictionary."""
    return {
        "total_requests": 0,
        "total_duplicate_groups": 0,
        "total_duplicate_calls": 0,
        "cacheable_misses": 0,
        "rate_limit_flags": 0,
        "estimated_cost_reduction": 0.0,
        "top_5_endpoints_by_waste": [],
    }


__all__ = ["analyze_calls"]