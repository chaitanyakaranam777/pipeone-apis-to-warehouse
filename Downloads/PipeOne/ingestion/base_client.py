"""
Base HTTP client with retry logic, rate-limit handling, and logging.
"""
import time
from typing import Any, Dict, Optional

import requests
from tenacity import (
    retry, stop_after_attempt, wait_exponential,
    retry_if_exception_type, before_sleep_log
)
import logging

from configs.settings import settings

logger = logging.getLogger(__name__)


class BaseAPIClient:
    """
    Reusable HTTP client with:
    - Configurable retries (exponential back-off)
    - Rate-limit detection (429 / X-RateLimit headers)
    - Structured logging per request
    """

    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        default_headers = {
            "Accept": "application/json",
            "User-Agent": "PipeOne-DataPipeline/1.0",
        }
        if headers:
            default_headers.update(headers)
        self.session.headers.update(default_headers)

    def _handle_rate_limit(self, response: requests.Response) -> None:
        """Sleep if rate limited."""
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            logger.warning(f"Rate limited. Sleeping {retry_after}s")
            time.sleep(retry_after)
            return

        remaining = response.headers.get("X-RateLimit-Remaining")
        if remaining is not None and int(remaining) < 5:
            reset_ts = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
            sleep_for = max(0, reset_ts - time.time()) + 1
            logger.warning(f"Rate limit low ({remaining} left). Sleeping {sleep_for:.1f}s")
            time.sleep(sleep_for)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=30),
        retry=retry_if_exception_type((requests.ConnectionError, requests.Timeout)),
        reraise=True,
    )
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """
        Perform a GET request with retry and rate-limit handling.
        Returns parsed JSON or raises on non-2xx.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.debug(f"GET {url} params={params}")
        response = self.session.get(url, params=params, timeout=30)
        self._handle_rate_limit(response)
        response.raise_for_status()
        logger.debug(f"Response {response.status_code} from {url}")
        return response.json()
