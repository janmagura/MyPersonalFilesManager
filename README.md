# Folder Structure Manager - Mind Map Organizer

A comprehensive Python application for creating, visualizing, and managing folder structures with automatic file sorting capabilities. Features a mind-map style interface for intuitive organization.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🌟 Features

### Core Functionality
- **Mind-Map Style Folder Structure**: Create and visualize folder hierarchies as an interactive mind map
- **Smart File Classification**: Automatic file sorting using intelligent algorithms
- **Pre-defined Templates**: Ready-to-use folder structures for common use cases
- **Custom Folder Creation**: Add, edit, and delete folders with custom properties
- **Project Folder Detection**: Automatically keeps project folders intact (Git repos, code projects, etc.)

### Visualization
- **Interactive Canvas**: Visual representation of your folder structure
- **Configurable Display Options**:
  - Show/hide file counts
  - Display file types
  - Toggle comments and descriptions
  - Custom color schemes
- **Tree View**: Traditional hierarchical view alongside mind map
- **Real-time Statistics**: File counts, sizes, and type distributions

### Data Management
- **Import/Export**: Save and load folder structures as JSON files
- **Password Protection**: Optional encryption for sensitive structures
- **Source Selection**: Choose any folder as the source for organization
- **Target Selection**: Specify where to create the organized structure
- **Preview Changes**: See what will happen before organizing files

### Smart Algorithms
- **Extension-based Classification**: High-confidence file type detection
- **Keyword Analysis**: Smart folder name and content analysis
- **MIME Type Detection**: Fallback classification method
- **Project Integrity**: Preserves complete project folders when detected

## 📋 Pre-defined Folder Structure

The app comes with a ready-to-use folder structure:

```
🏠 My Files
├── 🎬 Media
│   ├── 🎥 Videos (.mp4, .avi, .mkv, .mov)
│   ├── 📷 Photos & Pictures (.jpg, .png, .gif, .bmp)
│   └── 🎵 Audio & Music (.mp3, .wav, .flac)
├── 📄 Documents (.pdf, .doc, .docx, .txt)
├── 🔒 Private Data
├── 💻 Projects - Programming (.py, .js, .java, .cpp)
├── 📚 Projects - Books & Writing
├── 📦 Archives & Backups (.zip, .rar, .7z, .tar)
├── 📊 Data Files (.csv, .sql, .db)
└── 🗂️ Miscellaneous
```

Each folder includes:
- **Name**: Clear, descriptive title
- **Description**: What the folder contains
- **Purpose**: Why this folder exists
- **File Extensions**: Associated file types
- **Color Coding**: Visual distinction
- **Icon**: Emoji-based icon for quick recognition

## 🖼️ Application Structure Visualization

```
┌─────────────────────────────────────────────────────────────────┐
│                    FOLDER STRUCTURE MANAGER                      │
├─────────────────────────────────────────────────────────────────┤
│  [New] [Export] [Import] │ [Add] [Edit] [Delete] │ Source ████  │
├──────────────────────┬──────────────────────────────────────────┤
│                      │                                          │
│  FOLDER STRUCTURE    │        MIND MAP VISUALIZATION            │
│  ───────────────     │        ─────────────────────             │
│                      │                                          │
│  🏠 My Files         │           ┌─────────────┐                │
│  ├── 🎬 Media        │           │  🏠 My Files │                │
│  │   ├── 🎥 Videos   │           └──────┬──────┘                │
│  │   ├── 📷 Photos   │                  │                       │
│  │   └── 🎵 Audio    │      ┌───────────┼───────────┐           │
│  ├── 📄 Documents    │      │           │           │           │
│  ├── 🔒 Private      │  ┌───▼───┐  ┌───▼───┐  ┌───▼───┐        │
│  ├── 💻 Programming  │  │ Media │  │ Docs  │  │Private│        │
│  ├── 📚 Books        │  └───┬───┘  └───────┘  └───────┘        │
│  ├── 📦 Archives     │      │                                  │
│  ├── 📊 Data         │  ┌───▼───┐                              │
│  └── 🗂️ Misc        │  │Videos │                              │
│                      │  └───────┘                              │
│                      │                                          │
│  Name │ Type │ Files │                                          │
│  ──────────────────── │                                          │
│                      │                                          │
├──────────────────────┴──────────────────────────────────────────┤
│  [🔄 Organize Files] [👁️ Preview] ☑ Keep projects intact       │
├─────────────────────────────────────────────────────────────────┤
│  Status: Ready                          [████████░░] 85%        │
└─────────────────────────────────────────────────────────────────┘
```

