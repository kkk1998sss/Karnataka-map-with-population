import os
import json
import time
from typing import Dict, List, Optional
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
import uvicorn
from pathlib import Path

app = FastAPI(title="Karnataka Village Population Visualization")

# Templates
templates = Jinja2Templates(directory="templates")

# Global variables for caching
gdf = None
population_stats = None
topojson_data = None

def extract_compressed_shapefiles():
    """Extract compressed shapefiles for processing"""
    import gzip
    import shutil
    import os
    
    print("🗜️ Extracting compressed shapefiles...")
    
    # Files to extract
    files_to_extract = [
        'Karnataka.shp.gz',
        'Karnataka.shx.gz', 
        'Karnataka.dbf.gz',
        'Karnataka.prj.gz',
        'Karnataka.cpg.gz',
        'Karnataka.sbn.gz',
        'Karnataka.sbx.gz'
    ]
    
    extracted_count = 0
    for compressed_file in files_to_extract:
        if os.path.exists(compressed_file):
            # Extract the file
            output_file = compressed_file.replace('.gz', '')
            with gzip.open(compressed_file, 'rb') as f_in:
                with open(output_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            print(f"✅ Extracted {compressed_file} -> {output_file}")
            extracted_count += 1
        else:
            print(f"⚠️ Compressed file not found: {compressed_file}")
    
    print(f"🎉 Extracted {extracted_count} shapefile components")
    return extracted_count > 0

def load_and_process_data():
    """Load and process the Karnataka shapefile data with optimizations"""
    global gdf, population_stats, topojson_data
    
    print("Loading Karnataka data...")
    start_time = time.time()
    
    try:
        # First try to load the real shapefile using fiona directly
        try:
            import fiona
            import shapely
            from shapely.geometry import shape
            import pandas as pd
            import geopandas as gpd
            
            print("📁 Attempting to load real shapefile using fiona...")
            
            # Check if we have compressed shapefiles and need to extract them
            if os.path.exists("Karnataka.shp.gz") and not os.path.exists("Karnataka.shp"):
                print("🗜️ Extracting compressed shapefiles...")
                extract_compressed_shapefiles()
            
            # Read the shapefile using fiona (just like local!)
            with fiona.open("Karnataka.shp", "r") as src:
                print(f"✅ Successfully opened shapefile with {len(src)} features")
                print(f"📊 CRS: {src.crs}")
                
                # Convert to GeoDataFrame manually (same as local)
                features = []
                for feature in src:
                    # Convert fiona feature to GeoJSON-like structure
                    # Clean up properties to avoid duplicate column names
                    properties = dict(feature['properties'])
                    
                    # Remove any duplicate or problematic columns
                    if 'shrid2' in properties and 'shrid2_11' in properties:
                        del properties['shrid2_11']  # Keep only one shrid2
                    
                    # Remove other potentially problematic columns
                    problematic_cols = ['_mean_p_mi', '_core_p_mi', '_target_we', '_target_gr']
                    for col in problematic_cols:
                        if col in properties:
                            del properties[col]
                    
                    geojson_feature = {
                        'type': 'Feature',
                        'properties': properties,
                        'geometry': feature['geometry']
                    }
                    features.append(geojson_feature)
                
                # Create GeoDataFrame with explicit column handling
                # Extract properties and geometry separately
                properties_list = [f['properties'] for f in features]
                geometries = [f['geometry'] for f in features]
                
                # Create DataFrame from properties
                df = pd.DataFrame(properties_list)
                
                # Add geometry column
                df['geometry'] = geometries
                
                # Create GeoDataFrame
                gdf = gpd.GeoDataFrame(df, crs=src.crs)
                print(f"✅ Converted to GeoDataFrame with {len(gdf)} features")
                print(f"📊 Available columns: {list(gdf.columns)}")
                
                return process_real_data(gdf, start_time)
                
        except Exception as e:
            print(f"⚠️ Could not load shapefile with fiona: {e}")
            print("🔧 This might be due to Fiona compatibility issues")
            print("🔧 Trying to load sample data...")
        
        # Only fall back to sample data if absolutely necessary
        print("🧪 Creating sample data...")
        try:
            # Try to load existing deployable data first
            from data_loader import load_deployable_data
            print("🗺️ Loading existing deployable data...")
            deployable_data = load_deployable_data()
            if deployable_data:
                # Convert deployable data to the expected format
                converted_data = convert_deployable_to_features(deployable_data)
                gdf = create_sample_geodataframe(converted_data)
                print(f"✅ Loaded deployable data with {len(gdf)} features")
                return process_sample_data(gdf, start_time)
            else:
                raise Exception("No deployable data found")
        except Exception as e:
            print(f"⚠️ Could not load deployable data: {e}")
            print("🔧 Falling back to basic sample data...")
            gdf = create_sample_data()
            print(f"✅ Created {len(gdf)} sample villages")
            return process_sample_data(gdf, start_time)
        
    except Exception as e:
        print(f"❌ Error loading data: {str(e)}")
        return False

def process_real_data(gdf, start_time):
    """Process real shapefile data"""
    global population_stats, topojson_data
    
    # Check and rename columns if needed
    expected_columns = ['state_name', 'district_n', 'subdistric', 'village_na', 'pc11_tv_id', 'tot_p']
    actual_columns = list(gdf.columns)
    
    print(f"📊 Available columns: {actual_columns}")
    
    # Handle potential column name variations with more precise matching
    column_mapping = {}
    for expected in expected_columns:
        # First try exact match
        if expected in actual_columns:
            column_mapping[expected] = expected
        else:
            # Try partial matching only for specific cases
            for actual in actual_columns:
                if expected.lower() == actual.lower():
                    column_mapping[expected] = actual
                    break
                elif expected == 'village_na' and actual == 'village_na':
                    column_mapping[expected] = actual
                    break
                elif expected == 'district_n' and actual == 'district_n':
                    column_mapping[expected] = actual
                    break
                elif expected == 'subdistric' and actual == 'subdistric':
                    column_mapping[expected] = actual
                    break
                elif expected == 'state_name' and actual == 'state_name':
                    column_mapping[expected] = actual
                    break
                elif expected == 'pc11_tv_id' and actual == 'pc11_tv_id':
                    column_mapping[expected] = actual
                    break
                elif expected == 'tot_p' and actual == 'tot_p':
                    column_mapping[expected] = actual
                    break
    
    print(f"🔗 Column mapping: {column_mapping}")
    
    # Rename columns for consistency
    gdf = gdf.rename(columns=column_mapping)
    
    # Remove any duplicate columns that might cause issues
    print("🔧 Checking for duplicate columns...")
    duplicate_cols = gdf.columns[gdf.columns.duplicated()].tolist()
    if duplicate_cols:
        print(f"⚠️ Found duplicate columns: {duplicate_cols}")
        # Keep only the first occurrence of each column
        gdf = gdf.loc[:, ~gdf.columns.duplicated()]
        print(f"✅ Removed duplicate columns. New columns: {list(gdf.columns)}")
    
    # Ensure we have the essential columns
    essential_cols = ['state_name', 'district_n', 'subdistric', 'village_na', 'pc11_tv_id', 'tot_p', 'geometry']
    missing_cols = [col for col in essential_cols if col not in gdf.columns]
    if missing_cols:
        print(f"⚠️ Missing essential columns: {missing_cols}")
        # Add missing columns with default values
        for col in missing_cols:
            if col == 'geometry':
                continue  # Skip geometry, it should already exist
            gdf[col] = 'Unknown' if 'name' in col else 0
    
    # Ensure population column exists and is numeric
    if 'tot_p' in gdf.columns:
        gdf['tot_p'] = pd.to_numeric(gdf['tot_p'], errors='coerce').fillna(0)
    else:
        # Try to find population column
        pop_columns = [col for col in gdf.columns if 'pop' in col.lower() or 'tot' in col.lower()]
        if pop_columns:
            gdf['tot_p'] = pd.to_numeric(gdf[pop_columns[0]], errors='coerce').fillna(0)
        else:
            gdf['tot_p'] = 1000  # Default population for testing
    
    # Calculate population statistics for color scaling
    population_stats = {
        'min': float(gdf['tot_p'].min()),
        'max': float(gdf['tot_p'].max()),
        'mean': float(gdf['tot_p'].mean()),
        'median': float(gdf['tot_p'].median())
    }
    
    print(f"📊 Population stats: {population_stats}")
    
    # Simplify geometries for faster rendering (reduce complexity by 50%)
    print("🔧 Simplifying geometries...")
    gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.0001, preserve_topology=True)
    
    # Convert to TopoJSON for efficient transmission
    print("💾 Converting to TopoJSON...")
    topojson_data = gdf.to_crs(epsg=4326).to_json()
    
    total_time = time.time() - start_time
    print(f"✅ Data processing completed in {total_time:.2f} seconds")
    
    return True

