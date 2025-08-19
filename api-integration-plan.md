# Foreclosure Data API Integration Plan

## Phase 1: Free Trial Setup (Week 1)

### ATTOM Data API - Primary Source
- Sign up for 30-day free trial at https://api.developer.attomdata.com/home
- Get API key for 500 calls/day
- Test endpoints:
  - `/property/detail` - Property information
  - `/avm/detail` - Automated valuation
  - `/saleshistory/detail` - Transaction history

### Integration Points
1. **Lead Enhancement**: When user enters address in chatbot, lookup property details
2. **Risk Assessment**: Use foreclosure status to improve AI scoring
3. **Property Valuation**: Show estimated value to users
4. **Market Data**: Provide context about local foreclosure rates

## Phase 2: Backend Integration (Week 2)

### Python Enhancement (app_simple.py)
```python
# Add to existing backend
import requests
import os

ATTOM_API_KEY = os.getenv('ATTOM_API_KEY', '')
ATTOM_BASE_URL = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0'

async def get_property_data(address):
    """Get property details from ATTOM API"""
    headers = {
        'Accept': 'application/json',
        'apikey': ATTOM_API_KEY
    }
    
    # Property search endpoint
    url = f"{ATTOM_BASE_URL}/property/address"
    params = {
        'address1': address,
        'address2': '',  # city, state, zip if needed
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"API Error: {e}")
    
    return None

async def check_foreclosure_status(property_id):
    """Check foreclosure status for property"""
    url = f"{ATTOM_BASE_URL}/saleshistory/detail"
    # Implementation for foreclosure check
    pass
```

### New API Endpoints
```python
@app.route('/api/property/lookup', methods=['POST'])
def property_lookup():
    """Lookup property details for chatbot"""
    data = request.get_json()
    address = data.get('address', '')
    
    # Get property data from ATTOM
    property_data = get_property_data(address)
    
    if property_data:
        return jsonify({
            'success': True,
            'property': {
                'value': property_data.get('estimate', 'Unknown'),
                'foreclosure_risk': assess_foreclosure_risk(property_data),
                'market_data': get_local_market_data(property_data)
            }
        })
    
    return jsonify({'success': False, 'error': 'Property not found'})
```

## Phase 3: Frontend Integration (Week 3)

### Chatbot Enhancement
Update `js/ai-functions.js` to include property lookup:

```javascript
// Add to existing chatbot flow
async function lookupProperty(address) {
    try {
        const response = await fetch('/api/property/lookup', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({address: address})
        });
        
        const data = await response.json();
        if (data.success) {
            return data.property;
        }
    } catch (error) {
        console.log('Property lookup unavailable');
    }
    return null;
}

// Enhanced address collection step
function showStep5Enhanced() {
    // ... existing code ...
    
    // Add property lookup after address entry
    setTimeout(async () => {
        const address = getFullAddress();
        const propertyData = await lookupProperty(address);
        
        if (propertyData) {
            // Show property insights to user
            showPropertyInsights(propertyData);
        }
    }, 1000);
}
```

## Phase 4: Advanced Features (Week 4+)

### Real-Time Market Updates
- Daily foreclosure report generation
- Automated lead scoring based on local foreclosure rates
- Property value tracking for existing leads

### Enhanced User Experience
- "Properties in your area" insights
- Market trend sharing in chatbot
- Personalized urgency messaging based on local data

## Cost Analysis

### Free Tier Usage (Month 1)
- ATTOM Data: 30-day trial, up to 15,000 calls
- Estimated cost after trial: $200-500/month depending on volume

### ROI Projections
- Enhanced lead quality through property data
- Higher conversion rates with personalized insights
- Competitive advantage with real-time market data

## Implementation Priority
1. **Week 1**: ATTOM API setup and testing
2. **Week 2**: Basic property lookup integration
3. **Week 3**: Chatbot enhancement with property data
4. **Week 4**: Advanced analytics and reporting

## Success Metrics
- Improved lead conversion rates
- More accurate risk assessment
- Enhanced user engagement with property insights
- Reduced manual property research time