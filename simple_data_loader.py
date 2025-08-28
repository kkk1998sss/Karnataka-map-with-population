#!/usr/bin/env python3
"""
Simple Data Loader for Karnataka Village Data
This script handles Fiona compatibility issues and creates sample data if needed.
"""

import json
import time
import os
import numpy as np
import math

def create_irregular_polygon(center_lat, center_lon, base_size, complexity=8):
    """Create an irregular polygon that looks like a real village boundary"""
    # Generate random points around the center
    points = []
    num_points = complexity
    
    for i in range(num_points):
        # Random angle
        angle = (2 * math.pi * i) / num_points + np.random.uniform(-0.3, 0.3)
        
        # Random distance from center (varied to create irregularity)
        distance = base_size * np.random.uniform(0.6, 1.4)
        
        # Add some randomness to make it more natural
        lat_offset = distance * math.cos(angle) + np.random.uniform(-0.002, 0.002)
        lon_offset = distance * math.sin(angle) + np.random.uniform(-0.002, 0.002)
        
        lat = center_lat + lat_offset
        lon = center_lon + lon_offset
        
        points.append([lon, lat])
    
    # Ensure the polygon is closed
    points.append(points[0])
    
    return points

def create_village_boundary(center_lat, center_lon, village_type="standard"):
    """Create realistic village boundary based on village type"""
    
    if village_type == "compact":
        # Compact village (smaller, more circular)
        base_size = 0.005
        complexity = 6
    elif village_type == "spread":
        # Spread out village (larger, more irregular)
        base_size = 0.008
        complexity = 10
    elif village_type == "linear":
        # Linear village (along a road or river)
        base_size = 0.006
        complexity = 8
        # Make it more elongated
        points = []
        for i in range(complexity):
            angle = (2 * math.pi * i) / complexity
            distance = base_size * np.random.uniform(0.7, 1.3)
            # Elongate along one axis
            lat_offset = distance * 0.5 * math.cos(angle)
            lon_offset = distance * 1.2 * math.sin(angle)
            lat = center_lat + lat_offset + np.random.uniform(-0.001, 0.001)
            lon = center_lon + lon_offset + np.random.uniform(-0.001, 0.001)
            points.append([lon, lat])
        points.append(points[0])
        return points
    else:
        # Standard village
        base_size = 0.006
        complexity = 8
    
    return create_irregular_polygon(center_lat, center_lon, base_size, complexity)