def create_sample_data():
    """Create sample village data"""
    import numpy as np
    
    # Sample coordinates around Karnataka
    base_coords = [15.3173, 75.7139]  # Karnataka center
    
    sample_data = {
        'type': 'FeatureCollection',
        'features': []
    }
    
    # Create sample villages with realistic names
    village_names = [
        "Bangalore Rural", "Mysore Central", "Mangalore Coastal", "Hubli Industrial",
        "Belgaum Northern", "Gulbarga Eastern", "Bellary Mining", "Raichur Agricultural",
        "Bidar Historical", "Koppal Traditional", "Gadag Cultural", "Dharwad Educational",
        "Haveri Agricultural", "Davangere Industrial", "Shimoga Forest", "Udupi Coastal",
        "Chikmagalur Coffee", "Tumkur Industrial", "Kolar Gold", "Mandya Sugar"
    ]
    
    districts = [
        "Bangalore", "Mysore", "Mangalore", "Hubli", "Belgaum", "Gulbarga", 
        "Bellary", "Raichur", "Bidar", "Koppal", "Gadag", "Dharwad", "Haveri",
        "Davangere", "Shimoga", "Udupi", "Chikmagalur", "Tumkur", "Kolar", "Mandya"
    ]
    
    for i in range(100):
        # Create random village locations around Karnataka
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
        
        # Select village and district names
        village_idx = i % len(village_names)
        district_idx = i % len(districts)
        
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': [coords]
            },
            'properties': {
                'state_name': 'Karnataka',
                'village_na': f"{village_names[village_idx]} {i+1}",
                'district_n': districts[district_idx],
                'subdistric': f"Subdistrict {i//5 + 1}",
                'pc11_tv_id': f"CENSUS_{i+1:04d}",
                'tot_p': np.random.randint(500, 15000)  # Realistic population range
            }
        }
        
        sample_data['features'].append(feature)
    
    # Save sample data
    with open("sample_data.json", "w") as f:
        json.dump(sample_data, f)
    
    return create_sample_geodataframe(sample_data)

