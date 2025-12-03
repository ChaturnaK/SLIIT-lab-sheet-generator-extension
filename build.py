"""
Build script for creating Lab Sheet Generator executable.
Run this script to build the .exe file.
"""

import PyInstaller.__main__
import shutil
import os
from pathlib import Path

def build_exe():
    """Build the executable using PyInstaller."""
    
    print("=" * 60)
    print("Building Lab Sheet Generator Executable")
    print("=" * 60)
    
    # Clean previous builds
    print("\nCleaning previous builds...")
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Removed {dir_name}/")
    
    # Remove old spec file
    spec_file = 'LabSheetGenerator.spec'
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print(f"  Removed {spec_file}")
    
    print("\nBuilding executable...")
    
    # PyInstaller arguments
    args = [
        'app/main.py',                          # Entry point
        '--name=LabSheetGenerator',             # Executable name
        '--windowed',                           # No console window
        '--onefile',                            # Single executable file
        '--clean',                              # Clean PyInstaller cache
        '--noconfirm',                          # Replace output without asking
        
        # Add hidden imports that PyInstaller might miss
        '--hidden-import=PySide6.QtCore',
        '--hidden-import=PySide6.QtGui',
        '--hidden-import=PySide6.QtWidgets',
        
        # Exclude unnecessary packages to reduce size
        '--exclude-module=matplotlib',
        '--exclude-module=pytest',
        '--exclude-module=tkinter',
    ]
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print("\n" + "=" * 60)
    print("Build Complete!")
    print("=" * 60)
    print(f"\nExecutable location: {Path('dist/LabSheetGenerator.exe').absolute()}")
    print("\nYou can now:")
    print("  1. Run the executable from dist/LabSheetGenerator.exe")
    print("  2. Copy it to any location on your computer")
    print("  3. Share it with others")
    print("\nNote: First-time users will need to complete the setup wizard.")

if __name__ == '__main__':
    build_exe()