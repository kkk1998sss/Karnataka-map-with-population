#!/usr/bin/env python3
"""
Quick script to regenerate sample data with realistic village boundaries
"""

import os
import sys

def main():
    print("🔄 Regenerating sample data with realistic village boundaries...")
    
    # Check if simple_data_loader.py exists
    if not os.path.exists("simple_data_loader.py"):
        print("❌ simple_data_loader.py not found")
        return False
    
    try:
        # Import and run the data loader
        from simple_data_loader import create_sample_data
        
        # Remove old sample data
        if os.path.exists("sample_data.json"):
            os.remove("sample_data.json")
            print("🗑️ Removed old sample data")
        
        # Create new realistic sample data
        create_sample_data()
        
        print("✅ Sample data regenerated successfully!")
        print("🎯 You can now run: python main.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error regenerating data: {e}")
        return False

if __name__ == "__main__":
    main()
