#!/usr/bin/env python3
"""
Deployment Script for Karnataka Village Visualization
Prepares the application for server deployment
"""

import os
import shutil
import subprocess
from pathlib import Path

def create_deployment_package():
    """Create a deployment package with all necessary files"""
    print("🚀 Creating deployment package...")
    
    # Create deployment directory
    deploy_dir = Path("deployment")
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
    deploy_dir.mkdir()
    
    # Files to include in deployment
    deployment_files = [
        "server_app.py",
        "data_loader.py",
        "requirements.txt",
        "README.md",
        "templates/",
        ".gitignore"
    ]
    
    # Copy files
    for file_path in deployment_files:
        src = Path(file_path)
        dst = deploy_dir / file_path
        
        if src.is_file():
            # Copy file
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"📁 Copied: {file_path}")
        elif src.is_dir():
            # Copy directory
            shutil.copytree(src, dst)
            print(f"📁 Copied: {file_path}/")
    
    # Copy deployable data files
    data_files = [
        "deployable_data.json.gz",
        "deployable_data.json",
        "deployable_data_minimal.json"
    ]
    
    for data_file in data_files:
        if Path(data_file).exists():
            shutil.copy2(data_file, deploy_dir)
            print(f"📊 Copied: {data_file}")
    
    # Create deployment script
    create_deployment_scripts(deploy_dir)
    
    # Create deployment README
    create_deployment_readme(deploy_dir)
    
    print(f"\n✅ Deployment package created in: {deploy_dir}")
    print("📋 Next steps:")
    print("1. Upload the 'deployment' folder to your server")
    print("2. Run: pip install -r requirements.txt")
    print("3. Run: python server_app.py")
    print("4. Access at: http://your-server-ip:8000")

def create_deployment_scripts(deploy_dir):
    """Create deployment scripts for different platforms"""
    
    # Windows deployment script
    windows_script = """@echo off
echo Starting Karnataka Village Visualization...
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting server...
python server_app.py
pause
"""
    
    with open(deploy_dir / "start_server.bat", 'w') as f:
        f.write(windows_script)
    
    # Linux/Mac deployment script
    linux_script = """#!/bin/bash
echo "Starting Karnataka Village Visualization..."
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
echo ""
echo "Starting server..."
python server_app.py
"""
    
    with open(deploy_dir / "start_server.sh", 'w') as f:
        f.write(linux_script)
    
    # Make Linux script executable
    os.chmod(deploy_dir / "start_server.sh", 0o755)
    
    print("📜 Created deployment scripts")

def create_deployment_readme(deploy_dir):
    """Create deployment instructions"""
    readme_content = """# 🚀 Karnataka Village Visualization - Server Deployment

## Quick Start

### Option 1: Windows
1. Double-click `start_server.bat`
2. Wait for dependencies to install
3. Server starts automatically at http://localhost:8000

### Option 2: Linux/Mac
```bash
# Make script executable
chmod +x start_server.sh

# Run deployment script
./start_server.sh
```

### Option 3: Manual
```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python server_app.py
```

## Server Configuration

### Change Port (if needed)
Edit `server_app.py` and change the port number:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # Change 8000 to your port
```

### External Access
The server runs on `0.0.0.0:8000` by default, making it accessible from external IPs.

## Data Files

The application will automatically use the best available data file:
1. `deployable_data.json.gz` - Compressed data (recommended)
2. `deployable_data.json` - Full JSON data
3. `deployable_data_minimal.json` - Minimal data for testing
4. Fallback sample data (created automatically if needed)

## Health Check

Check if the server is running:
```bash
curl http://localhost:8000/api/health
```

## API Endpoints

- **Main App**: http://localhost:8000/
- **API Docs**: http://localhost:8000/docs
- **Village Data**: http://localhost:8000/api/data
- **Districts**: http://localhost:8000/api/districts
- **Health**: http://localhost:8000/api/health

## Troubleshooting

### Port Already in Use
Change the port in `server_app.py` or stop other services using port 8000.

### Dependencies Issues
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### Data Loading Issues
The application will automatically create sample data if no data files are found.

## Performance

- **Loading Time**: 2-5 seconds (typically)
- **Memory Usage**: Efficient with optimized data
- **Scalability**: Stateless design supports multiple instances

## Support

If you encounter issues:
1. Check the console output for error messages
2. Verify all files are present in the deployment directory
3. Ensure Python 3.8+ is installed
4. Check server firewall settings for port 8000
"""
    
    with open(deploy_dir / "DEPLOYMENT_README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)

def check_deployment_requirements():
    """Check if all requirements are met for deployment"""
    print("🔍 Checking deployment requirements...")
    
    required_files = [
        "server_app.py",
        "templates/index.html",
        "requirements.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    # Check if deployable data exists
    data_files = [
        "deployable_data.json.gz",
        "deployable_data.json",
        "deployable_data_minimal.json"
    ]
    
    found_data = [f for f in data_files if Path(f).exists()]
    if not found_data:
        print("⚠️  No deployable data files found. Will use fallback data.")
    else:
        print(f"✅ Found data files: {', '.join(found_data)}")
    
    print("✅ All deployment requirements met!")
    return True

def main():
    """Main deployment function"""
    print("🏘️ Karnataka Village Visualization - Deployment Tool")
    print("=" * 60)
    
    # Check requirements
    if not check_deployment_requirements():
        print("❌ Cannot proceed with deployment. Please fix missing files.")
        return
    
    # Create deployment package
    create_deployment_package()
    
    print("\n🎉 Deployment package ready!")
    print("\n📁 Files included:")
    print("   - server_app.py (main application)")
    print("   - data_loader.py (data loading utilities)")
    print("   - requirements.txt (Python dependencies)")
    print("   - templates/ (web interface)")
    print("   - deployable data files")
    print("   - start_server.bat (Windows)")
    print("   - start_server.sh (Linux/Mac)")
    print("   - DEPLOYMENT_README.md (instructions)")

if __name__ == "__main__":
    main()
