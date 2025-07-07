import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from config import ScraperConfig
from validators import create_professor_entry, save_professors_json
from utils import setup_logging, safe_request_delay

logger = setup_logging()

def extract_professors_from_dom(driver):
    """
    Parse the current DOM and extract all professor cards.
    Returns a list of (name, rating, link) tuples.
    """
    soup = BeautifulSoup(driver.page_source, "lxml")
    cards = soup.select('div.absolute > a')
    professors = []
    for a_tag in cards:
        try:
            # Profile link
            href = a_tag.get('href')
            if not href or not href.startswith('/professor/'):
                continue
            link = ScraperConfig.BASE_URL + href
            # Name
            h3 = a_tag.select_one('h3.text-3xl')
            name = h3.get_text(strip=True) if h3 else None
            # Rating
            rating_div = a_tag.select_one('div.flex.items-center.justify-end > div:last-child')
            rating = rating_div.get_text(strip=True) if rating_div else None
            professors.append((name, rating, link))
        except Exception as e:
            logger.warning(f"Failed to parse a professor card: {e}")
    return professors

def fine_grained_scroll_and_collect(driver, scroll_pause=0.15, increment=100, max_no_new=50):
    """
    Scroll through the page in small increments, extracting visible professors at each step.
    This ensures every professor is rendered at least once.
    """
    all_professors = set()
    last_count = 0
    no_new_count = 0
    scroll_position = 0
    total_height = driver.execute_script("return document.body.scrollHeight")
    logger.info(f"Total scrollable height: {total_height}")
    
    while scroll_position < total_height:
        driver.execute_script(f"window.scrollTo(0, {scroll_position});")
        time.sleep(scroll_pause)
        current_professors = extract_professors_from_dom(driver)
        for prof in current_professors:
            all_professors.add(prof)
        if len(all_professors) == last_count:
            no_new_count += 1
        else:
            no_new_count = 0
            last_count = len(all_professors)
        if no_new_count >= max_no_new:
            logger.info(f"Stopping: No new professors found for {no_new_count} increments.")
            break
        if scroll_position % 1000 == 0:
            logger.info(f"Scrolled to {scroll_position}, total unique professors: {len(all_professors)}")
        scroll_position += increment
        # Update total_height in case it grows
        total_height = driver.execute_script("return document.body.scrollHeight")
    # Final pass at the bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause * 2)
    current_professors = extract_professors_from_dom(driver)
    for prof in current_professors:
        all_professors.add(prof)
    logger.info(f"Fine-grained scroll finished. Collected {len(all_professors)} unique professors.")
    return list(all_professors)

def deduplicate_professors(professors):
    seen = set()
    unique = []
    for name, rating, link in professors:
        if link not in seen:
            seen.add(link)
            unique.append((name, rating, link))
    return unique

def main():
    logger.info("Starting PolyRatings scraper...")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument(f'user-agent={ScraperConfig.USER_AGENT}')
    options.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(ScraperConfig.REQUEST_TIMEOUT)
    driver.get(ScraperConfig.SEARCH_URL)
    logger.info(f"Loaded {ScraperConfig.SEARCH_URL}")
    time.sleep(5)

    professors_raw = fine_grained_scroll_and_collect(driver, scroll_pause=0.15, increment=100, max_no_new=100)
    logger.info(f"Extracted {len(professors_raw)} raw professor cards from DOM.")
    driver.quit()

    professors_raw = deduplicate_professors(professors_raw)
    logger.info(f"Deduplicated to {len(professors_raw)} unique professor cards.")

    professors = []
    for name, rating, link in professors_raw:
        entry = create_professor_entry(name, rating, link)
        if entry:
            professors.append(entry)
        else:
            logger.warning(f"Invalid entry skipped: {name}, {rating}, {link}")

    logger.info(f"Validated {len(professors)} professor entries.")

    if save_professors_json(professors, ScraperConfig.OUTPUT_PATH):
        logger.info(f"Saved {len(professors)} professors to {ScraperConfig.OUTPUT_PATH}")
    else:
        logger.error("Failed to save professors.json")

if __name__ == "__main__":
    main() 
