#!/usr/bin/env python3
"""
Create Deployable Data Script
Converts large shapefile into compressed, Git-friendly format for server deployment
"""

import json
import gzip
import base64
import pickle
from pathlib import Path
import geopandas as gpd
import pandas as pd
from shapely.geometry import shape
import numpy as np

def create_deployable_data():
    """
    Convert large shapefile into compressed, deployable format
    """
    print("🔄 Creating deployable data from shapefile...")
    
    try:
        # Check if shapefile exists
        shapefile_path = Path("Karnataka.shp")
        if not shapefile_path.exists():
            print("❌ Shapefile not found. Creating sample data instead.")
            create_sample_deployable_data()
            return
        
        print(f"📁 Loading shapefile: {shapefile_path}")
        
        # Load shapefile
        gdf = gpd.read_file(shapefile_path)
        print(f"✅ Loaded {len(gdf)} villages")
        
        # Simplify geometries for web performance
        print("🔧 Simplifying geometries...")
        gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.0001, preserve_topology=True)
        
        # Convert to Web Mercator projection
        gdf = gdf.to_crs(epsg=3857)
        
        # Extract essential data
        villages_data = []
        for idx, row in gdf.iterrows():
            village_data = {
                'id': idx,
                'name': str(row.get('village_na', f'Village_{idx}')),
                'district': str(row.get('district_n', 'Unknown')),
                'subdistrict': str(row.get('subdistric', 'Unknown')),
                'population': int(row.get('tot_p', 0)),
                'census_id': str(row.get('pc11_tv_id', '')),
                'geometry': row.geometry.__geo_interface__ if row.geometry else None
            }
            villages_data.append(village_data)
        
        # Calculate population statistics for color coding
        populations = [v['population'] for v in villages_data if v['population'] > 0]
        if populations:
            q1 = np.percentile(populations, 25)
            q2 = np.percentile(populations, 50)
            q3 = np.percentile(populations, 75)
        else:
            q1 = q2 = q3 = 0
        
        # Create deployable data structure
        deployable_data = {
            'metadata': {
                'total_villages': len(villages_data),
                'total_population': sum(populations),
                'population_stats': {
                    'min': min(populations) if populations else 0,
                    'max': max(populations) if populations else 0,
                    'q1': float(q1),
                    'q2': float(q2),
                    'q3': float(q3)
                },
                'districts': list(set(v['district'] for v in villages_data)),
                'data_format': 'deployable_compressed',
                'version': '1.0'
            },
            'villages': villages_data
        }
        
        # Save as compressed JSON
        compressed_file = "deployable_data.json.gz"
        with gzip.open(compressed_file, 'wt', encoding='utf-8') as f:
            json.dump(deployable_data, f, ensure_ascii=False, separators=(',', ':'))
        
        # Also save as regular JSON for development
        with open("deployable_data.json", 'w', encoding='utf-8') as f:
            json.dump(deployable_data, f, ensure_ascii=False, indent=2)
        
        # Create a minimal version for very small deployments
        minimal_data = {
            'metadata': deployable_data['metadata'],
            'villages': villages_data[:100]  # First 100 villages for minimal version
        }
        
        with open("deployable_data_minimal.json", 'w', encoding='utf-8') as f:
            json.dump(minimal_data, f, ensure_ascii=False, separators=(',', ':'))
        
        # Get file sizes
        compressed_size = Path(compressed_file).stat().st_size / (1024 * 1024)  # MB
        json_size = Path("deployable_data.json").stat().st_size / (1024 * 1024)  # MB
        minimal_size = Path("deployable_data_minimal.json").stat().st_size / (1024 * 1024)  # MB
        
        print(f"✅ Deployable data created successfully!")
        print(f"📊 File sizes:")
        print(f"   - Compressed (gzip): {compressed_size:.2f} MB")
        print(f"   - Full JSON: {json_size:.2f} MB")
        print(f"   - Minimal JSON: {minimal_size:.2f} MB")
        print(f"   - Original shapefile: ~133 MB")
        print(f"📁 Files created:")
        print(f"   - {compressed_file} (use this for deployment)")
        print(f"   - deployable_data.json (development)")
        print(f"   - deployable_data_minimal.json (minimal deployment)")
        
        return deployable_data
        
    except Exception as e:
        print(f"❌ Error processing shapefile: {e}")
        print("🔄 Falling back to sample data...")
        create_sample_deployable_data()
        return None

