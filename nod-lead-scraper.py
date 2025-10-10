#!/usr/bin/env python3
"""
LA County Notice of Default (NOD) Lead Scraper
Automatically scrapes foreclosure notices from LA County Recorder
and adds them to your Google Sheet

Requirements:
- pip install requests beautifulsoup4 google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
- Google Sheets API credentials (follow setup instructions below)
"""

import os
import re
import time
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configuration
GOOGLE_SHEET_ID = '1GrfyUDVS_Z66X80kVrXSGRHnbV1XOPp06uxF8lmbbiw'
SHEET_NAME = 'NOD Leads'  # Create this tab in your Google Sheet

# LA County Recorder URLs
LA_COUNTY_RECORDER_URL = 'https://www.lavote.gov/home/recorder'

class NODLeadScraper:
    def __init__(self, sheet_id, credentials_file=None):
        """
        Initialize the scraper

        Args:
            sheet_id: Google Sheet ID
            credentials_file: Path to Google API credentials JSON file
        """
        self.sheet_id = sheet_id
        self.credentials_file = credentials_file or 'credentials.json'
        self.service = None

    def authenticate_google_sheets(self):
        """Authenticate with Google Sheets API"""
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        try:
            # Try to use service account credentials
            if os.path.exists(self.credentials_file):
                creds = service_account.Credentials.from_service_account_file(
                    self.credentials_file, scopes=SCOPES)
                self.service = build('sheets', 'v4', credentials=creds)
                print("✅ Connected to Google Sheets")
                return True
            else:
                print(f"❌ Credentials file not found: {self.credentials_file}")
                print("\nTo set up Google Sheets API:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create a new project")
                print("3. Enable Google Sheets API")
                print("4. Create Service Account credentials")
                print("5. Download JSON key and save as 'credentials.json'")
                print("6. Share your Google Sheet with the service account email")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False

    def add_lead_to_sheet(self, lead_data):
        """
        Add a lead to Google Sheet

        Args:
            lead_data: Dictionary with lead information
        """
        if not self.service:
            print("❌ Not authenticated with Google Sheets")
            return False

        try:
            # Prepare row data
            row = [
                datetime.now().strftime('%Y-%m-%d'),  # Date Found
                lead_data.get('property_address', ''),
                lead_data.get('owner_name', ''),
                lead_data.get('phone', ''),  # Empty initially
                lead_data.get('email', ''),  # Empty initially
                lead_data.get('recording_date', ''),
                lead_data.get('days_since_nod', ''),
                lead_data.get('county', 'Los Angeles'),
                lead_data.get('estimated_value', ''),
                lead_data.get('lender', ''),
                'New',  # Status
                '',  # Last Contact
                '',  # Next Follow-up Date
                lead_data.get('notes', '')
            ]

            # Append to sheet
            body = {'values': [row]}
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.sheet_id,
                range=f'{SHEET_NAME}!A:N',
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()

            print(f"✅ Added lead: {lead_data.get('property_address', 'Unknown')}")
            return True

        except HttpError as error:
            print(f"❌ Error adding to sheet: {error}")
            return False

    def scrape_la_county_manual_instructions(self):
        """
        Provide manual instructions for LA County since they don't have
        an easily scrapable interface
        """
        print("\n" + "="*60)
        print("LA COUNTY RECORDER - MANUAL LEAD COLLECTION")
        print("="*60)
        print("\nLA County doesn't provide an easy-to-scrape public database.")
        print("Here's how to manually collect leads:\n")

        print("OPTION 1: LA County Recorder Website")
        print("-" * 40)
        print("1. Visit: https://www.lavote.gov/home/recorder/real-estate-records")
        print("2. Click 'View Real Estate Records'")
        print("3. Search by:")
        print("   - Document Type: 'Notice of Default' or 'NOD'")
        print("   - Date Range: Last 30 days")
        print("4. Export results or manually copy:\n")
        print("   - Property Address")
        print("   - Owner Name (Trustor)")
        print("   - Recording Date")
        print("   - Lender (Beneficiary)\n")

        print("OPTION 2: Third-Party Data Services (Recommended)")
        print("-" * 40)
        print("These services automatically collect and update NOD data:\n")
        print("1. ForeclosureRadar.com ($100-300/month)")
        print("   - Best for California")
        print("   - Daily updates")
        print("   - Includes property photos, values, contact info")
        print("   - Export to CSV → Import to Google Sheets\n")

        print("2. RealtyTrac.com ($50-200/month)")
        print("   - Nationwide coverage")
        print("   - Good for multi-state operations\n")

        print("3. PropertyShark.com ($99-300/month)")
        print("   - Detailed property data")
        print("   - Owner contact information\n")

        print("OPTION 3: Use This Script with CSV Import")
        print("-" * 40)
        print("1. Download NOD data from any source as CSV")
        print("2. Run this script with: python nod-lead-scraper.py import data.csv")
        print("3. Script will automatically add all leads to Google Sheet\n")

        print("="*60 + "\n")

    def import_from_csv(self, csv_file):
        """
        Import leads from a CSV file

        CSV format should have columns:
        Address, Owner Name, Recording Date, Lender, Notes
        """
        if not self.service:
            print("❌ Not authenticated with Google Sheets")
            return

        try:
            import csv

            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                count = 0

                for row in reader:
                    # Calculate days since NOD
                    days_since = ''
                    if row.get('Recording Date'):
                        try:
                            rec_date = datetime.strptime(row['Recording Date'], '%Y-%m-%d')
                            days_since = (datetime.now() - rec_date).days
                        except:
                            pass

                    lead_data = {
                        'property_address': row.get('Address', row.get('Property Address', '')),
                        'owner_name': row.get('Owner Name', row.get('Owner', '')),
                        'recording_date': row.get('Recording Date', ''),
                        'days_since_nod': str(days_since) if days_since else '',
                        'lender': row.get('Lender', row.get('Beneficiary', '')),
                        'estimated_value': row.get('Estimated Value', row.get('Value', '')),
                        'notes': row.get('Notes', '')
                    }

                    if self.add_lead_to_sheet(lead_data):
                        count += 1
                        time.sleep(0.5)  # Rate limiting

                print(f"\n✅ Imported {count} leads from {csv_file}")

        except Exception as e:
            print(f"❌ Error importing CSV: {str(e)}")

    def create_sheet_headers(self):
        """Create headers in the Google Sheet if they don't exist"""
        if not self.service:
            return

        try:
            headers = [[
                'Date Found',
                'Property Address',
                'Owner Name',
                'Phone Number',
                'Email',
                'Recording Date',
                'Days Since NOD',
                'County',
                'Estimated Value',
                'Lender',
                'Status',
                'Last Contact',
                'Next Follow-up Date',
                'Notes'
            ]]

            body = {'values': headers}
            self.service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id,
                range=f'{SHEET_NAME}!A1:N1',
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()

            print(f"✅ Created headers in '{SHEET_NAME}' tab")

        except HttpError as error:
            if 'Unable to parse range' in str(error):
                print(f"\n⚠️  Please create a tab named '{SHEET_NAME}' in your Google Sheet:")
                print(f"   https://docs.google.com/spreadsheets/d/{self.sheet_id}/edit")
            else:
                print(f"❌ Error creating headers: {error}")


