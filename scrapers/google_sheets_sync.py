#!/usr/bin/env python3
"""
Google Sheets Sync
Syncs collected NOD records to Google Sheets
"""

import os
import sys
from datetime import datetime
from typing import List, Dict
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('GoogleSheetsSync')

# Configuration
GOOGLE_SHEET_ID = '1me4hbzialZs06LGaG3U2P3CjixSakH46GSM_ZOwSApw'
SHEET_NAME = 'Sheet1'
CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')


class GoogleSheetsSync:
    """Sync records to Google Sheets"""

    # Column mapping (A=1, B=2, etc.)
    COLUMNS = [
        'date_found',           # A
        'recording_date',       # B
        'owner_name',           # C
        'phone',                # D
        'email',                # E
        'property_address',     # F
        'city',                 # G
        'county',               # H
        'estimated_value',      # I
        'mortgage_balance',     # J
        'equity',               # K
        'auction_date',         # L
        'status',               # M
        'lead_score',           # N
        'notes',                # O
        'last_contact',         # P
        'email_sent_date'       # Q
    ]

    def __init__(self, sheet_id: str = None, credentials_file: str = None):
        self.sheet_id = sheet_id or GOOGLE_SHEET_ID
        self.credentials_file = credentials_file or CREDENTIALS_FILE
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Sheets API"""
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        try:
            if os.path.exists(self.credentials_file):
                creds = service_account.Credentials.from_service_account_file(
                    self.credentials_file, scopes=SCOPES)
                self.service = build('sheets', 'v4', credentials=creds)
                logger.info("Connected to Google Sheets")
            else:
                logger.error(f"Credentials file not found: {self.credentials_file}")
                raise FileNotFoundError(f"Credentials file not found: {self.credentials_file}")
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise

    def get_existing_records(self) -> List[Dict]:
        """Get all existing records from the sheet"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=f'{SHEET_NAME}!A:Q'
            ).execute()

            values = result.get('values', [])

            if len(values) <= 1:
                return []

            # Skip header row
            records = []
            for i, row in enumerate(values[1:], start=2):
                record = {'row_number': i}
                for j, col in enumerate(self.COLUMNS):
                    record[col] = row[j] if j < len(row) else ''
                records.append(record)

            return records

        except HttpError as e:
            logger.error(f"Error getting existing records: {e}")
            return []

    def is_duplicate(self, new_record: Dict, existing_records: List[Dict]) -> bool:
        """Check if record already exists (by address + recording date)"""
        new_addr = new_record.get('property_address', '').lower().strip()
        new_date = new_record.get('recording_date', '')

        for existing in existing_records:
            existing_addr = existing.get('property_address', '').lower().strip()
            existing_date = existing.get('recording_date', '')

            # Match by address similarity and recording date
            if new_addr and existing_addr:
                # Simple address matching (first 20 chars)
                if new_addr[:20] == existing_addr[:20]:
                    if new_date == existing_date or not new_date:
                        return True

        return False

    def add_record(self, record: Dict) -> bool:
        """Add a single record to the sheet"""
        try:
            row = []
            for col in self.COLUMNS:
                value = record.get(col, '')
                if isinstance(value, (int, float)):
                    value = str(value)
                row.append(value or '')

            body = {'values': [row]}
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.sheet_id,
                range=f'{SHEET_NAME}!A:Q',
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()

            logger.info(f"Added record: {record.get('property_address', 'Unknown')}")
            return True

        except HttpError as e:
            logger.error(f"Error adding record: {e}")
            return False

    def sync_records(self, records: List[Dict]) -> Dict:
        """Sync a list of records, avoiding duplicates - uses batch append for efficiency"""
        existing = self.get_existing_records()
        logger.info(f"Found {len(existing)} existing records")

        stats = {
            'total': len(records),
            'added': 0,
            'duplicates': 0,
            'errors': 0
        }

        # Collect non-duplicate records for batch insert
        rows_to_add = []

        for record in records:
            # Set defaults
            record['status'] = record.get('status') or 'New'
            record['date_found'] = record.get('date_found') or datetime.now().strftime('%Y-%m-%d')

            if self.is_duplicate(record, existing):
                stats['duplicates'] += 1
                continue

            # Prepare row data
            row = []
            for col in self.COLUMNS:
                value = record.get(col, '')
                if isinstance(value, (int, float)):
                    value = str(value)
                row.append(value or '')

            rows_to_add.append(row)
            existing.append(record)  # Prevent duplicates within batch

        # Batch append all rows at once (single API call)
        if rows_to_add:
            try:
                body = {'values': rows_to_add}
                result = self.service.spreadsheets().values().append(
                    spreadsheetId=self.sheet_id,
                    range=f'{SHEET_NAME}!A:Q',
                    valueInputOption='USER_ENTERED',
                    body=body
                ).execute()

                stats['added'] = len(rows_to_add)
                logger.info(f"Batch added {len(rows_to_add)} records")

            except HttpError as e:
                logger.error(f"Error batch adding records: {e}")
                stats['errors'] = len(rows_to_add)

        logger.info(f"Sync complete: {stats['added']} added, {stats['duplicates']} duplicates, {stats['errors']} errors")
        return stats

    def update_record(self, row_number: int, updates: Dict) -> bool:
        """Update specific fields in an existing record"""
        try:
            for col_name, value in updates.items():
                if col_name in self.COLUMNS:
                    col_index = self.COLUMNS.index(col_name)
                    col_letter = chr(65 + col_index)  # A=65

                    body = {'values': [[str(value)]]}
                    self.service.spreadsheets().values().update(
                        spreadsheetId=self.sheet_id,
                        range=f'{SHEET_NAME}!{col_letter}{row_number}',
                        valueInputOption='USER_ENTERED',
                        body=body
                    ).execute()

            return True

        except HttpError as e:
            logger.error(f"Error updating record: {e}")
            return False


def main():
    """Test Google Sheets sync"""
    import argparse

    parser = argparse.ArgumentParser(description='Google Sheets Sync')
    parser.add_argument('--test', action='store_true', help='Run test mode')
    parser.add_argument('--list', action='store_true', help='List existing records')
    args = parser.parse_args()

    sync = GoogleSheetsSync()

    if args.list:
        records = sync.get_existing_records()
        print(f"\nFound {len(records)} records:")
        for record in records[:10]:
            print(f"  {record.get('property_address', 'No address')} | {record.get('status', 'No status')}")
        if len(records) > 10:
            print(f"  ... and {len(records) - 10} more")

    elif args.test:
        print("Running Google Sheets sync test...")
        test_record = {
            'date_found': datetime.now().strftime('%Y-%m-%d'),
            'recording_date': datetime.now().strftime('%Y-%m-%d'),
            'owner_name': 'TEST RECORD - DELETE',
            'property_address': '999 Test St, Test City, CA 90000',
            'city': 'Test City',
            'county': 'Los Angeles',
            'status': 'New',
            'notes': 'Automated test - please delete'
        }

        stats = sync.sync_records([test_record])
        print(f"\nSync results: {stats}")
        print("\nPlease check your Google Sheet and delete the test record.")


if __name__ == '__main__':
    main()
