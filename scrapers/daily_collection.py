#!/usr/bin/env python3
"""
Daily NOD Collection Script
Main entry point for collecting NOD leads from LA County and Riverside County

Usage:
    python daily_collection.py --all              # Collect from all sources
    python daily_collection.py --county la        # LA County only
    python daily_collection.py --county riverside # Riverside County only
    python daily_collection.py --enrich           # Enrich existing records with assessor data
    python daily_collection.py --test             # Test mode (no writes)
"""

import argparse
import logging
from datetime import datetime
from typing import List, Dict
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scrapers.zillow_scraper import ZillowForeclosureScraper
from scrapers.riverside_recorder import RiversideRecorderScraper
from scrapers.la_county_assessor import LACountyAssessorEnricher
from scrapers.google_sheets_sync import GoogleSheetsSync

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/nod_scraper.log')
    ]
)
logger = logging.getLogger('DailyCollection')


class DailyNODCollector:
    """Main collector that orchestrates all scrapers"""

    def __init__(self, test_mode: bool = False):
        self.test_mode = test_mode
        self.sheets_sync = None if test_mode else GoogleSheetsSync()
        self.assessor_enricher = None

    def collect_la_county(self, days_back: int = 7) -> List[Dict]:
        """Collect LA County foreclosure records from Zillow"""
        logger.info("Collecting LA County records from Zillow...")

        scraper = ZillowForeclosureScraper(county='Los Angeles')
        records = scraper.scrape_foreclosures(max_pages=3)

        logger.info(f"Collected {len(records)} LA County records")
        return records

    def collect_riverside_county(self, days_back: int = 7) -> List[Dict]:
        """Collect Riverside County foreclosure records from Zillow"""
        logger.info("Collecting Riverside County records from Zillow...")

        scraper = ZillowForeclosureScraper(county='Riverside')
        records = scraper.scrape_foreclosures(max_pages=3)

        logger.info(f"Collected {len(records)} Riverside County records")
        return records

    def _deduplicate_records(self, records: List[Dict]) -> List[Dict]:
        """Remove duplicate records based on address"""
        seen = set()
        unique = []

        for record in records:
            addr = record.get('property_address', '')[:30].lower()
            if addr and addr not in seen:
                seen.add(addr)
                unique.append(record)
            elif not addr:
                unique.append(record)

        return unique

    def enrich_with_assessor(self, records: List[Dict]) -> List[Dict]:
        """Enrich records with LA County Assessor data"""
        if not self.assessor_enricher:
            self.assessor_enricher = LACountyAssessorEnricher()

        enriched = []
        for record in records:
            if record.get('county') == 'Los Angeles':
                try:
                    enriched_record = self.assessor_enricher.enrich_record(record)
                    enriched.append(enriched_record)
                except Exception as e:
                    logger.warning(f"Error enriching record: {e}")
                    enriched.append(record)
            else:
                enriched.append(record)

        if self.assessor_enricher:
            self.assessor_enricher.close()

        return enriched

    def sync_to_sheets(self, records: List[Dict]) -> Dict:
        """Sync collected records to Google Sheets"""
        if self.test_mode:
            logger.info(f"TEST MODE: Would sync {len(records)} records to Google Sheets")
            return {'total': len(records), 'added': 0, 'duplicates': 0, 'errors': 0}

        return self.sheets_sync.sync_records(records)

    def run_full_collection(self, counties: List[str] = None, days_back: int = 7, enrich: bool = False) -> Dict:
        """Run full collection for specified counties"""
        if counties is None:
            counties = ['la', 'riverside']

        all_records = []
        stats = {
            'collection_time': datetime.now().isoformat(),
            'counties': counties,
            'days_back': days_back,
            'records_collected': {},
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

        stats['total_collected'] = len(all_records)
        logger.info(f"Total records collected: {len(all_records)}")

        # Optionally enrich with assessor data
        if enrich:
            logger.info("Enriching records with assessor data...")
            all_records = self.enrich_with_assessor(all_records)

        # Sync to Google Sheets
        if all_records:
            sync_stats = self.sync_to_sheets(all_records)
            stats['sync_stats'] = sync_stats

        # Log summary
        logger.info(f"Collection complete: {json.dumps(stats, indent=2)}")

        return stats


def main():
    parser = argparse.ArgumentParser(description='Daily NOD Lead Collection')
    parser.add_argument('--all', action='store_true', help='Collect from all counties')
    parser.add_argument('--county', type=str, choices=['la', 'riverside', 'both'],
                        help='Specific county to collect')
    parser.add_argument('--days', type=int, default=7, help='Days to look back')
    parser.add_argument('--enrich', action='store_true', help='Enrich with assessor data')
    parser.add_argument('--test', action='store_true', help='Test mode (no writes)')
    parser.add_argument('--output', type=str, help='Output JSON file for results')
    args = parser.parse_args()

    print("=" * 60)
    print("NOD LEAD COLLECTION")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test Mode: {args.test}")
    print("=" * 60)

    collector = DailyNODCollector(test_mode=args.test)

    # Determine which counties to collect
    if args.all or args.county == 'both':
        counties = ['la', 'riverside']
    elif args.county:
        counties = [args.county]
    else:
        # Default to both
        counties = ['la', 'riverside']

    # Run collection
    stats = collector.run_full_collection(
        counties=counties,
        days_back=args.days,
        enrich=args.enrich
    )

    # Output results
    print("\n" + "=" * 60)
    print("COLLECTION RESULTS")
    print("=" * 60)
    print(f"Counties: {', '.join(counties)}")
    print(f"Days back: {args.days}")
    print(f"Records collected: {stats.get('total_collected', 0)}")

    if 'sync_stats' in stats:
        sync = stats['sync_stats']
        print(f"\nSync Results:")
        print(f"  - Added: {sync.get('added', 0)}")
        print(f"  - Duplicates: {sync.get('duplicates', 0)}")
        print(f"  - Errors: {sync.get('errors', 0)}")

    print("=" * 60)

    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"\nResults saved to: {args.output}")

    return stats


if __name__ == '__main__':
    main()