def main():
    """Main execution"""
    import sys

    print("="*60)
    print("LA COUNTY NOD LEAD SCRAPER")
    print("="*60)
    print()

    scraper = NODLeadScraper(GOOGLE_SHEET_ID)

    # Try to authenticate
    if scraper.authenticate_google_sheets():
        # Try to create headers
        scraper.create_sheet_headers()

        # Check if CSV import was requested
        if len(sys.argv) > 2 and sys.argv[1] == 'import':
            csv_file = sys.argv[2]
            print(f"\nImporting leads from {csv_file}...\n")
            scraper.import_from_csv(csv_file)
        else:
            # Show manual instructions
            scraper.scrape_la_county_manual_instructions()

            # Add a test lead
            print("Adding a test lead to verify Google Sheets connection...\n")
            test_lead = {
                'property_address': '123 Test St, Los Angeles, CA 90001',
                'owner_name': 'Test Lead (DELETE THIS ROW)',
                'recording_date': datetime.now().strftime('%Y-%m-%d'),
                'days_since_nod': '0',
                'lender': 'Test Bank',
                'notes': 'This is a test lead - delete this row'
            }
            scraper.add_lead_to_sheet(test_lead)

            print("\n" + "="*60)
            print("NEXT STEPS:")
            print("="*60)
            print("\n1. Check your Google Sheet for the test lead:")
            print(f"   https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/edit")
            print("\n2. Delete the test row")
            print("\n3. Choose your lead collection method:")
            print("   - Manual: Follow instructions above")
            print("   - CSV Import: python nod-lead-scraper.py import yourfile.csv")
            print("   - Paid Service: Subscribe to ForeclosureRadar.com")
            print("\n4. Start calling leads using the script from FORECLOSURE-LEAD-FARMING-GUIDE.md")
            print()
    else:
        print("\n⚠️  Cannot proceed without Google Sheets authentication")
        print("Follow the setup instructions above to continue.")


if __name__ == '__main__':
    main()
