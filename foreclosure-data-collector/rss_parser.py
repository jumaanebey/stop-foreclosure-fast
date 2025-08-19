#!/usr/bin/env python3
"""
RSS Feed Parser for Foreclosure Listings
Collects foreclosure data from various RSS feeds
"""

import feedparser
import requests
import json
import sqlite3
import re
from datetime import datetime, timedelta
import logging
from urllib.parse import urlparse, urljoin
import time
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ForeclosureRSSParser:
    def __init__(self, db_path="foreclosure_data.db"):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # RSS feed sources
        self.rss_feeds = {
            'foreclosure_listings': [
                {
                    'name': 'ForeclosureListings.com - Texas',
                    'url': 'https://www.foreclosurelistings.com/rss/texas.xml',
                    'state': 'TX',
                    'active': True
                },
                {
                    'name': 'ForeclosureListings.com - California', 
                    'url': 'https://www.foreclosurelistings.com/rss/california.xml',
                    'state': 'CA',
                    'active': True
                },
                {
                    'name': 'ForeclosureListings.com - Florida',
                    'url': 'https://www.foreclosurelistings.com/rss/florida.xml', 
                    'state': 'FL',
                    'active': True
                }
            ],
            'reo_properties': [
                {
                    'name': 'Bank REO Properties',
                    'url': 'https://www.reonetwork.com/rss/properties.xml',
                    'type': 'REO',
                    'active': False  # Example - would need actual working feeds
                }
            ],
            'auction_sites': [
                {
                    'name': 'Auction.com Properties',
                    'url': 'https://www.auction.com/rss/foreclosures.xml',
                    'type': 'Auction',
                    'active': False  # Example - would need actual working feeds
                }
            ]
        }
        
        self.init_database()
    
    def init_database(self):
        """Initialize RSS-specific database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # RSS feed tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rss_feeds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feed_name TEXT UNIQUE,
                feed_url TEXT,
                last_parsed TIMESTAMP,
                status TEXT,
                total_entries INTEGER DEFAULT 0,
                active BOOLEAN DEFAULT 1
            )
        ''')
        
        # RSS entries
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rss_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feed_id INTEGER,
                title TEXT,
                link TEXT UNIQUE,
                description TEXT,
                published TIMESTAMP,
                guid TEXT,
                address TEXT,
                city TEXT,
                state TEXT,
                zip_code TEXT,
                price REAL,
                property_type TEXT,
                foreclosure_stage TEXT,
                raw_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (feed_id) REFERENCES rss_feeds (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("RSS database tables initialized")
    
    def register_feed(self, feed_info):
        """Register RSS feed in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO rss_feeds (feed_name, feed_url, status, active)
            VALUES (?, ?, 'pending', ?)
        ''', (feed_info['name'], feed_info['url'], feed_info['active']))
        
        conn.commit()
        conn.close()
    
    def parse_feed(self, feed_info):
        """Parse a single RSS feed"""
        logger.info(f"Parsing feed: {feed_info['name']}")
        
        try:
            # Parse RSS feed
            feed = feedparser.parse(feed_info['url'])
            
            if feed.bozo:
                logger.warning(f"Feed may have issues: {feed_info['name']}")
            
            entries = []
            for entry in feed.entries:
                parsed_entry = self.parse_entry(entry, feed_info)
                if parsed_entry:
                    entries.append(parsed_entry)
            
            # Update feed status
            self.update_feed_status(feed_info['name'], 'success', len(entries))
            
            logger.info(f"Parsed {len(entries)} entries from {feed_info['name']}")
            return entries
            
        except Exception as e:
            logger.error(f"Error parsing feed {feed_info['name']}: {e}")
            self.update_feed_status(feed_info['name'], 'error', 0)
            return []
    
    def parse_entry(self, entry, feed_info):
        """Parse individual RSS entry"""
        try:
            # Extract basic information
            parsed_entry = {
                'title': entry.get('title', ''),
                'link': entry.get('link', ''),
                'description': entry.get('description', ''),
                'published': self.parse_date(entry.get('published', '')),
                'guid': entry.get('guid', entry.get('id', '')),
                'raw_content': str(entry),
                'feed_name': feed_info['name'],
                'state': feed_info.get('state', ''),
                'foreclosure_stage': feed_info.get('type', 'Unknown')
            }
            
            # Extract address and location from title/description
            location_info = self.extract_location(entry)
            parsed_entry.update(location_info)
            
            # Extract price information
            price_info = self.extract_price(entry)
            parsed_entry.update(price_info)
            
            # Extract property type
            property_type = self.extract_property_type(entry)
            parsed_entry['property_type'] = property_type
            
            return parsed_entry
            
        except Exception as e:
            logger.warning(f"Error parsing entry: {e}")
            return None
    
    def extract_location(self, entry):
        """Extract location information from RSS entry"""
        text = f"{entry.get('title', '')} {entry.get('description', '')}"
        
        location_info = {
            'address': '',
            'city': '',
            'state': '',
            'zip_code': ''
        }
        
        # Look for ZIP code pattern
        zip_match = re.search(r'\\b(\\d{5}(?:-\\d{4})?)\\b', text)
        if zip_match:
            location_info['zip_code'] = zip_match.group(1)
        
        # Look for state abbreviations
        state_match = re.search(r'\\b([A-Z]{2})\\b', text)
        if state_match:
            location_info['state'] = state_match.group(1)
        
        # Try to extract city names (common patterns)
        city_patterns = [
            r'([A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*),\\s*[A-Z]{2}',  # City, ST
            r'in\\s+([A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*)',  # in City
        ]
        
        for pattern in city_patterns:
            city_match = re.search(pattern, text)
            if city_match:
                location_info['city'] = city_match.group(1)
                break
        
        # Try to extract street address
        address_patterns = [
            r'(\\d+\\s+[A-Za-z\\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Circle|Cir|Court|Ct))',
            r'(\\d+\\s+[A-Za-z\\s]+)',  # Fallback pattern
        ]
        
        for pattern in address_patterns:
            address_match = re.search(pattern, text, re.IGNORECASE)
            if address_match:
                location_info['address'] = address_match.group(1).strip()
                break
        
        return location_info
    
    def extract_price(self, entry):
        """Extract price information from RSS entry"""
        text = f"{entry.get('title', '')} {entry.get('description', '')}"
        
        price_info = {
            'price': None
        }
        
        # Look for price patterns
        price_patterns = [
            r'\\$([\\d,]+(?:\\.\\d{2})?)',  # $123,456.00
            r'([\\d,]+)\\s*dollars?',       # 123,456 dollars
            r'Price:?\\s*\\$?([\\d,]+)',    # Price: $123,456
            r'Starting.*\\$([\\d,]+)',      # Starting at $123,456
        ]
        
        for pattern in price_patterns:
            price_match = re.search(pattern, text, re.IGNORECASE)
            if price_match:
                try:
                    price_str = price_match.group(1).replace(',', '')
                    price_info['price'] = float(price_str)
                    break
                except ValueError:
                    continue
        
        return price_info
    
    def extract_property_type(self, entry):
        """Extract property type from RSS entry"""
        text = f"{entry.get('title', '')} {entry.get('description', '')}".lower()
        
        property_types = {
            'single family': ['single family', 'single-family', 'house', 'home'],
            'condo': ['condo', 'condominium'],
            'townhouse': ['townhouse', 'townhome', 'town home'],
            'multi-family': ['duplex', 'triplex', 'fourplex', 'multi-family', 'apartment'],
            'commercial': ['commercial', 'office', 'retail', 'warehouse'],
            'land': ['land', 'lot', 'acreage', 'vacant']
        }
        
        for prop_type, keywords in property_types.items():
            if any(keyword in text for keyword in keywords):
                return prop_type
        
        return 'Unknown'
    
    def parse_date(self, date_string):
        """Parse RSS date string to ISO format"""
        if not date_string:
            return datetime.now().isoformat()
        
        try:
            # feedparser usually handles this
            parsed_time = feedparser._parse_date(date_string)
            if parsed_time:
                return datetime(*parsed_time[:6]).isoformat()
        except:
            pass
        
        return datetime.now().isoformat()
    
    def save_entry(self, entry, feed_id):
        """Save RSS entry to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO rss_entries 
                (feed_id, title, link, description, published, guid, address, 
                 city, state, zip_code, price, property_type, foreclosure_stage, raw_content)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                feed_id,
                entry['title'],
                entry['link'],
                entry['description'],
                entry['published'],
                entry['guid'],
                entry['address'],
                entry['city'],
                entry['state'],
                entry['zip_code'],
                entry['price'],
                entry['property_type'],
                entry['foreclosure_stage'],
                entry['raw_content']
            ))
            
            conn.commit()
            return cursor.lastrowid
            
        except Exception as e:
            logger.warning(f"Error saving entry: {e}")
            return None
        finally:
            conn.close()
    
    def get_feed_id(self, feed_name):
        """Get feed ID from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM rss_feeds WHERE feed_name = ?', (feed_name,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def update_feed_status(self, feed_name, status, entry_count):
        """Update feed parsing status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE rss_feeds 
            SET last_parsed = ?, status = ?, total_entries = total_entries + ?
            WHERE feed_name = ?
        ''', (datetime.now().isoformat(), status, entry_count, feed_name))
        
        conn.commit()
        conn.close()
    
    def parse_all_feeds(self):
        """Parse all active RSS feeds"""
        all_entries = []
        
        # Register all feeds first
        for category, feeds in self.rss_feeds.items():
            for feed_info in feeds:
                if feed_info['active']:
                    self.register_feed(feed_info)
        
        # Parse each active feed
        for category, feeds in self.rss_feeds.items():
            logger.info(f"Processing {category} feeds")
            
            for feed_info in feeds:
                if not feed_info['active']:
                    continue
                
                try:
                    entries = self.parse_feed(feed_info)
                    
                    # Save entries to database
                    feed_id = self.get_feed_id(feed_info['name'])
                    if feed_id:
                        saved_count = 0
                        for entry in entries:
                            if self.save_entry(entry, feed_id):
                                saved_count += 1
                        
                        logger.info(f"Saved {saved_count} new entries from {feed_info['name']}")
                    
                    all_entries.extend(entries)
                    
                    # Rate limiting between feeds
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Failed to process feed {feed_info['name']}: {e}")
        
        return all_entries
    
    def get_recent_entries(self, days=7, limit=100):
        """Get recent RSS entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT re.*, rf.feed_name
            FROM rss_entries re
            JOIN rss_feeds rf ON re.feed_id = rf.id
            WHERE re.created_at >= ?
            ORDER BY re.created_at DESC
            LIMIT ?
        ''', (since_date, limit))
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def search_entries(self, location=None, price_min=None, price_max=None, property_type=None):
        """Search RSS entries with filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        conditions = []
        params = []
        
        if location:
            conditions.append('(city LIKE ? OR state LIKE ? OR zip_code LIKE ?)')
            params.extend([f'%{location}%', f'%{location}%', f'%{location}%'])
        
        if price_min:
            conditions.append('price >= ?')
            params.append(price_min)
        
        if price_max:
            conditions.append('price <= ?')
            params.append(price_max)
        
        if property_type:
            conditions.append('property_type = ?')
            params.append(property_type)
        
        where_clause = 'WHERE ' + ' AND '.join(conditions) if conditions else ''
        
        query = f'''
            SELECT re.*, rf.feed_name
            FROM rss_entries re
            JOIN rss_feeds rf ON re.feed_id = rf.id
            {where_clause}
            ORDER BY re.created_at DESC
            LIMIT 50
        '''
        
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_statistics(self):
        """Get RSS parsing statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total entries
        cursor.execute('SELECT COUNT(*) FROM rss_entries')
        total_entries = cursor.fetchone()[0]
        
        # Entries by feed
        cursor.execute('''
            SELECT rf.feed_name, COUNT(re.id) as count
            FROM rss_feeds rf
            LEFT JOIN rss_entries re ON rf.id = re.feed_id
            GROUP BY rf.feed_name
            ORDER BY count DESC
        ''')
        by_feed = cursor.fetchall()
        
        # Recent activity
        cursor.execute('''
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM rss_entries
            WHERE created_at >= date('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        ''')
        recent_activity = cursor.fetchall()
        
        # Feed status
        cursor.execute('''
            SELECT feed_name, status, last_parsed, total_entries
            FROM rss_feeds
            ORDER BY last_parsed DESC
        ''')
        feed_status = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_entries': total_entries,
            'by_feed': by_feed,
            'recent_activity': recent_activity,
            'feed_status': feed_status
        }

if __name__ == "__main__":
    parser = ForeclosureRSSParser()
    
    print("📡 RSS Foreclosure Feed Parser")
    print("=" * 50)
    
    # Show current statistics
    stats = parser.get_statistics()
    print(f"Current database contains {stats['total_entries']} RSS entries")
    
    if stats['by_feed']:
        print("\\nEntries by feed:")
        for feed, count in stats['by_feed']:
            print(f"  {feed}: {count}")
    
    print("\\nFeed status:")
    for feed_name, status, last_parsed, total in stats['feed_status']:
        print(f"  {feed_name}: {status} (Last: {last_parsed or 'Never'}, Total: {total})")
    
    # Parse all feeds
    print("\\nStarting RSS feed parsing...")
    entries = parser.parse_all_feeds()
    
    print(f"\\nParsing complete. Processed {len(entries)} entries")
    
    # Show recent entries
    recent = parser.get_recent_entries(days=1, limit=5)
    if recent:
        print("\\nRecent entries:")
        for entry in recent:
            price_info = f" - ${entry['price']:,.0f}" if entry['price'] else ""
            print(f"  {entry['title'][:80]}...{price_info}")
    
    # Updated statistics
    new_stats = parser.get_statistics()
    print(f"\\nDatabase now contains {new_stats['total_entries']} total RSS entries")