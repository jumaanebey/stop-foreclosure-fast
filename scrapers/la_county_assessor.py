#!/usr/bin/env python3
"""
LA County Assessor Enrichment
Fetches property details from LA County Assessor portal given an APN
URL: https://portal.assessor.lacounty.gov/
"""

import re
from datetime import datetime
from typing import Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('LACountyAssessor')


class LACountyAssessorEnricher:
    """Enriches property data using LA County Assessor portal"""

    BASE_URL = "https://portal.assessor.lacounty.gov/"

    def __init__(self):
        self.driver = None
        self.rate_limit = 5.0  # Seconds between requests

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
            logger.error(f"Failed to initialize Chrome driver: {e}")
            raise

    def _close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def lookup_by_apn(self, apn: str) -> Optional[Dict]:
        """Look up property details by APN (Assessor Parcel Number)"""
        if not apn:
            return None

        # Clean APN format
        apn_clean = re.sub(r'[^\d]', '', apn)

        try:
            self._init_driver()
            self.driver.get(self.BASE_URL)

            # Wait for page to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(2)

            # Look for search input
            search_inputs = self.driver.find_elements(By.CSS_SELECTOR,
                "input[type='text'], input[type='search'], input[name*='search'], input[id*='search']")

            if search_inputs:
                search_input = search_inputs[0]
                search_input.clear()
                search_input.send_keys(apn_clean)
                search_input.send_keys(Keys.RETURN)
                time.sleep(3)

                # Parse results
                return self._parse_property_details()

        except Exception as e:
            logger.error(f"Error looking up APN {apn}: {e}")

        return None

    def lookup_by_address(self, address: str) -> Optional[Dict]:
        """Look up property details by address"""
        if not address:
            return None

        try:
            self._init_driver()
            self.driver.get(self.BASE_URL)

            # Wait for page to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(2)

            # Look for address search tab or input
            try:
                address_tabs = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "Address")
                if address_tabs:
                    address_tabs[0].click()
                    time.sleep(1)
            except:
                pass

            # Find search input
            search_inputs = self.driver.find_elements(By.CSS_SELECTOR,
                "input[type='text'], input[name*='address'], input[id*='address']")

            if search_inputs:
                search_input = search_inputs[0]
                search_input.clear()
                search_input.send_keys(address)
                search_input.send_keys(Keys.RETURN)
                time.sleep(3)

                # If multiple results, click first one
                try:
                    result_links = self.driver.find_elements(By.CSS_SELECTOR,
                        "a[href*='property'], .result-link, tr.clickable")
                    if result_links:
                        result_links[0].click()
                        time.sleep(2)
                except:
                    pass

                return self._parse_property_details()

        except Exception as e:
            logger.error(f"Error looking up address {address}: {e}")

        return None

    def _parse_property_details(self) -> Dict:
        """Parse property details from the current page"""
        details = {}

        try:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text

            # Extract APN
            apn_match = re.search(r'APN[:\s]*(\d{4}[-\s]?\d{3}[-\s]?\d{3})', page_text, re.IGNORECASE)
            if apn_match:
                details['apn'] = apn_match.group(1)

            # Extract property address
            addr_patterns = [
                r'Situs Address[:\s]*([^\n]+)',
                r'Property Address[:\s]*([^\n]+)',
                r'Site Address[:\s]*([^\n]+)'
            ]
            for pattern in addr_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details['property_address'] = match.group(1).strip()
                    break

            # Extract owner name
            owner_patterns = [
                r'Owner(?:\s*Name)?[:\s]*([^\n]+)',
                r'Property Owner[:\s]*([^\n]+)',
                r'Taxpayer[:\s]*([^\n]+)'
            ]
            for pattern in owner_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details['owner_name'] = match.group(1).strip()
                    break

            # Extract assessed value
            value_patterns = [
                r'Total Value[:\s]*\$?([\d,]+)',
                r'Assessed Value[:\s]*\$?([\d,]+)',
                r'Market Value[:\s]*\$?([\d,]+)'
            ]
            for pattern in value_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    value = match.group(1).replace(',', '')
                    details['assessed_value'] = int(value)
                    # Estimate market value (typically 50-80% of market)
                    details['estimated_value'] = f"${int(int(value) * 1.5):,}"
                    break

            # Extract property type
            type_patterns = [
                r'Property Type[:\s]*([^\n]+)',
                r'Use Code[:\s]*([^\n]+)',
                r'Land Use[:\s]*([^\n]+)'
            ]
            for pattern in type_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details['property_type'] = match.group(1).strip()
                    break

            # Extract square footage
            sqft_match = re.search(r'(?:Sq\.?\s*Ft\.?|Square Feet|Living Area)[:\s]*([\d,]+)', page_text, re.IGNORECASE)
            if sqft_match:
                details['square_feet'] = int(sqft_match.group(1).replace(',', ''))

            # Extract bedrooms/bathrooms
            bed_match = re.search(r'(\d+)\s*(?:Bed|BR|Bedroom)', page_text, re.IGNORECASE)
            if bed_match:
                details['bedrooms'] = int(bed_match.group(1))

            bath_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:Bath|BA|Bathroom)', page_text, re.IGNORECASE)
            if bath_match:
                details['bathrooms'] = float(bath_match.group(1))

            # Extract year built
            year_match = re.search(r'Year Built[:\s]*(\d{4})', page_text, re.IGNORECASE)
            if year_match:
                details['year_built'] = int(year_match.group(1))

            # Extract lot size
            lot_match = re.search(r'Lot Size[:\s]*([\d,\.]+)\s*(?:sq\.?\s*ft|acres)?', page_text, re.IGNORECASE)
            if lot_match:
                details['lot_size'] = lot_match.group(1)

            # Extract city from address
            if details.get('property_address'):
                city_match = re.search(r',\s*([A-Za-z\s]+),?\s*CA', details['property_address'])
                if city_match:
                    details['city'] = city_match.group(1).strip()

            details['county'] = 'Los Angeles'
            details['enrichment_date'] = datetime.now().strftime('%Y-%m-%d')

        except Exception as e:
            logger.error(f"Error parsing property details: {e}")

        return details

    def enrich_record(self, record: Dict) -> Dict:
        """Enrich a record with assessor data"""
        enriched = record.copy()

        # Try APN first
        if record.get('apn'):
            assessor_data = self.lookup_by_apn(record['apn'])
            if assessor_data:
                for key, value in assessor_data.items():
                    if not enriched.get(key):
                        enriched[key] = value
                return enriched

        # Fall back to address
        if record.get('property_address'):
            assessor_data = self.lookup_by_address(record['property_address'])
            if assessor_data:
                for key, value in assessor_data.items():
                    if not enriched.get(key):
                        enriched[key] = value

        return enriched

    def close(self):
        """Clean up resources"""
        self._close_driver()


def main():
    """Test the LA County Assessor enricher"""
    import argparse

    parser = argparse.ArgumentParser(description='LA County Assessor Lookup')
    parser.add_argument('--apn', type=str, help='APN to look up')
    parser.add_argument('--address', type=str, help='Address to look up')
    parser.add_argument('--test', action='store_true', help='Run test mode')
    args = parser.parse_args()

    enricher = LACountyAssessorEnricher()

    try:
        if args.test:
            print("Running LA County Assessor test...")
            # Test with a known LA County address
            result = enricher.lookup_by_address("111 N Hope St, Los Angeles, CA")
            if result:
                print("Found property:")
                for key, value in result.items():
                    print(f"  {key}: {value}")
            else:
                print("No results found")

        elif args.apn:
            print(f"Looking up APN: {args.apn}")
            result = enricher.lookup_by_apn(args.apn)
            if result:
                for key, value in result.items():
                    print(f"  {key}: {value}")

        elif args.address:
            print(f"Looking up address: {args.address}")
            result = enricher.lookup_by_address(args.address)
            if result:
                for key, value in result.items():
                    print(f"  {key}: {value}")

        else:
            print("Please provide --apn or --address to look up")

    finally:
        enricher.close()


if __name__ == '__main__':
    main()
