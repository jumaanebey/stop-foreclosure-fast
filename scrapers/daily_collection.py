#!/usr/bin/env python3
"""
Daily NOD Collection Script

Main entry point for collecting NOD (Notice of Default) leads from
LA County and Riverside County recorders, enriching with assessor data,
and pushing to Google Sheets.

This is the primary script to run for daily lead collection.

Usage:
    python daily_collection.py --all              # Collect from all sources
    python daily_collection.py --county la        # LA County only
    python daily_collection.py --county riverside # Riverside County only
    python daily_collection.py --enrich           # Enrich records with assessor data
    python daily_collection.py --days 14          # Look back 14 days
    python daily_collection.py --test             # Test mode (no writes to sheet)
    python daily_collection.py --output out.json  # Save results to JSON file

Cron Setup:
    # Run daily at 6 AM
    0 6 * * * /path/to/venv/bin/python /path/to/scrapers/daily_collection.py --all --enrich

Configuration:
    - Google Sheet ID: 1me4hbzialZs06LGaG3U2P3CjixSakH46GSM_ZOwSApw
    - Credentials: credentials.json in project root
"""

import argparse
import logging
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import scrapers - use try/except for flexibility
try:
    from .la_county_recorder import LACountyRecorderScraper
    from .riverside_recorder import RiversideRecorderScraper
    from .property_enricher import PropertyEnricher
    from .base_scraper import GoogleSheetsManager, generate_lead_id
except ImportError:
    from la_county_recorder import LACountyRecorderScraper
    from riverside_recorder import RiversideRecorderScraper
    from property_enricher import PropertyEnricher
    from base_scraper import GoogleSheetsManager, generate_lead_id

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/nod_scraper.log', mode='a')
    ]
)
logger = logging.getLogger('DailyCollection')


