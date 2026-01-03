#!/usr/bin/env python3
"""
Daily Foreclosure Data Collection Script
Automated system to collect foreclosure data from multiple sources
"""

import schedule
import time
import logging
import sys
import os
from datetime import datetime, timedelta
import sqlite3
import json
import subprocess

# Add current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from county_scraper import CountyForeclosureScraper
from rss_parser import ForeclosureRSSParser

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/foreclosure_collector.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DailyForeclosureCollector:
    def __init__(self, db_path="/tmp/foreclosure_data.db"):
        self.db_path = db_path
        self.county_scraper = CountyForeclosureScraper(db_path)
        self.rss_parser = ForeclosureRSSParser(db_path)
        
        # Collection statistics
        self.collection_stats = {
            'last_run': None,
            'total_runs': 0,
            'successful_runs': 0,
            'failed_runs': 0,
            'counties_collected': 0,
            'rss_feeds_collected': 0,
            'total_records_added': 0
        }
        
        # Load existing stats
        self.load_collection_stats()
    
    def load_collection_stats(self):
        """Load collection statistics from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create stats table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS collection_stats (
                    id INTEGER PRIMARY KEY,
                    stats_json TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Get latest stats
            cursor.execute('SELECT stats_json FROM collection_stats ORDER BY updated_at DESC LIMIT 1')
            result = cursor.fetchone()
            
            if result:
                stored_stats = json.loads(result[0])
                self.collection_stats.update(stored_stats)
            
            conn.close()
            
        except Exception as e:
            logger.warning(f"Could not load collection stats: {e}")
    
    def save_collection_stats(self):
        """Save collection statistics to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO collection_stats (stats_json) VALUES (?)
            ''', (json.dumps(self.collection_stats),))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save collection stats: {e}")
    
    def collect_county_data(self):
        """Collect data from county websites"""
        logger.info("Starting county data collection...")
        
        try:
            # Get initial count
            initial_count = self.get_record_count('foreclosure_properties')
            
            # Run county scraping
            foreclosures = self.county_scraper.scrape_all_counties()
            
            # Get final count
            final_count = self.get_record_count('foreclosure_properties')
            new_records = final_count - initial_count
            
            logger.info(f"County collection complete: {len(foreclosures)} found, {new_records} new records added")
            
            self.collection_stats['counties_collected'] += len(self.county_scraper.counties)
            self.collection_stats['total_records_added'] += new_records
            
            return True
            
        except Exception as e:
            logger.error(f"County data collection failed: {e}")
            return False
    
    def collect_rss_data(self):
        """Collect data from RSS feeds"""
        logger.info("Starting RSS data collection...")
        
        try:
            # Get initial count
            initial_count = self.get_record_count('rss_entries')
            
            # Run RSS parsing
            entries = self.rss_parser.parse_all_feeds()
            
            # Get final count
            final_count = self.get_record_count('rss_entries')
            new_records = final_count - initial_count
            
            logger.info(f"RSS collection complete: {len(entries)} processed, {new_records} new records added")
            
            # Count active feeds
            active_feeds = sum(len(feeds) for feeds in self.rss_parser.rss_feeds.values() 
                             if isinstance(feeds, list))
            
            self.collection_stats['rss_feeds_collected'] += active_feeds
            self.collection_stats['total_records_added'] += new_records
            
            return True
            
        except Exception as e:
            logger.error(f"RSS data collection failed: {e}")
            return False
    
    def get_record_count(self, table_name):
        """Get current record count for a table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception:
            return 0
    
    def cleanup_old_data(self, days_to_keep=90):
        """Clean up old data to prevent database bloat"""
        logger.info(f"Cleaning up data older than {days_to_keep} days...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
            
            # Clean up old RSS entries (keep foreclosure_properties longer)
            cursor.execute('''
                DELETE FROM rss_entries 
                WHERE created_at < ? 
                AND (title LIKE '%sold%' OR title LIKE '%closed%')
            ''', (cutoff_date,))
            
            deleted_rss = cursor.rowcount
            
            # Clean up old log entries
            cursor.execute('''
                DELETE FROM scraping_log 
                WHERE scrape_date < ?
            ''', (cutoff_date,))
            
            deleted_logs = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cleanup complete: {deleted_rss} old RSS entries, {deleted_logs} old log entries removed")
            
        except Exception as e:
            logger.error(f"Data cleanup failed: {e}")
    
    def generate_daily_report(self):
        """Generate daily collection report"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Today's activity
            today = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute('''
                SELECT COUNT(*) FROM foreclosure_properties 
                WHERE DATE(created_at) = ?
            ''', (today,))
            new_foreclosures_today = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT COUNT(*) FROM rss_entries 
                WHERE DATE(created_at) = ?
            ''', (today,))
            new_rss_today = cursor.fetchone()[0]
            
            # Total statistics
            cursor.execute('SELECT COUNT(*) FROM foreclosure_properties')
            total_foreclosures = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM rss_entries')
            total_rss = cursor.fetchone()[0]
            
            # Recent activity by state
            cursor.execute('''
                SELECT state, COUNT(*) as count 
                FROM foreclosure_properties 
                WHERE created_at >= date('now', '-7 days')
                AND state IS NOT NULL 
                GROUP BY state 
                ORDER BY count DESC 
                LIMIT 5
            ''')
            recent_by_state = cursor.fetchall()
            
            conn.close()
            
            report = {
                'date': today,
                'collection_stats': self.collection_stats,
                'daily_activity': {
                    'new_foreclosures': new_foreclosures_today,
                    'new_rss_entries': new_rss_today
                },
                'total_records': {
                    'foreclosure_properties': total_foreclosures,
                    'rss_entries': total_rss,
                    'total': total_foreclosures + total_rss
                },
                'recent_activity_by_state': dict(recent_by_state)
            }
            
            # Save report
            report_filename = f"/tmp/foreclosure_report_{today}.json"
            with open(report_filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Daily report generated: {report_filename}")
            logger.info(f"Today's collection: {new_foreclosures_today} foreclosures, {new_rss_today} RSS entries")
            logger.info(f"Database totals: {total_foreclosures} foreclosures, {total_rss} RSS entries")
            
            return report
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return None
    
    def run_daily_collection(self):
        """Run the complete daily collection process"""
        logger.info("=" * 60)
        logger.info("STARTING DAILY FORECLOSURE DATA COLLECTION")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        success = True
        
        try:
            # Update stats
            self.collection_stats['total_runs'] += 1
            self.collection_stats['last_run'] = start_time.isoformat()
            
            # Collect county data
            if not self.collect_county_data():
                success = False
            
            # Brief pause between collections
            time.sleep(30)
            
            # Collect RSS data
            if not self.collect_rss_data():
                success = False
            
            # Clean up old data (weekly on Sundays)
            if datetime.now().weekday() == 6:  # Sunday
                self.cleanup_old_data()
            
            # Generate daily report
            self.generate_daily_report()
            
            # Update success stats
            if success:
                self.collection_stats['successful_runs'] += 1
                logger.info("✅ Daily collection completed successfully")
            else:
                self.collection_stats['failed_runs'] += 1
                logger.warning("⚠️ Daily collection completed with errors")
            
        except Exception as e:
            self.collection_stats['failed_runs'] += 1
            logger.error(f"❌ Daily collection failed: {e}")
            success = False
        
        finally:
            # Save updated stats
            self.save_collection_stats()
            
            # Log completion
            duration = datetime.now() - start_time
            logger.info(f"Collection completed in {duration.total_seconds():.1f} seconds")
            logger.info("=" * 60)
        
        return success
    
    def run_test_collection(self):
        """Run a test collection to verify everything is working"""
        logger.info("Running test collection...")
        
        # Test county scraper
        try:
            test_foreclosures = self.county_scraper.scrape_harris_county()
            logger.info(f"County test: Found {len(test_foreclosures)} foreclosures")
        except Exception as e:
            logger.error(f"County test failed: {e}")
        
        # Test RSS parser
        try:
            test_entries = self.rss_parser.parse_all_feeds()
            logger.info(f"RSS test: Processed {len(test_entries)} entries")
        except Exception as e:
            logger.error(f"RSS test failed: {e}")
        
        # Test database
        try:
            stats = self.generate_daily_report()
            if stats:
                logger.info("Database test: Successfully generated report")
            else:
                logger.error("Database test: Failed to generate report")
        except Exception as e:
            logger.error(f"Database test failed: {e}")

def main():
    """Main function to run the daily collector"""
    collector = DailyForeclosureCollector()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'test':
            # Run test collection
            collector.run_test_collection()
            
        elif command == 'collect':
            # Run single collection
            collector.run_daily_collection()
            
        elif command == 'report':
            # Generate report only
            collector.generate_daily_report()
            
        elif command == 'schedule':
            # Schedule daily collections
            logger.info("Starting scheduled foreclosure data collection...")
            logger.info("Collections will run daily at 6:00 AM")
            
            # Schedule daily collection at 6 AM
            schedule.every().day.at("06:00").do(collector.run_daily_collection)
            
            # Schedule test run every hour (for monitoring)
            schedule.every().hour.do(lambda: logger.info(f"Scheduler running... Next collection at 6:00 AM"))
            
            # Keep the scheduler running
            while True:
                schedule.run_pending()
                time.sleep(3600)  # Check every hour
                
        else:
            print("Usage: python daily_collector.py [test|collect|report|schedule]")
            print("  test     - Run test collection")
            print("  collect  - Run single collection")
            print("  report   - Generate daily report")
            print("  schedule - Start scheduled daily collections")
    
    else:
        # Default: run single collection
        collector.run_daily_collection()

if __name__ == "__main__":
    main()