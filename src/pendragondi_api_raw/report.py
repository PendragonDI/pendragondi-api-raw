"""
Report rendering for Pendragondi API Raw.

Provides functions to convert analysis results into user–friendly
representations.  The raw analyzer returns a dictionary of summary
statistics; these helpers produce Markdown or JSON outputs suitable for
reports, dashboards or further processing.
"""

import json
from typing import Dict, Any, List, Tuple


def render_markdown_report(stats: Dict[str, Any]) -> str:
    """
    Render a Markdown report from analysis statistics.

    Args:
        stats: Dictionary returned from ``analyze_calls()``.

    Returns:
        A Markdown string containing a human–readable summary of the
        statistics.
    """
    lines: List[str] = []
    lines.append("# Pendragondi API — Optimization Report")
    lines.append("")
    lines.append(f"Total API Calls: {stats['total_requests']}")
    lines.append(f"Duplicate Call Groups: {stats['total_duplicate_groups']}")
    lines.append(f"Duplicate Calls: {stats['total_duplicate_calls']}")
    lines.append(f"Cacheable Misses: {stats['cacheable_misses']}")
    lines.append(f"Rate Limit Warnings: {stats['rate_limit_flags']}")
    lines.append(f"Estimated Savings: ${stats['estimated_cost_reduction']}")
    lines.append("\n---\n")
    lines.append("## Top Endpoints by Waste")
    lines.append("")
    lines.append("| Endpoint | Duplicate Calls |")
    lines.append("|---------|-----------------|")
    for endpoint, count in stats.get("top_5_endpoints_by_waste", []):
        lines.append(f"| {endpoint} | {count} |")
    return "\n".join(lines)


def render_json_report(stats: Dict[str, Any]) -> str:
    """
    Render a JSON report from analysis statistics.

    Args:
        stats: Dictionary returned from ``analyze_calls()``.

    Returns:
        A JSON string encoding the statistics.
    """
    return json.dumps(stats, indent=2)


__all__ = ["render_markdown_report", "render_json_report"]