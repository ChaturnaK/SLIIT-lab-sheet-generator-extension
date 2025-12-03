# Lab Sheet Generator

A desktop application for university students to generate lab sheet templates automatically.

## Features

- First-time setup wizard for student information
- Store multiple module names and codes
- Generate formatted lab sheets in .docx format
- Custom university logo support
- Cross-platform (Windows, macOS, Linux)

## Installation

### For Development

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the application:
   ```bash
   python -m app.main
   ```

## Building the Executable

To create a standalone .exe file:

```bash
# Make sure all dependencies are installed
pip install -r requirements.txt

# Run the build script
python build.py
```

The executable will be created in the `dist/` folder as `LabSheetGenerator.exe`.

### Manual Build (Alternative)

If you prefer to build manually:

```bash
pyinstaller --name="LabSheetGenerator" --windowed --onefile app/main.py
```

### Distribution

The generated `.exe` file is standalone and can be:
- Copied to any Windows computer
- Shared with other students
- Run without Python installation
- Placed anywhere (Desktop, USB drive, etc.)

**Note**: On first run, users will see the setup wizard to configure their information.

## Project Structure

```
lab-sheet-generator-app/
│
├── app/                   ← source code
│   ├── __init__.py
│   ├── main.py            ← app entry point (GUI)
│   ├── generator.py       ← code for docx creation
│   ├── config.py          ← load/save user settings
│   ├── ui/                ← UI files
│   │   ├── __init__.py
│   │   ├── setup_ui.py    ← first-time setup screen
│   │   ├── main_ui.py     ← main window
│   │   └── assets/
│   │       └── default_logo.png
│   └── utils/
│       ├── paths.py       ← handles config paths
│       └── validators.py  ← input validation
│
├── tests/
│   └── test_generator.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

## Configuration

The app stores user configuration in:
- **Windows**: `%APPDATA%/LabSheetGenerator/config.json`
- **macOS/Linux**: `~/.config/LabSheetGenerator/config.json`

Generated lab sheets are saved to:
- `Documents/LabSheets/`

## Usage

1. On first run, enter your student information and module details
2. Upload your university logo
3. Select a module and practical number
4. Click "Generate" to create your lab sheet

## License

MIT License