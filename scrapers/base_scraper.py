#!/usr/bin/env python3
"""
Base Scraper - Common utilities for all county scrapers

This module provides:
- BaseScraper: Abstract base class with HTTP session management, rate limiting, retries
- RecordStandardizer: Normalizes records from different sources to common format
- GoogleSheetsManager: Integration with Google Sheets for lead storage
- Utility functions for data processing

Configuration:
- Google Sheet ID: 1me4hbzialZs06LGaG3U2P3CjixSakH46GSM_ZOwSApw
"""

import os
import time
import logging
import hashlib
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

import requests
from bs4 import BeautifulSoup

# Optional imports for Google Sheets
try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/nod_scraper.log', mode='a')
    ]
)

class BaseScraper(ABC):
    """
    Abstract base class for county record scrapers.

    Provides:
    - HTTP session management with automatic retries
    - Rate limiting to avoid being blocked
    - Logging infrastructure
    - Common parsing utilities

    Subclasses must implement:
    - search_nod_records(date_from, date_to) -> list
    - parse_record(record_data) -> dict
    """

    # Default User-Agent strings to rotate
    USER_AGENTS = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    ]

    def __init__(self, county_name: str, rate_limit_seconds: float = 2.0, max_retries: int = 3):
        """
        Initialize the base scraper.

        Args:
            county_name: Name of the county (used for logging and identification)
            rate_limit_seconds: Minimum seconds between requests (default: 2.0)
            max_retries: Maximum number of retry attempts for failed requests
        """
        self.county_name = county_name
        self.rate_limit = rate_limit_seconds
        self.max_retries = max_retries
        self.logger = logging.getLogger(f'{county_name}Scraper')
        self.last_request_time = 0
        self._request_count = 0

        # Create session with retry strategy
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry strategy and proper headers."""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,  # Exponential backoff: 1s, 2s, 4s
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set default headers
        session.headers.update({
            'User-Agent': self.USER_AGENTS[0],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

        return session

    def _rotate_user_agent(self):
        """Rotate User-Agent to avoid detection."""
        import random
        self.session.headers['User-Agent'] = random.choice(self.USER_AGENTS)

    def _rate_limit_wait(self):
        """Respect rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            wait_time = self.rate_limit - elapsed
            self.logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
            time.sleep(wait_time)
        self.last_request_time = time.time()

    def _make_request(self, url: str, method: str = 'GET', **kwargs) -> requests.Response:
        """
        Make HTTP request with rate limiting and retry logic.

        Args:
            url: The URL to request
            method: HTTP method (GET or POST)
            **kwargs: Additional arguments passed to requests

        Returns:
            requests.Response object

        Raises:
            requests.RequestException on failure after all retries
        """
        self._rate_limit_wait()
        self._request_count += 1

        # Rotate User-Agent every 10 requests
        if self._request_count % 10 == 0:
            self._rotate_user_agent()

        # Set default timeout if not provided
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 30

        try:
            if method.upper() == 'GET':
                response = self.session.get(url, **kwargs)
            elif method.upper() == 'POST':
                response = self.session.post(url, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            self.logger.debug(f"Request successful: {url} (status: {response.status_code})")
            return response

        except requests.RequestException as e:
            self.logger.error(f"Request failed: {url} - {e}")
            raise

    def _parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML content using BeautifulSoup.

        Args:
            html: Raw HTML string

        Returns:
            BeautifulSoup object for parsing
        """
        # Try lxml first, fall back to html.parser
        try:
            return BeautifulSoup(html, 'lxml')
        except Exception:
            return BeautifulSoup(html, 'html.parser')

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
    """
    Generate unique lead ID from record data.

    Uses APN + recording date + county to create a deterministic ID.

    Args:
        record: Dictionary containing record data

    Returns:
        12-character uppercase hex string
    """
    # Use APN + recording date as unique identifier
    unique_str = f"{record.get('apn', '')}-{record.get('recording_date', '')}-{record.get('county', '')}"
    return hashlib.md5(unique_str.encode()).hexdigest()[:12].upper()


class GoogleSheetsManager:
    """
    Manager for Google Sheets integration.

    Handles authentication, reading, writing, and deduplication of leads
    in the foreclosure tracking spreadsheet.

    Configuration:
        - Sheet ID: 1me4hbzialZs06LGaG3U2P3CjixSakH46GSM_ZOwSApw
        - Requires credentials.json service account file in project root
    """

    # Default Google Sheet ID for foreclosure leads
    DEFAULT_SHEET_ID = '1me4hbzialZs06LGaG3U2P3CjixSakH46GSM_ZOwSApw'

    # Column mapping for the leads spreadsheet
    COLUMNS = [
        'lead_id',              # A - Unique identifier
        'date_found',           # B - Date lead was discovered
        'recording_date',       # C - NOD recording date
        'days_since_nod',       # D - Calculated urgency
        'owner_name',           # E - Property owner / trustor
        'phone',                # F - Contact phone
        'email',                # G - Contact email
        'property_address',     # H - Full property address
        'city',                 # I - City
        'county',               # J - County name
        'apn',                  # K - Assessor Parcel Number
        'estimated_value',      # L - Estimated property value
        'mortgage_balance',     # M - Outstanding mortgage
        'equity',               # N - Calculated equity
        'lender',               # O - Lender / beneficiary
        'trustee',              # P - Trustee
        'auction_date',         # Q - Scheduled auction date
        'days_to_auction',      # R - Days until auction
        'stage',                # S - NOD / NTS / Auction / Sold
        'status',               # T - New / Contacted / Closed
        'lead_score',           # U - Priority ranking
        'notes',                # V - Additional notes
        'source',               # W - Data source
    ]

    def __init__(self, sheet_id: str = None, credentials_path: str = None):
        """
        Initialize Google Sheets manager.

        Args:
            sheet_id: Google Sheet ID (uses default if not provided)
            credentials_path: Path to service account credentials JSON
        """
        self.sheet_id = sheet_id or self.DEFAULT_SHEET_ID
        self.logger = logging.getLogger('GoogleSheetsManager')

        # Find credentials file
        if credentials_path:
            self.credentials_path = credentials_path
        else:
            # Look in common locations
            possible_paths = [
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json'),
                os.path.expanduser('~/.config/gspread/credentials.json'),
                'credentials.json',
            ]
            self.credentials_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    self.credentials_path = path
                    break

        self.client = None
        self.sheet = None
        self.worksheet = None

    def connect(self) -> bool:
        """
        Connect to Google Sheets API.

        Returns:
            True if connection successful, False otherwise
        """
        if not GSPREAD_AVAILABLE:
            self.logger.error("gspread library not available. Install with: pip install gspread oauth2client")
            return False

        if not self.credentials_path or not os.path.exists(self.credentials_path):
            self.logger.error(f"Credentials file not found: {self.credentials_path}")
            return False

        try:
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_path, scope)
            self.client = gspread.authorize(creds)
            self.sheet = self.client.open_by_key(self.sheet_id)
            self.worksheet = self.sheet.sheet1  # Use first worksheet
            self.logger.info(f"Connected to Google Sheet: {self.sheet.title}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to connect to Google Sheets: {e}")
            return False

    def get_all_records(self) -> List[Dict]:
        """
        Get all existing records from the sheet.

        Returns:
            List of dictionaries with record data
        """
        if not self.worksheet:
            if not self.connect():
                return []

        try:
            # Get all values including header
            all_values = self.worksheet.get_all_values()

            if len(all_values) <= 1:
                return []

            # Parse rows into dictionaries
            records = []
            for i, row in enumerate(all_values[1:], start=2):  # Skip header
                record = {'_row_number': i}
                for j, col in enumerate(self.COLUMNS):
                    record[col] = row[j] if j < len(row) else ''
                records.append(record)

            self.logger.info(f"Retrieved {len(records)} existing records")
            return records

        except Exception as e:
            self.logger.error(f"Error getting records: {e}")
            return []

    def is_duplicate(self, record: Dict, existing_records: List[Dict] = None) -> bool:
        """
        Check if a record already exists (by APN + recording date OR address).

        Args:
            record: New record to check
            existing_records: Optional list of existing records (fetched if not provided)

        Returns:
            True if duplicate found, False otherwise
        """
        if existing_records is None:
            existing_records = self.get_all_records()

        new_apn = record.get('apn', '').strip()
        new_date = record.get('recording_date', '').strip()
        new_addr = record.get('property_address', '').lower().strip()[:30]

        for existing in existing_records:
            # Check by APN + recording date (most reliable)
            if new_apn and new_apn == existing.get('apn', '').strip():
                if new_date == existing.get('recording_date', '').strip():
                    return True

            # Fallback: check by address similarity
            if new_addr:
                existing_addr = existing.get('property_address', '').lower().strip()[:30]
                if new_addr == existing_addr:
                    return True

        return False

    def add_record(self, record: Dict) -> bool:
        """
        Add a single record to the sheet.

        Args:
            record: Dictionary with record data

        Returns:
            True if successful, False otherwise
        """
        if not self.worksheet:
            if not self.connect():
                return False

        try:
            # Build row from record
            row = []
            for col in self.COLUMNS:
                value = record.get(col, '')
                if value is None:
                    value = ''
                elif isinstance(value, (int, float)):
                    value = str(value)
                row.append(str(value))

            # Append to sheet
            self.worksheet.append_row(row, value_input_option='USER_ENTERED')
            self.logger.debug(f"Added record: {record.get('property_address', 'Unknown')}")
            return True

        except Exception as e:
            self.logger.error(f"Error adding record: {e}")
            return False

    def add_records_batch(self, records: List[Dict]) -> Dict:
        """
        Add multiple records in a single batch operation.

        Args:
            records: List of record dictionaries

        Returns:
            Dictionary with stats: {added, duplicates, errors}
        """
        if not self.worksheet:
            if not self.connect():
                return {'added': 0, 'duplicates': 0, 'errors': len(records)}

        stats = {'added': 0, 'duplicates': 0, 'errors': 0}

        # Get existing records for deduplication
        existing = self.get_all_records()

        # Filter duplicates and prepare rows
        rows_to_add = []
        for record in records:
            # Set defaults
            if not record.get('status'):
                record['status'] = 'New'
            if not record.get('date_found'):
                record['date_found'] = datetime.now().strftime('%Y-%m-%d')
            if not record.get('lead_id'):
                record['lead_id'] = generate_lead_id(record)

            # Check for duplicate
            if self.is_duplicate(record, existing):
                stats['duplicates'] += 1
                continue

            # Build row
            row = []
            for col in self.COLUMNS:
                value = record.get(col, '')
                if value is None:
                    value = ''
                elif isinstance(value, (int, float)):
                    value = str(value)
                row.append(str(value))

            rows_to_add.append(row)
            existing.append(record)  # Prevent duplicates within batch

        # Batch append all rows
        if rows_to_add:
            try:
                self.worksheet.append_rows(rows_to_add, value_input_option='USER_ENTERED')
                stats['added'] = len(rows_to_add)
                self.logger.info(f"Batch added {len(rows_to_add)} records")
            except Exception as e:
                self.logger.error(f"Error batch adding records: {e}")
                stats['errors'] = len(rows_to_add)

        return stats

    def update_record(self, row_number: int, updates: Dict) -> bool:
        """
        Update specific fields in an existing record.

        Args:
            row_number: Row number in spreadsheet (1-indexed)
            updates: Dictionary of field names and new values

        Returns:
            True if successful, False otherwise
        """
        if not self.worksheet:
            if not self.connect():
                return False

        try:
            for col_name, value in updates.items():
                if col_name in self.COLUMNS:
                    col_index = self.COLUMNS.index(col_name) + 1  # 1-indexed
                    self.worksheet.update_cell(row_number, col_index, str(value))

            self.logger.debug(f"Updated row {row_number}")
            return True

        except Exception as e:
            self.logger.error(f"Error updating record: {e}")
            return False

    def ensure_headers(self):
        """Ensure the first row contains column headers."""
        if not self.worksheet:
            if not self.connect():
                return

        try:
            # Check if headers exist
            first_row = self.worksheet.row_values(1)
            if not first_row or first_row[0] != 'lead_id':
                # Insert headers
                self.worksheet.insert_row(self.COLUMNS, 1)
                self.logger.info("Added column headers to sheet")
        except Exception as e:
            self.logger.error(f"Error ensuring headers: {e}")


# Utility functions for data normalization

def normalize_phone(phone: str) -> str:
    """Normalize phone number to standard format."""
    import re
    if not phone:
        return ''
    # Remove non-numeric characters
    digits = re.sub(r'\D', '', phone)
    # Format as (XXX) XXX-XXXX
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    return phone


def normalize_address(address: str) -> str:
    """Normalize address format."""
    if not address:
        return ''

    # Standardize common abbreviations
    replacements = {
        r'\bST\b': 'Street',
        r'\bAVE\b': 'Avenue',
        r'\bBLVD\b': 'Boulevard',
        r'\bDR\b': 'Drive',
        r'\bLN\b': 'Lane',
        r'\bRD\b': 'Road',
        r'\bCT\b': 'Court',
        r'\bPL\b': 'Place',
    }

    import re
    result = address.strip()
    for pattern, replacement in replacements.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    return result


def parse_currency(value: str) -> Optional[float]:
    """Parse currency string to float."""
    import re
    if not value:
        return None
    # Remove currency symbols and commas
    cleaned = re.sub(r'[$,]', '', str(value))
    try:
        return float(cleaned)
    except ValueError:
        return None


def format_currency(value: float) -> str:
    """Format number as currency string."""
    if value is None:
        return ''
    return f"${value:,.0f}"
