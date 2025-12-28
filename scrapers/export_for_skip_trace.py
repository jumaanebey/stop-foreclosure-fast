#!/usr/bin/env python3
"""
Export Leads for Skip Tracing
Exports leads without phone numbers in a format ready for skip tracing
"""

import os
import sys
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Configuration
GOOGLE_SHEET_ID = '1me4hbzialZs06LGaG3U2P3CjixSakH46GSM_ZOwSApw'
SHEET_NAME = 'Sheet1'
CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')

def get_leads_for_skip_trace(limit=50, high_value_only=False):
    """Get leads that need phone numbers"""

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)

    # Get all data
    result = service.spreadsheets().values().get(
        spreadsheetId=GOOGLE_SHEET_ID,
        range=f'{SHEET_NAME}!A:Q'
    ).execute()

    values = result.get('values', [])

    if len(values) <= 1:
        return []

    # Column indices (0-based)
    # A=0: date_found, B=1: recording_date, C=2: owner_name, D=3: phone,
    # E=4: email, F=5: property_address, G=6: city, H=7: county,
    # I=8: estimated_value

    leads_to_trace = []

    for i, row in enumerate(values[1:], start=2):  # Skip header
        # Pad row to ensure we have enough columns
        while len(row) < 17:
            row.append('')

        owner_name = row[2] if len(row) > 2 else ''
        phone = row[3] if len(row) > 3 else ''
        address = row[5] if len(row) > 5 else ''
        city = row[6] if len(row) > 6 else ''
        county = row[7] if len(row) > 7 else ''
        value = row[8] if len(row) > 8 else ''

        # Skip if already has phone number
        if phone and phone.strip():
            continue

        # Skip if no owner name
        if not owner_name or not owner_name.strip():
            continue

        # Filter for high value if requested
        if high_value_only:
            try:
                value_num = int(value.replace('$', '').replace(',', ''))
                if value_num < 400000:
                    continue
            except:
                continue

        leads_to_trace.append({
            'row': i,
            'owner_name': owner_name.strip(),
            'address': address.strip(),
            'city': city.strip(),
            'county': county.strip(),
            'value': value
        })

        if len(leads_to_trace) >= limit:
            break

    return leads_to_trace


def export_for_claude(leads, output_file=None):
    """Export leads in a format ready for Claude for Chrome"""

    output = []
    output.append("=" * 60)
    output.append("SKIP TRACE LIST - Copy to Claude for Chrome")
    output.append("=" * 60)
    output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    output.append(f"Total leads to trace: {len(leads)}")
    output.append("=" * 60)
    output.append("")
    output.append("INSTRUCTIONS FOR CLAUDE FOR CHROME:")
    output.append("-" * 40)
    output.append("1. Go to TruePeopleSearch.com")
    output.append("2. Copy the list below")
    output.append("3. Give Claude this prompt:")
    output.append("")
    output.append('"""')
    output.append("Search TruePeopleSearch.com for each of these property owners.")
    output.append("Find their phone number and email if available.")
    output.append("")
    output.append("Return results as a table:")
    output.append("Row # | Name | Phone | Email")
    output.append("")
    output.append("Here are the people to search:")
    output.append('"""')
    output.append("")
    output.append("=" * 60)
    output.append("LEADS TO SKIP TRACE:")
    output.append("=" * 60)
    output.append("")

    for lead in leads:
        output.append(f"Row {lead['row']}: {lead['owner_name']}")
        output.append(f"   City: {lead['city']}, CA")
        if lead['address']:
            output.append(f"   Address: {lead['address']}")
        if lead['value']:
            output.append(f"   Property Value: {lead['value']}")
        output.append("")

    output.append("=" * 60)
    output.append("")
    output.append("SIMPLE LIST FORMAT (for batch search):")
    output.append("-" * 40)

    for lead in leads:
        city = lead['city'] if lead['city'] else lead['county']
        output.append(f"{lead['owner_name']}, {city}, CA")

    output.append("")
    output.append("=" * 60)
    output.append("After getting results, update your Google Sheet:")
    output.append(f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/edit")
    output.append("=" * 60)

    result = "\n".join(output)

    if output_file:
        with open(output_file, 'w') as f:
            f.write(result)
        print(f"Exported to: {output_file}")

    return result


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Export leads for skip tracing')
    parser.add_argument('--limit', type=int, default=25, help='Number of leads to export (default: 25)')
    parser.add_argument('--high-value', action='store_true', help='Only export high-value leads ($400k+)')
    parser.add_argument('--output', type=str, help='Output file path')
    args = parser.parse_args()

    print("Fetching leads that need phone numbers...")

    leads = get_leads_for_skip_trace(
        limit=args.limit,
        high_value_only=args.high_value
    )

    if not leads:
        print("No leads found that need skip tracing!")
        print("(All leads may already have phone numbers)")
        return

    print(f"Found {len(leads)} leads to skip trace")

    output_file = args.output or '/tmp/skip_trace_list.txt'
    result = export_for_claude(leads, output_file)

    print("\n" + result)


if __name__ == '__main__':
    main()
