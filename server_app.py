#!/usr/bin/env python3
"""
Server-Ready Karnataka Village Population Visualization
Uses deployable data files instead of large shapefiles for easy server deployment
"""

import json
import gzip
from pathlib import Path
from typing import Dict, Any, Optional
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import numpy as np

# Initialize FastAPI app
app = FastAPI(
    title="Karnataka Village Population Visualization",
    description="Interactive map showing village boundaries with population-based coloring",
    version="2.0.0"
)

# Templates
templates = Jinja2Templates(directory="templates")

# Global data storage
village_data = None
population_stats = None
districts_list = []

def load_deployable_data(data_file: str = None) -> Optional[Dict[str, Any]]:
    """
    Load deployable data from various formats
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

def initialize_data():
    """Initialize application data on startup"""
    global village_data, population_stats, districts_list
    
    print("🚀 Initializing Karnataka Village Visualization...")
    
    # Load deployable data
    data = load_deployable_data()
    if not data:
        raise RuntimeError("Failed to load village data")
    
    village_data = data
    population_stats = data['metadata']['population_stats']
    districts_list = data['metadata']['districts']
    
    print(f"✅ Application initialized with {len(village_data['villages'])} villages")
    print(f"📊 Population range: {population_stats['min']:,} - {population_stats['max']:,}")
    print(f"🗺️ Districts: {', '.join(districts_list[:5])}{'...' if len(districts_list) > 5 else ''}")

@app.on_event("startup")
async def startup_event():
    """Initialize data when application starts"""
    try:
        initialize_data()
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        print("🔄 Creating fallback sample data...")
        create_fallback_data()
        initialize_data()

def create_fallback_data():
    """Create fallback data if no deployable data is available"""
    print("🎯 Creating fallback sample data...")
    
    # Generate 50 realistic sample villages
    districts = ['Bangalore Urban', 'Mysore', 'Mandya', 'Hassan', 'Tumkur']
    sample_villages = []
    
    for i in range(50):
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
    
    fallback_data = {
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
            'data_format': 'fallback_sample',
            'version': '2.0.0',
            'note': 'This is fallback sample data. Use create_deployable_data.py for real data.'
        },
        'villages': sample_villages
    }
    
    # Save fallback data
    with open("fallback_data.json", 'w', encoding='utf-8') as f:
        json.dump(fallback_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Fallback data created with {len(sample_villages)} villages")

@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    """Main application page"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "total_villages": village_data['metadata']['total_villages'],
        "total_population": f"{village_data['metadata']['total_population']:,}",
        "districts_count": len(districts_list)
    })

@app.get("/api/data")
async def get_village_data():
    """Get complete village data for the map"""
    if not village_data:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": village['id'],
                "properties": {
                    "name": village['name'],
                    "district": village['district'],
                    "subdistrict": village['subdistrict'],
                    "population": village['population'],
                    "census_id": village['census_id']
                },
                "geometry": village['geometry']
            }
            for village in village_data['villages']
        ]
    }

@app.get("/api/districts")
async def get_districts():
    """Get list of all districts"""
    if not districts_list:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    return {"districts": districts_list}

@app.get("/api/villages")
async def get_villages(search: str = "", district: str = ""):
    """Get filtered list of villages"""
    if not village_data:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    villages = village_data['villages']
    
    # Apply filters
    if district:
        villages = [v for v in villages if v['district'].lower() == district.lower()]
    
    if search:
        search_lower = search.lower()
        villages = [v for v in villages if search_lower in v['name'].lower() or search_lower in v['district'].lower()]
    
    # Return limited results for performance
    return {
        "villages": villages[:100],  # Limit to 100 results
        "total": len(villages),
        "showing": min(100, len(villages))
    }

@app.get("/api/stats")
async def get_statistics():
    """Get population statistics for color coding"""
    if not population_stats:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    return {
        "population_stats": population_stats,
        "total_villages": village_data['metadata']['total_villages'],
        "total_population": village_data['metadata']['total_population'],
        "districts_count": len(districts_list)
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "data_loaded": village_data is not None,
        "villages_count": len(village_data['villages']) if village_data else 0,
        "data_format": village_data['metadata']['data_format'] if village_data else None
    }

if __name__ == "__main__":
    print("🚀 Starting Karnataka Village Visualization Server...")
    print("📁 Looking for deployable data files...")
    
    # Check for data files
    data_files = [
        "deployable_data.json.gz",
        "deployable_data.json", 
        "deployable_data_minimal.json",
        "sample_data.json"
    ]
    
    found_files = [f for f in data_files if Path(f).exists()]
    if found_files:
        print(f"✅ Found data files: {', '.join(found_files)}")
    else:
        print("⚠️  No data files found. Will create fallback data on startup.")
    
    print("🌐 Starting server at http://localhost:8000")
    print("📊 API documentation at http://localhost:8000/docs")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
