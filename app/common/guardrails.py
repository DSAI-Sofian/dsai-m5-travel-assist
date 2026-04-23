from typing import Any, Callable


def execute_with_retry(
    handler: Callable[..., Any],
    *args: Any,
    max_retries: int = 2,
    **kwargs: Any,
) -> Any:
    """
    Execute a handler with simple retry logic.

    - Retries up to max_retries (default: 2)
    - Raises final exception if all attempts fail
    """
    last_error: Exception | None = None

    for _ in range(max_retries + 1):
        try:
            return handler(*args, **kwargs)
        except Exception as exc:
            last_error = exc

    if last_error:
        raise last_error