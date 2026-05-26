#!/usr/bin/env python3
"""
Thunar File Manager Plugin - Folder Structure Manager
Integrates the folder management app with Thunar file manager.

Installation:
1. Copy this file to ~/.local/share/thunar/thunar-uca/
2. Or system-wide: /usr/share/thunar/thunar-uca/
3. Create a corresponding .xml configuration file
4. Restart Thunar

Usage:
- Right-click on any folder in Thunar
- Select "Organize with Folder Manager"
- The main app will open with the selected folder as source
"""

import os
import sys
import subprocess
from pathlib import Path

# Get the directory where this plugin is located
PLUGIN_DIR = Path(__file__).parent
APP_DIR = PLUGIN_DIR.parent

# Path to the main application
MAIN_APP = APP_DIR / 'folder_manager_app.py'


def get_selected_paths():
    """
    Get selected file/folder paths from Thunar environment variables.
    Thunar passes selected items via environment variables.
    """
    selected = []
    
    # Thunar passes multiple selections as THUNAR_SELECTED_0, THUNAR_SELECTED_1, etc.
    i = 0
    while True:
        env_var = f'THUNAR_SELECTED_{i}'
        path = os.environ.get(env_var)
        if path:
            selected.append(Path(path))
            i += 1
        else:
            break
    
    # If no THUNAR_SELECTED variables, try THUNAR_CURRENT_FILE
    if not selected:
        current = os.environ.get('THUNAR_CURRENT_FILE')
        if current:
            selected.append(Path(current))
    
    # Fallback to command line arguments
    if not selected and len(sys.argv) > 1:
        selected = [Path(arg) for arg in sys.argv[1:]]
    
    return selected


def launch_folder_manager(source_paths=None):
    """Launch the main folder manager application"""
    
    cmd = [sys.executable, str(MAIN_APP)]
    
    if source_paths:
        # Pass source paths as arguments
        for path in source_paths:
            cmd.extend(['--source', str(path)])
    
    try:
        # Launch in background
        subprocess.Popen(cmd, start_new_session=True)
        return True
    except Exception as e:
        print(f"Error launching folder manager: {e}")
        return False


def show_context_menu():
    """Display a simple context menu or dialog"""
    selected = get_selected_paths()
    
    if selected:
        print(f"Selected items: {[str(p) for p in selected]}")
        
        # For folders, offer to organize contents
        folders = [p for p in selected if p.is_dir()]
        files = [p for p in selected if p.is_file()]
        
        if folders:
            print(f"\nFound {len(folders)} folder(s) to organize:")
            for folder in folders:
                print(f"  - {folder}")
            
            # Launch with first folder as source
            launch_folder_manager(folders)
        elif files:
            print(f"\nFound {len(files)} file(s)")
            # Use parent directory as source
            parent = files[0].parent
            launch_folder_manager([parent])
    else:
        print("No items selected")
        launch_folder_manager()


def main():
    """Main entry point for Thunar plugin"""
    
    # Check if running from Thunar
    if 'THUNAR_CURRENT_FILE' in os.environ or any(k.startswith('THUNAR_SELECTED_') for k in os.environ.keys()):
        print("Launched from Thunar")
        show_context_menu()
    else:
        # Launched directly
        print("Launched directly (not from Thunar)")
        launch_folder_manager()


if __name__ == '__main__':
    main()
