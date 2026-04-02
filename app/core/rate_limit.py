from collections import defaultdict, deque
from collections.abc import Callable
from threading import Lock
from time import time

from fastapi import HTTPException, Request, status

Buckets = defaultdict[str, deque[float]]
_buckets: Buckets = defaultdict(deque)
_lock = Lock()


def reset_rate_limits() -> None:
    with _lock:
        _buckets.clear()


def rate_limit(*, key_prefix: str, max_requests: int, window_seconds: int) -> Callable:
    def dependency(request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"{key_prefix}:{client_ip}"
        now = time()

        with _lock:
            bucket = _buckets[key]
            while bucket and (now - bucket[0]) > window_seconds:
                bucket.popleft()

            if len(bucket) >= max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Try again shortly.",
                )
            bucket.append(now)

    return dependency
