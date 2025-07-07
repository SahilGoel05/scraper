"""
Data validation functions for the PolyRatings scraper.
"""

import json
import re
from typing import Dict, List, Any, Optional
from jsonschema import validate, ValidationError
from config import ScraperConfig

# JSON schema for professor data
PROFESSOR_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "minLength": ScraperConfig.MIN_NAME_LENGTH,
            "maxLength": ScraperConfig.MAX_NAME_LENGTH,
            "pattern": r"^[A-Za-z\s,\.'-]+$"
        },
        "rating": {
            "type": "number",
            "minimum": ScraperConfig.MIN_RATING,
            "maximum": ScraperConfig.MAX_RATING
        },
        "link": {
            "type": "string",
            "format": "uri",
            "pattern": r"^https://polyratings\.dev/professor/[a-f0-9-]+$"
        }
    },
    "required": ["name", "rating", "link"],
    "additionalProperties": False
}

PROFESSORS_LIST_SCHEMA = {
    "type": "array",
    "items": PROFESSOR_SCHEMA,
    "minItems": 1
}

def validate_professor_data(professor: Dict[str, Any]) -> bool:
    """
    Validate a single professor data entry.
    
    Args:
        professor: Dictionary containing professor data
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        validate(instance=professor, schema=PROFESSOR_SCHEMA)
        return True
    except ValidationError as e:
        print(f"Validation error for professor {professor.get('name', 'Unknown')}: {e.message}")
        return False

def validate_professors_list(professors: List[Dict[str, Any]]) -> bool:
    """
    Validate a list of professor data entries.
    
    Args:
        professors: List of professor dictionaries
        
    Returns:
        bool: True if all entries are valid, False otherwise
    """
    try:
        validate(instance=professors, schema=PROFESSORS_LIST_SCHEMA)
        return True
    except ValidationError as e:
        print(f"Validation error for professors list: {e.message}")
        return False

def clean_professor_name(name: str) -> str:
    """
    Clean and normalize professor name.
    
    Args:
        name: Raw professor name
        
    Returns:
        str: Cleaned professor name
    """
    if not name:
        return ""
    
    # Remove extra whitespace
    name = re.sub(r'\s+', ' ', name.strip())
    
    # Remove any non-alphabetic characters except spaces, commas, periods, apostrophes, and hyphens
    name = re.sub(r'[^A-Za-z\s,\.\'-]', '', name)
    
    return name

def validate_rating(rating: Any) -> Optional[float]:
    """
    Validate and convert rating to float.
    
    Args:
        rating: Rating value (could be string or number)
        
    Returns:
        Optional[float]: Valid rating as float, or None if invalid
    """
    try:
        rating_float = float(rating)
        if ScraperConfig.MIN_RATING <= rating_float <= ScraperConfig.MAX_RATING:
            return round(rating_float, 2)
        else:
            print(f"Rating {rating_float} is outside valid range [{ScraperConfig.MIN_RATING}, {ScraperConfig.MAX_RATING}]")
            return None
    except (ValueError, TypeError):
        print(f"Invalid rating value: {rating}")
        return None

def validate_professor_link(link: str) -> Optional[str]:
    """
    Validate professor profile link.
    
    Args:
        link: Professor profile URL
        
    Returns:
        Optional[str]: Valid URL or None if invalid
    """
    if not link:
        return None
    
    # Check if it's a valid polyratings.dev professor URL
    if re.match(r'^https://polyratings\.dev/professor/[a-f0-9-]+$', link):
        return link
    else:
        print(f"Invalid professor link format: {link}")
        return None

def create_professor_entry(name: str, rating: Any, link: str) -> Optional[Dict[str, Any]]:
    """
    Create a validated professor entry.
    
    Args:
        name: Professor name
        rating: Professor rating
        link: Professor profile link
        
    Returns:
        Optional[Dict[str, Any]]: Valid professor entry or None if invalid
    """
    # Clean and validate name
    clean_name = clean_professor_name(name)
    if not clean_name:
        print(f"Invalid professor name: {name}")
        return None
    
    # Validate rating
    valid_rating = validate_rating(rating)
    if valid_rating is None:
        return None
    
    # Validate link
    valid_link = validate_professor_link(link)
    if valid_link is None:
        return None
    
    professor_entry = {
        "name": clean_name,
        "rating": valid_rating,
        "link": valid_link
    }
    
    # Final validation
    if validate_professor_data(professor_entry):
        return professor_entry
    else:
        return None

def save_professors_json(professors: List[Dict[str, Any]], output_path: str) -> bool:
    """
    Save professors data to JSON file with validation.
    
    Args:
        professors: List of professor dictionaries
        output_path: Path to output JSON file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Validate the entire list
        if not validate_professors_list(professors):
            print("Validation failed for professors list")
            return False
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(professors, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully saved {len(professors)} professors to {output_path}")
        return True
        
    except Exception as e:
        print(f"Error saving professors data: {e}")
        return False

def load_professors_json(input_path: str) -> Optional[List[Dict[str, Any]]]:
    """
    Load and validate professors data from JSON file.
    
    Args:
        input_path: Path to input JSON file
        
    Returns:
        Optional[List[Dict[str, Any]]]: Valid professors list or None if invalid
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            professors = json.load(f)
        
        if validate_professors_list(professors):
            print(f"Successfully loaded {len(professors)} professors from {input_path}")
            return professors
        else:
            print("Validation failed for loaded professors data")
            return None
            
    except Exception as e:
        print(f"Error loading professors data: {e}")
        return None 
