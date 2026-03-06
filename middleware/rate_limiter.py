"""
Rate Limiting middleware.
Tracks requests per user/session using in-memory storage.
"""
import time
from collections import defaultdict
from typing import Dict, List

from fastapi import HTTPException, Request, status

from config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW_SECONDS
from utils.logger import logger


class RateLimiter:
    """
    In-memory sliding window rate limiter.
    Tracks request timestamps per user (identified by IP or username).
    """

    def __init__(
        self,
        max_requests: int = RATE_LIMIT_REQUESTS,
        window_seconds: int = RATE_LIMIT_WINDOW_SECONDS,
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # { user_key: [timestamp1, timestamp2, ...] }
        self._requests: Dict[str, List[float]] = defaultdict(list)

    def _clean_old_requests(self, key: str) -> None:
        """Remove expired timestamps outside the current window."""
        cutoff = time.time() - self.window_seconds
        self._requests[key] = [
            ts for ts in self._requests[key] if ts > cutoff
        ]

    def get_identifier(self, request: Request, username: str = None) -> str:
        """Get a unique identifier for the requester."""
        if username:
            return f"user:{username}"
        # Fallback to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"

    def check_rate_limit(self, request: Request, username: str = None) -> dict:
        """
        Check if the user has exceeded the rate limit.
        Returns rate limit info dict.
        Raises 429 if limit exceeded.
        """
        key = self.get_identifier(request, username)
        self._clean_old_requests(key)

        current_count = len(self._requests[key])
        remaining = max(0, self.max_requests - current_count)

        if current_count >= self.max_requests:
            # Calculate reset time
            oldest = min(self._requests[key])
            reset_in = int(oldest + self.window_seconds - time.time()) + 1

            logger.warning(
                f"Rate limit exceeded for {key} "
                f"({current_count}/{self.max_requests} in {self.window_seconds}s)"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": self.max_requests,
                    "window_seconds": self.window_seconds,
                    "retry_after_seconds": reset_in,
                    "message": f"Too many requests. Please retry after {reset_in} seconds.",
                },
            )

        # Record this request
        self._requests[key].append(time.time())
        remaining -= 1

        logger.info(f"Rate limit check passed for {key}: {remaining} requests remaining")

        return {
            "limit": self.max_requests,
            "remaining": max(0, remaining),
            "reset_in_seconds": self.window_seconds,
        }


# Global rate limiter instance
rate_limiter = RateLimiter()