## 🏗️ Software Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         GUI LAYER                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  ToolbarFrame   │  │   TreePanel     │  │  CanvasPanel    │  │
│  │  (Actions)      │  │  (Hierarchy)    │  │ (Mind Map View) │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              FolderManagerGUI                            │    │
│  │  - Manages UI components                                 │    │
│  │  - Handles user interactions                             │    │
│  │  - Coordinates between views                             │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       LOGIC LAYER                               │
│  ┌──────────────────────┐    ┌──────────────────────┐          │
│  │ FolderStructureMgr   │    │  SmartFileClassifier │          │
│  │ ──────────────────── │    │  ─────────────────── │          │
│  │ • Node Management    │    │ • Extension Map      │          │
│  │ • Path Generation    │    │ • Keyword Analysis   │          │
│  │ • Import/Export      │    │ • MIME Detection     │          │
│  │ • Statistics         │    │ • Project Detection  │          │
│  └──────────────────────┘    └──────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │   FolderNode     │  │    FileStats     │  │   FileType   │  │
│  │   (Dataclass)    │  │   (Dataclass)    │  │    (Enum)    │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 📦 Installation

### Requirements
- Python 3.8 or higher
- Tkinter (usually included with Python)
- Optional: `cryptography` for password protection
- Optional: `Pillow` for enhanced image support

### Install Dependencies

```bash
# Basic installation (no additional packages needed for core features)
python3 folder_manager_app.py

# With optional dependencies for full features
pip install cryptography Pillow
```

### Windows
1. Download the repository
2. Ensure Python 3.8+ is installed
3. Run: `python folder_manager_app.py`

### Linux
1. Clone or download the repository
2. Make executable: `chmod +x folder_manager_app.py`
3. Run: `./folder_manager_app.py` or `python3 folder_manager_app.py`

## 🧩 Thunar File Manager Plugin

### Installation

1. **Copy plugin files**:
   ```bash
   # Copy to user directory
   mkdir -p ~/.local/share/thunar/uca-scripts
   cp thunar_plugin/thunar-folder-manager.py ~/.local/share/thunar/uca-scripts/
   cp thunar_plugin/thunar-uca.xml ~/.local/share/Thunar/uca.xml
   
   # Or system-wide (requires sudo)
   sudo cp thunar_plugin/thunar-folder-manager.py /usr/share/thunar/uca-scripts/
   sudo cp thunar_plugin/thunar-uca.xml /etc/xdg/Thunar/uca.xml
   ```

2. **Make executable**:
   ```bash
   chmod +x ~/.local/share/thunar/uca-scripts/thunar-folder-manager.py
   ```

3. **Restart Thunar**:
   ```bash
   thunar -q  # Quit Thunar
   thunar &   # Restart
   ```

### Usage

After installation:
1. Right-click on any folder in Thunar
2. Select **"Organize with Folder Manager"** from the context menu
3. The application opens with the selected folder as the source

## 🚀 Quick Start Guide

### 1. Launch the Application
```bash
python3 folder_manager_app.py
```

### 2. Select Source Directory
- Click **"Browse"** next to "Source"
- Navigate to the folder containing your unorganized files
- Click "Open"

### 3. Select Target Directory
- Click **"Browse"** next to "Target"
- Choose where to create the organized structure
- Click "Open"

### 4. Customize Structure (Optional)
- Use the tree view to see the folder hierarchy
- Right-click to add, edit, or delete folders
- Configure file extensions and colors for each folder

### 5. Preview Changes
- Click **"👁️ Preview Changes"** to see what will be organized
- Review the file type distribution

### 6. Organize Files
- Check **"Keep project folders intact"** if you have code projects
- Click **"🔄 Organize Files"**
- Wait for the process to complete

### 7. Save Your Structure
- Click **"📤 Export"** to save your folder structure
- Optionally add password protection
- Load it later with **"📥 Import"**

## 🧠 Smart Classification Algorithm

The app uses a multi-layered approach to classify files:

### Layer 1: Extension Matching (Confidence: 95%)
```python
.mp4 → VIDEO
.jpg → IMAGE
.pdf → DOCUMENT
.py → CODE
```

### Layer 2: Filename Keywords (Confidence: 70%)
```python
"vacation_photo.jpg" → IMAGE (contains "photo")
"meeting_recording.wav" → AUDIO (contains "recording")
"project_report.docx" → DOCUMENT (contains "report")
```

