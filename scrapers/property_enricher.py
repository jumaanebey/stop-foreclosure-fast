#!/usr/bin/env python3
"""
Property Enricher

Enriches NOD records with property data from county assessor portals.
Combines data from:
- LA County Assessor: https://portal.assessor.lacounty.gov/
- Riverside County Assessor: https://www.rivcoassessor.org/

This module provides:
- Property address lookup from APN
- Estimated property value
- Owner name verification
- Mailing address for contact
- Property characteristics (beds, baths, sqft)

Usage:
    from property_enricher import PropertyEnricher

    enricher = PropertyEnricher()
    enriched_record = enricher.enrich(record)
    enricher.close()
"""

import re
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('PropertyEnricher')


class PropertyEnricher:
    """
    Enriches property records with assessor data.

    Supports LA County and Riverside County assessor portals.
    Uses Selenium for web scraping since these portals require
    JavaScript rendering.

    Attributes:
        LA_ASSESSOR_URL: LA County Assessor portal URL
        RIVERSIDE_ASSESSOR_URL: Riverside County Assessor portal URL
        driver: Selenium WebDriver instance
        rate_limit: Seconds between requests
    """

    # Assessor portal URLs
    LA_ASSESSOR_URL = "https://portal.assessor.lacounty.gov/"
    RIVERSIDE_ASSESSOR_URL = "https://www.rivcoassessor.org/property-search"

    # User agents for rotation
    USER_AGENTS = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    ]

    def __init__(self, rate_limit_seconds: float = 5.0):
        """
        Initialize the property enricher.

        Args:
            rate_limit_seconds: Minimum seconds between requests (default: 5.0)
        """
        self.rate_limit = rate_limit_seconds
        self.driver = None
        self.last_request_time = 0
        self._request_count = 0

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
            logger.info("Chrome WebDriver initialized for property enrichment")

        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            raise

    def _close_driver(self):
        """Close the WebDriver and clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.warning(f"Error closing driver: {e}")
            finally:
                self.driver = None

    def _rate_limit_wait(self):
        """Respect rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            wait_time = self.rate_limit - elapsed
            logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
            time.sleep(wait_time)
        self.last_request_time = time.time()

    def enrich(self, record: Dict) -> Dict:
        """
        Enrich a record with assessor data.

        Automatically detects county and routes to appropriate assessor.

        Args:
            record: Dictionary with at least 'county' and either 'apn' or 'property_address'

        Returns:
            Enriched record dictionary
        """
        county = record.get('county', '').lower()

        if 'los angeles' in county or 'la' in county:
            return self.enrich_la_county(record)
        elif 'riverside' in county:
            return self.enrich_riverside_county(record)
        else:
            logger.warning(f"Unsupported county for enrichment: {county}")
            return record

    def enrich_la_county(self, record: Dict) -> Dict:
        """
        Enrich record with LA County Assessor data.

        Args:
            record: Record dictionary with APN or address

        Returns:
            Enriched record
        """
        enriched = record.copy()

        try:
            self._init_driver()
            self._rate_limit_wait()

            # Try APN first (more reliable)
            if record.get('apn'):
                assessor_data = self._lookup_la_by_apn(record['apn'])
            elif record.get('property_address'):
                assessor_data = self._lookup_la_by_address(record['property_address'])
            else:
                logger.warning("No APN or address available for LA County lookup")
                return enriched

            if assessor_data:
                # Merge assessor data into record (don't overwrite existing values)
                for key, value in assessor_data.items():
                    if not enriched.get(key) and value:
                        enriched[key] = value

                enriched['enrichment_date'] = datetime.now().strftime('%Y-%m-%d')
                enriched['enrichment_source'] = 'LA County Assessor'
                logger.info(f"Enriched LA County record: {enriched.get('property_address', 'Unknown')}")

        except Exception as e:
            logger.error(f"Error enriching LA County record: {e}")

        return enriched

    def enrich_riverside_county(self, record: Dict) -> Dict:
        """
        Enrich record with Riverside County Assessor data.

        Args:
            record: Record dictionary with APN or address

        Returns:
            Enriched record
        """
        enriched = record.copy()

        try:
            self._init_driver()
            self._rate_limit_wait()

            # Try APN first
            if record.get('apn'):
                assessor_data = self._lookup_riverside_by_apn(record['apn'])
            elif record.get('property_address'):
                assessor_data = self._lookup_riverside_by_address(record['property_address'])
            else:
                logger.warning("No APN or address available for Riverside County lookup")
                return enriched

            if assessor_data:
                for key, value in assessor_data.items():
                    if not enriched.get(key) and value:
                        enriched[key] = value

                enriched['enrichment_date'] = datetime.now().strftime('%Y-%m-%d')
                enriched['enrichment_source'] = 'Riverside County Assessor'
                logger.info(f"Enriched Riverside County record: {enriched.get('property_address', 'Unknown')}")

        except Exception as e:
            logger.error(f"Error enriching Riverside County record: {e}")

        return enriched

    def _lookup_la_by_apn(self, apn: str) -> Optional[Dict]:
        """
        Look up property by APN in LA County Assessor.

        Args:
            apn: Assessor Parcel Number

        Returns:
            Dictionary with property details or None
        """
        # Clean APN format
        apn_clean = re.sub(r'[^\d]', '', apn)

        try:
            self.driver.get(self.LA_ASSESSOR_URL)
            time.sleep(3)

            # Wait for page load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Find search input
            search_selectors = [
                "input[type='text']",
                "input[type='search']",
                "input[name*='search']",
                "input[id*='search']",
                "#searchInput"
            ]

            for selector in search_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        search_input = elements[0]
                        search_input.clear()
                        search_input.send_keys(apn_clean)
                        search_input.send_keys(Keys.RETURN)
                        time.sleep(4)
                        return self._parse_la_property_details()
                except Exception:
                    continue

        except Exception as e:
            logger.error(f"Error looking up LA County APN {apn}: {e}")

        return None

    def _lookup_la_by_address(self, address: str) -> Optional[Dict]:
        """
        Look up property by address in LA County Assessor.

        Args:
            address: Property address

        Returns:
            Dictionary with property details or None
        """
        try:
            self.driver.get(self.LA_ASSESSOR_URL)
            time.sleep(3)

            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Try to find address search tab
            try:
                address_tabs = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "Address")
                if address_tabs:
                    address_tabs[0].click()
                    time.sleep(2)
            except Exception:
                pass

            # Find and fill address input
            search_selectors = [
                "input[type='text']",
                "input[name*='address']",
                "input[id*='address']",
                "#addressInput"
            ]

            for selector in search_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        search_input = elements[0]
                        search_input.clear()
                        search_input.send_keys(address)
                        search_input.send_keys(Keys.RETURN)
                        time.sleep(4)

                        # Click first result if multiple
                        try:
                            result_links = self.driver.find_elements(By.CSS_SELECTOR,
                                "a[href*='property'], .result-link, tr.clickable, .property-result")
                            if result_links:
                                result_links[0].click()
                                time.sleep(3)
                        except Exception:
                            pass

                        return self._parse_la_property_details()
                except Exception:
                    continue

        except Exception as e:
            logger.error(f"Error looking up LA County address {address}: {e}")

        return None

    def _parse_la_property_details(self) -> Dict:
        """
        Parse property details from LA County Assessor page.

        Returns:
            Dictionary with extracted property information
        """
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
                r'Site Address[:\s]*([^\n]+)',
                r'Location[:\s]*([^\n]+)'
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
                r'Taxpayer[:\s]*([^\n]+)',
                r'Owner 1[:\s]*([^\n]+)'
            ]
            for pattern in owner_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    owner_text = match.group(1).strip()
                    # Clean up owner name
                    if owner_text and len(owner_text) > 2:
                        details['owner_name'] = owner_text
                        break

            # Extract mailing address
            mail_patterns = [
                r'Mailing Address[:\s]*([^\n]+(?:\n[^\n]+)?)',
                r'Mail To[:\s]*([^\n]+)',
            ]
            for pattern in mail_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details['mailing_address'] = match.group(1).strip().replace('\n', ', ')
                    break

            # Extract assessed/estimated value
            value_patterns = [
                r'Total Value[:\s]*\$?([\d,]+)',
                r'Assessed Value[:\s]*\$?([\d,]+)',
                r'Market Value[:\s]*\$?([\d,]+)',
                r'Net Value[:\s]*\$?([\d,]+)'
            ]
            for pattern in value_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    value = int(match.group(1).replace(',', ''))
                    details['assessed_value'] = value
                    # Estimate market value (assessed is typically 50-80% of market)
                    details['estimated_value'] = f"${int(value * 1.5):,}"
                    break

            # Extract property characteristics
            # Square footage
            sqft_match = re.search(r'(?:Sq\.?\s*Ft\.?|Square Feet|Living Area|Bldg Area)[:\s]*([\d,]+)', page_text, re.IGNORECASE)
            if sqft_match:
                details['square_feet'] = int(sqft_match.group(1).replace(',', ''))

            # Bedrooms
            bed_match = re.search(r'(\d+)\s*(?:Bed|BR|Bedroom)', page_text, re.IGNORECASE)
            if bed_match:
                details['bedrooms'] = int(bed_match.group(1))

            # Bathrooms
            bath_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:Bath|BA|Bathroom)', page_text, re.IGNORECASE)
            if bath_match:
                details['bathrooms'] = float(bath_match.group(1))

            # Year built
            year_match = re.search(r'Year Built[:\s]*(\d{4})', page_text, re.IGNORECASE)
            if year_match:
                details['year_built'] = int(year_match.group(1))

            # Lot size
            lot_match = re.search(r'Lot Size[:\s]*([\d,\.]+)\s*(?:sq\.?\s*ft|acres)?', page_text, re.IGNORECASE)
            if lot_match:
                details['lot_size'] = lot_match.group(1)

            # Property type
            type_patterns = [
                r'Property Type[:\s]*([^\n]+)',
                r'Use Code[:\s]*([^\n]+)',
                r'Land Use[:\s]*([^\n]+)',
                r'Property Class[:\s]*([^\n]+)'
            ]
            for pattern in type_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details['property_type'] = match.group(1).strip()
                    break

            # Extract city from address if available
            if details.get('property_address'):
                city_match = re.search(r',\s*([A-Za-z\s]+),?\s*CA', details['property_address'])
                if city_match:
                    details['city'] = city_match.group(1).strip()

            details['county'] = 'Los Angeles'

        except Exception as e:
            logger.error(f"Error parsing LA property details: {e}")

        return details

    def _lookup_riverside_by_apn(self, apn: str) -> Optional[Dict]:
        """
        Look up property by APN in Riverside County Assessor.

        Args:
            apn: Assessor Parcel Number

        Returns:
            Dictionary with property details or None
        """
        # Clean APN format
        apn_clean = re.sub(r'[^\d]', '', apn)

        try:
            self.driver.get(self.RIVERSIDE_ASSESSOR_URL)
            time.sleep(3)

            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Find APN search input
            search_selectors = [
                "input[name*='apn']",
                "input[id*='apn']",
                "input[name*='parcel']",
                "input[type='text']",
                "#apnInput"
            ]

            for selector in search_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        search_input = elements[0]
                        search_input.clear()
                        search_input.send_keys(apn_clean)
                        search_input.send_keys(Keys.RETURN)
                        time.sleep(4)
                        return self._parse_riverside_property_details()
                except Exception:
                    continue

        except Exception as e:
            logger.error(f"Error looking up Riverside County APN {apn}: {e}")

        return None

    def _lookup_riverside_by_address(self, address: str) -> Optional[Dict]:
        """
        Look up property by address in Riverside County Assessor.

        Args:
            address: Property address

        Returns:
            Dictionary with property details or None
        """
        try:
            self.driver.get(self.RIVERSIDE_ASSESSOR_URL)
            time.sleep(3)

            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Try address search
            search_selectors = [
                "input[name*='address']",
                "input[id*='address']",
                "input[type='text']",
                "#addressInput"
            ]

            for selector in search_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        search_input = elements[0]
                        search_input.clear()
                        search_input.send_keys(address)
                        search_input.send_keys(Keys.RETURN)
                        time.sleep(4)

                        # Click first result
                        try:
                            result_links = self.driver.find_elements(By.CSS_SELECTOR,
                                "a[href*='property'], .result-link, tr.clickable")
                            if result_links:
                                result_links[0].click()
                                time.sleep(3)
                        except Exception:
                            pass

                        return self._parse_riverside_property_details()
                except Exception:
                    continue

        except Exception as e:
            logger.error(f"Error looking up Riverside County address {address}: {e}")

        return None

    def _parse_riverside_property_details(self) -> Dict:
        """
        Parse property details from Riverside County Assessor page.

        Returns:
            Dictionary with extracted property information
        """
        details = {}

        try:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text

            # Extract APN (Riverside format: XXX-XXX-XXX)
            apn_match = re.search(r'APN[:\s]*(\d{3}[-\s]?\d{3}[-\s]?\d{3})', page_text, re.IGNORECASE)
            if not apn_match:
                apn_match = re.search(r'Parcel[:\s#]*(\d{3}[-\s]?\d{3}[-\s]?\d{3})', page_text, re.IGNORECASE)
            if apn_match:
                details['apn'] = apn_match.group(1)

            # Extract property address
            addr_patterns = [
                r'Situs[:\s]*([^\n]+)',
                r'Property Address[:\s]*([^\n]+)',
                r'Location[:\s]*([^\n]+)'
            ]
            for pattern in addr_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details['property_address'] = match.group(1).strip()
                    break

            # Extract owner name
            owner_patterns = [
                r'Owner[:\s]*([^\n]+)',
                r'Taxpayer[:\s]*([^\n]+)',
            ]
            for pattern in owner_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details['owner_name'] = match.group(1).strip()
                    break

            # Extract mailing address
            mail_match = re.search(r'Mailing[:\s]*([^\n]+)', page_text, re.IGNORECASE)
            if mail_match:
                details['mailing_address'] = mail_match.group(1).strip()

            # Extract assessed value
            value_patterns = [
                r'Total Value[:\s]*\$?([\d,]+)',
                r'Net Value[:\s]*\$?([\d,]+)',
                r'Assessed[:\s]*\$?([\d,]+)'
            ]
            for pattern in value_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    value = int(match.group(1).replace(',', ''))
                    details['assessed_value'] = value
                    details['estimated_value'] = f"${int(value * 1.5):,}"
                    break

            # Extract city
            if details.get('property_address'):
                city_match = re.search(r',\s*([A-Za-z\s]+),?\s*CA', details['property_address'])
                if city_match:
                    details['city'] = city_match.group(1).strip()

            details['county'] = 'Riverside'

        except Exception as e:
            logger.error(f"Error parsing Riverside property details: {e}")

        return details

    def enrich_batch(self, records: List[Dict], max_records: int = None) -> List[Dict]:
        """
        Enrich a batch of records.

        Args:
            records: List of record dictionaries
            max_records: Maximum number of records to enrich (None for all)

        Returns:
            List of enriched records
        """
        enriched = []
        count = 0

        try:
            self._init_driver()

            for record in records:
                if max_records and count >= max_records:
                    break

                try:
                    enriched_record = self.enrich(record)
                    enriched.append(enriched_record)
                    count += 1
                    logger.info(f"Enriched {count}/{len(records)}: {enriched_record.get('property_address', 'Unknown')}")
                except Exception as e:
                    logger.error(f"Error enriching record: {e}")
                    enriched.append(record)  # Keep original if enrichment fails

        finally:
            self._close_driver()

        logger.info(f"Enriched {count} of {len(records)} records")
        return enriched

    def close(self):
        """Clean up resources."""
        self._close_driver()


