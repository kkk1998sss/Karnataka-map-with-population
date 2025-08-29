#!/usr/bin/env python3
"""
Data loader for Karnataka village data
"""

import gzip
import json
import os

def load_deployable_data():
    """Load deployable data from compressed JSON file"""
    try:
        if os.path.exists("deployable_data.json.gz"):
            with gzip.open("deployable_data.json.gz", "rt", encoding="utf-8") as f:
                data = json.load(f)
                print(f"📁 Loading data from: deployable_data.json.gz")
                print(f"✅ Loaded {len(data.get('villages', []))} villages")
                print(f"📊 Total population: {data.get('metadata', {}).get('total_population', 'Unknown'):,}")
                print(f"🗺️ Districts: {data.get('metadata', {}).get('district_count', 'Unknown')}")
                return data
        else:
            print("⚠️ deployable_data.json.gz not found")
            return None
    except Exception as e:
        print(f"❌ Error loading deployable data: {e}")
        return None

if __name__ == "__main__":
    data = load_deployable_data()
    if data:
        print(f"✅ Successfully loaded data with {len(data.get('villages', []))} villages")
    else:
        print("❌ Failed to load data")
