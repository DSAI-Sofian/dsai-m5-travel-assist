from typing import Any, Mapping


def interpret_trip_intent(req):
    """
    Thin intent wrapper for planner inputs.

    This preserves current behavior by passing through the request as-is,
    while making intent interpretation a separate module for future expansion.
    """
    return dict(req)

