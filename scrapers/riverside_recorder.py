#!/usr/bin/env python3
"""
Riverside County Recorder Scraper
Scrapes Notice of Default records from Riverside County WebSelfService portal
URL: https://webselfservice.riversideacr.com/Web/action/ACTIONGROUP2111S1
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

from base_scraper import BaseScraper, RecordStandardizer, generate_lead_id


class RiversideRecorderScraper(BaseScraper):
    """Scraper for Riverside County Recorder NOD records"""

    BASE_URL = "https://webselfservice.riversideacr.com/Web/action/ACTIONGROUP2111S1"

    def __init__(self):
        super().__init__(county_name="Riverside", rate_limit_seconds=3.0)
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

        try:
            from webdriver_manager.chrome import ChromeDriverManager
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome driver: {e}")
            raise

    def _close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def search_nod_records(self, date_from: datetime, date_to: datetime) -> List[Dict]:
        """Search for NOD records in Riverside County"""
        records = []

        try:
            self._init_driver()
            self.driver.get(self.BASE_URL)

            # Wait for page to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(2)

            # Look for Document Type Search option
            try:
                # Click on Document Type Search link/button
                doc_type_links = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "Document Type")
                if doc_type_links:
                    doc_type_links[0].click()
                    time.sleep(2)
            except Exception as e:
                self.logger.warning(f"Could not find Document Type search link: {e}")

            # Try to find and fill the search form
            try:
                # Look for document type dropdown or input
                doc_type_inputs = self.driver.find_elements(By.CSS_SELECTOR,
                    "select[name*='doc'], input[name*='doc'], select[id*='doc'], input[id*='doc']")

                if doc_type_inputs:
                    doc_input = doc_type_inputs[0]
                    if doc_input.tag_name == 'select':
                        select = Select(doc_input)
                        # Try to find NOD option
                        for option in select.options:
                            if 'default' in option.text.lower() or 'nod' in option.text.lower():
                                select.select_by_visible_text(option.text)
                                break
                    else:
                        doc_input.send_keys("Notice of Default")

                # Look for date fields
                date_from_inputs = self.driver.find_elements(By.CSS_SELECTOR,
                    "input[name*='from'], input[name*='start'], input[id*='from'], input[id*='start']")
                date_to_inputs = self.driver.find_elements(By.CSS_SELECTOR,
                    "input[name*='to'], input[name*='end'], input[id*='to'], input[id*='end']")

                if date_from_inputs:
                    date_from_inputs[0].clear()
                    date_from_inputs[0].send_keys(date_from.strftime("%m/%d/%Y"))

                if date_to_inputs:
                    date_to_inputs[0].clear()
                    date_to_inputs[0].send_keys(date_to.strftime("%m/%d/%Y"))

                # Submit search
                submit_buttons = self.driver.find_elements(By.CSS_SELECTOR,
                    "button[type='submit'], input[type='submit'], button[name*='search']")
                if submit_buttons:
                    submit_buttons[0].click()
                    time.sleep(3)

                # Parse results
                records = self._parse_search_results()

            except Exception as e:
                self.logger.error(f"Error filling search form: {e}")

        except Exception as e:
            self.logger.error(f"Error during search: {e}")

        finally:
            self._close_driver()

        return records

    def _parse_search_results(self) -> List[Dict]:
        """Parse search results from the page"""
        records = []

        try:
            # Wait for results to load
            time.sleep(2)

            # Look for result tables
            tables = self.driver.find_elements(By.TAG_NAME, "table")

            for table in tables:
                rows = table.find_elements(By.TAG_NAME, "tr")

                # Skip header row
                for row in rows[1:]:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 3:
                        record = {
                            'raw_cells': [cell.text for cell in cells],
                            'source': 'Riverside County Recorder'
                        }
                        records.append(record)

            # Also check for div-based results
            result_divs = self.driver.find_elements(By.CSS_SELECTOR,
                ".result, .record, .document-row, [class*='result']")

            for div in result_divs:
                record = {
                    'raw_text': div.text,
                    'source': 'Riverside County Recorder'
                }
                records.append(record)

            self.logger.info(f"Found {len(records)} raw records")

        except Exception as e:
            self.logger.error(f"Error parsing results: {e}")

        return records

    def parse_record(self, record_data: Dict) -> Dict:
        """Parse raw record into standardized format"""
        parsed = {
            'county': 'Riverside',
            'source': 'Riverside County Recorder',
            'stage': 'NOD',
            'status': 'New'
        }

        # Parse from raw cells if available
        if 'raw_cells' in record_data:
            cells = record_data['raw_cells']
            # Common column orders: Doc#, Date, Type, Grantor, Grantee, Pages
            if len(cells) >= 4:
                parsed['document_number'] = cells[0]
                parsed['recording_date'] = self._parse_date(cells[1])
                parsed['owner_name'] = cells[3] if len(cells) > 3 else ''
                parsed['lender'] = cells[4] if len(cells) > 4 else ''

        # Parse from raw text if available
        elif 'raw_text' in record_data:
            text = record_data['raw_text']

            # Extract document number
            doc_match = re.search(r'\d{4}-\d+', text)
            if doc_match:
                parsed['document_number'] = doc_match.group()

            # Extract date
            date_match = re.search(r'\d{1,2}/\d{1,2}/\d{2,4}', text)
            if date_match:
                parsed['recording_date'] = self._parse_date(date_match.group())

            # Extract names (typically all caps)
            name_matches = re.findall(r'[A-Z][A-Z\s,]+[A-Z]', text)
            if name_matches:
                parsed['owner_name'] = name_matches[0].strip()
                if len(name_matches) > 1:
                    parsed['lender'] = name_matches[1].strip()

        # Generate lead ID
        parsed['lead_id'] = generate_lead_id(parsed)

        return RecordStandardizer.standardize(parsed)

    def _parse_date(self, date_str: str) -> str:
        """Parse date string to YYYY-MM-DD format"""
        if not date_str:
            return ''

        formats = ['%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d', '%m-%d-%Y']

        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue

        return date_str


def main():
    """Test the Riverside County scraper"""
    import argparse

    parser = argparse.ArgumentParser(description='Riverside County NOD Scraper')
    parser.add_argument('--days', type=int, default=7, help='Days to look back')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    args = parser.parse_args()

    scraper = RiversideRecorderScraper()

    if args.test:
        print("Running Riverside County scraper test...")
        print(f"Looking back {args.days} days")

    records = scraper.collect_records(days_back=args.days)

    print(f"\nCollected {len(records)} records:")
    for record in records[:5]:  # Show first 5
        print(f"  - {record.get('owner_name', 'Unknown')} | {record.get('recording_date', 'No date')} | {record.get('property_address', 'No address')}")

    if len(records) > 5:
        print(f"  ... and {len(records) - 5} more")

    return records


if __name__ == '__main__':
    main()
