# PolyRatings Scraper

An automated web scraper for extracting professor data from the PolyRatings website.

## Features

- **Automated scraping**: Extracts professor data including names, departments, ratings, and review counts
- **Virtual scrolling support**: Handles the website's virtual scrolling implementation to capture all professors
- **Data validation**: Ensures data integrity with comprehensive validation
- **GitHub Actions integration**: Automated daily scraping with automatic commits
- **Error handling**: Robust error handling and logging
- **Configurable**: Easy to modify scraping parameters and settings

## Setup

### Prerequisites

- Python 3.11+
- Chrome browser (for Selenium WebDriver)

### Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Download ChromeDriver (if not already installed):
   - The scraper will automatically download the appropriate ChromeDriver version

## Usage

### Manual Scraping

Run the scraper manually:
```bash
python scraper.py
```

The scraper will:
1. Launch a Chrome browser
2. Navigate to the PolyRatings website
3. Scroll through all professor cards
4. Extract professor data
5. Save results to `data/professors.json`

### Automated Scraping

The scraper is configured to run automatically via GitHub Actions:
- **Schedule**: Daily at 2 AM UTC
- **Manual trigger**: Available via GitHub Actions UI
- **Auto-commit**: Changes are automatically committed to the repository

## Configuration

### Scraper Settings (`config.py`)

- `SCROLL_PAUSE_TIME`: Time to wait between scrolls (default: 0.5s)
- `SCROLL_INCREMENT`: Pixels to scroll each time (default: 100px)
- `MAX_SCROLL_ATTEMPTS`: Maximum scroll attempts before stopping (default: 50)
- `DATA_FILE_PATH`: Output file path (default: `data/professors.json`)

### Data Validation (`validation.py`)

The scraper validates each professor record to ensure:
- Required fields are present
- Data types are correct
- Rating values are within valid ranges
- Department names are properly formatted

## Output Format

The scraper generates a JSON file with the following structure:

```json
{
  "scraped_at": "2024-01-15T10:30:00Z",
  "total_professors": 2186,
  "professors": [
    {
      "name": "Professor Name",
      "department": "Computer Science",
      "rating": 4.2,
      "review_count": 45,
      "url": "https://polyratings.com/professor/...",
      "scraped_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

## Data Fields

Each professor record contains:
- **name**: Professor's full name
- **department**: Academic department
- **rating**: Average rating (1.0-5.0 scale)
- **review_count**: Number of reviews
- **url**: Link to professor's page
- **scraped_at**: Timestamp of when data was scraped

## Error Handling

The scraper includes comprehensive error handling:
- Network timeouts and retries
- Invalid data detection and logging
- Graceful handling of missing elements
- Detailed error logging for debugging

## Performance

- **Typical runtime**: 5-10 minutes
- **Memory usage**: Low (streaming processing)
- **Network usage**: Minimal (single page load with virtual scrolling)

## Troubleshooting

### Common Issues

1. **ChromeDriver not found**: The scraper will automatically download the correct version
2. **Slow scraping**: Increase `SCROLL_PAUSE_TIME` in config
3. **Missing professors**: Decrease `SCROLL_INCREMENT` for more thorough scraping
4. **Browser crashes**: Check Chrome version compatibility

### Debug Mode

Enable debug logging by modifying the logging level in `scraper.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

When modifying the scraper:
1. Test changes locally first
2. Update configuration as needed
3. Ensure data validation still works
4. Test with different scroll parameters

## License

This scraper is part of the PolyRatings project and follows the same license terms. 
