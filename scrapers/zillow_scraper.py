#!/usr/bin/env python3
"""
Zillow Foreclosure Scraper
Scrapes foreclosure listings from Zillow (free, no login required)
Works for LA County and Riverside County
"""

import re
from datetime import datetime
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ZillowScraper')


class ZillowForeclosureScraper:
    """Scraper for Zillow foreclosure listings"""

    COUNTY_URLS = {
        'Los Angeles': 'https://www.zillow.com/los-angeles-county-ca/foreclosures/',
        'Riverside': 'https://www.zillow.com/riverside-county-ca/foreclosures/'
    }

    def __init__(self, county: str = 'Los Angeles'):
        self.county = county
        self.driver = None

    def _init_driver(self):
        """Initialize Selenium WebDriver"""
        if self.driver is not None:
            return

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        try:
            from webdriver_manager.chrome import ChromeDriverManager
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            raise

    def _close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def scrape_foreclosures(self, max_pages: int = 3) -> List[Dict]:
        """Scrape foreclosure listings from Zillow"""
        if self.county not in self.COUNTY_URLS:
            logger.error(f"Unknown county: {self.county}")
            return []

        all_records = []

        try:
            self._init_driver()

            for page in range(1, max_pages + 1):
                url = self.COUNTY_URLS[self.county]
                if page > 1:
                    url = f"{url}{page}_p/"

                logger.info(f"Scraping page {page}: {url}")
                self.driver.get(url)
                time.sleep(5)

                # Scroll to load all listings
                for _ in range(3):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)

                # Parse listings
                records = self._parse_listings()
                all_records.extend(records)

                logger.info(f"Page {page}: Found {len(records)} listings")

                if len(records) < 10:  # Probably last page
                    break

                time.sleep(2)  # Rate limiting

        except Exception as e:
            logger.error(f"Error during scraping: {e}")

        finally:
            self._close_driver()

        # Deduplicate
        unique = self._deduplicate(all_records)
        logger.info(f"Total unique listings: {len(unique)}")

        return unique

    def _parse_listings(self) -> List[Dict]:
        """Parse property listings from current page"""
        records = []

        try:
            # Get page text
            body = self.driver.find_element(By.TAG_NAME, 'body')
            page_text = body.text

            # Split by property patterns
            # Zillow format: "ADDRESS\nAGENT/BROKER\n$PRICE\nBEDS BATHS SQFT - Foreclosure"

            # Find all property cards by looking for price patterns
            lines = page_text.split('\n')

            current_record = {}
            for i, line in enumerate(lines):
                line = line.strip()

                # Skip empty lines
                if not line:
                    continue

                # Detect address (number + street name)
                if re.match(r'^\d+\s+[A-Za-z]', line) and not line.startswith('$'):
                    # Save previous record if exists
                    if current_record.get('property_address'):
                        records.append(current_record)

                    # Start new record
                    current_record = {
                        'property_address': line,
                        'county': self.county,
                        'source': 'Zillow',
                        'stage': 'Foreclosure',
                        'status': 'New',
                        'date_found': datetime.now().strftime('%Y-%m-%d')
                    }

                    # Extract city from address
                    city_match = re.search(r',\s*([A-Za-z\s]+),\s*CA', line)
                    if city_match:
                        current_record['city'] = city_match.group(1).strip()

                # Detect price
                elif line.startswith('$') and current_record:
                    price_match = re.match(r'\$([\d,]+)', line)
                    if price_match:
                        current_record['estimated_value'] = line.split()[0]

                # Detect beds/baths/sqft
                elif re.search(r'\d+\s*bds?\s*\d+\s*ba', line, re.IGNORECASE) and current_record:
                    # Extract property details
                    beds_match = re.search(r'(\d+)\s*bds?', line, re.IGNORECASE)
                    baths_match = re.search(r'(\d+)\s*ba', line, re.IGNORECASE)
                    sqft_match = re.search(r'([\d,]+)\s*sqft', line, re.IGNORECASE)

                    if beds_match:
                        current_record['bedrooms'] = beds_match.group(1)
                    if baths_match:
                        current_record['bathrooms'] = baths_match.group(1)
                    if sqft_match:
                        current_record['square_feet'] = sqft_match.group(1)

                    # Confirm it's a foreclosure
                    if 'foreclosure' in line.lower():
                        current_record['stage'] = 'Foreclosure'

                # Detect days on Zillow
                elif 'days on zillow' in line.lower() and current_record:
                    days_match = re.search(r'(\d+)\s*days', line, re.IGNORECASE)
                    if days_match:
                        current_record['days_on_market'] = days_match.group(1)

            # Don't forget last record
            if current_record.get('property_address'):
                records.append(current_record)

        except Exception as e:
            logger.error(f"Error parsing listings: {e}")

        return records

    def _deduplicate(self, records: List[Dict]) -> List[Dict]:
        """Remove duplicate listings"""
        seen = set()
        unique = []

        for record in records:
            addr = record.get('property_address', '')[:40].lower()
            if addr and addr not in seen:
                seen.add(addr)
                unique.append(record)

        return unique


def main():
    """Test the Zillow scraper"""
    import argparse

    parser = argparse.ArgumentParser(description='Zillow Foreclosure Scraper')
    parser.add_argument('--county', type=str, default='Los Angeles',
                        choices=['Los Angeles', 'Riverside'],
                        help='County to scrape')
    parser.add_argument('--pages', type=int, default=2, help='Number of pages to scrape')
    args = parser.parse_args()

    print(f"Scraping {args.county} County foreclosures from Zillow...")

    scraper = ZillowForeclosureScraper(county=args.county)
    records = scraper.scrape_foreclosures(max_pages=args.pages)

    print(f"\nCollected {len(records)} foreclosure listings:")
    print("-" * 60)

    for record in records[:10]:
        print(f"Address: {record.get('property_address', 'N/A')}")
        print(f"  City: {record.get('city', 'N/A')}")
        print(f"  Price: {record.get('estimated_value', 'N/A')}")
        print(f"  Beds/Baths: {record.get('bedrooms', '?')}/{record.get('bathrooms', '?')}")
        print()

    if len(records) > 10:
        print(f"... and {len(records) - 10} more")

    return records


if __name__ == '__main__':
    main()
