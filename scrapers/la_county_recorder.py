#!/usr/bin/env python3
"""
LA County Recorder Scraper

Scrapes Notice of Default (NOD) records from LA County Registrar-Recorder/Clerk.
Primary source: https://registrarrecorderclerk.lacounty.gov/
Fallback: Netronline https://datastore.netronline.com/losangeles

This scraper extracts:
- Recording date
- Document type (filtered for NOD only)
- Grantor (property owner/trustor)
- Grantee (lender/beneficiary)
- APN (Assessor Parcel Number)
- Document number

Usage:
    python la_county_recorder.py --days 7
    python la_county_recorder.py --test
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


class LACountyRecorderScraper(BaseScraper):
    """
    Scraper for LA County Registrar-Recorder/Clerk NOD records.

    This scraper uses Selenium to navigate the LA County recorder portal
    and extract Notice of Default filings. The portal requires JavaScript
    rendering, hence the use of Selenium.

    Attributes:
        BASE_URL: Main LA County recorder portal URL
        NETRONLINE_URL: Alternative data source URL
        driver: Selenium WebDriver instance
    """

    # LA County Registrar-Recorder/Clerk portal
    BASE_URL = "https://registrarrecorderclerk.lacounty.gov/"

    # Netronline alternative (may require subscription)
    NETRONLINE_URL = "https://datastore.netronline.com/losangeles"

    # Document search endpoint
    SEARCH_URL = "https://lavote.net/home/records/real-estate-records/online-document-search"

    def __init__(self, rate_limit_seconds: float = 3.0):
        """
        Initialize the LA County Recorder scraper.

        Args:
            rate_limit_seconds: Minimum seconds between requests (default: 3.0)
        """
        super().__init__(county_name="Los Angeles", rate_limit_seconds=rate_limit_seconds)
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

        This method attempts to search the LA County recorder portal for
        Notice of Default documents filed between the given dates.

        Args:
            date_from: Start date for the search
            date_to: End date for the search

        Returns:
            List of raw record dictionaries
        """
        records = []

        try:
            self._init_driver()

            # Try primary source first
            self.logger.info(f"Searching LA County NOD records from {date_from.strftime('%Y-%m-%d')} to {date_to.strftime('%Y-%m-%d')}")

            # Navigate to document search
            self.driver.get(self.SEARCH_URL)
            time.sleep(3)

            # Wait for page to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Look for search form elements
            records = self._search_via_form(date_from, date_to)

            # If primary source fails, try alternative methods
            if not records:
                self.logger.info("Primary source returned no results, trying alternative methods...")
                records = self._search_via_netronline(date_from, date_to)

        except Exception as e:
            self.logger.error(f"Error during NOD search: {e}")

        finally:
            self._close_driver()

        self.logger.info(f"Found {len(records)} raw NOD records")
        return records

    def _search_via_form(self, date_from: datetime, date_to: datetime) -> List[Dict]:
        """
        Search for NOD records using the main search form.

        Args:
            date_from: Start date
            date_to: End date

        Returns:
            List of raw record dictionaries
        """
        records = []

        try:
            # Find and interact with document type selector
            doc_type_selectors = [
                "select[name*='doc']",
                "select[id*='doc']",
                "select[name*='type']",
                "#documentType",
                ".doc-type-select"
            ]

            doc_type_element = None
            for selector in doc_type_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        doc_type_element = elements[0]
                        break
                except Exception:
                    continue

            if doc_type_element and doc_type_element.tag_name == 'select':
                select = Select(doc_type_element)
                # Look for NOD option
                for option in select.options:
                    option_text = option.text.lower()
                    if 'default' in option_text or 'nod' in option_text:
                        select.select_by_visible_text(option.text)
                        self.logger.info(f"Selected document type: {option.text}")
                        time.sleep(1)
                        break

            # Find and fill date fields
            date_from_selectors = [
                "input[name*='from']",
                "input[name*='start']",
                "input[id*='from']",
                "input[id*='start']",
                "#startDate",
                ".date-from"
            ]

            date_to_selectors = [
                "input[name*='to']",
                "input[name*='end']",
                "input[id*='to']",
                "input[id*='end']",
                "#endDate",
                ".date-to"
            ]

            # Try to fill date from
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

            # Try to fill date to
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

            # Submit the search
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button[name*='search']",
                "#searchButton",
                ".search-btn",
                "button.btn-primary"
            ]

            for selector in submit_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        elements[0].click()
                        self.logger.info("Search submitted")
                        time.sleep(5)  # Wait for results
                        break
                except Exception:
                    continue

            # Parse results
            records = self._parse_search_results()

        except Exception as e:
            self.logger.error(f"Error in form search: {e}")

        return records

    def _search_via_netronline(self, date_from: datetime, date_to: datetime) -> List[Dict]:
        """
        Alternative search using Netronline datastore.

        Note: Netronline may require subscription for full access.

        Args:
            date_from: Start date
            date_to: End date

        Returns:
            List of raw record dictionaries
        """
        records = []

        try:
            self.driver.get(self.NETRONLINE_URL)
            time.sleep(3)

            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Netronline typically has different structure
            # Look for NOD/foreclosure links
            links = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "Default")
            if not links:
                links = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "Foreclosure")

            if links:
                links[0].click()
                time.sleep(3)
                records = self._parse_search_results()

        except Exception as e:
            self.logger.error(f"Error in Netronline search: {e}")

        return records

    def _parse_search_results(self) -> List[Dict]:
        """
        Parse search results from the current page.

        Looks for table-based and div-based result layouts.

        Returns:
            List of raw record dictionaries
        """
        records = []

        try:
            # Wait for results to load
            time.sleep(2)

            # Try to find results in tables
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
                                'source': 'LA County Recorder',
                                'row_html': row.get_attribute('innerHTML')
                            }
                            records.append(record)

            # Also check for card/div-based results
            result_cards = self.driver.find_elements(By.CSS_SELECTOR,
                ".result-item, .record-card, .document-row, [class*='result'], [class*='record']")

            for card in result_cards:
                card_text = card.text.lower()
                if 'default' in card_text or 'nod' in card_text:
                    record = {
                        'raw_text': card.text,
                        'source': 'LA County Recorder',
                        'card_html': card.get_attribute('innerHTML')
                    }
                    records.append(record)

            # Handle pagination if present
            next_buttons = self.driver.find_elements(By.CSS_SELECTOR,
                "a.next, button.next, [aria-label='Next'], .pagination .next")

            if next_buttons and len(records) > 0:
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
                            'source': 'LA County Recorder'
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
            'county': 'Los Angeles',
            'source': 'LA County Recorder',
            'stage': 'NOD',
            'status': 'New'
        }

        # Parse from raw cells (table format)
        if 'raw_cells' in record_data:
            cells = record_data['raw_cells']

            # Common LA County column orders:
            # [Doc#, Date, Type, Grantor, Grantee, Pages, APN]
            # or [Date, Doc#, Type, Parties, APN]

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

                    # APN pattern: XXXX-XXX-XXX
                    elif re.match(r'\d{4}[-\s]?\d{3}[-\s]?\d{3}', cell_clean):
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
            apn_match = re.search(r'APN[:\s]*(\d{4}[-\s]?\d{3}[-\s]?\d{3})', text, re.IGNORECASE)
            if not apn_match:
                apn_match = re.search(r'(\d{4}[-\s]?\d{3}[-\s]?\d{3})', text)
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

        self.logger.info(f"Collecting LA County NOD records for last {days_back} days")

        raw_records = self.search_nod_records(date_from, date_to)

        parsed_records = []
        for record in raw_records:
            try:
                parsed = self.parse_record(record)
                parsed['county'] = 'Los Angeles'
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

        self.logger.info(f"Collected {len(unique_records)} unique LA County NOD records")
        return unique_records


def main():
    """Test the LA County Recorder scraper."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description='LA County NOD Scraper')
    parser.add_argument('--days', type=int, default=7, help='Days to look back (default: 7)')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    parser.add_argument('--output', type=str, help='Output JSON file')
    args = parser.parse_args()

    print("=" * 60)
    print("LA COUNTY NOD SCRAPER")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Looking back: {args.days} days")
    print("=" * 60)

    scraper = LACountyRecorderScraper()

    if args.test:
        print("\nRunning in TEST mode...")
        print("Testing connection to LA County Recorder portal...")

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
