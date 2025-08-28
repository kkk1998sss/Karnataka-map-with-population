#!/usr/bin/env python3
"""
Data Optimization Script for Karnataka Village Data
This script pre-processes the large shapefile to improve loading performance.
"""

import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import shape
import json
import time
import os

def optimize_shapefile():
    """Optimize the shapefile for web performance"""
    
    print("🚀 Starting data optimization...")
    start_time = time.time()
    
    try:
        # Load the original shapefile
        print("📁 Loading Karnataka shapefile...")
        gdf = gpd.read_file("Karnataka.shp")
        
        print(f"✅ Loaded {len(gdf)} villages")
        print(f"📊 Available columns: {list(gdf.columns)}")
        
        # Check for required columns and handle variations
        expected_columns = {
            'state_name': ['state_name', 'state', 'state_nam'],
            'district_n': ['district_n', 'district', 'dist_nam', 'dist_name'],
            'subdistric': ['subdistric', 'subdistrict', 'sub_dist', 'subdist'],
            'village_na': ['village_na', 'village', 'village_n', 'village_name'],
            'pc11_tv_id': ['pc11_tv_id', 'census_id', 'village_id', 'id'],
            'tot_p': ['tot_p', 'population', 'pop', 'total_pop', 'total_p']
        }
        
        # Map actual columns to expected names
        column_mapping = {}
        for expected, possible_names in expected_columns.items():
            for actual in gdf.columns:
                if actual.lower() in [name.lower() for name in possible_names]:
                    column_mapping[expected] = actual
                    break
        
        print(f"🔗 Column mapping: {column_mapping}")
        
        # Rename columns for consistency
        gdf = gdf.rename(columns=column_mapping)
        
        # Ensure population column exists and is numeric
        if 'tot_p' not in gdf.columns:
            # Try to find any population-related column
            pop_columns = [col for col in gdf.columns if any(word in col.lower() for word in ['pop', 'tot', 'people'])]
            if pop_columns:
                gdf['tot_p'] = pd.to_numeric(gdf[pop_columns[0]], errors='coerce').fillna(0)
                print(f"📈 Using population column: {pop_columns[0]}")
            else:
                # Create dummy population data for testing
                gdf['tot_p'] = np.random.randint(100, 10000, len(gdf))
                print("⚠️ No population column found, using dummy data")
        
        # Convert population to numeric and handle missing values
        gdf['tot_p'] = pd.to_numeric(gdf['tot_p'], errors='coerce').fillna(0)
        
        # Calculate population statistics
        population_stats = {
            'min': float(gdf['tot_p'].min()),
            'max': float(gdf['tot_p'].max()),
            'mean': float(gdf['tot_p'].mean()),
            'median': float(gdf['tot_p'].median()),
            'total': float(gdf['tot_p'].sum())
        }
        
        print(f"📊 Population statistics:")
        for key, value in population_stats.items():
            print(f"   {key}: {value:,.0f}")
        
        # Simplify geometries for faster rendering
        print("🔧 Simplifying geometries...")
        original_vertices = sum(len(geom.coords) if hasattr(geom, 'coords') else 0 for geom in gdf.geometry)
        
        # Adaptive simplification based on geometry complexity
        tolerance = 0.0001  # Start with small tolerance
        gdf['geometry'] = gdf['geometry'].simplify(tolerance=tolerance, preserve_topology=True)
        
        simplified_vertices = sum(len(geom.coords) if hasattr(geom, 'coords') else 0 for geom in gdf.geometry)
        reduction = ((original_vertices - simplified_vertices) / original_vertices) * 100
        
        print(f"📐 Geometry simplification: {reduction:.1f}% reduction in vertices")
        
        # Convert to Web Mercator for better web performance
        print("🌐 Converting to Web Mercator projection...")
        gdf_web = gdf.to_crs(epsg=3857)
        
        # Create optimized GeoJSON
        print("💾 Creating optimized GeoJSON...")
        optimized_geojson = gdf_web.to_json()
        
        # Save optimized data
        with open("optimized_data.json", "w") as f:
            json.dump({
                "type": "FeatureCollection",
                "features": json.loads(optimized_geojson)["features"]
            }, f)
        
        # Create a lightweight version for quick preview
        print("⚡ Creating lightweight preview data...")
        preview_gdf = gdf_web.sample(min(1000, len(gdf_web)))  # Sample for preview
        preview_geojson = preview_gdf.to_json()
        
        with open("preview_data.json", "w") as f:
            json.dump({
                "type": "FeatureCollection",
                "features": json.loads(preview_geojson)["features"]
            }, f)
        
        # Save metadata
        metadata = {
            "total_villages": len(gdf),
            "population_stats": population_stats,
            "columns": list(gdf.columns),
            "geometry_type": str(gdf.geometry.geom_type.iloc[0]) if len(gdf) > 0 else "Unknown",
            "bounds": gdf.total_bounds.tolist(),
            "optimization_time": time.time() - start_time
        }
        
        with open("metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        total_time = time.time() - start_time
        print(f"✅ Optimization completed in {total_time:.2f} seconds")
        print(f"📁 Generated files:")
        print(f"   - optimized_data.json (full dataset)")
        print(f"   - preview_data.json (lightweight preview)")
        print(f"   - metadata.json (dataset information)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during optimization: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def create_sample_data():
    """Create a small sample dataset for testing if the main file is too large"""
    print("🧪 Creating sample dataset for testing...")
    
    # Create sample village data
    sample_data = {
        'type': 'FeatureCollection',
        'features': []
    }
    
    # Sample coordinates around Karnataka
    base_coords = [15.3173, 75.7139]  # Karnataka center
    
    for i in range(100):
        # Create random village locations
        lat = base_coords[0] + np.random.uniform(-2, 2)
        lon = base_coords[1] + np.random.uniform(-2, 2)
        
        # Create simple polygon (square)
        size = 0.01
        coords = [
            [lon - size, lat - size],
            [lon + size, lat - size],
            [lon + size, lat + size],
            [lon - size, lat + size],
            [lon - size, lat - size]
        ]
        
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': [coords]
            },
            'properties': {
                'village_na': f'Sample Village {i+1}',
                'district_n': f'District {i//10 + 1}',
                'subdistric': f'Subdistrict {i//5 + 1}',
                'pc11_tv_id': f'CENSUS_{i+1:04d}',
                'tot_p': np.random.randint(100, 10000)
            }
        }
        
        sample_data['features'].append(feature)
    
    # Save sample data
    with open("sample_data.json", "w") as f:
        json.dump(sample_data, f)
    
    print("✅ Sample dataset created: sample_data.json")

if __name__ == "__main__":
    print("=" * 60)
    print("🗺️  Karnataka Village Data Optimizer")
    print("=" * 60)
    
    # Check if shapefile exists
    if not os.path.exists("Karnataka.shp"):
        print("❌ Karnataka.shp not found in current directory")
        print("📁 Available files:")
        for file in os.listdir("."):
            if file.endswith(('.shp', '.dbf', '.shx')):
                print(f"   - {file}")
        
        print("\n🧪 Creating sample data for testing...")
        create_sample_data()
    else:
        # Try to optimize the real data
        success = optimize_shapefile()
        if not success:
            print("\n🧪 Creating sample data as fallback...")
            create_sample_data()
    
    print("\n🎯 Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run the web app: python main.py")
    print("3. Open browser at: http://localhost:8000")
