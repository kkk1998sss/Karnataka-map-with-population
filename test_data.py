#!/usr/bin/env python3
"""
Test script to verify data structure and debug issues
"""

import json
import os

def test_sample_data():
    """Test if sample data exists and is valid"""
    print("🧪 Testing sample data...")
    
    if not os.path.exists("sample_data.json"):
        print("❌ sample_data.json not found")
        return False
    
    try:
        with open("sample_data.json", "r") as f:
            data = json.load(f)
        
        print(f"✅ Sample data loaded successfully")
        print(f"📊 Type: {type(data)}")
        print(f"📊 Keys: {list(data.keys())}")
        
        if 'features' in data:
            print(f"✅ Features found: {len(data['features'])}")
            
            # Check first feature
            if data['features']:
                first_feature = data['features'][0]
                print(f"📊 First feature keys: {list(first_feature.keys())}")
                
                if 'properties' in first_feature:
                    props = first_feature['properties']
                    print(f"📊 Properties: {list(props.keys())}")
                    
                    # Check required fields
                    required_fields = ['village_na', 'district_n', 'subdistric', 'pc11_tv_id', 'tot_p']
                    for field in required_fields:
                        if field in props:
                            print(f"✅ {field}: {props[field]}")
                        else:
                            print(f"❌ {field}: Missing")
                else:
                    print("❌ No properties in feature")
            else:
                print("❌ No features found")
        else:
            print("❌ No 'features' key found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing sample data: {e}")
        return False

def test_api_response():
    """Test the API response structure"""
    print("\n🌐 Testing API response...")
    
    try:
        import requests
        
        # Test the main data endpoint
        response = requests.get("http://localhost:8000/api/data", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API response received")
            print(f"📊 Response keys: {list(data.keys())}")
            
            if 'topojson' in data:
                topojson = data['topojson']
                if isinstance(topojson, str):
                    parsed = json.loads(topojson)
                else:
                    parsed = topojson
                
                print(f"📊 TopoJSON type: {type(parsed)}")
                print(f"📊 TopoJSON keys: {list(parsed.keys())}")
                
                if 'features' in parsed:
                    print(f"✅ Features found: {len(parsed['features'])}")
                else:
                    print("❌ No features in TopoJSON")
            
            if 'population_stats' in data:
                stats = data['population_stats']
                print(f"📊 Population stats: {stats}")
            
            if 'village_count' in data:
                print(f"📊 Village count: {data['village_count']}")
            
            return True
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"📊 Response: {response.text}")
            return False
            
    except ImportError:
        print("⚠️ Requests not available, skipping API test")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def create_minimal_sample_data():
    """Create a minimal sample data file for testing"""
    print("\n🔧 Creating minimal sample data...")
    
    minimal_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [75.7139, 15.3173],
                        [75.7239, 15.3173],
                        [75.7239, 15.3273],
                        [75.7139, 15.3273],
                        [75.7139, 15.3173]
                    ]]
                },
                "properties": {
                    "village_na": "Test Village 1",
                    "district_n": "Test District",
                    "subdistric": "Test Subdistrict",
                    "pc11_tv_id": "TEST_001",
                    "tot_p": 5000
                }
            }
        ]
    }
    
    try:
        with open("minimal_sample.json", "w") as f:
            json.dump(minimal_data, f, indent=2)
        print("✅ Minimal sample data created: minimal_sample.json")
        return True
    except Exception as e:
        print(f"❌ Error creating minimal data: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 Karnataka Village Data Test")
    print("=" * 60)
    
    # Test sample data
    sample_ok = test_sample_data()
    
    # Test API if available
    api_ok = test_api_response()
    
    # Create minimal data if needed
    if not sample_ok:
        create_minimal_sample_data()
    
    print("\n📋 Test Summary:")
    print(f"   Sample Data: {'✅' if sample_ok else '❌'}")
    print(f"   API Response: {'✅' if api_ok else '❌'}")
    
    if not sample_ok:
        print("\n💡 Recommendations:")
        print("   1. Run: python simple_data_loader.py")
        print("   2. Check if sample_data.json was created")
        print("   3. Verify the JSON structure")
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    main()
