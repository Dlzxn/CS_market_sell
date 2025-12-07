import time
import asyncio
from collections import deque


def rate_limit_async(max_calls: int = 5, per_seconds: float = 1.0):
    calls = deque()

    def rate_limit_async(func):
        async def _wrapper(*args, **kwargs):
            nonlocal calls
            now = time.time()

            while calls and now - calls[0] > per_seconds:
                calls.popleft()

            if len(calls) >= max_calls:
                sleep_time = per_seconds - (now - calls[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

            calls.append(time.time())
            return await func(*args, **kwargs)

        return _wrapper
    return rate_limit_async