# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### 1. Fiona/GeoPandas Compatibility Issues

**Problem**: `module 'fiona' has no attribute 'path'` or similar errors

**Solution**: 
- The application will automatically fall back to sample data
- To fix shapefile support, install compatible versions:
  ```bash
  pip install geopandas==0.13.2 fiona==1.9.4
  ```

**Alternative**: Use the simple requirements file:
```bash
pip install -r requirements_simple.txt
```

### 2. Missing Static Directory Error

**Problem**: `RuntimeError: Directory 'static' does not exist`

**Solution**: 
- This has been fixed in the updated version
- The application no longer requires a static directory

### 3. Python Version Issues

**Problem**: Python version compatibility errors

**Solution**:
- Ensure Python 3.8 or higher is installed
- Check version: `python --version`
- Download from: https://python.org

### 4. Port Already in Use

**Problem**: Port 8000 is already occupied

**Solution**:
- Change port in `main.py`:
  ```python
  uvicorn.run(app, host="0.0.0.0", port=8001)  # Change to 8001
  ```
- Or stop other services using port 8000

### 5. Dependencies Installation Failures

**Problem**: `pip install` fails

**Solution**:
- Upgrade pip: `python -m pip install --upgrade pip`
- Use simple requirements: `pip install -r requirements_simple.txt`
- Install packages individually if needed

### 6. Shapefile Loading Issues

**Problem**: Cannot load Karnataka.shp

**Solution**:
- The application automatically creates sample data
- Sample data provides 100 realistic villages for testing
- All features work with sample data

### 7. Browser Not Opening

**Problem**: Browser doesn't open automatically

**Solution**:
- Manually navigate to: http://localhost:8000
- Check if the server is running in the terminal
- Ensure no firewall is blocking the connection

### 8. Memory Issues

**Problem**: Application crashes with large shapefiles

**Solution**:
- Use sample data for testing
- Ensure sufficient RAM (4GB+ recommended)
- Close other applications to free memory

## Quick Fix Commands

### Reset and Start Fresh
```bash
# Remove existing data
del sample_data.json
del processed_data.json

# Reinstall dependencies
pip install -r requirements_simple.txt

# Start application
python start_app.py
```

### Force Sample Data
```bash
# Create sample data manually
python simple_data_loader.py

# Start application
python main.py
```

### Check System Status
```bash
# Check Python version
python --version

# Check installed packages
pip list

# Check if port is available
netstat -an | findstr :8000
```

## Performance Tips

1. **Use Sample Data First**: Test with sample data before loading large shapefiles
2. **Close Other Applications**: Free up memory and CPU resources
3. **Check Internet Connection**: Map tiles require internet access
4. **Use Compatible Browsers**: Chrome, Firefox, Edge work best

## Getting Help

If you continue to experience issues:

1. **Check the Console**: Look for error messages in the terminal
2. **Review Logs**: Check for specific error details
3. **Try Sample Data**: Ensure the application works with sample data first
4. **Update Dependencies**: Use the latest compatible versions

## Success Indicators

✅ **Application starts without errors**  
✅ **Browser opens to http://localhost:8000**  
✅ **Map loads with village boundaries**  
✅ **Population colors are visible**  
✅ **Search and filter functions work**  

The application is designed to be robust and will automatically handle most issues by falling back to sample data when needed.
