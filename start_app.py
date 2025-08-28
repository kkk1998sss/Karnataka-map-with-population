#!/usr/bin/env python3
"""
Startup Script for Karnataka Village Population Visualization
This script handles dependency checking and launches the application.
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    
    try:
        # Try simple requirements first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_simple.txt"])
        print("✅ Basic dependencies installed successfully")
        
        # Try to install optional packages for shapefile support
        print("📦 Installing optional packages for shapefile support...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "geopandas==0.13.2", "fiona==1.9.4"])
            print("✅ Shapefile support packages installed")
        except:
            print("⚠️ Could not install shapefile support packages")
            print("   The application will use sample data instead")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'pandas', 'jinja2', 'aiofiles', 'numpy'
    ]
    
    # Optional packages (for shapefile support)
    optional_packages = ['geopandas', 'shapely', 'pyproj', 'fiona']
    
    missing_packages = []
    
    print("📋 Checking required packages...")
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    print("\n📋 Checking optional packages (for shapefile support)...")
    optional_missing = []
    for package in optional_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            optional_missing.append(package)
            print(f"⚠️ {package} (optional)")
    
    if optional_missing:
        print(f"\n⚠️ Some optional packages are missing: {', '.join(optional_missing)}")
        print("   The application will use sample data instead of the real shapefile.")
        print("   To enable shapefile support, install: pip install geopandas==0.13.2 fiona==1.9.4")
    
    return len(missing_packages) == 0

def check_shapefile():
    """Check if the Karnataka shapefile exists"""
    shapefile_exists = os.path.exists("Karnataka.shp")
    dbf_exists = os.path.exists("Karnataka.dbf")
    
    if shapefile_exists and dbf_exists:
        print("✅ Karnataka shapefile found")
        return True
    else:
        print("⚠️ Karnataka shapefile not found")
        if not shapefile_exists:
            print("   Missing: Karnataka.shp")
        if not dbf_exists:
            print("   Missing: Karnataka.dbf")
        return False

def create_sample_data():
    """Create sample data for testing"""
    print("🧪 Creating sample data for testing...")
    try:
        subprocess.check_call([sys.executable, "simple_data_loader.py"])
        return True
    except subprocess.CalledProcessError:
        print("⚠️ Sample data creation failed, continuing anyway")
        return False

def start_application():
    """Start the FastAPI application"""
    print("🚀 Starting Karnataka Village Population Visualization...")
    
    try:
        # Start the application
        process = subprocess.Popen([
            sys.executable, "main.py"
        ])
        
        # Wait a moment for the server to start
        print("⏳ Waiting for server to start...")
        time.sleep(3)
        
        # Try to open the browser
        try:
            webbrowser.open("http://localhost:8000")
            print("🌐 Browser opened automatically")
        except:
            print("🌐 Please open your browser and navigate to: http://localhost:8000")
        
        print("\n🎯 Application is running!")
        print("📊 Dashboard: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("\n⏹️ Press Ctrl+C to stop the application")
        
        # Keep the process running
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping application...")
            process.terminate()
            process.wait()
            print("✅ Application stopped")
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        return False
    
    return True

def main():
    """Main startup function"""
    print("=" * 60)
    print("🏘️ Karnataka Village Population Visualization")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ main.py not found. Please run this script from the project directory.")
        return False
    
    # Check dependencies
    print("\n📋 Checking dependencies...")
    if not check_dependencies():
        print("\n📦 Installing missing dependencies...")
        if not install_dependencies():
            print("❌ Failed to install dependencies. Please install manually:")
            print("   pip install -r requirements_simple.txt")
            return False
    
    # Check shapefile
    print("\n🗺️ Checking data files...")
    shapefile_available = check_shapefile()
    
    # Create sample data if needed
    if not shapefile_available or not os.path.exists("sample_data.json"):
        create_sample_data()
    
    # Start the application
    print("\n🚀 Launching application...")
    return start_application()

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Startup failed. Please check the error messages above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Startup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
