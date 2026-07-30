"""
API Utilities for handling external API calls with retry logic and rate limiting.

This module provides:
- Retry decorators for API calls
- Rate limiting helpers
- Error handling for common API issues
"""

import time
import functools
from typing import Callable, Any
import requests
from src.utils import setup_logger

logger = setup_logger("APIUtils")


def retry_on_failure(
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    status_codes: tuple = (429, 500, 502, 503, 504),
    exceptions: tuple = (requests.exceptions.RequestException, requests.exceptions.Timeout, requests.exceptions.ConnectionError)
):
    """
    Decorator to retry API calls on specific HTTP status codes or exceptions.
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for exponential backoff between retries
        status_codes: HTTP status codes that trigger retry
        exceptions: Exception types that trigger retry
    
    Usage:
        @retry_on_failure(max_retries=3, backoff_factor=2.0)
        def fetch_data():
            return requests.get("https://api.example.com/data")
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    response = func(*args, **kwargs)
                    
                    # Check if response has status code and it's in retry list
                    if hasattr(response, 'status_code') and response.status_code in status_codes:
                        if attempt < max_retries:
                            wait_time = backoff_factor ** attempt
                            logger.warning(
                                f"API call returned status {response.status_code}. "
                                f"Retrying in {wait_time:.1f}s (attempt {attempt + 1}/{max_retries})"
                            )
                            time.sleep(wait_time)
                            continue
                    
                    return response
                    
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = backoff_factor ** attempt
                        logger.warning(
                            f"API call failed with {type(e).__name__}: {e}. "
                            f"Retrying in {wait_time:.1f}s (attempt {attempt + 1}/{max_retries})"
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(f"API call failed after {max_retries} retries: {e}")
                        raise
            
            # If we exhausted retries, raise the last exception
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator


def rate_limit_delay(delay: float = 1.0):
    """
    Decorator to add delay between API calls for rate limiting.
    
    Args:
        delay: Delay in seconds between calls
    
    Usage:
        @rate_limit_delay(delay=1.0)
        def fetch_data():
            return requests.get("https://api.example.com/data")
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)
            time.sleep(delay)
            return result
        return wrapper
    return decorator


def handle_api_errors(default_return=None):
    """
    Decorator to handle API errors gracefully and return a default value.
    
    Args:
        default_return: Value to return if API call fails
    
    Usage:
        @handle_api_errors(default_return=None)
        def fetch_data():
            return requests.get("https://api.example.com/data")
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed: {e}")
                return default_return
            except Exception as e:
                logger.error(f"Unexpected error in API call: {e}")
                return default_return
        return wrapper
    return decorator