class DailyNODCollector:
    """
    Main collector that orchestrates all NOD scrapers.

    This class coordinates:
    - LA County Recorder scraping
    - Riverside County Recorder scraping
    - Property enrichment with assessor data
    - Deduplication
    - Google Sheets synchronization

    Attributes:
        test_mode: If True, don't write to Google Sheets
        sheets_manager: Google Sheets integration manager
        property_enricher: Property data enricher
    """

    def __init__(self, test_mode: bool = False):
        """
        Initialize the daily collector.

        Args:
            test_mode: If True, run without writing to Google Sheets
        """
        self.test_mode = test_mode
        self.sheets_manager = None if test_mode else GoogleSheetsManager()
        self.property_enricher = None

    def collect_la_county(self, days_back: int = 7) -> List[Dict]:
        """
        Collect LA County NOD records from county recorder.

        Args:
            days_back: Number of days to look back

        Returns:
            List of NOD records
        """
        logger.info(f"Collecting LA County NOD records (last {days_back} days)...")

        try:
            scraper = LACountyRecorderScraper()
            records = scraper.collect_records(days_back=days_back)
            logger.info(f"Collected {len(records)} LA County records")
            return records
        except Exception as e:
            logger.error(f"Error collecting LA County records: {e}")
            return []

    def collect_riverside_county(self, days_back: int = 7) -> List[Dict]:
        """
        Collect Riverside County NOD records from county recorder.

        Args:
            days_back: Number of days to look back

        Returns:
            List of NOD records
        """
        logger.info(f"Collecting Riverside County NOD records (last {days_back} days)...")

        try:
            scraper = RiversideRecorderScraper()
            records = scraper.collect_records(days_back=days_back)
            logger.info(f"Collected {len(records)} Riverside County records")
            return records
        except Exception as e:
            logger.error(f"Error collecting Riverside County records: {e}")
            return []

    def deduplicate_records(self, records: List[Dict]) -> List[Dict]:
        """
        Remove duplicate records based on APN, document number, or address.

        Args:
            records: List of records to deduplicate

        Returns:
            List of unique records
        """
        seen = set()
        unique = []

        for record in records:
            # Create deduplication key
            apn = record.get('apn', '').strip()
            doc_num = record.get('document_number', '').strip()
            addr = record.get('property_address', '')[:30].lower().strip()

            # Use the most reliable identifier available
            if apn:
                key = f"apn:{apn}"
            elif doc_num:
                key = f"doc:{doc_num}"
            elif addr:
                key = f"addr:{addr}"
            else:
                # No identifier, keep the record
                unique.append(record)
                continue

            if key not in seen:
                seen.add(key)
                unique.append(record)
            else:
                logger.debug(f"Duplicate found: {key}")

        logger.info(f"Deduplicated {len(records)} records to {len(unique)} unique records")
        return unique

    def enrich_records(self, records: List[Dict], max_records: int = None) -> List[Dict]:
        """
        Enrich records with assessor data.

        Args:
            records: List of records to enrich
            max_records: Maximum number to enrich (None for all)

        Returns:
            List of enriched records
        """
        if not records:
            return records

        logger.info(f"Enriching {len(records)} records with assessor data...")

        try:
            if not self.property_enricher:
                self.property_enricher = PropertyEnricher()

            enriched = self.property_enricher.enrich_batch(records, max_records=max_records)
            return enriched

        except Exception as e:
            logger.error(f"Error enriching records: {e}")
            return records

        finally:
            if self.property_enricher:
                self.property_enricher.close()
                self.property_enricher = None

    def sync_to_sheets(self, records: List[Dict]) -> Dict:
        """
        Sync collected records to Google Sheets.

        Args:
            records: List of records to sync

        Returns:
            Dictionary with sync statistics
        """
        if self.test_mode:
            logger.info(f"TEST MODE: Would sync {len(records)} records to Google Sheets")
            return {'total': len(records), 'added': 0, 'duplicates': len(records), 'errors': 0}

        if not self.sheets_manager:
            self.sheets_manager = GoogleSheetsManager()

        try:
            # Ensure lead_id is set for all records
            for record in records:
                if not record.get('lead_id'):
                    record['lead_id'] = generate_lead_id(record)

            stats = self.sheets_manager.add_records_batch(records)
            return stats

        except Exception as e:
            logger.error(f"Error syncing to Google Sheets: {e}")
            return {'total': len(records), 'added': 0, 'duplicates': 0, 'errors': len(records)}

    def run_full_collection(self, counties: List[str] = None, days_back: int = 7,
                            enrich: bool = False, max_enrich: int = None) -> Dict:
        """
        Run full collection for specified counties.

        This is the main entry point for daily collection.

        Args:
            counties: List of counties to collect from (default: both)
            days_back: Number of days to look back
            enrich: Whether to enrich with assessor data
            max_enrich: Maximum records to enrich (None for all)

        Returns:
            Dictionary with collection statistics
        """
        if counties is None:
            counties = ['la', 'riverside']

        all_records = []
        stats = {
            'collection_time': datetime.now().isoformat(),
            'counties': counties,
            'days_back': days_back,
            'enrich': enrich,
            'records_collected': {},
            'total_raw': 0,
            'total_unique': 0,
            'sync_stats': {}
        }

        # Collect from each county
        for county in counties:
            county = county.lower()
            try:
                if county in ['la', 'los angeles']:
                    records = self.collect_la_county(days_back)
                    stats['records_collected']['la'] = len(records)
                    all_records.extend(records)

                elif county == 'riverside':
                    records = self.collect_riverside_county(days_back)
                    stats['records_collected']['riverside'] = len(records)
                    all_records.extend(records)

                else:
                    logger.warning(f"Unknown county: {county}")

            except Exception as e:
                logger.error(f"Error collecting from {county}: {e}")
                stats['records_collected'][county] = f"Error: {str(e)}"

        stats['total_raw'] = len(all_records)
        logger.info(f"Total raw records collected: {len(all_records)}")

        # Deduplicate
        all_records = self.deduplicate_records(all_records)
        stats['total_unique'] = len(all_records)

        # Optionally enrich with assessor data
        if enrich and all_records:
            logger.info("Enriching records with assessor data...")
            all_records = self.enrich_records(all_records, max_records=max_enrich)
            stats['enriched'] = True

        # Sync to Google Sheets
        if all_records:
            sync_stats = self.sync_to_sheets(all_records)
            stats['sync_stats'] = sync_stats

        # Log summary
        logger.info(f"Collection complete: {json.dumps(stats, indent=2)}")

        return stats


