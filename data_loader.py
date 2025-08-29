#!/usr/bin/env python3
"""
Data Loader for Deployable Data
Loads compressed or JSON data files for the Karnataka Village Visualization
"""

import json
import gzip
from pathlib import Path
from typing import Dict, Any, Optional

def load_deployable_data(data_file: str = None) -> Optional[Dict[str, Any]]:
    """
    Load deployable data from various formats
    
    Args:
        data_file: Path to data file. If None, tries to find best available file.
    
    Returns:
        Dictionary containing village data and metadata
    """
    if data_file is None:
        # Try to find the best available data file
        possible_files = [
            "deployable_data.json.gz",      # Compressed (best for deployment)
            "deployable_data.json",         # Full JSON
            "deployable_data_minimal.json", # Minimal JSON
            "sample_data.json"              # Fallback sample data
        ]
        
        for file_path in possible_files:
            if Path(file_path).exists():
                data_file = file_path
                break
    
    if not data_file or not Path(data_file).exists():
        print(f"❌ No data file found. Please run create_deployable_data.py first.")
        return None
    
    try:
        print(f"📁 Loading data from: {data_file}")
        
        if data_file.endswith('.gz'):
            # Load compressed data
            with gzip.open(data_file, 'rt', encoding='utf-8') as f:
                data = json.load(f)
        else:
            # Load regular JSON
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        
        print(f"✅ Loaded {data['metadata']['total_villages']} villages")
        print(f"📊 Total population: {data['metadata']['total_population']:,}")
        print(f"🗺️ Districts: {len(data['metadata']['districts'])}")
        
        return data
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None

def get_village_by_id(data: Dict[str, Any], village_id: int) -> Optional[Dict[str, Any]]:
    """Get village data by ID"""
    for village in data['villages']:
        if village['id'] == village_id:
            return village
    return None

def get_villages_by_district(data: Dict[str, Any], district: str) -> list:
    """Get all villages in a specific district"""
    return [v for v in data['villages'] if v['district'].lower() == district.lower()]

def get_population_stats(data: Dict[str, Any]) -> Dict[str, Any]:
    """Get population statistics"""
    return data['metadata']['population_stats']

if __name__ == "__main__":
    # Test the loader
    data = load_deployable_data()
    if data:
        print("\n🎯 Data loaded successfully!")
        print(f"📁 Data format: {data['metadata']['data_format']}")
        print(f"🔢 Version: {data['metadata']['version']}")
    else:
        print("\n❌ Failed to load data")
