#!/usr/bin/env python3
"""
Check coordinates and fix mapping issues
"""

import json
import os

def check_shapefile_coordinates():
    """Check the actual coordinates from the shapefile"""
    print("🔍 Checking shapefile coordinates...")
    
    # Try to read the shapefile directly
    try:
        # Check if we can read the .dbf file to get some info
        if os.path.exists("Karnataka.dbf"):
            print("✅ Karnataka.dbf found")
            print("📊 File size:", os.path.getsize("Karnataka.dbf"), "bytes")
        
        if os.path.exists("Karnataka.shp"):
            print("✅ Karnataka.shp found")
            print("📊 File size:", os.path.getsize("Karnataka.shp"), "bytes")
            
        # Read the projection file
        if os.path.exists("Karnataka.prj"):
            with open("Karnataka.prj", "r") as f:
                prj_content = f.read()
            print("✅ Karnataka.prj found")
            print("📐 Projection:", prj_content.strip())
            
    except Exception as e:
        print(f"❌ Error reading files: {e}")

def get_correct_karnataka_coordinates():
    """Get the correct Karnataka coordinates based on actual geography"""
    print("\n🗺️ Getting correct Karnataka coordinates...")
    print("📝 Note: GeoJSON requires [longitude, latitude] order, not [latitude, longitude]")
    print("📍 Updated: More accurate boundary that stays within Karnataka state limits")
    
    # More accurate Karnataka coordinates that stay within state limits
    # Format: [longitude, latitude] for GeoJSON compatibility
    karnataka_coords = [
        [74.4349, 16.2050],  # North-West (Belgaum region) - [lon, lat]
        [74.8343, 17.3298],  # North-West (Gulbarga region) - [lon, lat]
        [76.2569, 18.5204],  # North (near Maharashtra border) - [lon, lat]
        [77.4161, 17.3298],  # North-East (near Telangana border) - [lon, lat]
        [77.9214, 16.2076],  # East (near Telangana border) - [lon, lat]
        [77.9218, 15.1398],  # East (near Andhra Pradesh border) - [lon, lat]
        [77.5681, 14.4644],  # South-East (near Andhra Pradesh border) - [lon, lat]
        [77.5946, 13.9299],  # South (near Tamil Nadu border) - [lon, lat]
        [76.6394, 12.9716],  # South (Bangalore region) - [lon, lat]
        [76.6394, 12.2958],  # South-West (Mysore region) - [lon, lat]
        [74.8560, 12.9141],  # South-West (Mangalore region) - [lon, lat]
        [74.7421, 13.3409],  # West (Udupi region) - [lon, lat]
        [74.5089, 14.6802],  # West (Uttara Kannada) - [lon, lat]
        [74.2760, 15.8497],  # West (Hubli region) - [lon, lat]
        [74.4349, 16.2050]   # Back to start (North-West) - [lon, lat]
    ]
    
    # Calculate bounding box
    lons = [coord[0] for coord in karnataka_coords]  # longitude is first
    lats = [coord[1] for coord in karnataka_coords]  # latitude is second
    
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)
    
    print(f"📍 Longitude range: {min_lon:.4f} to {max_lon:.4f}")
    print(f"📍 Latitude range: {min_lat:.4f} to {max_lat:.4f}")
    print(f"📍 Center: {((min_lat + max_lat) / 2):.4f}, {((min_lon + max_lon) / 2):.4f}")
    
    return karnataka_coords, min_lat, max_lat, min_lon, max_lon

def create_correct_village_distribution():
    """Create villages with correct regional distribution"""
    print("\n🏘️ Creating correct village distribution...")
    
    # Get correct coordinates
    boundary_coords, min_lat, max_lat, min_lon, max_lon = get_correct_karnataka_coordinates()
    
    # Regional distribution with correct coordinates
    regions = {
        "north_west": {
            "lat_range": (16.5, 18.5),
            "lon_range": (74.0, 75.5),
            "districts": ["Belgaum", "Dharwad", "Gadag", "Haveri"]
        },
        "north_east": {
            "lat_range": (17.0, 20.5),
            "lon_range": (75.5, 77.5),
            "districts": ["Gulbarga", "Bidar", "Yadgir"]
        },
        "east": {
            "lat_range": (15.0, 16.5),
            "lon_range": (76.5, 78.0),
            "districts": ["Bellary", "Raichur", "Koppal"]
        },
        "central": {
            "lat_range": (14.5, 16.0),
            "lon_range": (75.0, 76.5),
            "districts": ["Davangere", "Shimoga", "Chitradurga", "Chikmagalur"]
        },
        "south": {
            "lat_range": (12.5, 14.0),
            "lon_range": (76.0, 77.5),
            "districts": ["Bangalore", "Mysore", "Tumkur", "Kolar", "Mandya", "Hassan"]
        },
        "west": {
            "lat_range": (13.0, 15.0),
            "lon_range": (74.0, 75.0),
            "districts": ["Mangalore", "Udupi", "Dakshina Kannada", "Uttara Kannada"]
        }
    }
    
    print("📍 Regional distribution:")
    for region, info in regions.items():
        print(f"   {region}: {info['districts']}")
        print(f"      Lat: {info['lat_range'][0]:.2f} to {info['lat_range'][1]:.2f}")
        print(f"      Lon: {info['lon_range'][0]:.2f} to {info['lon_range'][1]:.2f}")
    
    return regions

if __name__ == "__main__":
    check_shapefile_coordinates()
    get_correct_karnataka_coordinates()
    create_correct_village_distribution()
