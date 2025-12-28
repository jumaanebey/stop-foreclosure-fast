#!/usr/bin/env python3
"""
DIY Skip Tracer
Finds property owner names and contact info from addresses
Sources: LA County Assessor + TruePeopleSearch
"""

import os
import sys
import re
import time
import random
import logging
from typing import Dict, Optional, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SkipTracer')


class SkipTracer:
    """Skip trace addresses to find owner contact info"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None

    def _init_driver(self):
        """Initialize Selenium with stealth settings"""
        if self.driver:
            return

        options = Options()
        if self.headless:
            options.add_argument('--headless=new')

        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)

        # Rotate user agents
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        options.add_argument(f'user-agent={random.choice(user_agents)}')

        try:
            from webdriver_manager.chrome import ChromeDriverManager
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            # Remove webdriver flag
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            logger.error(f"Failed to init driver: {e}")
            raise

    def _close_driver(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def _random_delay(self, min_sec: float = 2, max_sec: float = 5):
        """Random delay to avoid detection"""
        time.sleep(random.uniform(min_sec, max_sec))

    def get_owner_from_assessor(self, address: str, county: str = 'Los Angeles') -> Optional[str]:
        """
        Look up property owner from county assessor
        Returns owner name or None
        """
        if county != 'Los Angeles':
            logger.info(f"Assessor lookup only supports LA County, skipping {county}")
            return None

        self._init_driver()

        try:
            # LA County Assessor Portal
            url = 'https://portal.assessor.lacounty.gov/'
            logger.info(f"Looking up owner for: {address}")

            self.driver.get(url)
            self._random_delay(3, 5)

            # Find and fill the search box
            try:
                search_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'searchBox'))
                )
                search_box.clear()

                # Type slowly like a human
                for char in address:
                    search_box.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))

                self._random_delay(1, 2)

                # Click search button
                search_btn = self.driver.find_element(By.ID, 'searchButton')
                search_btn.click()

                self._random_delay(3, 5)

                # Look for owner name in results
                page_text = self.driver.find_element(By.TAG_NAME, 'body').text

                # Common patterns for owner name
                owner_patterns = [
                    r'Owner[:\s]+([A-Z][A-Z\s,\.]+)',
                    r'OWNER[:\s]+([A-Z][A-Z\s,\.]+)',
                    r'Name[:\s]+([A-Z][A-Z\s,\.]+)',
                ]

                for pattern in owner_patterns:
                    match = re.search(pattern, page_text)
                    if match:
                        owner = match.group(1).strip()
                        # Clean up the name
                        owner = re.sub(r'\s+', ' ', owner)
                        if len(owner) > 3 and len(owner) < 50:
                            logger.info(f"Found owner: {owner}")
                            return owner

                logger.info("Owner not found in assessor results")
                return None

            except TimeoutException:
                logger.warning("Assessor search timed out")
                return None

        except Exception as e:
            logger.error(f"Assessor lookup error: {e}")
            return None

    def search_truepeoplesearch(self, name: str = None, address: str = None) -> Dict:
        """
        Search TruePeopleSearch for contact info
        Can search by name or address
        Returns dict with phone, email
        """
        self._init_driver()

        result = {
            'phone': None,
            'email': None,
            'name': name
        }

        try:
            if address:
                # Search by address
                # Clean address for URL
                addr_clean = re.sub(r'[^\w\s]', '', address)
                addr_clean = addr_clean.replace(' ', '-').lower()
                url = f'https://www.truepeoplesearch.com/resultaddress?streetaddress={addr_clean[:50]}'
            elif name:
                # Search by name
                name_clean = name.replace(' ', '-').lower()
                url = f'https://www.truepeoplesearch.com/results?name={name_clean}'
            else:
                return result

            logger.info(f"Searching TruePeopleSearch: {name or address}")

            self.driver.get(url)
            self._random_delay(3, 6)

            page_text = self.driver.find_element(By.TAG_NAME, 'body').text

            # Check for blocking
            if 'verify you are human' in page_text.lower() or 'captcha' in page_text.lower():
                logger.warning("TruePeopleSearch is blocking - CAPTCHA detected")
                return result

            # Extract phone numbers (format: (XXX) XXX-XXXX or XXX-XXX-XXXX)
            phone_patterns = [
                r'\((\d{3})\)\s*(\d{3})-(\d{4})',
                r'(\d{3})-(\d{3})-(\d{4})',
            ]

            for pattern in phone_patterns:
                matches = re.findall(pattern, page_text)
                if matches:
                    # Take first phone number found
                    if len(matches[0]) == 3:
                        phone = f"({matches[0][0]}) {matches[0][1]}-{matches[0][2]}"
                        result['phone'] = phone
                        logger.info(f"Found phone: {phone}")
                        break

            # Extract email
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails = re.findall(email_pattern, page_text)
            if emails:
                # Filter out site emails
                for email in emails:
                    if 'truepeoplesearch' not in email.lower() and 'example' not in email.lower():
                        result['email'] = email
                        logger.info(f"Found email: {email}")
                        break

            # Extract name if we searched by address
            if address and not name:
                # Look for name patterns at top of results
                name_match = re.search(r'^([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', page_text, re.MULTILINE)
                if name_match:
                    result['name'] = name_match.group(1)
                    logger.info(f"Found name: {result['name']}")

            return result

        except Exception as e:
            logger.error(f"TruePeopleSearch error: {e}")
            return result

    def skip_trace_address(self, address: str, county: str = 'Los Angeles') -> Dict:
        """
        Full skip trace for an address
        1. Look up owner from assessor
        2. Search for contact info
        Returns dict with owner_name, phone, email
        """
        result = {
            'owner_name': None,
            'phone': None,
            'email': None,
            'address': address
        }

        # Step 1: Get owner name from assessor
        owner = self.get_owner_from_assessor(address, county)
        if owner:
            result['owner_name'] = owner

        self._random_delay(2, 4)

        # Step 2: Search TruePeopleSearch
        # Try by address first (more reliable)
        tps_result = self.search_truepeoplesearch(address=address)

        if tps_result.get('phone'):
            result['phone'] = tps_result['phone']
        if tps_result.get('email'):
            result['email'] = tps_result['email']
        if tps_result.get('name') and not result['owner_name']:
            result['owner_name'] = tps_result['name']

        # If we have owner name but no phone, try searching by name
        if result['owner_name'] and not result['phone']:
            self._random_delay(2, 4)
            name_result = self.search_truepeoplesearch(name=result['owner_name'])
            if name_result.get('phone'):
                result['phone'] = name_result['phone']
            if name_result.get('email') and not result['email']:
                result['email'] = name_result['email']

        return result

    def skip_trace_batch(self, addresses: List[Dict], delay_between: int = 10) -> List[Dict]:
        """
        Skip trace multiple addresses with delays
        addresses: list of dicts with 'address' and 'county' keys
        """
        results = []

        try:
            self._init_driver()

            for i, addr_info in enumerate(addresses):
                address = addr_info.get('address', '')
                county = addr_info.get('county', 'Los Angeles')
                row = addr_info.get('row', i + 1)

                if not address:
                    continue

                logger.info(f"\n[{i+1}/{len(addresses)}] Skip tracing: {address}")

                result = self.skip_trace_address(address, county)
                result['row'] = row
                results.append(result)

                # Delay between searches to avoid detection
                if i < len(addresses) - 1:
                    delay = delay_between + random.randint(0, 5)
                    logger.info(f"Waiting {delay} seconds before next search...")
                    time.sleep(delay)

        finally:
            self._close_driver()

        return results

    def close(self):
        """Clean up"""
        self._close_driver()


def update_google_sheet(results: List[Dict]):
    """Update Google Sheet with skip trace results"""
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    SHEET_ID = '1me4hbzialZs06LGaG3U2P3CjixSakH46GSM_ZOwSApw'
    CREDS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')

    creds = service_account.Credentials.from_service_account_file(
        CREDS_FILE,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    service = build('sheets', 'v4', credentials=creds)

    updated = 0
    for result in results:
        row = result.get('row')
        if not row:
            continue

        updates = []

        # Column C = Owner Name
        if result.get('owner_name'):
            updates.append({
                'range': f'Sheet1!C{row}',
                'values': [[result['owner_name']]]
            })

        # Column D = Phone
        if result.get('phone'):
            updates.append({
                'range': f'Sheet1!D{row}',
                'values': [[result['phone']]]
            })

        # Column E = Email
        if result.get('email'):
            updates.append({
                'range': f'Sheet1!E{row}',
                'values': [[result['email']]]
            })

        if updates:
            body = {'data': updates, 'valueInputOption': 'USER_ENTERED'}
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=SHEET_ID,
                body=body
            ).execute()
            updated += 1
            logger.info(f"Updated row {row}")

    return updated


def main():
    import argparse
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    parser = argparse.ArgumentParser(description='Skip Trace Tool')
    parser.add_argument('--address', type=str, help='Single address to trace')
    parser.add_argument('--from-sheet', action='store_true', help='Trace addresses from Google Sheet')
    parser.add_argument('--limit', type=int, default=5, help='Max addresses to trace')
    parser.add_argument('--headless', action='store_true', default=True, help='Run browser in headless mode')
    parser.add_argument('--no-headless', action='store_true', help='Show browser window')
    parser.add_argument('--update-sheet', action='store_true', help='Update Google Sheet with results')
    args = parser.parse_args()

    headless = not args.no_headless

    tracer = SkipTracer(headless=headless)

    try:
        if args.address:
            # Single address
            print(f"\nSkip tracing: {args.address}")
            result = tracer.skip_trace_address(args.address)
            print(f"\nResults:")
            print(f"  Owner: {result.get('owner_name', 'Not found')}")
            print(f"  Phone: {result.get('phone', 'Not found')}")
            print(f"  Email: {result.get('email', 'Not found')}")

        elif args.from_sheet:
            # From Google Sheet
            SHEET_ID = '1me4hbzialZs06LGaG3U2P3CjixSakH46GSM_ZOwSApw'
            CREDS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')

            creds = service_account.Credentials.from_service_account_file(
                CREDS_FILE,
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
            service = build('sheets', 'v4', credentials=creds)

            result = service.spreadsheets().values().get(
                spreadsheetId=SHEET_ID,
                range='Sheet1!A:Q'
            ).execute()

            rows = result.get('values', [])

            # Find addresses without phone numbers
            addresses = []
            for i, row in enumerate(rows[1:], start=2):
                while len(row) < 10:
                    row.append('')

                phone = row[3] if len(row) > 3 else ''
                address = row[5] if len(row) > 5 else ''
                county = row[7] if len(row) > 7 else 'Los Angeles'

                # Skip if has phone or no address
                if phone and phone.strip():
                    continue
                if not address or 'test' in address.lower():
                    continue

                addresses.append({
                    'row': i,
                    'address': address,
                    'county': county
                })

                if len(addresses) >= args.limit:
                    break

            if not addresses:
                print("No addresses need skip tracing!")
                return

            print(f"\nFound {len(addresses)} addresses to skip trace")
            print("=" * 60)

            results = tracer.skip_trace_batch(addresses, delay_between=10)

            print("\n" + "=" * 60)
            print("SKIP TRACE RESULTS")
            print("=" * 60)

            for result in results:
                print(f"\nRow {result.get('row')}: {result.get('address', '')[:40]}")
                print(f"  Owner: {result.get('owner_name', 'Not found')}")
                print(f"  Phone: {result.get('phone', 'Not found')}")
                print(f"  Email: {result.get('email', 'Not found')}")

            if args.update_sheet:
                print("\nUpdating Google Sheet...")
                updated = update_google_sheet(results)
                print(f"Updated {updated} rows")

        else:
            parser.print_help()

    finally:
        tracer.close()


if __name__ == '__main__':
    main()
