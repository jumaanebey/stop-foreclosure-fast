#!/usr/bin/env python3
"""
Setup script for Foreclosure Data Collection System
Initializes the database and runs initial data collection
"""

import os
import sys
import sqlite3
import subprocess
import json
from datetime import datetime

def install_requirements():
    """Install required Python packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def create_directory_structure():
    """Create necessary directories"""
    print("📁 Creating directory structure...")
    
    directories = [
        '/tmp/foreclosure_data',
        '/tmp/foreclosure_reports',
        '/tmp/foreclosure_logs'
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"  Created: {directory}")
        except Exception as e:
            print(f"  Warning: Could not create {directory}: {e}")
    
    print("✅ Directory structure created")

def initialize_database():
    """Initialize the foreclosure database"""
    print("🗄️ Initializing foreclosure database...")
    
    try:
        from county_scraper import CountyForeclosureScraper
        from rss_parser import ForeclosureRSSParser
        
        # Initialize both databases
        county_scraper = CountyForeclosureScraper('/tmp/foreclosure_data.db')
        rss_parser = ForeclosureRSSParser('/tmp/foreclosure_data.db')
        
        print("✅ Database initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def create_sample_data():
    """Create sample foreclosure data for testing"""
    print("📝 Creating sample foreclosure data...")
    
    try:
        conn = sqlite3.connect('/tmp/foreclosure_data.db')
        cursor = conn.cursor()
        
        # Sample foreclosure properties
        sample_properties = [
            {
                'address': '123 Main Street',
                'city': 'Houston',
                'state': 'TX',
                'zip_code': '77001',
                'county': 'Harris County',
                'foreclosure_stage': 'Notice of Default',
                'auction_date': '2024-03-15',
                'filing_date': '2024-01-15',
                'lender': 'Wells Fargo Bank',
                'amount': 450000.00,
                'case_number': 'FC-2024-001',
                'property_type': 'Single Family',
                'estimated_value': 520000.00,
                'data_source': 'Sample Data'
            },
            {
                'address': '456 Oak Avenue',
                'city': 'Dallas',
                'state': 'TX',
                'zip_code': '75201',
                'county': 'Dallas County',
                'foreclosure_stage': 'Trustee Sale',
                'auction_date': '2024-02-28',
                'filing_date': '2023-12-01',
                'lender': 'Bank of America',
                'amount': 380000.00,
                'case_number': 'FC-2024-002',
                'property_type': 'Townhouse',
                'estimated_value': 420000.00,
                'data_source': 'Sample Data'
            },
            {
                'address': '789 Pine Street',
                'city': 'San Antonio',
                'state': 'TX',
                'zip_code': '78201',
                'county': 'Bexar County',
                'foreclosure_stage': 'REO',
                'auction_date': '2024-01-10',
                'filing_date': '2023-10-15',
                'lender': 'Chase Bank',
                'amount': 290000.00,
                'case_number': 'FC-2024-003',
                'property_type': 'Condo',
                'estimated_value': 310000.00,
                'data_source': 'Sample Data'
            }
        ]
        
        for prop in sample_properties:
            cursor.execute('''
                INSERT INTO foreclosure_properties 
                (address, city, state, zip_code, county, foreclosure_stage, 
                 auction_date, filing_date, lender, amount, case_number, 
                 property_type, estimated_value, data_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                prop['address'], prop['city'], prop['state'], prop['zip_code'],
                prop['county'], prop['foreclosure_stage'], prop['auction_date'],
                prop['filing_date'], prop['lender'], prop['amount'], prop['case_number'],
                prop['property_type'], prop['estimated_value'], prop['data_source']
            ))
        
        # Sample RSS entries
        sample_rss = [
            {
                'title': 'Foreclosure - 321 Elm Street, Austin, TX 78701',
                'link': 'https://example.com/foreclosure/321-elm',
                'address': '321 Elm Street',
                'city': 'Austin',
                'state': 'TX',
                'zip_code': '78701',
                'price': 395000.00,
                'property_type': 'Single Family',
                'foreclosure_stage': 'Auction'
            },
            {
                'title': 'REO Property - 654 Maple Drive, Fort Worth, TX 76101',
                'link': 'https://example.com/reo/654-maple',
                'address': '654 Maple Drive',
                'city': 'Fort Worth',
                'state': 'TX',
                'zip_code': '76101',
                'price': 275000.00,
                'property_type': 'Townhouse',
                'foreclosure_stage': 'REO'
            }
        ]
        
        for entry in sample_rss:
            cursor.execute('''
                INSERT INTO rss_entries 
                (title, link, address, city, state, zip_code, price, property_type, foreclosure_stage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry['title'], entry['link'], entry['address'], entry['city'],
                entry['state'], entry['zip_code'], entry['price'], 
                entry['property_type'], entry['foreclosure_stage']
            ))
        
        conn.commit()
        conn.close()
        
        print("✅ Sample data created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Sample data creation failed: {e}")
        return False

def test_system():
    """Test the foreclosure data collection system"""
    print("🧪 Testing foreclosure data collection system...")
    
    try:
        from daily_collector import DailyForeclosureCollector
        
        collector = DailyForeclosureCollector('/tmp/foreclosure_data.db')
        
        # Test database connection
        stats = collector.generate_daily_report()
        if stats:
            print("✅ Database test passed")
            print(f"  Total records: {stats['total_records']['total']}")
        else:
            print("❌ Database test failed")
            return False
        
        # Test county scraper
        print("  Testing county scraper...")
        test_result = collector.county_scraper.get_statistics()
        print(f"  County scraper ready: {test_result['total_records']} existing records")
        
        # Test RSS parser
        print("  Testing RSS parser...")
        rss_stats = collector.rss_parser.get_statistics()
        print(f"  RSS parser ready: {rss_stats['total_entries']} existing entries")
        
        print("✅ System test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False

def create_startup_script():
    """Create a startup script for the foreclosure data collector"""
    print("📝 Creating startup script...")
    
    startup_script = '''#!/bin/bash
# Foreclosure Data Collector Startup Script

cd "$(dirname "$0")"

echo "🏠 Starting Foreclosure Data Collection System..."
echo "Time: $(date)"

# Run daily collection
python3 daily_collector.py collect

# Optional: Start scheduled collections (uncomment to enable)
# python3 daily_collector.py schedule

echo "Collection completed at: $(date)"
'''
    
    try:
        with open('start_collector.sh', 'w') as f:
            f.write(startup_script)
        
        # Make it executable
        os.chmod('start_collector.sh', 0o755)
        
        print("✅ Startup script created: start_collector.sh")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create startup script: {e}")
        return False

def print_usage_instructions():
    """Print usage instructions"""
    print("\n" + "=" * 60)
    print("🎉 FORECLOSURE DATA COLLECTION SYSTEM SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("📋 USAGE INSTRUCTIONS:")
    print()
    print("1. Run a test collection:")
    print("   python3 daily_collector.py test")
    print()
    print("2. Run a single data collection:")
    print("   python3 daily_collector.py collect")
    print()
    print("3. Generate a daily report:")
    print("   python3 daily_collector.py report")
    print()
    print("4. Start scheduled daily collections:")
    print("   python3 daily_collector.py schedule")
    print()
    print("5. Use the startup script:")
    print("   ./start_collector.sh")
    print()
    print("📊 INTEGRATION WITH YOUR WEBSITE:")
    print()
    print("The foreclosure data is now available via API endpoints:")
    print("• /api/foreclosure/lookup - Lookup property data")
    print("• /api/foreclosure/area-insights - Get area statistics")
    print("• /api/foreclosure/stats - Database statistics")
    print()
    print("Database location: /tmp/foreclosure_data.db")
    print("Reports location: /tmp/foreclosure_reports/")
    print("Logs location: /tmp/foreclosure_logs/")
    print()
    print("=" * 60)

def main():
    """Main setup function"""
    print("🏠 FORECLOSURE DATA COLLECTION SYSTEM SETUP")
    print("=" * 60)
    print()
    
    success = True
    
    # Install requirements
    if not install_requirements():
        success = False
    
    # Create directories
    create_directory_structure()
    
    # Initialize database
    if not initialize_database():
        success = False
    
    # Create sample data
    if not create_sample_data():
        success = False
    
    # Test system
    if not test_system():
        success = False
    
    # Create startup script
    if not create_startup_script():
        success = False
    
    if success:
        print_usage_instructions()
    else:
        print("\n❌ Setup completed with some errors. Please review the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()