def convert_deployable_to_features(deployable_data):
    """Convert deployable data format to features format"""
    if 'villages' not in deployable_data:
        raise ValueError("Deployable data does not contain 'villages' key")
    
    # Convert villages to features format
    features = []
    for village in deployable_data['villages']:
        # Use the actual geometry from the data
        feature = {
            'type': 'Feature',
            'geometry': village.get('geometry', {
                'type': 'Polygon',
                'coordinates': [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]  # Fallback
            }),
            'properties': {
                'state_name': 'Karnataka',
                'village_na': village.get('name', 'Unknown'),
                'district_n': village.get('district', 'Unknown'),
                'subdistrict': village.get('subdistrict', 'Unknown'),
                'pc11_tv_id': village.get('census_id', 'Unknown'),
                'tot_p': village.get('population', 1000)
            }
        }
        features.append(feature)
    
    return {
        'type': 'FeatureCollection',
        'features': features
    }

def create_sample_geodataframe(sample_data):
    """Convert sample data to GeoDataFrame-like structure"""
    # Create a simple structure that mimics GeoDataFrame
    class SampleGeoDataFrame:
        def __init__(self, data):
            self.data = data
            self.features = data['features']
        
        def __len__(self):
            return len(self.features)
        
        @property
        def columns(self):
            return ['state_name', 'village_na', 'district_n', 'subdistric', 'pc11_tv_id', 'tot_p']
        
        def rename(self, columns):
            # Simple rename implementation
            return self
        
        def to_crs(self, epsg):
            # Simple CRS conversion
            return self
        
        def to_json(self):
            return json.dumps(self.data)
    
    return SampleGeoDataFrame(sample_data)

