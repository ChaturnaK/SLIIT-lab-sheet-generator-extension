"""
Build script for creating Lab Sheet Generator executable.
Run this script to build the .exe file.

Usage:
    python build.py
"""

import sys
import shutil
import os
from pathlib import Path

def clean_previous_builds():
    """Remove previous build artifacts."""
    print("\n🧹 Cleaning previous builds...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   ✓ Removed {dir_name}/")
    
    # Remove spec file
    spec_file = 'LabSheetGenerator.spec'
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print(f"   ✓ Removed {spec_file}")

def check_dependencies():
    """Check if all required packages are installed."""
    print("\n📦 Checking dependencies...")
    
    required_packages = {
        'PySide6': 'PySide6',
        'docx': 'python-docx',
        'PIL': 'Pillow',
        'PyInstaller': 'pyinstaller'
    }
    
    missing = []
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"   ✓ {package_name}")
        except ImportError:
            print(f"   ✗ {package_name} - MISSING")
            missing.append(package_name)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("\nInstall them with:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True

def build_exe():
    """Build the executable using PyInstaller."""
    
    print("=" * 60)
    print("  Lab Sheet Generator - Build Script")
    print("=" * 60)
    
    # Clean previous builds
    clean_previous_builds()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("\n🔨 Building executable...")
    print("   This may take a few minutes...\n")
    
    # Import PyInstaller
    try:
        import PyInstaller.__main__
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        os.system("pip install pyinstaller")
        import PyInstaller.__main__
    
    # PyInstaller arguments
    args = [
        'app/main.py',                              # Entry point (main.py in root)
        '--name=LabSheetGenerator',             # Executable name
        '--windowed',                           # No console window
        '--onefile',                            # Single executable file
        '--clean',                              # Clean PyInstaller cache
        '--noconfirm',                          # Replace output without asking
        
        # Hidden imports that PyInstaller might miss
        '--hidden-import=PySide6.QtCore',
        '--hidden-import=PySide6.QtGui',
        '--hidden-import=PySide6.QtWidgets',
        '--hidden-import=docx',
        '--hidden-import=docx.shared',
        '--hidden-import=docx.enum.text',
        '--hidden-import=docx.oxml',
        '--hidden-import=docx.oxml.ns',
        '--hidden-import=docx.oxml.shared',
        '--hidden-import=PIL',
        '--hidden-import=PIL.Image',
        '--hidden-import=lxml',
        '--hidden-import=lxml.etree',
        
        # Exclude unnecessary packages to reduce size
        '--exclude-module=matplotlib',
        '--exclude-module=numpy',
        '--exclude-module=pytest',
        '--exclude-module=tkinter',
    ]
    
    # Run PyInstaller
    try:
        PyInstaller.__main__.run(args)
        
        print("\n" + "=" * 60)
        print("  ✅ Build Complete!")
        print("=" * 60)
        
        exe_path = Path('dist/LabSheetGenerator.exe')
        if exe_path.exists():
            print(f"\n📍 Executable location:")
            print(f"   {exe_path.absolute()}")
            print(f"\n📊 File size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
        else:
            print("\n⚠️  Executable not found in expected location.")
            print("   Check for errors above.")
            return
        
        print("\n📝 Next steps:")
        print("   1. Test the executable: dist\\LabSheetGenerator.exe")
        print("   2. Copy it anywhere you want")
        print("   3. Share it with others")
        print("\n💡 Note: First-time users will see the setup wizard.")
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ Build failed with error:")
        print(f"   {e}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        build_exe()
    except KeyboardInterrupt:
        print("\n\n⚠️  Build cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)