#!/usr/bin/env python3
"""
Simple test server to verify basic Flask functionality
"""

from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({
        'status': 'healthy',
        'message': 'Foreclosure AI is running!',
        'version': '1.0.0'
    })

@app.route('/api/ai/health')
def health():
    return jsonify({
        'status': 'healthy',
        'ai_systems': {
            'basic_server': 'operational'
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)