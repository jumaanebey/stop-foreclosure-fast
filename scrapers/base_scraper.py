#!/usr/bin/env python3
"""
Base Scraper - Common utilities for all county scrapers
"""

import os
import time
import logging
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class BaseScraper(ABC):
    """Abstract base class for county record scrapers"""

    def __init__(self, county_name: str, rate_limit_seconds: float = 2.0):
        self.county_name = county_name
        self.rate_limit = rate_limit_seconds
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.logger = logging.getLogger(f'{county_name}Scraper')
        self.last_request_time = 0

    def _rate_limit_wait(self):
        """Respect rate limiting between requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()

    def _make_request(self, url: str, method: str = 'GET', **kwargs) -> requests.Response:
        """Make HTTP request with rate limiting and retry logic"""
        self._rate_limit_wait()

        max_retries = 3
        for attempt in range(max_retries):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, timeout=30, **kwargs)
                else:
                    response = self.session.post(url, timeout=30, **kwargs)

                response.raise_for_status()
                return response

            except requests.RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise

    def _parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content"""
        return BeautifulSoup(html, 'lxml')

    @abstractmethod
    def search_nod_records(self, date_from: datetime, date_to: datetime) -> list:
        """Search for Notice of Default records in date range"""
        pass

    @abstractmethod
    def parse_record(self, record_data) -> dict:
        """Parse a single record into standardized format"""
        pass

    def collect_records(self, days_back: int = 7) -> list:
        """Collect NOD records from the last N days"""
        date_to = datetime.now()
        date_from = date_to - timedelta(days=days_back)

        self.logger.info(f"Collecting {self.county_name} NOD records from {date_from.strftime('%Y-%m-%d')} to {date_to.strftime('%Y-%m-%d')}")

        raw_records = self.search_nod_records(date_from, date_to)

        parsed_records = []
        for record in raw_records:
            try:
                parsed = self.parse_record(record)
                parsed['county'] = self.county_name
                parsed['collected_date'] = datetime.now().strftime('%Y-%m-%d')
                parsed_records.append(parsed)
            except Exception as e:
                self.logger.error(f"Error parsing record: {e}")
                continue

        self.logger.info(f"Collected {len(parsed_records)} records from {self.county_name}")
        return parsed_records


class RecordStandardizer:
    """Standardize records from different sources into common format"""

    STANDARD_FIELDS = [
        'lead_id',
        'date_found',
        'recording_date',
        'days_since_nod',
        'owner_name',
        'phone',
        'email',
        'property_address',
        'city',
        'county',
        'apn',
        'estimated_value',
        'mortgage_balance',
        'equity',
        'lender',
        'trustee',
        'auction_date',
        'days_to_auction',
        'stage',
        'status',
        'lead_score',
        'notes',
        'source'
    ]

    @staticmethod
    def standardize(record: dict) -> dict:
        """Convert raw record to standard format"""
        standardized = {field: '' for field in RecordStandardizer.STANDARD_FIELDS}

        # Map common field variations
        field_mappings = {
            'owner_name': ['grantor', 'owner', 'trustor', 'property_owner'],
            'lender': ['grantee', 'beneficiary', 'lender_name'],
            'property_address': ['address', 'situs_address', 'site_address'],
            'recording_date': ['record_date', 'file_date', 'filed_date'],
            'apn': ['parcel_number', 'assessor_parcel', 'ain'],
        }

        for standard_field, alternatives in field_mappings.items():
            if record.get(standard_field):
                standardized[standard_field] = record[standard_field]
            else:
                for alt in alternatives:
                    if record.get(alt):
                        standardized[standard_field] = record[alt]
                        break

        # Copy any remaining fields that match standard names
        for field in RecordStandardizer.STANDARD_FIELDS:
            if record.get(field) and not standardized.get(field):
                standardized[field] = record[field]

        # Calculate days since NOD
        if standardized.get('recording_date'):
            try:
                rec_date = datetime.strptime(standardized['recording_date'], '%Y-%m-%d')
                standardized['days_since_nod'] = (datetime.now() - rec_date).days
            except:
                pass

        # Calculate days to auction
        if standardized.get('auction_date'):
            try:
                auc_date = datetime.strptime(standardized['auction_date'], '%Y-%m-%d')
                standardized['days_to_auction'] = (auc_date - datetime.now()).days
            except:
                pass

        # Set defaults
        standardized['date_found'] = standardized.get('date_found') or datetime.now().strftime('%Y-%m-%d')
        standardized['status'] = standardized.get('status') or 'New'
        standardized['stage'] = standardized.get('stage') or 'NOD'

        return standardized


def generate_lead_id(record: dict) -> str:
    """Generate unique lead ID from record data"""
    import hashlib

    # Use APN + recording date as unique identifier
    unique_str = f"{record.get('apn', '')}-{record.get('recording_date', '')}-{record.get('county', '')}"
    return hashlib.md5(unique_str.encode()).hexdigest()[:12].upper()
