#!/usr/bin/env python3
"""
Compress shapefile components for GitHub upload
"""

import gzip
import shutil
import os

def compress_file(filename):
    """Compress a file using gzip"""
    if os.path.exists(filename):
        compressed_name = filename + '.gz'
        with open(filename, 'rb') as f_in:
            with gzip.open(compressed_name, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        print(f"✅ Compressed {filename} -> {compressed_name}")
        return compressed_name
    else:
        print(f"❌ File not found: {filename}")
        return None

def main():
    """Compress all shapefile components"""
    print("🗜️ Compressing shapefile components...")
    
    # Shapefile components to compress
    files_to_compress = [
        'Karnataka.shp',
        'Karnataka.shx', 
        'Karnataka.dbf',
        'Karnataka.prj',
        'Karnataka.cpg',
        'Karnataka.sbn',
        'Karnataka.sbx'
    ]
    
    compressed_files = []
    for filename in files_to_compress:
        compressed = compress_file(filename)
        if compressed:
            compressed_files.append(compressed)
    
    print(f"\n🎉 Compressed {len(compressed_files)} files:")
    for f in compressed_files:
        size = os.path.getsize(f) / (1024 * 1024)  # Size in MB
        print(f"  📁 {f}: {size:.1f} MB")
    
    print("\n📋 Next steps:")
    print("1. Add compressed files to .gitignore exceptions")
    print("2. Push to GitHub")
    print("3. Server will extract and process just like local!")

if __name__ == "__main__":
    main()
