#!/usr/bin/env python3
"""
County Foreclosure Data Scraper
Collects foreclosure data from Texas county clerk websites
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import sqlite3
from datetime import datetime, timedelta
import logging
import os
from urllib.parse import urljoin, urlparse
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CountyForeclosureScraper:
    def __init__(self, db_path="foreclosure_data.db"):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.init_database()
        
        # County configurations
        self.counties = {
            'harris': {
                'name': 'Harris County',
                'state': 'TX',
                'base_url': 'https://www.cclerk.hctx.net',
                'search_url': '/PublicRecords.aspx',
                'scraper_method': self.scrape_harris_county
            },
            'dallas': {
                'name': 'Dallas County', 
                'state': 'TX',
                'base_url': 'https://www.dallascounty.org',
                'search_url': '/government/county-clerk/recording/foreclosures.php',
                'scraper_method': self.scrape_dallas_county
            },
            'tarrant': {
                'name': 'Tarrant County',
                'state': 'TX', 
                'base_url': 'https://www.tarrantcountytx.gov',
                'search_url': '/en/county-clerk/real-estate-records/foreclosures.html',
                'scraper_method': self.scrape_tarrant_county
            }
        }
    
    def init_database(self):
        """Initialize SQLite database for foreclosure data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS foreclosure_properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT NOT NULL,
                city TEXT,
                state TEXT,
                zip_code TEXT,
                county TEXT,
                foreclosure_stage TEXT,
                auction_date TEXT,
                filing_date TEXT,
                lender TEXT,
                amount REAL,
                case_number TEXT,
                trustee TEXT,
                property_type TEXT,
                estimated_value REAL,
                source_url TEXT,
                data_source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(address, county, case_number)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraping_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                county TEXT,
                scrape_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                records_found INTEGER,
                status TEXT,
                error_message TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
    
    def respect_robots_txt(self, base_url):
        """Check robots.txt compliance"""
        try:
            robots_url = urljoin(base_url, '/robots.txt')
            response = self.session.get(robots_url, timeout=10)
            if response.status_code == 200:
                # Simple robots.txt check - in production use robotparser
                if 'Disallow: /' in response.text:
                    logger.warning(f"Robots.txt may disallow scraping for {base_url}")
                    return False
            return True
        except Exception as e:
            logger.warning(f"Could not check robots.txt for {base_url}: {e}")
            return True  # Proceed with caution
    
    def rate_limit_delay(self):
        """Respect rate limits - 1 second between requests"""
        time.sleep(1)
    
    def scrape_harris_county(self):
        """Scrape Harris County foreclosure data"""
        county_info = self.counties['harris']
        base_url = county_info['base_url']
        
        if not self.respect_robots_txt(base_url):
            logger.error("Robots.txt check failed for Harris County")
            return []
        
        try:
            # Note: This is a simplified example - actual implementation would need
            # to analyze the specific search forms and data structure
            search_url = base_url + county_info['search_url']
            
            logger.info(f"Scraping Harris County foreclosures from {search_url}")
            
            # Example implementation - would need to be customized based on actual site structure
            response = self.session.get(search_url, timeout=15)
            self.rate_limit_delay()
            
            if response.status_code != 200:
                logger.error(f"Failed to access Harris County site: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # This is where you'd parse the actual foreclosure data
            # Each county has different HTML structure, so this needs customization
            foreclosures = []
            
            # Placeholder for actual parsing logic
            # foreclosure_listings = soup.find_all('div', class_='foreclosure-listing')
            # for listing in foreclosure_listings:
            #     foreclosure_data = self.parse_harris_listing(listing)
            #     if foreclosure_data:
            #         foreclosures.append(foreclosure_data)
            
            logger.info(f"Found {len(foreclosures)} foreclosures in Harris County")
            return foreclosures
            
        except Exception as e:
            logger.error(f"Error scraping Harris County: {e}")
            self.log_scraping_attempt('harris', 0, 'error', str(e))
            return []
    
    def scrape_dallas_county(self):
        """Scrape Dallas County foreclosure data"""
        county_info = self.counties['dallas']
        
        try:
            logger.info("Scraping Dallas County foreclosures")
            
            # Similar implementation pattern as Harris County
            # Each county website has different structure
            foreclosures = []
            
            # Placeholder implementation
            logger.info(f"Found {len(foreclosures)} foreclosures in Dallas County")
            return foreclosures
            
        except Exception as e:
            logger.error(f"Error scraping Dallas County: {e}")
            self.log_scraping_attempt('dallas', 0, 'error', str(e))
            return []
    
    def scrape_tarrant_county(self):
        """Scrape Tarrant County foreclosure data"""
        county_info = self.counties['tarrant']
        
        try:
            logger.info("Scraping Tarrant County foreclosures")
            
            foreclosures = []
            
            # Placeholder implementation
            logger.info(f"Found {len(foreclosures)} foreclosures in Tarrant County")
            return foreclosures
            
        except Exception as e:
            logger.error(f"Error scraping Tarrant County: {e}")
            self.log_scraping_attempt('tarrant', 0, 'error', str(e))
            return []
    
    def parse_address(self, address_text):
        """Parse address into components"""
        try:
            # Simple address parsing - in production use a library like usaddress
            parts = address_text.strip().split(',')
            if len(parts) >= 3:
                street = parts[0].strip()
                city = parts[1].strip()
                state_zip = parts[2].strip().split()
                state = state_zip[0] if state_zip else ''
                zip_code = state_zip[1] if len(state_zip) > 1 else ''
                
                return {
                    'street': street,
                    'city': city,
                    'state': state,
                    'zip_code': zip_code
                }
        except Exception as e:
            logger.warning(f"Could not parse address: {address_text}")
        
        return {
            'street': address_text,
            'city': '',
            'state': '',
            'zip_code': ''
        }
    
    def save_foreclosure(self, foreclosure_data):
        """Save foreclosure data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO foreclosure_properties 
                (address, city, state, zip_code, county, foreclosure_stage, 
                 auction_date, filing_date, lender, amount, case_number, 
                 trustee, property_type, estimated_value, source_url, data_source, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                foreclosure_data.get('address'),
                foreclosure_data.get('city'),
                foreclosure_data.get('state'),
                foreclosure_data.get('zip_code'),
                foreclosure_data.get('county'),
                foreclosure_data.get('foreclosure_stage'),
                foreclosure_data.get('auction_date'),
                foreclosure_data.get('filing_date'),
                foreclosure_data.get('lender'),
                foreclosure_data.get('amount'),
                foreclosure_data.get('case_number'),
                foreclosure_data.get('trustee'),
                foreclosure_data.get('property_type'),
                foreclosure_data.get('estimated_value'),
                foreclosure_data.get('source_url'),
                foreclosure_data.get('data_source'),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            return cursor.lastrowid
            
        except sqlite3.IntegrityError:
            logger.debug(f"Duplicate foreclosure record: {foreclosure_data.get('address')}")
            return None
        except Exception as e:
            logger.error(f"Error saving foreclosure: {e}")
            return None
        finally:
            conn.close()
    
    def log_scraping_attempt(self, county, records_found, status, error_message=None):
        """Log scraping attempt results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scraping_log (county, records_found, status, error_message)
            VALUES (?, ?, ?, ?)
        ''', (county, records_found, status, error_message))
        
        conn.commit()
        conn.close()
    
    def scrape_all_counties(self):
        """Scrape all configured counties"""
        total_foreclosures = []
        
        for county_key, county_info in self.counties.items():
            logger.info(f"Starting scrape for {county_info['name']}")
            
            try:
                foreclosures = county_info['scraper_method']()
                
                # Save each foreclosure to database
                saved_count = 0
                for foreclosure in foreclosures:
                    foreclosure['county'] = county_info['name']
                    foreclosure['state'] = county_info['state']
                    foreclosure['data_source'] = f"{county_info['name']} County Clerk"
                    
                    if self.save_foreclosure(foreclosure):
                        saved_count += 1
                
                total_foreclosures.extend(foreclosures)
                self.log_scraping_attempt(county_key, len(foreclosures), 'success')
                
                logger.info(f"Completed {county_info['name']}: {len(foreclosures)} found, {saved_count} saved")
                
            except Exception as e:
                logger.error(f"Failed to scrape {county_info['name']}: {e}")
                self.log_scraping_attempt(county_key, 0, 'error', str(e))
            
            # Rate limiting between counties
            time.sleep(2)
        
        return total_foreclosures
    
    def export_to_csv(self, filename=None):
        """Export foreclosure data to CSV"""
        if not filename:
            filename = f"foreclosures_{datetime.now().strftime('%Y%m%d')}.csv"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT address, city, state, zip_code, county, foreclosure_stage,
                   auction_date, filing_date, lender, amount, case_number,
                   created_at, updated_at
            FROM foreclosure_properties 
            ORDER BY updated_at DESC
        ''')
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'Address', 'City', 'State', 'ZIP', 'County', 'Stage',
                'Auction Date', 'Filing Date', 'Lender', 'Amount', 'Case Number',
                'Created', 'Updated'
            ])
            
            for row in cursor.fetchall():
                writer.writerow(row)
        
        conn.close()
        logger.info(f"Data exported to {filename}")
        return filename
    
    def get_statistics(self):
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total records
        cursor.execute('SELECT COUNT(*) FROM foreclosure_properties')
        total_records = cursor.fetchone()[0]
        
        # Records by county
        cursor.execute('''
            SELECT county, COUNT(*) as count 
            FROM foreclosure_properties 
            GROUP BY county 
            ORDER BY count DESC
        ''')
        by_county = cursor.fetchall()
        
        # Recent activity
        cursor.execute('''
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM foreclosure_properties 
            WHERE created_at >= date('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        ''')
        recent_activity = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_records': total_records,
            'by_county': by_county,
            'recent_activity': recent_activity
        }

if __name__ == "__main__":
    scraper = CountyForeclosureScraper()
    
    print("🏛️ County Foreclosure Data Scraper")
    print("=" * 50)
    
    # Show current statistics
    stats = scraper.get_statistics()
    print(f"Current database contains {stats['total_records']} foreclosure records")
    
    if stats['by_county']:
        print("\nRecords by county:")
        for county, count in stats['by_county']:
            print(f"  {county}: {count}")
    
    # Run scraping
    print("\nStarting data collection...")
    foreclosures = scraper.scrape_all_counties()
    
    # Show results
    print(f"\nScraping complete. Found {len(foreclosures)} total foreclosures")
    
    # Export to CSV
    csv_file = scraper.export_to_csv()
    print(f"Data exported to: {csv_file}")
    
    # Updated statistics
    new_stats = scraper.get_statistics()
    print(f"Database now contains {new_stats['total_records']} total records")