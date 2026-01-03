#!/bin/bash
# Run the semi-automated skip tracer
cd "$(dirname "$0")"
source venv/bin/activate
python3 scrapers/skip_trace_assisted.py