def main():
    """Test the property enricher."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description='Property Enricher')
    parser.add_argument('--apn', type=str, help='APN to look up')
    parser.add_argument('--address', type=str, help='Address to look up')
    parser.add_argument('--county', type=str, choices=['la', 'riverside'], default='la',
                        help='County for lookup (default: la)')
    parser.add_argument('--test', action='store_true', help='Run test mode')
    args = parser.parse_args()

    print("=" * 60)
    print("PROPERTY ENRICHER")
    print("=" * 60)

    enricher = PropertyEnricher()

    try:
        if args.test:
            print("\nRunning in TEST mode...")
            # Test with a sample record
            test_record = {
                'county': 'Los Angeles' if args.county == 'la' else 'Riverside',
                'apn': args.apn or '',
                'property_address': args.address or '111 N Hope St, Los Angeles, CA'
            }
            print(f"Test record: {test_record}")
            result = enricher.enrich(test_record)

        elif args.apn:
            print(f"\nLooking up APN: {args.apn}")
            record = {'county': 'Los Angeles' if args.county == 'la' else 'Riverside', 'apn': args.apn}
            result = enricher.enrich(record)

        elif args.address:
            print(f"\nLooking up address: {args.address}")
            record = {'county': 'Los Angeles' if args.county == 'la' else 'Riverside', 'property_address': args.address}
            result = enricher.enrich(record)

        else:
            print("\nPlease provide --apn or --address to look up")
            return

        print("\nResult:")
        for key, value in result.items():
            if value:
                print(f"  {key}: {value}")

    finally:
        enricher.close()

    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
