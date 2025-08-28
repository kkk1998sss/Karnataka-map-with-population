#!/usr/bin/env python3
"""
Read Karnataka shapefile data using alternative methods
"""

import json
import os
import sys

def read_shapefile_alternative():
    """Try to read the shapefile using alternative methods"""
    print("🔍 Attempting to read Karnataka shapefile...")
    
    try:
        # Method 1: Try using shapely directly
        try:
            import shapely
            from shapely.geometry import shape
            print("✅ Shapely available")
        except ImportError:
            print("❌ Shapely not available")
            return None
        
        # Method 2: Try using fiona directly with different import
        try:
            import fiona
            print(f"✅ Fiona version: {fiona.__version__}")
            
            # Try to read the shapefile
            with fiona.open("Karnataka.shp", "r") as src:
                print(f"✅ Successfully opened shapefile")
                print(f"📊 CRS: {src.crs}")
                print(f"📊 Schema: {src.schema}")
                print(f"📊 Number of features: {len(src)}")
                
                # Read first few features
                features = []
                for i, feature in enumerate(src):
                    if i < 3:  # Just first 3 features
                        features.append({
                            'id': feature['id'],
                            'properties': feature['properties'],
                            'geometry': feature['geometry']
                        })
                        print(f"📍 Feature {i}: {feature['properties']}")
                    else:
                        break
                
                return features
                
        except Exception as e:
            print(f"⚠️ Fiona error: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def check_shapefile_files():
    """Check what shapefile files are available"""
    print("\n📁 Checking shapefile files...")
    
    shapefile_extensions = ['.shp', '.shx', '.dbf', '.prj', '.cpg', '.sbn', '.sbx']
    
    for ext in shapefile_extensions:
        filename = f"Karnataka{ext}"
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✅ {filename}: {size:,} bytes")
        else:
            print(f"❌ {filename}: Not found")
    
    # Check the .dbf file content to see what columns are available
    if os.path.exists("Karnataka.dbf"):
        print("\n📊 Checking .dbf file structure...")
        try:
            import dbfpy
            print("✅ dbfpy available")
        except ImportError:
            print("❌ dbfpy not available, trying alternative...")
            try:
                # Try to read as binary to see structure
                with open("Karnataka.dbf", "rb") as f:
                    header = f.read(32)
                    print(f"📊 DBF header: {header[:16].hex()}")
            except Exception as e:
                print(f"⚠️ Could not read DBF: {e}")

if __name__ == "__main__":
    print("🗺️ Karnataka Shapefile Reader")
    print("=" * 40)
    
    check_shapefile_files()
    
    print("\n" + "=" * 40)
    features = read_shapefile_alternative()
    
    if features:
        print(f"\n✅ Successfully read {len(features)} features")
        # Save sample to JSON for inspection
        with open("shapefile_sample.json", "w") as f:
            json.dump(features, f, indent=2)
        print("💾 Saved sample to shapefile_sample.json")
    else:
        print("\n❌ Could not read shapefile data")
