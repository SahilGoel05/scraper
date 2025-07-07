"""
Configuration settings for the PolyRatings scraper.
"""

import os
from typing import Dict, Any

class ScraperConfig:
    """Configuration class for the scraper."""
    
    # Target website
    BASE_URL = "https://polyratings.dev"
    SEARCH_URL = f"{BASE_URL}/search/name"
    
    # Output settings
    OUTPUT_FILE = "professors.json"
    OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "data", OUTPUT_FILE)
    
    # Request settings
    REQUEST_TIMEOUT = 30
    REQUEST_DELAY = 1.0  # Delay between requests in seconds
    MAX_RETRIES = 3
    
    # User agent to avoid being blocked
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    # Headers for requests
    HEADERS = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    # Selenium settings (if needed)
    SELENIUM_TIMEOUT = 30
    SELENIUM_IMPLICIT_WAIT = 10
    
    # Data validation settings
    MIN_RATING = 0.0
    MAX_RATING = 4.0
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 100
    
    # Logging settings
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def get_request_headers(cls) -> Dict[str, str]:
        """Get headers for HTTP requests."""
        return cls.HEADERS.copy()
    
    @classmethod
    def get_selenium_options(cls) -> Dict[str, Any]:
        """Get Selenium options for web driver."""
        return {
            "timeout": cls.SELENIUM_TIMEOUT,
            "implicit_wait": cls.SELENIUM_IMPLICIT_WAIT,
            "user_agent": cls.USER_AGENT,
        } 
