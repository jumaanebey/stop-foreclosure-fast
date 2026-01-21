#!/usr/bin/env python3
"""
Riverside County Recorder Scraper

Scrapes Notice of Default (NOD) records from Riverside County WebSelfService portal.
Source: https://webselfservice.riversideacr.com/Web/action/ACTIONGROUP2111S1

This scraper extracts:
- Recording date
- Document type (filtered for NOD only)
- Grantor (property owner/trustor)
- Grantee (lender/beneficiary)
- APN (Assessor Parcel Number)
- Document number

Usage:
    python riverside_recorder.py --days 7
    python riverside_recorder.py --test
"""

import re
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import from base_scraper
try:
    from .base_scraper import BaseScraper, RecordStandardizer, generate_lead_id
except ImportError:
    from base_scraper import BaseScraper, RecordStandardizer, generate_lead_id


class RiversideRecorderScraper(BaseScraper):
    """
    Scraper for Riverside County Recorder NOD records.

    This scraper uses Selenium to navigate the Riverside County
    WebSelfService portal and extract Notice of Default filings.

    Attributes:
        BASE_URL: Riverside County recorder portal URL
        SEARCH_URL: Direct link to document search
        driver: Selenium WebDriver instance
    """

    # Riverside County WebSelfService portal
    BASE_URL = "https://webselfservice.riversideacr.com/Web/action/ACTIONGROUP2111S1"

    # Alternative search endpoint
    SEARCH_URL = "https://webselfservice.riversideacr.com/Web/user/TGOS050S1/TGOSEntry"

    def __init__(self, rate_limit_seconds: float = 3.0):
        """
        Initialize the Riverside County Recorder scraper.

        Args:
            rate_limit_seconds: Minimum seconds between requests (default: 3.0)
        """
        super().__init__(county_name="Riverside", rate_limit_seconds=rate_limit_seconds)
        self.driver = None

    def _init_driver(self):
        """Initialize Selenium WebDriver with Chrome in headless mode."""
        if self.driver is not None:
            return

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)

        # Add random user agent
        import random
        options.add_argument(f'--user-agent={random.choice(self.USER_AGENTS)}')

        try:
            from webdriver_manager.chrome import ChromeDriverManager
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            # Evade detection
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            self.logger.info("Chrome WebDriver initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome driver: {e}")
            raise

    def _close_driver(self):
        """Close the WebDriver and clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                self.logger.warning(f"Error closing driver: {e}")
            finally:
                self.driver = None

    def search_nod_records(self, date_from: datetime, date_to: datetime) -> List[Dict]:
        """
        Search for NOD records in the specified date range.

        This method navigates the Riverside County WebSelfService portal
        to search for Notice of Default documents.

        Args:
            date_from: Start date for the search
            date_to: End date for the search

        Returns:
            List of raw record dictionaries
        """
        records = []

        try:
            self._init_driver()

            self.logger.info(f"Searching Riverside County NOD records from {date_from.strftime('%Y-%m-%d')} to {date_to.strftime('%Y-%m-%d')}")

            # Try primary URL first
            self.driver.get(self.BASE_URL)

            # Wait for page to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)

            # Navigate to Document Type Search if available
            try:
                doc_type_links = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "Document Type")
                if not doc_type_links:
                    doc_type_links = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "Search")
                if doc_type_links:
                    doc_type_links[0].click()
                    time.sleep(2)
            except Exception as e:
                self.logger.warning(f"Could not find Document Type search link: {e}")

            # Try to find and fill the search form
            records = self._fill_and_submit_search(date_from, date_to)

            # If no results, try alternative search
            if not records:
                self.logger.info("Primary search returned no results, trying alternative...")
                self.driver.get(self.SEARCH_URL)
                time.sleep(3)
                records = self._fill_and_submit_search(date_from, date_to)

        except Exception as e:
            self.logger.error(f"Error during search: {e}")

        finally:
            self._close_driver()

        self.logger.info(f"Found {len(records)} raw NOD records from Riverside County")
        return records

    def _fill_and_submit_search(self, date_from: datetime, date_to: datetime) -> List[Dict]:
        """
        Fill out the search form and submit it.

        Args:
            date_from: Start date
            date_to: End date

        Returns:
            List of raw record dictionaries
        """
        records = []

        try:
            # Document type selectors to try
            doc_type_selectors = [
                "select[name*='doc']",
                "select[id*='doc']",
                "input[name*='doc']",
                "input[id*='doc']",
                "select[name*='type']",
                "#docType",
                ".doc-type-select"
            ]

            # Try to find and select document type
            for selector in doc_type_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        doc_input = elements[0]
                        if doc_input.tag_name == 'select':
                            select = Select(doc_input)
                            for option in select.options:
                                option_text = option.text.lower()
                                if 'default' in option_text or 'nod' in option_text:
                                    select.select_by_visible_text(option.text)
                                    self.logger.info(f"Selected document type: {option.text}")
                                    time.sleep(1)
                                    break
                        else:
                            doc_input.clear()
                            doc_input.send_keys("Notice of Default")
                        break
                except Exception:
                    continue

            # Date field selectors
            date_from_selectors = [
                "input[name*='from']",
                "input[name*='start']",
                "input[id*='from']",
                "input[id*='start']",
                "input[name*='begin']",
                "#startDate",
                "#fromDate"
            ]

            date_to_selectors = [
                "input[name*='to']",
                "input[name*='end']",
                "input[id*='to']",
                "input[id*='end']",
                "#endDate",
                "#toDate"
            ]

            # Fill date from
            for selector in date_from_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        elements[0].clear()
                        elements[0].send_keys(date_from.strftime("%m/%d/%Y"))
                        self.logger.debug(f"Filled start date: {date_from.strftime('%m/%d/%Y')}")
                        break
                except Exception:
                    continue

            # Fill date to
            for selector in date_to_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        elements[0].clear()
                        elements[0].send_keys(date_to.strftime("%m/%d/%Y"))
                        self.logger.debug(f"Filled end date: {date_to.strftime('%m/%d/%Y')}")
                        break
                except Exception:
                    continue

            # Submit selectors
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button[name*='search']",
                "input[value*='Search']",
                "#searchButton",
                ".search-btn",
                "button.btn-primary"
            ]

            # Submit the search
            for selector in submit_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        elements[0].click()
                        self.logger.info("Search submitted")
                        time.sleep(5)
                        break
                except Exception:
                    continue

            # Parse results
            records = self._parse_search_results()

        except Exception as e:
            self.logger.error(f"Error filling search form: {e}")

        return records

    def _parse_search_results(self) -> List[Dict]:
        """
        Parse search results from the current page.

        Looks for table-based and div-based result layouts, filtering
        for NOD documents only.

        Returns:
            List of raw record dictionaries
        """
        records = []

        try:
            # Wait for results to load
            time.sleep(2)

            # Look for result tables
            tables = self.driver.find_elements(By.CSS_SELECTOR, "table, .results-table, #resultsTable")

            for table in tables:
                rows = table.find_elements(By.TAG_NAME, "tr")

                # Skip header row(s)
                for row in rows[1:]:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 3:
                        # Filter for NOD documents
                        row_text = row.text.lower()
                        if 'default' in row_text or 'nod' in row_text:
                            record = {
                                'raw_cells': [cell.text for cell in cells],
                                'source': 'Riverside County Recorder',
                                'row_html': row.get_attribute('innerHTML')
                            }
                            records.append(record)

            # Also check for div-based results
            result_divs = self.driver.find_elements(By.CSS_SELECTOR,
                ".result-item, .record-card, .document-row, [class*='result'], [class*='record']")

            for div in result_divs:
                div_text = div.text.lower()
                if 'default' in div_text or 'nod' in div_text:
                    record = {
                        'raw_text': div.text,
                        'source': 'Riverside County Recorder',
                        'div_html': div.get_attribute('innerHTML')
                    }
                    records.append(record)

            # Handle pagination if present
            if len(records) > 0:
                next_buttons = self.driver.find_elements(By.CSS_SELECTOR,
                    "a.next, button.next, [aria-label='Next'], .pagination .next")

                if next_buttons:
                    try:
                        # Limit pagination to avoid too many requests
                        for page in range(3):  # Max 3 additional pages
                            next_buttons[0].click()
                            time.sleep(3)

                            page_records = self._parse_single_page()
                            if not page_records:
                                break
                            records.extend(page_records)

                            next_buttons = self.driver.find_elements(By.CSS_SELECTOR,
                                "a.next, button.next, [aria-label='Next']")
                            if not next_buttons:
                                break

                    except Exception as e:
                        self.logger.warning(f"Pagination error: {e}")

            self.logger.info(f"Parsed {len(records)} raw records from search results")

        except Exception as e:
            self.logger.error(f"Error parsing results: {e}")

        return records

    def _parse_single_page(self) -> List[Dict]:
        """Parse records from a single results page."""
        records = []

        tables = self.driver.find_elements(By.CSS_SELECTOR, "table, .results-table")
        for table in tables:
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows[1:]:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 3:
                    row_text = row.text.lower()
                    if 'default' in row_text or 'nod' in row_text:
                        record = {
                            'raw_cells': [cell.text for cell in cells],
                            'source': 'Riverside County Recorder'
                        }
                        records.append(record)

        return records

    def parse_record(self, record_data: Dict) -> Dict:
        """
        Parse raw record data into standardized format.

        Handles multiple data formats (table cells, raw text, etc.)
        and extracts key fields like owner name, recording date, APN.

        Args:
            record_data: Raw record dictionary from search

        Returns:
            Standardized record dictionary
        """
        parsed = {
            'county': 'Riverside',
            'source': 'Riverside County Recorder',
            'stage': 'NOD',
            'status': 'New'
        }

        # Parse from raw cells (table format)
        if 'raw_cells' in record_data:
            cells = record_data['raw_cells']

            # Common Riverside County column orders:
            # [Doc#, Date, Type, Grantor, Grantee, Pages, APN]

            if len(cells) >= 4:
                # Try to identify columns by content patterns
                for i, cell in enumerate(cells):
                    cell_clean = cell.strip()

                    # Document number pattern: YYYY-XXXXXX
                    if re.match(r'\d{4}-\d{6,}', cell_clean):
                        parsed['document_number'] = cell_clean

                    # Date pattern: MM/DD/YYYY or YYYY-MM-DD
                    elif re.match(r'\d{1,2}/\d{1,2}/\d{2,4}', cell_clean):
                        parsed['recording_date'] = self._parse_date(cell_clean)
                    elif re.match(r'\d{4}-\d{2}-\d{2}', cell_clean):
                        parsed['recording_date'] = cell_clean

                    # APN pattern: XXX-XXX-XXX
                    elif re.match(r'\d{3}[-\s]?\d{3}[-\s]?\d{3}', cell_clean):
                        parsed['apn'] = cell_clean

                    # Names (usually all caps, contains comma)
                    elif re.match(r'^[A-Z\s,]+$', cell_clean) and len(cell_clean) > 5:
                        if not parsed.get('owner_name'):
                            parsed['owner_name'] = cell_clean
                        elif not parsed.get('lender'):
                            parsed['lender'] = cell_clean

        # Parse from raw text (card/div format)
        elif 'raw_text' in record_data:
            text = record_data['raw_text']

            # Extract document number
            doc_match = re.search(r'(\d{4}-\d{6,})', text)
            if doc_match:
                parsed['document_number'] = doc_match.group(1)

            # Extract date
            date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{2,4})', text)
            if date_match:
                parsed['recording_date'] = self._parse_date(date_match.group(1))

            # Extract APN
            apn_match = re.search(r'APN[:\s]*(\d{3}[-\s]?\d{3}[-\s]?\d{3})', text, re.IGNORECASE)
            if not apn_match:
                apn_match = re.search(r'(\d{3}[-\s]?\d{3}[-\s]?\d{3})', text)
            if apn_match:
                parsed['apn'] = apn_match.group(1)

            # Extract names (look for all-caps sequences)
            name_matches = re.findall(r'\b([A-Z][A-Z\s,\.]+[A-Z])\b', text)
            if name_matches:
                # Filter out common non-name strings
                names = [n for n in name_matches if len(n) > 4 and 'NOTICE' not in n and 'DEFAULT' not in n]
                if names:
                    parsed['owner_name'] = names[0].strip()
                    if len(names) > 1:
                        parsed['lender'] = names[1].strip()

            # Try to extract trustee
            trustee_match = re.search(r'Trustee[:\s]*([A-Za-z\s,\.]+)', text, re.IGNORECASE)
            if trustee_match:
                parsed['trustee'] = trustee_match.group(1).strip()[:100]

        # Generate lead ID
        parsed['lead_id'] = generate_lead_id(parsed)

        # Calculate days since NOD
        if parsed.get('recording_date'):
            try:
                rec_date = datetime.strptime(parsed['recording_date'], '%Y-%m-%d')
                parsed['days_since_nod'] = (datetime.now() - rec_date).days
            except (ValueError, TypeError):
                pass

        return RecordStandardizer.standardize(parsed)

    def _parse_date(self, date_str: str) -> str:
        """
        Parse various date formats to YYYY-MM-DD.

        Args:
            date_str: Date string in various formats

        Returns:
            Date in YYYY-MM-DD format, or original string if parsing fails
        """
        if not date_str:
            return ''

        formats = [
            '%m/%d/%Y',
            '%m/%d/%y',
            '%Y-%m-%d',
            '%m-%d-%Y',
            '%m-%d-%y',
            '%d-%b-%Y',
            '%b %d, %Y'
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue

        return date_str

    def collect_records(self, days_back: int = 7) -> List[Dict]:
        """
        Collect NOD records from the last N days.

        Args:
            days_back: Number of days to look back (default: 7)

        Returns:
            List of standardized record dictionaries
        """
        date_to = datetime.now()
        date_from = date_to - timedelta(days=days_back)

        self.logger.info(f"Collecting Riverside County NOD records for last {days_back} days")

        raw_records = self.search_nod_records(date_from, date_to)

        parsed_records = []
        for record in raw_records:
            try:
                parsed = self.parse_record(record)
                parsed['county'] = 'Riverside'
                parsed['collected_date'] = datetime.now().strftime('%Y-%m-%d')
                parsed_records.append(parsed)
            except Exception as e:
                self.logger.error(f"Error parsing record: {e}")
                continue

        # Remove duplicates based on document number or APN
        seen = set()
        unique_records = []
        for record in parsed_records:
            key = record.get('document_number') or record.get('apn') or record.get('owner_name', '')
            if key and key not in seen:
                seen.add(key)
                unique_records.append(record)
            elif not key:
                unique_records.append(record)

        self.logger.info(f"Collected {len(unique_records)} unique Riverside County NOD records")
        return unique_records


def main():
    """Test the Riverside County scraper."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description='Riverside County NOD Scraper')
    parser.add_argument('--days', type=int, default=7, help='Days to look back (default: 7)')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    parser.add_argument('--output', type=str, help='Output JSON file')
    args = parser.parse_args()

    print("=" * 60)
    print("RIVERSIDE COUNTY NOD SCRAPER")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Looking back: {args.days} days")
    print("=" * 60)

    scraper = RiversideRecorderScraper()

    if args.test:
        print("\nRunning in TEST mode...")
        print("Testing connection to Riverside County WebSelfService portal...")

    records = scraper.collect_records(days_back=args.days)

    print(f"\nCollected {len(records)} records:")
    for i, record in enumerate(records[:10]):
        print(f"\n  [{i+1}]")
        print(f"      Owner: {record.get('owner_name', 'Unknown')}")
        print(f"      Date: {record.get('recording_date', 'No date')}")
        print(f"      APN: {record.get('apn', 'No APN')}")
        print(f"      Address: {record.get('property_address', 'No address')}")

    if len(records) > 10:
        print(f"\n  ... and {len(records) - 10} more")

    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(records, f, indent=2)
        print(f"\nResults saved to: {args.output}")

    print("\n" + "=" * 60)
    return records


if __name__ == '__main__':
    main()