def create_sample_data():
    """Create sample village data with realistic boundaries"""
    print("🧪 Creating realistic sample dataset for testing...")
    
    # Sample coordinates around Karnataka (more realistic distribution)
    karnataka_centers = [
        [15.3173, 75.7139],  # Central Karnataka
        [12.9716, 77.5946],  # Bangalore region
        [12.2958, 76.6394],  # Mysore region
        [12.9141, 74.8560],  # Mangalore region
        [15.8497, 75.2760],  # Hubli region
        [16.2050, 74.4349],  # Belgaum region
        [17.3298, 76.8343],  # Gulbarga region
        [15.1398, 76.9214],  # Bellary region
        [16.2076, 77.3553],  # Raichur region
        [17.9134, 77.5171],  # Bidar region
        [15.3363, 76.1326],  # Koppal region
        [15.4313, 75.6296],  # Gadag region
        [15.4589, 75.0078],  # Dharwad region
        [14.7933, 75.4047],  # Haveri region
        [14.4644, 75.9218],  # Davangere region
        [13.9299, 75.5681],  # Shimoga region
        [13.3409, 74.7421],  # Udupi region
        [13.3166, 75.7720],  # Chikmagalur region
        [13.3409, 77.1025],  # Tumkur region
        [12.9553, 78.6569],  # Kolar region
        [12.5221, 76.8975],  # Mandya region
        [13.0087, 76.0995],  # Hassan region
        [14.2108, 76.4004],  # Chitradurga region
        [13.3409, 77.1025],  # Tumakuru region
        [12.7234, 77.2810],  # Ramanagara region
        [13.4352, 77.7275],  # Chikkaballapura region
        [12.3375, 75.8069],  # Kodagu region
        [12.8433, 74.8365],  # Dakshina Kannada region
        [14.6802, 74.5089],  # Uttara Kannada region
        [16.1854, 75.6963],  # Bagalkot region
        [16.8244, 75.7154]   # Vijayapura region
    ]
    
    sample_data = {
        'type': 'FeatureCollection',
        'features': []
    }
    
    # Create sample villages with realistic names and characteristics
    village_templates = [
        {"name": "Bangalore Rural", "district": "Bangalore", "type": "spread", "pop_range": (8000, 20000)},
        {"name": "Mysore Central", "district": "Mysore", "type": "compact", "pop_range": (5000, 15000)},
        {"name": "Mangalore Coastal", "district": "Dakshina Kannada", "type": "linear", "pop_range": (3000, 12000)},
        {"name": "Hubli Industrial", "district": "Dharwad", "type": "spread", "pop_range": (10000, 25000)},
        {"name": "Belgaum Northern", "district": "Belgaum", "type": "compact", "pop_range": (4000, 12000)},
        {"name": "Gulbarga Eastern", "district": "Gulbarga", "type": "standard", "pop_range": (3000, 10000)},
        {"name": "Bellary Mining", "district": "Bellary", "type": "spread", "pop_range": (6000, 18000)},
        {"name": "Raichur Agricultural", "district": "Raichur", "type": "standard", "pop_range": (2000, 8000)},
        {"name": "Bidar Historical", "district": "Bidar", "type": "compact", "pop_range": (3000, 9000)},
        {"name": "Koppal Traditional", "district": "Koppal", "type": "standard", "pop_range": (2000, 7000)},
        {"name": "Gadag Cultural", "district": "Gadag", "type": "compact", "pop_range": (4000, 11000)},
        {"name": "Dharwad Educational", "district": "Dharwad", "type": "spread", "pop_range": (8000, 20000)},
        {"name": "Haveri Agricultural", "district": "Haveri", "type": "standard", "pop_range": (2000, 8000)},
        {"name": "Davangere Industrial", "district": "Davangere", "type": "spread", "pop_range": (7000, 18000)},
        {"name": "Shimoga Forest", "district": "Shimoga", "type": "linear", "pop_range": (3000, 10000)},
        {"name": "Udupi Coastal", "district": "Udupi", "type": "linear", "pop_range": (4000, 12000)},
        {"name": "Chikmagalur Coffee", "district": "Chikmagalur", "type": "standard", "pop_range": (2000, 8000)},
        {"name": "Tumkur Industrial", "district": "Tumkur", "type": "spread", "pop_range": (6000, 16000)},
        {"name": "Kolar Gold", "district": "Kolar", "type": "compact", "pop_range": (3000, 9000)},
        {"name": "Mandya Sugar", "district": "Mandya", "type": "standard", "pop_range": (4000, 12000)}
    ]
    
    for i in range(100):
        # Select a center region and add some randomness
        center_idx = i % len(karnataka_centers)
        base_center = karnataka_centers[center_idx]
        
        # Add realistic variation within each region
        lat = base_center[0] + np.random.uniform(-0.5, 0.5)
        lon = base_center[1] + np.random.uniform(-0.5, 0.5)
        
        # Select village template
        template_idx = i % len(village_templates)
        template = village_templates[template_idx]
        
        # Create realistic village boundary
        boundary_coords = create_village_boundary(lat, lon, template["type"])
        
        # Generate realistic population based on village type
        min_pop, max_pop = template["pop_range"]
        population = np.random.randint(min_pop, max_pop)
        
        # Add some population variation based on location
        if "Industrial" in template["name"]:
            population = int(population * np.random.uniform(1.2, 1.5))
        elif "Agricultural" in template["name"]:
            population = int(population * np.random.uniform(0.8, 1.1))
        
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': [boundary_coords]
            },
            'properties': {
                'state_name': 'Karnataka',  # Fixed state name
                'village_na': f"{template['name']} {i+1}",  # Village name
                'district_n': template['district'],  # District name
                'subdistric': f"{template['district']} {i//5 + 1}",  # Subdistrict name
                'pc11_tv_id': f"CENSUS_{i+1:04d}",  # Census ID
                'tot_p': int(population),  # Total population
                'village_type': template['type'],

            }
        }
        
        sample_data['features'].append(feature)
    
    # Save sample data
    with open("sample_data.json", "w") as f:
        json.dump(sample_data, f, indent=2)
    
    print("✅ Realistic sample dataset created: sample_data.json")
    print(f"   📊 Total villages: {len(sample_data['features'])}")
    print(f"   🗺️  Village types: compact, spread, linear, standard")
    print(f"   📍 Geographic distribution: 30 regions across Karnataka")
    return sample_data

