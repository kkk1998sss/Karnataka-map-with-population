# Karnataka Village Population Visualization

## Project Overview
This web application visualizes village-level population data for Karnataka state using shapefile data. The application displays each village with a different color corresponding to its population, optimized for fast loading and smooth user experience.

## Technical Approach

### Data Processing Strategy
1. **Shapefile Loading**: Using GeoPandas to load the large Karnataka shapefile (113MB DBF + 20MB SHP)
2. **Data Optimization**: 
   - Simplify geometries for faster rendering
   - Implement spatial indexing
   - Use TopoJSON format for efficient transmission
3. **Performance Optimization**:
   - Pre-process and cache data
   - Implement progressive loading
   - Use efficient data formats

### Technology Stack
- **Backend**: FastAPI (Python) - Fast, modern web framework
- **Frontend**: Leaflet.js with custom styling
- **Data Processing**: GeoPandas, Pandas, Shapely
- **Data Format**: TopoJSON for efficient transmission

### Key Features
- Interactive map with village boundaries
- Population-based color coding
- Fast loading (< 10 seconds target)
- Responsive design
- Search and filter capabilities

## Installation & Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

3. Open browser at: http://localhost:8000

## Data Fields Used
- `state_name`: State Name
- `district_n`: District Name  
- `subdistric`: Subdistrict Name
- `village_na`: Village Name
- `pc11_tv_id`: Village Census ID
- `tot_p`: Total Population of the village

## Performance Targets
- Map loading time: < 10 seconds
- Smooth pan/zoom experience
- Responsive UI interactions
