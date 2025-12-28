#!/usr/bin/env python3
"""
PropertyShark Scraper
Scrapes pre-foreclosure/NOD listings from PropertyShark (free tier)
Works for both LA County and Riverside County
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

from base_scraper import BaseScraper, RecordStandardizer, generate_lead_id


class PropertySharkScraper(BaseScraper):
    """Scraper for PropertyShark foreclosure listings"""

    COUNTY_URLS = {
        'Los Angeles': 'https://www.propertyshark.com/mason/ca/Los-Angeles-County/Foreclosures',
        'Riverside': 'https://www.propertyshark.com/mason/ca/Riverside-County/Foreclosures'
    }

    def __init__(self, county: str = 'Los Angeles'):
        super().__init__(county_name=county, rate_limit_seconds=10.0)
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
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        # Avoid detection
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])

        try:
            from webdriver_manager.chrome import ChromeDriverManager
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome driver: {e}")
            raise

    def _close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def search_nod_records(self, date_from: datetime, date_to: datetime) -> List[Dict]:
        """Search for foreclosure records on PropertyShark"""
        records = []

        if self.county not in self.COUNTY_URLS:
            self.logger.error(f"Unknown county: {self.county}")
            return records

        url = self.COUNTY_URLS[self.county]

        try:
            self._init_driver()
            self.driver.get(url)

            # Wait for page to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)

            # Scroll to load more results
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            # Parse the listings
            records = self._parse_listings()

        except Exception as e:
            self.logger.error(f"Error during PropertyShark search: {e}")

        finally:
            self._close_driver()

        return records

    def _parse_listings(self) -> List[Dict]:
        """Parse property listings from the page"""
        records = []

        try:
            # Look for property cards/rows
            property_elements = self.driver.find_elements(By.CSS_SELECTOR,
                ".property-card, .listing-item, .result-item, [class*='property'], table tr")

            for elem in property_elements:
                try:
                    text = elem.text
                    if not text or len(text) < 10:
                        continue

                    record = {
                        'raw_text': text,
                        'source': 'PropertyShark'
                    }

                    # Try to extract specific fields from the element
                    try:
                        # Look for address
                        address_elem = elem.find_elements(By.CSS_SELECTOR,
                            ".address, .property-address, [class*='address'], h3, h4")
                        if address_elem:
                            record['property_address'] = address_elem[0].text

                        # Look for price/value
                        price_elem = elem.find_elements(By.CSS_SELECTOR,
                            ".price, .value, [class*='price'], [class*='value']")
                        if price_elem:
                            record['estimated_value'] = price_elem[0].text

                        # Look for status
                        status_elem = elem.find_elements(By.CSS_SELECTOR,
                            ".status, [class*='status'], .foreclosure-status")
                        if status_elem:
                            record['foreclosure_status'] = status_elem[0].text

                    except:
                        pass

                    records.append(record)

                except Exception as e:
                    self.logger.debug(f"Error parsing element: {e}")
                    continue

            # Deduplicate by address
            seen_addresses = set()
            unique_records = []
            for record in records:
                addr = record.get('property_address', record.get('raw_text', ''))[:50]
                if addr not in seen_addresses:
                    seen_addresses.add(addr)
                    unique_records.append(record)

            self.logger.info(f"Found {len(unique_records)} unique listings")
            return unique_records

        except Exception as e:
            self.logger.error(f"Error parsing listings: {e}")
            return records

    def parse_record(self, record_data: Dict) -> Dict:
        """Parse raw record into standardized format"""
        parsed = {
            'county': self.county,
            'source': 'PropertyShark',
            'stage': 'NOD',
            'status': 'New',
            'date_found': datetime.now().strftime('%Y-%m-%d')
        }

        # Use extracted fields if available
        if record_data.get('property_address'):
            parsed['property_address'] = record_data['property_address']

            # Try to extract city from address
            city_match = re.search(r',\s*([A-Za-z\s]+),?\s*CA', record_data['property_address'])
            if city_match:
                parsed['city'] = city_match.group(1).strip()

        if record_data.get('estimated_value'):
            value_str = record_data['estimated_value']
            # Clean up price format
            value_clean = re.sub(r'[^\d]', '', value_str)
            if value_clean:
                parsed['estimated_value'] = f"${int(value_clean):,}"

        # Parse from raw text
        if 'raw_text' in record_data:
            text = record_data['raw_text']

            # Extract address if not already found
            if not parsed.get('property_address'):
                # Look for street address pattern
                addr_match = re.search(r'\d+\s+[A-Za-z0-9\s]+(?:St|Ave|Blvd|Dr|Rd|Way|Ln|Ct)', text, re.IGNORECASE)
                if addr_match:
                    parsed['property_address'] = addr_match.group().strip()

            # Extract price/value if not already found
            if not parsed.get('estimated_value'):
                price_match = re.search(r'\$[\d,]+', text)
                if price_match:
                    parsed['estimated_value'] = price_match.group()

            # Extract date
            date_match = re.search(r'\d{1,2}/\d{1,2}/\d{2,4}', text)
            if date_match:
                parsed['recording_date'] = self._parse_date(date_match.group())

            # Look for owner name (often in ALL CAPS)
            name_matches = re.findall(r'\b[A-Z][A-Z]+\s+[A-Z][A-Z]+\b', text)
            if name_matches:
                # Filter out common non-name words
                exclude = ['PRE', 'FORECLOSURE', 'NOTICE', 'DEFAULT', 'LOS', 'ANGELES', 'RIVERSIDE']
                for name in name_matches:
                    if not any(word in name for word in exclude):
                        parsed['owner_name'] = name
                        break

        # Generate lead ID
        parsed['lead_id'] = generate_lead_id(parsed)

        return RecordStandardizer.standardize(parsed)

    def _parse_date(self, date_str: str) -> str:
        """Parse date string to YYYY-MM-DD format"""
        if not date_str:
            return ''

        formats = ['%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d']

        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue

        return ''


def main():
    """Test the PropertyShark scraper"""
    import argparse

    parser = argparse.ArgumentParser(description='PropertyShark Foreclosure Scraper')
    parser.add_argument('--county', type=str, default='Los Angeles',
                        choices=['Los Angeles', 'Riverside'],
                        help='County to scrape')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    args = parser.parse_args()

    scraper = PropertySharkScraper(county=args.county)

    if args.test:
        print(f"Running PropertyShark scraper test for {args.county} County...")

    records = scraper.collect_records(days_back=30)  # PropertyShark shows recent listings

    print(f"\nCollected {len(records)} records:")
    for record in records[:5]:
        print(f"  - {record.get('property_address', 'No address')} | {record.get('estimated_value', 'No value')}")

    if len(records) > 5:
        print(f"  ... and {len(records) - 5} more")

    return records


if __name__ == '__main__':
    main()
