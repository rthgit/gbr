#!/usr/bin/env python3
"""
Create Updated ZIP Package for Zenodo
"""

import shutil
import os
from datetime import datetime

def create_updated_zip():
    """Create updated ZIP package with correct author information"""
    
    print("🚀 Creating Updated ZIP Package for Zenodo...")
    print("="*60)
    
    # Remove old ZIP if exists
    old_zip = "quantum-gravity-discovery-v1.0.0.zip"
    if os.path.exists(old_zip):
        os.remove(old_zip)
        print(f"✅ Removed old ZIP: {old_zip}")
    
    # Create new ZIP with updated version
    new_zip = "quantum-gravity-discovery-v1.0.1.zip"
    
    print(f"📦 Creating new ZIP: {new_zip}")
    shutil.make_archive("quantum-gravity-discovery-v1.0.1", 'zip', 'zenodo_quantum_gravity_discovery')
    
    # Get file size
    file_size = os.path.getsize(new_zip) / (1024 * 1024)  # MB
    print(f"📊 Package size: {file_size:.2f} MB")
    
    # Count files in directory
    total_files = 0
    for root, dirs, files in os.walk('zenodo_quantum_gravity_discovery'):
        total_files += len(files)
    
    print(f"📊 Total files: {total_files}")
    
    print("\n" + "="*60)
    print("🎉 UPDATED ZENODO PACKAGE COMPLETE!")
    print("="*60)
    print(f"📦 Updated ZIP: {new_zip}")
    print(f"📊 Size: {file_size:.2f} MB")
    print(f"📊 Files: {total_files}")
    print("\n🎯 READY FOR ZENODO UPLOAD WITH CORRECT AUTHOR INFO!")
    print("📋 Authors: Christian Quintino De Luca (ORCID: 0009-0000-4198-5449), Gregorio De Luca")
    print("🏢 Affiliation: RTH Italia - Research & Technology Hub")
    print("📧 Email: info@rthitalia.com")
    print("📅 Date: October 20, 2025")
    
    return new_zip

if __name__ == "__main__":
    create_updated_zip()