def try_load_shapefile():
    """Try to load the shapefile with error handling"""
    try:
        import geopandas as gpd
        print("📁 Attempting to load Karnataka shapefile...")
        
        # Check if shapefile exists
        if not os.path.exists("Karnataka.shp"):
            print("❌ Karnataka.shp not found")
            return None
        
        # Try to load with GeoPandas
        gdf = gpd.read_file("Karnataka.shp")
        print(f"✅ Successfully loaded {len(gdf)} villages")
        
        # Process the data
        return process_geodataframe(gdf)
        
    except ImportError as e:
        print(f"❌ GeoPandas not available: {e}")
        return None
    except Exception as e:
        print(f"❌ Error loading shapefile: {e}")
        print("🔧 This might be due to Fiona compatibility issues")
        return None

def process_geodataframe(gdf):
    """Process the loaded GeoDataFrame"""
    print("🔧 Processing loaded data...")
    
    # Check columns
    print(f"📊 Available columns: {list(gdf.columns)}")
    
    # Handle column mapping
    column_mapping = {}
    expected_columns = {
        'state_name': ['state_name', 'state', 'state_nam'],
        'district_n': ['district_n', 'district', 'dist_nam', 'dist_name'],
        'subdistric': ['subdistric', 'subdistrict', 'sub_dist', 'subdist'],
        'village_na': ['village_na', 'village', 'village_n', 'village_name'],
        'pc11_tv_id': ['pc11_tv_id', 'census_id', 'village_id', 'id'],
        'tot_p': ['tot_p', 'population', 'pop', 'total_pop', 'total_p']
    }
    
    for expected, possible_names in expected_columns.items():
        for actual in gdf.columns:
            if actual.lower() in [name.lower() for name in possible_names]:
                column_mapping[expected] = actual
                break
    
    print(f"🔗 Column mapping: {column_mapping}")
    
    # Rename columns
    gdf = gdf.rename(columns=column_mapping)
    
    # Ensure population column exists
    if 'tot_p' not in gdf.columns:
        pop_columns = [col for col in gdf.columns if any(word in col.lower() for word in ['pop', 'tot', 'people'])]
        if pop_columns:
            gdf['tot_p'] = pd.to_numeric(gdf[pop_columns[0]], errors='coerce').fillna(0)
        else:
            gdf['tot_p'] = np.random.randint(500, 15000, len(gdf))
    
    # Convert to numeric
    gdf['tot_p'] = pd.to_numeric(gdf['tot_p'], errors='coerce').fillna(0)
    
    # Simplify geometries
    print("🔧 Simplifying geometries...")
    gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.0001, preserve_topology=True)
    
    # Convert to GeoJSON
    print("💾 Converting to GeoJSON...")
    geojson_data = gdf.to_crs(epsg=4326).to_json()
    
    # Save processed data
    with open("processed_data.json", "w") as f:
        json.dump(json.loads(geojson_data), f)
    
    print("✅ Processed data saved: processed_data.json")
    return geojson_data

def main():
    """Main function to load or create data"""
    print("=" * 60)
    print("🗺️  Karnataka Village Data Loader")
    print("=" * 60)
    
    # Try to load the real shapefile first
    real_data = try_load_shapefile()
    
    if real_data is not None:
        print("✅ Successfully loaded real shapefile data")
        return True
    else:
        print("⚠️ Could not load real shapefile, creating realistic sample data...")
        create_sample_data()
        return False

if __name__ == "__main__":
    main()
