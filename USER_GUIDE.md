# Lab Sheet Generator - User Guide

## Table of Contents
1. [Installation](#installation)
2. [First Time Setup](#first-time-setup)
3. [Generating Lab Sheets](#generating-lab-sheets)
4. [Managing Configuration](#managing-configuration)
5. [Troubleshooting](#troubleshooting)

---

## Installation

### Option 1: Download Executable (Recommended for Users)
1. Download `LabSheetGenerator.exe` from the releases
2. Place it anywhere on your computer (e.g., Desktop, Documents)
3. Double-click to run - no installation required!

### Option 2: Run from Source (For Developers)
```bash
# Clone the repository
git clone <repository-url>
cd lab-sheet-generator-app

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m app.main
```

---

## First Time Setup

When you run the application for the first time, you'll see the **Setup Wizard**.

### Step 1: Enter Student Information
- **Full Name**: Enter your full name as you want it to appear on lab sheets
  - Example: `NONIS P.K.D.T.`
- **Student ID**: Enter your university student ID
  - Example: `IT23614130`

### Step 2: Upload University Logo
1. Click **"Upload Logo"** button
2. Select your university logo image file (PNG, JPG, or JPEG)
3. The logo will be displayed in the preview box
4. **Note**: The logo is optional but recommended

### Step 3: Add Your Modules
1. Click **"Add Module"** button
2. Enter the module details:
   - **Module Name**: Full name of the module
     - Example: `Programming Paradigms`
   - **Module Code**: Module code in format XX0000
     - Example: `SE2052`
3. Click **OK** to add the module
4. Repeat for all your modules this semester
5. You can remove modules by selecting them and clicking **"Remove Module"**

### Step 4: Finish Setup
1. Click **"Finish Setup"** button
2. Your configuration will be saved
3. The main window will open automatically

---

## Generating Lab Sheets

### Quick Generation
1. **Select Module**: Choose from the dropdown list
2. **Select Practical Number**: Use the spin box (1-99)
3. Click **"Generate Lab Sheet"** button
4. Wait for the success message
5. The lab sheet will be saved to `Documents/LabSheets/`

### Opening Generated Files
- **Automatic**: Click "Open" in the success dialog
- **Manual**: 
  - Menu → File → Open Output Folder
  - Navigate to `Documents/LabSheets/`

### File Naming
Generated files are named automatically:
- Format: `Practical_XX_<StudentID>.docx`
- Example: `Practical_06_IT23614130.docx`

---

## Managing Configuration

### Editing Your Information
1. Menu → **Settings** → **Edit Configuration**
2. The setup wizard opens with your current information
3. Make your changes
4. Click **"Finish Setup"** to save

### Changing Output Folder
1. Menu → **File** → **Change Output Folder**
2. Select the new folder location
3. All future lab sheets will be saved there

### Resetting Configuration
1. Menu → **Settings** → **Reset Configuration**
2. Confirm the reset
3. Application will close
4. Run again to start fresh setup

---

## Troubleshooting

### Issue: "No modules configured" error
**Solution**: Add modules in Settings → Edit Configuration

### Issue: Logo not appearing in generated document
**Possible causes**:
1. Logo file was moved or deleted
2. Logo wasn't uploaded during setup

**Solution**: 
- Settings → Edit Configuration
- Upload the logo again

### Issue: Cannot find generated files
**Solution**: 
- Menu → File → Open Output Folder
- Default location: `C:\Users\<YourName>\Documents\LabSheets\`

### Issue: Module code validation error
**Requirement**: Module codes must be in format XX0000
- ✓ Correct: `SE2052`, `CS1010`, `IT2305`
- ✗ Incorrect: `SE 2052`, `se2052`, `SE205`

### Issue: Application won't start
**Solution**:
1. Make sure you have .NET Framework installed (Windows)
2. Try running as Administrator
3. Check Windows Defender isn't blocking it

---

## Tips & Best Practices

### For Best Results
- ✓ Use a high-quality logo (PNG recommended)
- ✓ Keep module codes consistent with your university format
- ✓ Add all your modules at once during setup
- ✓ Use descriptive module names

### Organizing Your Lab Sheets
- Create subfolders by module in the output folder
- Use the practical number consistently
- Keep backup copies of important lab sheets

### Sharing with Classmates
1. Share the `LabSheetGenerator.exe` file
2. Each person sets up their own information
3. Everyone can use the same logo

---

## Keyboard Shortcuts

- **Alt + F**: Open File menu
- **Alt + S**: Open Settings menu
- **Alt + H**: Open Help menu
- **Enter**: Generate lab sheet (when main window is focused)

---

## Support

For issues, suggestions, or contributions:
- Report bugs on GitHub Issues
- Submit feature requests
- Contribute to the codebase

---

## Version History

### v1.0.0 (Current)
- Initial release
- Basic lab sheet generation
- Configuration management
- Module management
- Logo support