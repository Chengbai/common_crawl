# 2025. Common Crawl utils.

import time
import random

from functools import wraps
from pydantic import validate_call, Field
from typing import Annotated


def retry_with_exponential_backoff(
    max_retries: Annotated[int, Field(default=5, ge=1, description="max retries")],
    initial_delay: Annotated[
        float, Field(default=1, ge=1, description="initila delay in seconds")
    ],
    max_delay: Annotated[
        float, Field(default=60, ge=1, description="max delay in seconds")
    ],
    backoff_factor: Annotated[
        float, Field(default=2, ge=1, description="backoff factor")
    ],
):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries:
                        print(
                            f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f} seconds..."
                        )
                        time.sleep(delay)
                        delay = min(
                            delay * backoff_factor + random.uniform(0, 0.5 * delay),
                            max_delay,
                        )  # Add jitter
                    else:
                        raise Exception(
                            f"Function {func.__name__} failed after {max_retries} attempts."
                        ) from e

        return wrapper

    return decorator
