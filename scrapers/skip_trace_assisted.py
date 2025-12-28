#!/usr/bin/env python3
"""
Semi-Automated Skip Tracer
Opens browser for you to handle CAPTCHAs, then extracts data
"""

import os
import sys
import re
import time
import logging
from typing import Dict, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from google.oauth2 import service_account
from googleapiclient.discovery import build

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SkipTrace')

SHEET_ID = '1me4hbzialZs06LGaG3U2P3CjixSakH46GSM_ZOwSApw'
CREDS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')


class AssistedSkipTracer:
    """Semi-automated skip tracer - you handle CAPTCHAs, script extracts data"""

    def __init__(self):
        self.driver = None
        self.service = None
        self._init_sheets()

    def _init_sheets(self):
        """Initialize Google Sheets API"""
        creds = service_account.Credentials.from_service_account_file(
            CREDS_FILE,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        self.service = build('sheets', 'v4', credentials=creds)

    def _init_browser(self):
        """Open Chrome browser (visible, not headless)"""
        if self.driver:
            return

        options = Options()
        # NOT headless - user needs to see and interact
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])

        from webdriver_manager.chrome import ChromeDriverManager
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

    def get_addresses_to_trace(self, limit: int = 10) -> List[Dict]:
        """Get addresses from sheet that need phone numbers"""
        result = self.service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range='Sheet1!A:Q'
        ).execute()

        rows = result.get('values', [])
        addresses = []

        for i, row in enumerate(rows[1:], start=2):
            while len(row) < 10:
                row.append('')

            phone = row[3] if len(row) > 3 else ''
            address = row[5] if len(row) > 5 else ''
            county = row[7] if len(row) > 7 else 'Los Angeles'

            if phone and phone.strip():
                continue
            if not address or 'test' in address.lower() or len(address) < 10:
                continue

            addresses.append({
                'row': i,
                'address': address,
                'county': county
            })

            if len(addresses) >= limit:
                break

        return addresses

    def extract_from_page(self) -> Dict:
        """Extract contact info from current page"""
        result = {'name': None, 'phone': None, 'email': None}

        try:
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text

            # Extract phone (format: (XXX) XXX-XXXX)
            phone_match = re.search(r'\((\d{3})\)\s*(\d{3})-(\d{4})', page_text)
            if phone_match:
                result['phone'] = f"({phone_match.group(1)}) {phone_match.group(2)}-{phone_match.group(3)}"

            # Extract email
            email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_text)
            if email_match:
                email = email_match.group(0)
                if 'truepeoplesearch' not in email.lower():
                    result['email'] = email

            # Extract name (look for pattern at top of results)
            # Usually format: "FirstName LastName" or "FirstName MiddleInitial LastName"
            lines = page_text.split('\n')
            for line in lines[:20]:
                line = line.strip()
                # Skip obvious non-name lines
                if any(x in line.lower() for x in ['search', 'address', 'phone', 'email', 'results', 'truepeoplesearch']):
                    continue
                # Match name pattern (2-3 capitalized words)
                if re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+(\s+[A-Z][a-z]+)?$', line):
                    result['name'] = line
                    break

        except Exception as e:
            logger.error(f"Extract error: {e}")

        return result

    def update_sheet_row(self, row: int, name: str = None, phone: str = None, email: str = None):
        """Update a single row in the sheet"""
        updates = []

        if name:
            updates.append({'range': f'Sheet1!C{row}', 'values': [[name]]})
        if phone:
            updates.append({'range': f'Sheet1!D{row}', 'values': [[phone]]})
        if email:
            updates.append({'range': f'Sheet1!E{row}', 'values': [[email]]})

        if updates:
            body = {'data': updates, 'valueInputOption': 'USER_ENTERED'}
            self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=SHEET_ID,
                body=body
            ).execute()
            return True
        return False

    def run_interactive(self):
        """Interactive skip tracing session"""
        print("=" * 60)
        print("SEMI-AUTOMATED SKIP TRACER")
        print("=" * 60)
        print()
        print("How it works:")
        print("1. Browser opens to TruePeopleSearch")
        print("2. YOU complete any CAPTCHA that appears")
        print("3. Script extracts the contact info")
        print("4. Data is saved to your Google Sheet")
        print()

        addresses = self.get_addresses_to_trace(limit=20)

        if not addresses:
            print("All leads already have phone numbers!")
            return

        print(f"Found {len(addresses)} addresses to skip trace")
        print()

        self._init_browser()

        for i, addr_info in enumerate(addresses):
            row = addr_info['row']
            address = addr_info['address']

            print(f"\n[{i+1}/{len(addresses)}] Row {row}: {address[:50]}")
            print("-" * 50)

            # Build search URL for address
            addr_parts = address.replace(',', ' ').split()
            street = ' '.join(addr_parts[:4])  # First 4 words usually street address
            city_state = ' '.join(addr_parts[4:]) if len(addr_parts) > 4 else ''

            url = f'https://www.truepeoplesearch.com/resultaddress?streetaddress={street.replace(" ", "+")}'
            if city_state:
                url += f'&citystatezip={city_state.replace(" ", "+")}'

            print(f"Opening: {url[:80]}...")
            self.driver.get(url)

            print()
            print(">>> Complete any CAPTCHA in the browser <<<")
            print(">>> Then press ENTER to extract data <<<")
            print(">>> Or type 'skip' to skip this address <<<")
            print(">>> Or type 'quit' to stop <<<")
            print()

            user_input = input("> ").strip().lower()

            if user_input == 'quit':
                print("Stopping...")
                break
            elif user_input == 'skip':
                print("Skipped")
                continue

            # Extract data from page
            data = self.extract_from_page()

            print(f"  Found: Name={data.get('name', 'N/A')}, Phone={data.get('phone', 'N/A')}, Email={data.get('email', 'N/A')}")

            if data.get('phone') or data.get('email') or data.get('name'):
                # Ask to confirm
                save = input("  Save to Google Sheet? [Y/n]: ").strip().lower()
                if save != 'n':
                    self.update_sheet_row(row, data.get('name'), data.get('phone'), data.get('email'))
                    print("  ✓ Saved!")
            else:
                # Let user manually enter
                print("  No data found. Enter manually:")
                name = input("  Owner Name: ").strip() or None
                phone = input("  Phone: ").strip() or None
                email = input("  Email: ").strip() or None

                if name or phone or email:
                    self.update_sheet_row(row, name, phone, email)
                    print("  ✓ Saved!")

            time.sleep(1)

        print("\n" + "=" * 60)
        print("Skip tracing complete!")
        print(f"Sheet: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
        print("=" * 60)

        self.driver.quit()


def main():
    tracer = AssistedSkipTracer()
    tracer.run_interactive()


if __name__ == '__main__':
    main()