def create_sample_deployable_data():
    """
    Create sample deployable data when shapefile is not available
    """
    print("🎯 Creating sample deployable data...")
    
    # Generate 100 realistic sample villages
    districts = ['Bangalore Urban', 'Mysore', 'Mandya', 'Hassan', 'Tumkur']
    sample_villages = []
    
    for i in range(100):
        district = districts[i % len(districts)]
        population = np.random.randint(100, 10000)
        
        # Create simple polygon (square around a point)
        lat = 12.9716 + (np.random.random() - 0.5) * 2  # Around Bangalore
        lon = 77.5946 + (np.random.random() - 0.5) * 2
        
        # Create a simple square polygon
        square_size = 0.01
        geometry = {
            "type": "Polygon",
            "coordinates": [[
                [lon - square_size, lat - square_size],
                [lon + square_size, lat - square_size],
                [lon + square_size, lat + square_size],
                [lon - square_size, lat + square_size],
                [lon - square_size, lat - square_size]
            ]]
        }
        
        village_data = {
            'id': i,
            'name': f'Sample_Village_{i+1}',
            'district': district,
            'subdistrict': f'Subdistrict_{i+1}',
            'population': population,
            'census_id': f'SAMPLE_{i+1:06d}',
            'geometry': geometry
        }
        sample_villages.append(village_data)
    
    # Calculate population statistics
    populations = [v['population'] for v in sample_villages]
    q1 = np.percentile(populations, 25)
    q2 = np.percentile(populations, 50)
    q3 = np.percentile(populations, 75)
    
    deployable_data = {
        'metadata': {
            'total_villages': len(sample_villages),
            'total_population': sum(populations),
            'population_stats': {
                'min': min(populations),
                'max': max(populations),
                'q1': float(q1),
                'q2': float(q2),
                'q3': float(q3)
            },
            'districts': districts,
            'data_format': 'sample_deployable',
            'version': '1.0',
            'note': 'This is sample data. Use real shapefile for production.'
        },
        'villages': sample_villages
    }
    
    # Save files
    with open("deployable_data.json", 'w', encoding='utf-8') as f:
        json.dump(deployable_data, f, ensure_ascii=False, indent=2)
    
    with open("deployable_data_minimal.json", 'w', encoding='utf-8') as f:
        json.dump(deployable_data, f, ensure_ascii=False, separators=(',', ':'))
    
    # Compress
    with gzip.open("deployable_data.json.gz", 'wt', encoding='utf-8') as f:
        json.dump(deployable_data, f, ensure_ascii=False, separators=(',', ':'))
    
    print(f"✅ Sample deployable data created!")
    print(f"📊 Generated {len(sample_villages)} sample villages")
    print(f"📁 Files created for deployment")

def create_loader_script():
    """
    Create a data loader script that can load the deployable data
    """
    loader_code = '''#!/usr/bin/env python3
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
        print("\\n🎯 Data loaded successfully!")
        print(f"📁 Data format: {data['metadata']['data_format']}")
        print(f"🔢 Version: {data['metadata']['version']}")
    else:
        print("\\n❌ Failed to load data")
'''
    
    with open("data_loader.py", 'w', encoding='utf-8') as f:
        f.write(loader_code)
    
    print("✅ Created data_loader.py for easy data loading")

if __name__ == "__main__":
    print("🚀 Karnataka Village Data Converter")
    print("=" * 50)
    
    # Create deployable data
    data = create_deployable_data()
    
    # Create loader script
    create_loader_script()
    
    print("\n🎉 Conversion complete!")
    print("\n📋 Next steps:")
    print("1. Add large files to .gitignore (already done)")
    print("2. Commit deployable_data.json.gz to Git")
    print("3. Deploy to server with the compressed data file")
    print("4. Use data_loader.py to load the data in your application")