### Layer 3: MIME Type Detection (Confidence: 60-80%)
```python
video/* → VIDEO
image/* → IMAGE
text/* → DOCUMENT
application/zip → ARCHIVE
```

### Layer 4: Folder Context Analysis
- Analyzes folder names for keywords
- Examines folder contents for dominant file types
- Detects project indicators (.git, package.json, etc.)

### Project Folder Detection

The app intelligently identifies project folders that should remain intact:

**Indicators:**
- Version control: `.git/`
- Package managers: `package.json`, `Cargo.toml`, `pom.xml`
- Build files: `Makefile`, `setup.py`, `build.gradle`
- IDE configs: `.vscode/`, `.idea/`
- Dependencies: `node_modules/`, `__pycache__/`

**Mixed Content Detection:**
- Code + Documentation = Keep intact
- Code + Data = Keep intact
- Multiple file types with structure = Keep intact

## 🎨 Customization

### Adding Custom Folders

1. Click **"➕ Add Folder"**
2. Fill in the details:
   - **Name**: Folder name
   - **Description**: Brief description
   - **Purpose**: Detailed purpose
   - **File Extensions**: Comma-separated list (e.g., `.py,.js,.ts`)
   - **Color**: Choose a color for visualization

### Modifying Visualization

Use the checkboxes above the mind map:
- ☑ **File Count**: Show number of files in each folder
- ☑ **File Types**: Display associated file types
- ☑ **Comments**: Show folder descriptions
- ☑ **Colors**: Use custom folder colors

### Color Coding Best Practices

- **Warm colors** (red, orange): Important or urgent folders
- **Cool colors** (blue, green): Regular content folders
- **Neutral colors** (gray): Archive or miscellaneous folders
- **Bright colors**: Frequently accessed folders

## 📊 File Statistics

The app tracks:
- **Total files** per folder
- **Total size** in bytes
- **File type distribution** (videos, images, documents, etc.)
- **Extension breakdown**
- **Last modified date**

## 🔒 Security Features

### Password Protection

When exporting your folder structure:
1. Click **"📤 Export"**
2. Choose **"Yes"** for password protection
3. Enter a secure password
4. The file is encrypted using Fernet (symmetric encryption)

To import a protected file:
1. Click **"📥 Import"**
2. Select the encrypted file
3. Choose **"Yes"** for password protection
4. Enter the correct password

## 🛠️ Troubleshooting

### Common Issues

**Issue**: Application won't start
- **Solution**: Ensure Python 3.8+ is installed and tkinter is available

**Issue**: Can't see mind map
- **Solution**: Resize the window or click "Auto Layout"

**Issue**: Files not organizing correctly
- **Solution**: Check file extensions are correctly configured in folder settings

**Issue**: Thunar plugin not appearing
- **Solution**: 
  1. Verify XML file is in correct location
  2. Restart Thunar completely (`thunar -q`)
  3. Check Thunar UCA is enabled

**Issue**: Permission errors during organization
- **Solution**: Run application with appropriate permissions or check file ownership

## 📝 Examples

### Example 1: Organizing Downloads Folder

```
Source: ~/Downloads
Target: ~/Organized Files

Before:
Downloads/
├── vacation.jpg
├── report.pdf
├── song.mp3
├── movie.mp4
└── archive.zip

After:
Organized Files/
├── Photos & Pictures/
│   └── vacation.jpg
├── Documents/
│   └── report.pdf
├── Audio & Music/
│   └── song.mp3
├── Videos/
│   └── movie.mp4
└── Archives & Backups/
    └── archive.zip
```

### Example 2: Preserving Project Structure

```
Source: ~/Work
Target: ~/Organized Work

With "Keep project folders intact" enabled:

Work/
└── my-python-project/
    ├── src/
    │   └── main.py
    ├── tests/
    ├── requirements.txt
    └── README.md

Stays intact as:
Organized Work/
└── projects/
    └── my-python-project/
        ├── src/
        │   └── main.py
        ├── tests/
        ├── requirements.txt
        └── README.md
```

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional file type classifiers
- More pre-defined templates
- Enhanced visualization options
- Plugin support for other file managers
- Machine learning-based classification

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built with Python and Tkinter
- Uses cryptography library for encryption
- Inspired by mind-mapping tools and file managers

---

**Happy Organizing! 🗂️✨**
