"""
Utility functions for the PolyRatings scraper.
"""

import time
import logging
import re
from typing import Optional, List, Dict, Any
from urllib.parse import urljoin, urlparse
from config import ScraperConfig

def setup_logging() -> logging.Logger:
    """
    Set up logging configuration.
    
    Returns:
        logging.Logger: Configured logger
    """
    logging.basicConfig(
        level=getattr(logging, ScraperConfig.LOG_LEVEL),
        format=ScraperConfig.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('scraper.log')
        ]
    )
    return logging.getLogger(__name__)

def safe_request_delay():
    """Add a delay between requests to be respectful to the server."""
    time.sleep(ScraperConfig.REQUEST_DELAY)

def extract_professor_id_from_url(url: str) -> Optional[str]:
    """
    Extract professor ID from a professor profile URL.
    
    Args:
        url: Professor profile URL
        
    Returns:
        Optional[str]: Professor ID (UUID) or None if not found
    """
    if not url:
        return None
    
    # Pattern to match UUID in professor URL
    pattern = r'/professor/([a-f0-9-]{36})$'
    match = re.search(pattern, url)
    
    if match:
        return match.group(1)
    else:
        return None

def build_professor_url(professor_id: str) -> str:
    """
    Build professor profile URL from professor ID.
    
    Args:
        professor_id: Professor UUID
        
    Returns:
        str: Complete professor profile URL
    """
    return f"{ScraperConfig.BASE_URL}/professor/{professor_id}"

def extract_rating_from_text(rating_text: str) -> Optional[float]:
    """
    Extract rating value from text that might contain additional information.
    
    Args:
        rating_text: Text containing rating (e.g., "4.5", "3.67", "0.64")
        
    Returns:
        Optional[float]: Rating as float or None if invalid
    """
    if not rating_text:
        return None
    
    # Extract number from text (handles cases like "3.67" or "0.64")
    pattern = r'(\d+\.?\d*)'
    match = re.search(pattern, rating_text.strip())
    
    if match:
        try:
            rating = float(match.group(1))
            if ScraperConfig.MIN_RATING <= rating <= ScraperConfig.MAX_RATING:
                return round(rating, 2)
        except ValueError:
            pass
    
    return None

def clean_html_text(text: str) -> str:
    """
    Clean HTML text by removing extra whitespace and special characters.
    
    Args:
        text: Raw HTML text
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Decode HTML entities
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    
    return text

def is_valid_uuid(uuid_string: str) -> bool:
    """
    Check if a string is a valid UUID.
    
    Args:
        uuid_string: String to validate
        
    Returns:
        bool: True if valid UUID, False otherwise
    """
    pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
    return bool(re.match(pattern, uuid_string.lower()))

def retry_on_failure(func, max_retries: int = None, delay: float = 1.0):
    """
    Decorator to retry a function on failure.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retries (defaults to config)
        delay: Delay between retries in seconds
        
    Returns:
        Decorated function
    """
    if max_retries is None:
        max_retries = ScraperConfig.MAX_RETRIES
    
    def wrapper(*args, **kwargs):
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print(f"All {max_retries + 1} attempts failed. Last error: {e}")
        
        raise last_exception
    
    return wrapper

def format_progress(current: int, total: int, description: str = "Progress") -> str:
    """
    Format progress information.
    
    Args:
        current: Current item number
        total: Total number of items
        description: Description of what's being processed
        
    Returns:
        str: Formatted progress string
    """
    if total == 0:
        return f"{description}: 0/0 (0%)"
    
    percentage = (current / total) * 100
    return f"{description}: {current}/{total} ({percentage:.1f}%)"

def validate_url(url: str) -> bool:
    """
    Validate if a URL is properly formatted.
    
    Args:
        url: URL to validate
        
    Returns:
        bool: True if valid URL, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.
    
    Args:
        lst: List to split
        chunk_size: Size of each chunk
        
    Returns:
        List[List[Any]]: List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)] 