def process_sample_data(gdf, start_time):
    """Process sample data"""
    global population_stats, topojson_data
    
    # Calculate population statistics (only for village features, not state boundary)
    populations = []
    for f in gdf.features:
        if f['properties'].get('type') != 'state_boundary' and 'tot_p' in f['properties']:
            populations.append(f['properties']['tot_p'])
    
    if not populations:
        print("⚠️ No population data found in village features")
        populations = [1000]  # Default fallback
    
    population_stats = {
        'min': float(min(populations)),
        'max': float(max(populations)),
        'mean': float(sum(populations) / len(populations)),
        'median': float(sorted(populations)[len(populations)//2])
    }
    
    print(f"📊 Population stats: {population_stats}")
    print(f"🏘️ Total features: {len(gdf.features)}")
    print(f"👥 Village features with population: {len(populations)}")
    
    # Convert to proper GeoJSON format for frontend
    if hasattr(gdf, 'data'):
        # Use the original data structure
        topojson_data = gdf.data
    else:
        # Fallback to JSON conversion
        topojson_data = gdf.to_json()
    
    total_time = time.time() - start_time
    print(f"✅ Sample data processing completed in {total_time:.2f} seconds")
    
    return True

@app.on_event("startup")
async def startup_event():
    """Initialize data on startup"""
    print("Starting Karnataka Village Population Visualization...")
    success = load_and_process_data()
    if not success:
        print("Failed to load data. Please check the shapefile.")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Main page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/data")
async def get_data():
    """Get the processed data"""
    if gdf is None or topojson_data is None or population_stats is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    # Ensure the data is properly formatted
    try:
        # Get the data in the right format
        if hasattr(gdf, 'data'):
            # Use the original data structure from SampleGeoDataFrame
            data_for_frontend = gdf.data
        else:
            # Parse the JSON if it's a string
            if isinstance(topojson_data, str):
                data_for_frontend = json.loads(topojson_data)
            else:
                data_for_frontend = topojson_data
        
        # Verify the data structure
        if 'features' not in data_for_frontend:
            raise ValueError("Data does not contain 'features'")
        
        print(f"📤 Sending {len(data_for_frontend['features'])} features to frontend")
        
        return {
            "topojson": data_for_frontend,
            "population_stats": population_stats,
            "village_count": len(gdf),
            "columns": list(gdf.columns) if hasattr(gdf, 'columns') else ['village_na', 'district_n', 'subdistric', 'pc11_tv_id', 'tot_p']
        }
    except Exception as e:
        print(f"Error formatting data: {e}")
        raise HTTPException(status_code=500, detail=f"Data formatting error: {str(e)}")

@app.get("/api/villages")
async def get_villages(
    district: Optional[str] = None,
    subdistrict: Optional[str] = None,
    limit: int = 100
):
    """Get village data with optional filtering"""
    if gdf is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    # Handle both real and sample data
    if hasattr(gdf, 'features'):
        # Sample data - filter out state boundary features
        filtered_features = [f for f in gdf.features if f['properties'].get('type') != 'state_boundary']
        if district:
            filtered_features = [f for f in filtered_features if f['properties']['district_n'] == district]
        if subdistrict:
            filtered_features = [f for f in filtered_features if f['properties']['subdistric'] == subdistrict]
        
        villages_data = []
        for i, feature in enumerate(filtered_features[:limit]):
            props = feature['properties']
            villages_data.append({
                'id': i,
                'village_name': props.get('village_na', 'Unknown'),
                'district': props.get('district_n', 'Unknown'),
                'subdistrict': props.get('subdistric', 'Unknown'),
                'population': int(props.get('tot_p', 0)),
                'census_id': props.get('pc11_tv_id', 'Unknown')
            })
        
        return {
            "villages": villages_data,
            "total": len(filtered_features),
            "returned": len(villages_data)
        }
    else:
        # Real GeoDataFrame data
        filtered_gdf = gdf.copy()
        
        if district:
            filtered_gdf = filtered_gdf[filtered_gdf['district_n'] == district]
        if subdistrict:
            filtered_gdf = filtered_gdf[filtered_gdf['subdistric'] == subdistrict]
        
        # Convert to JSON with limited features for performance
        villages_data = []
        for idx, row in filtered_gdf.head(limit).iterrows():
            villages_data.append({
                'id': idx,
                'village_name': row.get('village_na', 'Unknown'),
                'district': row.get('district_n', 'Unknown'),
                'subdistrict': row.get('subdistric', 'Unknown'),
                'population': int(row.get('tot_p', 0)),
                'census_id': row.get('pc11_tv_id', 'Unknown')
            })
        
        return {
            "villages": villages_data,
            "total": len(filtered_gdf),
            "returned": len(villages_data)
        }

@app.get("/api/health")
async def health_check():
    """Health check endpoint for Render deployment"""
    return {
        "status": "healthy", 
        "timestamp": time.time(),
        "service": "Karnataka Village Population Visualization",
        "data_loaded": gdf is not None
    }

@app.get("/api/districts")
async def get_districts():
    """Get list of districts"""
    if gdf is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    # Handle both real and sample data
    if hasattr(gdf, 'features'):
        # Sample data - filter out state boundary features
        districts = []
        for f in gdf.features:
            if f['properties'].get('type') != 'state_boundary' and 'district_n' in f['properties']:
                districts.append(f['properties']['district_n'])
        districts = list(set(districts))
    else:
        # Real GeoDataFrame data
        districts = gdf['district_n'].unique().tolist()
    
    return {"districts": sorted(districts)}

if __name__ == "__main__":
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
