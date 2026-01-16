"""
Rate Limiter for Gemini API
Handles free tier limits: 15 req/min, 1500 req/day
"""

import time
from collections import deque
from threading import Lock
from datetime import datetime, timedelta
from loguru import logger
from config import settings


class RateLimiter:
    """Thread-safe rate limiter for API calls"""
    
    def __init__(
        self,
        max_per_minute: int = None,
        max_per_day: int = None
    ):
        self.max_per_minute = max_per_minute or settings.MAX_REQUESTS_PER_MINUTE
        self.max_per_day = max_per_day or settings.MAX_REQUESTS_PER_DAY
        
        self.minute_requests = deque()
        self.day_requests = deque()
        self.lock = Lock()
        
        logger.info(f"RateLimiter initialized: {self.max_per_minute}/min, {self.max_per_day}/day")
    
    def _clean_old_requests(self):
        """Remove requests outside the time windows"""
        now = datetime.now()
        
        # Clean minute window
        minute_ago = now - timedelta(minutes=1)
        while self.minute_requests and self.minute_requests[0] < minute_ago:
            self.minute_requests.popleft()
        
        # Clean day window
        day_ago = now - timedelta(days=1)
        while self.day_requests and self.day_requests[0] < day_ago:
            self.day_requests.popleft()
    
    def acquire(self, timeout: float = 60.0) -> bool:
        """
        Acquire permission to make an API call
        Returns True if allowed, False if timeout exceeded
        """
        start_time = time.time()
        
        while True:
            with self.lock:
                self._clean_old_requests()
                
                # Check if we can make a request
                if (len(self.minute_requests) < self.max_per_minute and
                    len(self.day_requests) < self.max_per_day):
                    
                    now = datetime.now()
                    self.minute_requests.append(now)
                    self.day_requests.append(now)
                    
                    logger.debug(
                        f"Request allowed. "
                        f"Minute: {len(self.minute_requests)}/{self.max_per_minute}, "
                        f"Day: {len(self.day_requests)}/{self.max_per_day}"
                    )
                    return True
            
            # Check timeout
            if time.time() - start_time > timeout:
                logger.warning("Rate limiter timeout exceeded")
                return False
            
            # Wait before retry
            time.sleep(0.5)
    
    def get_stats(self) -> dict:
        """Get current rate limit statistics"""
        with self.lock:
            self._clean_old_requests()
            return {
                "minute_used": len(self.minute_requests),
                "minute_limit": self.max_per_minute,
                "day_used": len(self.day_requests),
                "day_limit": self.max_per_day,
                "minute_remaining": self.max_per_minute - len(self.minute_requests),
                "day_remaining": self.max_per_day - len(self.day_requests)
            }


# Global rate limiter instance
rate_limiter = RateLimiter()