def run_daily_collection(**kwargs) -> Dict:
    """
    Convenience function to run daily collection.

    This is the main entry point for programmatic use.

    Args:
        **kwargs: Arguments passed to DailyNODCollector.run_full_collection()

    Returns:
        Dictionary with collection statistics
    """
    test_mode = kwargs.pop('test_mode', False)
    collector = DailyNODCollector(test_mode=test_mode)
    return collector.run_full_collection(**kwargs)


def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description='Daily NOD Lead Collection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python daily_collection.py --all                    # Collect from all counties
    python daily_collection.py --county la              # LA County only
    python daily_collection.py --county riverside       # Riverside County only
    python daily_collection.py --all --enrich           # Collect and enrich
    python daily_collection.py --days 14                # Look back 14 days
    python daily_collection.py --test                   # Test mode (no writes)
    python daily_collection.py --output results.json    # Save to JSON file

Cron Setup:
    0 6 * * * /path/to/venv/bin/python /path/to/daily_collection.py --all --enrich
        """
    )
    parser.add_argument('--all', action='store_true',
                        help='Collect from all counties (LA + Riverside)')
    parser.add_argument('--county', type=str, choices=['la', 'riverside', 'both'],
                        help='Specific county to collect from')
    parser.add_argument('--days', type=int, default=7,
                        help='Days to look back (default: 7)')
    parser.add_argument('--enrich', action='store_true',
                        help='Enrich records with assessor data')
    parser.add_argument('--max-enrich', type=int, default=None,
                        help='Maximum records to enrich (default: all)')
    parser.add_argument('--test', action='store_true',
                        help='Test mode - collect but do not write to Google Sheets')
    parser.add_argument('--output', type=str,
                        help='Output JSON file for results')
    parser.add_argument('--quiet', action='store_true',
                        help='Quiet mode - minimal output')
    args = parser.parse_args()

    # Print header
    if not args.quiet:
        print("=" * 70)
        print("  CALIFORNIA NOD (NOTICE OF DEFAULT) LEAD COLLECTION")
        print("=" * 70)
        print(f"  Date:        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Test Mode:   {'Yes' if args.test else 'No'}")
        print(f"  Days Back:   {args.days}")
        print(f"  Enrich:      {'Yes' if args.enrich else 'No'}")
        print("=" * 70)
        print()

    # Initialize collector
    collector = DailyNODCollector(test_mode=args.test)

    # Determine which counties to collect
    if args.all or args.county == 'both':
        counties = ['la', 'riverside']
    elif args.county:
        counties = [args.county]
    else:
        # Default to both
        counties = ['la', 'riverside']

    if not args.quiet:
        print(f"Collecting from: {', '.join([c.upper() for c in counties])}")
        print()

    # Run collection
    stats = collector.run_full_collection(
        counties=counties,
        days_back=args.days,
        enrich=args.enrich,
        max_enrich=args.max_enrich
    )

    # Output results
    if not args.quiet:
        print()
        print("=" * 70)
        print("  COLLECTION RESULTS")
        print("=" * 70)
        print(f"  Counties:          {', '.join([c.upper() for c in counties])}")
        print(f"  Days Searched:     {args.days}")
        print(f"  Raw Records:       {stats.get('total_raw', 0)}")
        print(f"  Unique Records:    {stats.get('total_unique', 0)}")

        # Per-county breakdown
        if stats.get('records_collected'):
            print("\n  Per-County Breakdown:")
            for county, count in stats['records_collected'].items():
                print(f"    - {county.upper()}: {count}")

        # Sync results
        if 'sync_stats' in stats and stats['sync_stats']:
            sync = stats['sync_stats']
            print(f"\n  Google Sheets Sync:")
            print(f"    - Added:      {sync.get('added', 0)}")
            print(f"    - Duplicates: {sync.get('duplicates', 0)}")
            print(f"    - Errors:     {sync.get('errors', 0)}")

        print("=" * 70)

    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(stats, f, indent=2, default=str)
        if not args.quiet:
            print(f"\nResults saved to: {args.output}")

    # Return exit code based on success
    if stats.get('sync_stats', {}).get('errors', 0) > 0:
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main() or 0)
