"""
California NOD (Notice of Default) Scraper System

This package provides tools for scraping foreclosure notices from
California county recorder offices, enriching them with assessor data,
and pushing leads to Google Sheets for tracking.

Modules:
    - base_scraper: Common utilities for HTTP, rate limiting, logging, Google Sheets
    - la_county_recorder: LA County NOD scraper (registrar-recorder/clerk)
    - riverside_recorder: Riverside County NOD scraper
    - property_enricher: Property data enrichment from county assessors
    - daily_collection: Main entry point for daily scraping runs

Usage:
    from scrapers.daily_collection import run_daily_collection
    run_daily_collection()

Or run directly:
    python -m scrapers.daily_collection

Configuration:
    - Google Sheet ID: 1me4hbzialZs06LGaG3U2P3CjixSakH46GSM_ZOwSApw
    - Credentials: credentials.json (service account)
"""

__version__ = "1.0.0"
__author__ = "Stop Foreclosure Fast"

# Import main classes for easier access
from .base_scraper import BaseScraper, RecordStandardizer, generate_lead_id, GoogleSheetsManager
from .la_county_recorder import LACountyRecorderScraper
from .riverside_recorder import RiversideRecorderScraper
from .property_enricher import PropertyEnricher
from .daily_collection import DailyNODCollector, run_daily_collection

__all__ = [
    "BaseScraper",
    "RecordStandardizer",
    "generate_lead_id",
    "GoogleSheetsManager",
    "LACountyRecorderScraper",
    "RiversideRecorderScraper",
    "PropertyEnricher",
    "DailyNODCollector",
    "run_daily_collection",
]
