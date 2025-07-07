"""
Tests for the validators module.
"""

import unittest
from validators import (
    validate_professor_data,
    clean_professor_name,
    validate_rating,
    validate_professor_link,
    create_professor_entry
)

class TestValidators(unittest.TestCase):
    """Test cases for validator functions."""
    
    def test_clean_professor_name(self):
        """Test professor name cleaning."""
        test_cases = [
            ("  John   Doe  ", "John Doe"),
            ("Smith, Jane", "Smith, Jane"),
            ("O'Connor, Mary", "O'Connor, Mary"),
            ("", ""),
            ("Dr. Smith", "Dr. Smith"),
        ]
        
        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = clean_professor_name(input_name)
                self.assertEqual(result, expected)
    
    def test_validate_rating(self):
        """Test rating validation."""
        valid_ratings = [0.0, 2.5, 4.0, "3.67", "0.64"]
        invalid_ratings = [-1.0, 5.0, "invalid", "", None]
        
        for rating in valid_ratings:
            with self.subTest(rating=rating):
                result = validate_rating(rating)
                self.assertIsNotNone(result)
                self.assertIsInstance(result, float)
        
        for rating in invalid_ratings:
            with self.subTest(rating=rating):
                result = validate_rating(rating)
                self.assertIsNone(result)
    
    def test_validate_professor_link(self):
        """Test professor link validation."""
        valid_links = [
            "https://polyratings.dev/professor/12345678-1234-1234-1234-123456789abc",
            "https://polyratings.dev/professor/00000000-0000-0000-0000-000000000000"
        ]
        invalid_links = [
            "https://polyratings.dev/professor/invalid",
            "https://othersite.com/professor/12345678-1234-1234-1234-123456789abc",
            "invalid-url",
            ""
        ]
        
        for link in valid_links:
            with self.subTest(link=link):
                result = validate_professor_link(link)
                self.assertEqual(result, link)
        
        for link in invalid_links:
            with self.subTest(link=link):
                result = validate_professor_link(link)
                self.assertIsNone(result)
    
    def test_create_professor_entry(self):
        """Test creating a valid professor entry."""
        valid_entry = create_professor_entry(
            "Smith, John",
            3.5,
            "https://polyratings.dev/professor/12345678-1234-1234-1234-123456789abc"
        )
        
        self.assertIsNotNone(valid_entry)
        self.assertEqual(valid_entry["name"], "Smith, John")
        self.assertEqual(valid_entry["rating"], 3.5)
        self.assertEqual(valid_entry["link"], "https://polyratings.dev/professor/12345678-1234-1234-1234-123456789abc")
    
    def test_validate_professor_data(self):
        """Test professor data validation."""
        valid_professor = {
            "name": "Smith, John",
            "rating": 3.5,
            "link": "https://polyratings.dev/professor/12345678-1234-1234-1234-123456789abc"
        }
        
        self.assertTrue(validate_professor_data(valid_professor))
        
        # Test invalid data
        invalid_professors = [
            {"name": "", "rating": 3.5, "link": "https://polyratings.dev/professor/12345678-1234-1234-1234-123456789abc"},
            {"name": "Smith, John", "rating": 5.0, "link": "https://polyratings.dev/professor/12345678-1234-1234-1234-123456789abc"},
            {"name": "Smith, John", "rating": 3.5, "link": "invalid-link"},
        ]
        
        for invalid_professor in invalid_professors:
            with self.subTest(invalid_professor=invalid_professor):
                self.assertFalse(validate_professor_data(invalid_professor))

if __name__ == "__main__":
    unittest.main() 
