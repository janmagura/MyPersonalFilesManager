#!/usr/bin/env python3
"""
Folder Structure Manager - Mind-Map Style File Organization Tool
A comprehensive tool for creating, visualizing, and managing folder structures
with automatic file sorting capabilities.
"""

import os
import sys
import json
import hashlib
import shutil
import mimetypes
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, colorchooser
import threading
from collections import defaultdict

# Try to import optional dependencies
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import cryptography
    from cryptography.fernet import Fernet
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


class FileType(Enum):
    """Enumeration of file types for categorization"""
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    ARCHIVE = "archive"
    CODE = "code"
    DATA = "data"
    EXECUTABLE = "executable"
    FONT = "font"
    OTHER = "other"


@dataclass
class FolderNode:
    """Represents a node in the folder structure mind-map"""
    id: str
    name: str
    description: str = ""
    purpose: str = ""
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    file_extensions: List[str] = field(default_factory=list)
    file_types: List[FileType] = field(default_factory=list)
    color: str = "#FFFFFF"
    text_color: str = "#000000"
    icon: str = "📁"
    is_predefined: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'purpose': self.purpose,
            'parent_id': self.parent_id,
            'children': self.children,
            'file_extensions': self.file_extensions,
            'file_types': [ft.value for ft in self.file_types],
            'color': self.color,
            'text_color': self.text_color,
            'icon': self.icon,
            'is_predefined': self.is_predefined,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FolderNode':
        """Create from dictionary"""
        file_types = [FileType(ft) for ft in data.get('file_types', []) if ft in [e.value for e in FileType]]
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            purpose=data.get('purpose', ''),
            parent_id=data.get('parent_id'),
            children=data.get('children', []),
            file_extensions=data.get('file_extensions', []),
            file_types=file_types,
            color=data.get('color', '#FFFFFF'),
            text_color=data.get('text_color', '#000000'),
            icon=data.get('icon', '📁'),
            is_predefined=data.get('is_predefined', False),
            metadata=data.get('metadata', {})
        )


@dataclass
class FileStats:
    """Statistics about files in a folder"""
    total_files: int = 0
    total_size: int = 0
    file_type_counts: Dict[FileType, int] = field(default_factory=dict)
    extensions: Dict[str, int] = field(default_factory=dict)
    last_modified: Optional[datetime] = None


class SmartFileClassifier:
    """Intelligent file classification system"""
    
    # File extension mappings
    EXTENSION_MAP = {
        FileType.VIDEO: ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpeg', '.mpg'],
        FileType.IMAGE: ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff', '.raw', '.psd', '.ai'],
        FileType.DOCUMENT: ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx', '.md', '.epub'],
        FileType.AUDIO: ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus'],
        FileType.ARCHIVE: ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso'],
        FileType.CODE: ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.html', '.css', '.scss', '.json', '.xml', '.yaml', '.yml'],
        FileType.DATA: ['.csv', '.sql', '.db', '.sqlite', '.parquet', '.feather', '.pickle', '.pkl', '.npy', '.npz'],
        FileType.EXECUTABLE: ['.exe', '.msi', '.deb', '.rpm', '.app', '.dmg', '.bin', '.sh', '.bat', '.cmd'],
        FileType.FONT: ['.ttf', '.otf', '.woff', '.woff2', '.eot'],
    }
    
    # Keywords for folder name analysis
    KEYWORD_MAP = {
        'video': ['video', 'movie', 'film', 'clip', 'recording', 'screen'],
        'image': ['photo', 'picture', 'image', 'screenshot', 'snapshot', 'pic'],
        'document': ['doc', 'document', 'report', 'paper', 'manuscript', 'book'],
        'audio': ['music', 'audio', 'sound', 'podcast', 'recording', 'song'],
        'archive': ['archive', 'backup', 'old', 'compressed', 'zip'],
        'code': ['code', 'src', 'source', 'project', 'dev', 'programming', 'script'],
        'data': ['data', 'dataset', 'database', 'export', 'dump'],
        'private': ['private', 'personal', 'confidential', 'secret', 'secure'],
        'work': ['work', 'office', 'business', 'professional'],
        'personal': ['personal', 'home', 'family'],
    }
    
    @classmethod
    def classify_file(cls, filepath: Path) -> Tuple[FileType, float]:
        """
        Classify a file and return confidence score
        Returns: (FileType, confidence_score)
        """
        ext = filepath.suffix.lower()
        name = filepath.name.lower()
        
        # Check extension first (high confidence)
        for file_type, extensions in cls.EXTENSION_MAP.items():
            if ext in extensions:
                return file_type, 0.95
        
        # Check filename keywords (medium confidence)
        for file_type, keywords in cls.KEYWORD_MAP.items():
            for keyword in keywords:
                if keyword in name:
                    try:
                        return FileType[keyword.upper()], 0.7
                    except KeyError:
                        continue
        
        # Check MIME type as fallback
        mime_type, _ = mimetypes.guess_type(str(filepath))
        if mime_type:
            if mime_type.startswith('video/'):
                return FileType.VIDEO, 0.8
            elif mime_type.startswith('image/'):
                return FileType.IMAGE, 0.8
            elif mime_type.startswith('audio/'):
                return FileType.AUDIO, 0.8
            elif mime_type.startswith('text/'):
                return FileType.DOCUMENT, 0.6
            elif mime_type.startswith('application/'):
                if 'zip' in mime_type or 'compressed' in mime_type:
                    return FileType.ARCHIVE, 0.7
        
        return FileType.OTHER, 0.3
    
    @classmethod
    def classify_folder(cls, folderpath: Path) -> Optional[FileType]:
        """Classify a folder based on its contents and name"""
        name = folderpath.name.lower()
        
        # Check folder name keywords
        for file_type, keywords in cls.KEYWORD_MAP.items():
            for keyword in keywords:
                if keyword in name:
                    try:
                        return FileType[keyword.upper()]
                    except KeyError:
                        continue
        
        # Analyze contents
        type_counts = defaultdict(int)
        total_files = 0
        
        try:
            for item in folderpath.iterdir():
                if item.is_file():
                    file_type, _ = cls.classify_file(item)
                    type_counts[file_type] += 1
                    total_files += 1
        except PermissionError:
            pass
        
        if total_files > 0:
            dominant_type = max(type_counts.items(), key=lambda x: x[1])
            if dominant_type[1] / total_files > 0.5:  # More than 50% same type
                return dominant_type[0]
        
        return None
    
    @classmethod
    def should_keep_folder_intact(cls, folderpath: Path) -> bool:
        """
        Determine if a folder should be kept intact (not broken apart)
        Returns True for project folders, git repos, etc.
        """
        # Check for project indicators
        indicators = [
            '.git', 'package.json', 'setup.py', 'requirements.txt',
            'Cargo.toml', 'pom.xml', 'build.gradle', 'Makefile',
            '.vscode', '.idea', 'node_modules', '__pycache__'
        ]
        
        for indicator in indicators:
            if (folderpath / indicator).exists():
                return True
        
        # Check if folder has mixed content that suggests a project
        has_code = False
        has_docs = False
        has_data = False
        
        try:
            for item in list(folderpath.iterdir())[:20]:  # Check first 20 items
                if item.is_file():
                    file_type, _ = cls.classify_file(item)
                    if file_type == FileType.CODE:
                        has_code = True
                    elif file_type == FileType.DOCUMENT:
                        has_docs = True
                    elif file_type == FileType.DATA:
                        has_data = True
        except (PermissionError, OSError):
            pass
        
        # If folder has code + other elements, keep intact
        if has_code and (has_docs or has_data):
            return True
        
        return False


class FolderStructureManager:
    """Manages the folder structure and file operations"""
    
    def __init__(self):
        self.nodes: Dict[str, FolderNode] = {}
        self.root_id: Optional[str] = None
        self.stats: Dict[str, FileStats] = {}
    
    def create_default_structure(self) -> None:
        """Create a default folder structure with common categories"""
        predefined = [
            {
                'id': 'root',
                'name': 'My Files',
                'description': 'Root folder for all organized files',
                'purpose': 'Main container for the entire file organization system',
                'icon': '🏠',
                'color': '#E3F2FD',
                'is_predefined': True
            },
            {
                'id': 'media',
                'name': 'Media',
                'description': 'All media files',
                'purpose': 'Container for videos, photos, and audio',
                'parent_id': 'root',
                'icon': '🎬',
                'color': '#FFF3E0',
                'is_predefined': True
            },
            {
                'id': 'videos',
                'name': 'Videos',
                'description': 'Video files and movies',
                'purpose': 'Store all video content including movies, clips, recordings',
                'parent_id': 'media',
                'file_types': [FileType.VIDEO],
                'file_extensions': ['.mp4', '.avi', '.mkv', '.mov'],
                'icon': '🎥',
                'color': '#FFEBEE',
                'is_predefined': True
            },
            {
                'id': 'photos',
                'name': 'Photos & Pictures',
                'description': 'Photographs and images',
                'purpose': 'Personal photos, screenshots, and image files',
                'parent_id': 'media',
                'file_types': [FileType.IMAGE],
                'file_extensions': ['.jpg', '.png', '.gif', '.bmp'],
                'icon': '📷',
                'color': '#FCE4EC',
                'is_predefined': True
            },
            {
                'id': 'audio',
                'name': 'Audio & Music',
                'description': 'Music and audio files',
                'purpose': 'Songs, podcasts, sound effects, and recordings',
                'parent_id': 'media',
                'file_types': [FileType.AUDIO],
                'file_extensions': ['.mp3', '.wav', '.flac'],
                'icon': '🎵',
                'color': '#F3E5F5',
                'is_predefined': True
            },
            {
                'id': 'documents',
                'name': 'Documents',
                'description': 'Text documents and office files',
                'purpose': 'Word docs, PDFs, spreadsheets, presentations',
                'parent_id': 'root',
                'file_types': [FileType.DOCUMENT],
                'file_extensions': ['.pdf', '.doc', '.docx', '.txt'],
                'icon': '📄',
                'color': '#E8F5E9',
                'is_predefined': True
            },
            {
                'id': 'private',
                'name': 'Private Data',
                'description': 'Sensitive and personal information',
                'purpose': 'Secure storage for confidential files',
                'parent_id': 'root',
                'icon': '🔒',
                'color': '#FFCDD2',
                'is_predefined': True
            },
            {
                'id': 'projects_prog',
                'name': 'Projects - Programming',
                'description': 'Software development projects',
                'purpose': 'Code repositories, development work, programming projects',
                'parent_id': 'root',
                'file_types': [FileType.CODE],
                'file_extensions': ['.py', '.js', '.java', '.cpp'],
                'icon': '💻',
                'color': '#E1BEE7',
                'is_predefined': True
            },
            {
                'id': 'projects_books',
                'name': 'Projects - Books & Writing',
                'description': 'Writing projects and manuscripts',
                'purpose': 'Books, articles, stories, and writing projects',
                'parent_id': 'root',
                'file_types': [FileType.DOCUMENT],
                'icon': '📚',
                'color': '#FFE0B2',
                'is_predefined': True
            },
            {
                'id': 'archives',
                'name': 'Archives & Backups',
                'description': 'Compressed files and backups',
                'purpose': 'Old files, backups, compressed archives',
                'parent_id': 'root',
                'file_types': [FileType.ARCHIVE],
                'file_extensions': ['.zip', '.rar', '.7z', '.tar'],
                'icon': '📦',
                'color': '#CFD8DC',
                'is_predefined': True
            },
            {
                'id': 'data_files',
                'name': 'Data Files',
                'description': 'Datasets and database files',
                'purpose': 'CSV files, databases, data exports',
                'parent_id': 'root',
                'file_types': [FileType.DATA],
                'file_extensions': ['.csv', '.sql', '.db'],
                'icon': '📊',
                'color': '#B3E5FC',
                'is_predefined': True
            },
            {
                'id': 'misc',
                'name': 'Miscellaneous',
                'description': 'Files that don\'t fit other categories',
                'purpose': 'Catch-all for unclassified files',
                'parent_id': 'root',
                'icon': '🗂️',
                'color': '#ECEFF1',
                'is_predefined': True
            }
        ]
        
        for item in predefined:
            node = FolderNode.from_dict(item)
            self.nodes[node.id] = node
            
            if node.parent_id:
                parent = self.nodes.get(node.parent_id)
                if parent:
                    parent.children.append(node.id)
            
            if not node.parent_id:
                self.root_id = node.id
    
    def add_node(self, node: FolderNode) -> None:
        """Add a new node to the structure"""
        self.nodes[node.id] = node
        
        if node.parent_id and node.parent_id in self.nodes:
            self.nodes[node.parent_id].children.append(node.id)
        elif not node.parent_id:
            self.root_id = node.id
    
    def remove_node(self, node_id: str) -> None:
        """Remove a node and its children"""
        if node_id not in self.nodes:
            return
        
        # Remove from parent's children
        node = self.nodes[node_id]
        if node.parent_id and node.parent_id in self.nodes:
            if node_id in self.nodes[node.parent_id].children:
                self.nodes[node.parent_id].children.remove(node_id)
        
        # Recursively remove children
        for child_id in node.children[:]:
            self.remove_node(child_id)
        
        del self.nodes[node_id]
    
    def get_path_to_node(self, node_id: str) -> List[str]:
        """Get the path from root to a node"""
        if node_id not in self.nodes:
            return []
        
        path = []
        current_id = node_id
        
        while current_id:
            path.append(self.nodes[current_id].name)
            current_id = self.nodes[current_id].parent_id
        
        return list(reversed(path))
    
    def find_best_match(self, file_type: FileType, filename: str = "") -> Optional[str]:
        """Find the best folder node for a given file type"""
        candidates = []
        
        for node_id, node in self.nodes.items():
            score = 0
            
            # Check file type match
            if file_type in node.file_types:
                score += 10
            
            # Check extension match
            ext = Path(filename).suffix.lower()
            if ext in node.file_extensions:
                score += 15
            
            # Check keyword match in name/description
            keywords = SmartFileClassifier.KEYWORD_MAP.get(file_type.value, [])
            name_lower = f"{node.name} {node.description}".lower()
            for keyword in keywords:
                if keyword in name_lower:
                    score += 5
            
            if score > 0:
                candidates.append((node_id, score))
        
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]
        
        # Default to misc or root
        for node_id, node in self.nodes.items():
            if node.name == 'Miscellaneous':
                return node_id
        
        return self.root_id
    
    def export_structure(self, filepath: str, password: Optional[str] = None) -> bool:
        """Export the folder structure to a JSON file"""
        try:
            data = {
                'version': '1.0',
                'created': datetime.now().isoformat(),
                'nodes': {nid: node.to_dict() for nid, node in self.nodes.items()},
                'root_id': self.root_id
            }
            
            json_str = json.dumps(data, indent=2)
            
            if password and HAS_CRYPTO:
                key = hashlib.sha256(password.encode()).digest()
                fernet = Fernet(hashlib.base64.b64encode(key))
                json_str = fernet.encrypt(json_str.encode()).decode()
            
            with open(filepath, 'w') as f:
                f.write(json_str)
            
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False
    
    def import_structure(self, filepath: str, password: Optional[str] = None) -> bool:
        """Import a folder structure from a JSON file"""
        try:
            with open(filepath, 'r') as f:
                json_str = f.read()
            
            if password and HAS_CRYPTO:
                key = hashlib.sha256(password.encode()).digest()
                fernet = Fernet(hashlib.base64.b64encode(key))
                json_str = fernet.decrypt(json_str.encode()).decode()
            
            data = json.loads(json_str)
            
            self.nodes = {}
            for node_id, node_data in data['nodes'].items():
                self.nodes[node_id] = FolderNode.from_dict(node_data)
            
            self.root_id = data.get('root_id')
            
            # Rebuild parent-child relationships
            for node in self.nodes.values():
                node.children = []
            
            for node in self.nodes.values():
                if node.parent_id and node.parent_id in self.nodes:
                    self.nodes[node.parent_id].children.append(node.id)
            
            return True
        except Exception as e:
            print(f"Import error: {e}")
            return False
    
    def calculate_stats(self, base_path: Path) -> Dict[str, FileStats]:
        """Calculate statistics for each folder node"""
        self.stats = {}
        
        for node_id, node in self.nodes.items():
            stats = FileStats()
            folder_path = base_path / '/'.join(self.get_path_to_node(node_id))
            
            if folder_path.exists():
                try:
                    for item in folder_path.rglob('*'):
                        if item.is_file():
                            stats.total_files += 1
                            try:
                                stats.total_size += item.stat().st_size
                            except (OSError, IOError):
                                pass
                            
                            file_type, _ = SmartFileClassifier.classify_file(item)
                            stats.file_type_counts[file_type] = stats.file_type_counts.get(file_type, 0) + 1
                            
                            ext = item.suffix.lower()
                            stats.extensions[ext] = stats.extensions.get(ext, 0) + 1
                            
                            try:
                                mtime = datetime.fromtimestamp(item.stat().st_mtime)
                                if stats.last_modified is None or mtime > stats.last_modified:
                                    stats.last_modified = mtime
                            except (OSError, IOError):
                                pass
                except PermissionError:
                    pass
            
            self.stats[node_id] = stats
        
        return self.stats


class FolderManagerGUI:
    """Main GUI application"""
    
    def __init__(self):
        self.manager = FolderStructureManager()
        self.manager.create_default_structure()
        
        self.source_path: Optional[Path] = None
        self.target_path: Optional[Path] = None
        self.selected_node_id: Optional[str] = None
        
        # Visualization settings
        self.show_file_count = tk.BooleanVar(value=True)
        self.show_file_types = tk.BooleanVar(value=True)
        self.show_comments = tk.BooleanVar(value=True)
        self.show_colors = tk.BooleanVar(value=True)
        
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the main GUI window"""
        self.root = tk.Tk()
        self.root.title("Folder Structure Manager - Mind Map Organizer")
        self.root.geometry("1400x900")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top toolbar
        self.create_toolbar(main_frame)
        
        # Middle section - split into tree and canvas
        middle_frame = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left panel - Tree view
        left_panel = ttk.Frame(middle_frame)
        middle_frame.add(left_panel, weight=1)
        self.create_tree_panel(left_panel)
        
        # Right panel - Canvas visualization
        right_panel = ttk.Frame(middle_frame)
        middle_frame.add(right_panel, weight=2)
        self.create_canvas_panel(right_panel)
        
        # Bottom panel - Actions and status
        bottom_frame = ttk.LabelFrame(main_frame, text="Actions")
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        self.create_action_panel(bottom_frame)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(5, 0))
        
        # Bind events
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.canvas.bind('<Configure>', self.on_canvas_resize)
    
    def create_toolbar(self, parent):
        """Create the top toolbar"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X)
        
        # File operations
        ttk.Button(toolbar, text="📁 New Structure", command=self.new_structure).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📤 Export", command=self.export_structure).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📥 Import", command=self.import_structure).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        
        # Add/Edit nodes
        ttk.Button(toolbar, text="➕ Add Folder", command=self.add_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="✏️ Edit", command=self.edit_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🗑️ Delete", command=self.delete_folder).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        
        # Source/Target selection
        ttk.Label(toolbar, text="Source:").pack(side=tk.LEFT, padx=(10, 5))
        self.source_var = tk.StringVar(value="Not selected")
        ttk.Entry(toolbar, textvariable=self.source_var, width=40, state='readonly').pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Browse", command=self.select_source).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(toolbar, text="Target:").pack(side=tk.LEFT, padx=(20, 5))
        self.target_var = tk.StringVar(value="Not selected")
        ttk.Entry(toolbar, textvariable=self.target_var, width=40, state='readonly').pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Browse", command=self.select_target).pack(side=tk.LEFT, padx=2)
    
    def create_tree_panel(self, parent):
        """Create the tree view panel"""
        panel = ttk.LabelFrame(parent, text="Folder Structure")
        panel.pack(fill=tk.BOTH, expand=True)
        
        # Tree view
        columns = ('Name', 'Type', 'Files', 'Description')
        self.tree = ttk.Treeview(panel, columns=columns, show='tree headings')
        
        self.tree.heading('#0', text='Folder')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Type', text='Type')
        self.tree.heading('Files', text='Files')
        self.tree.heading('Description', text='Description')
        
        self.tree.column('#0', width=200)
        self.tree.column('Name', width=150)
        self.tree.column('Type', width=100)
        self.tree.column('Files', width=80)
        self.tree.column('Description', width=200)
        
        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(panel, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scroll_x = ttk.Scrollbar(panel, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        tree_scroll_y.grid(row=0, column=1, sticky='ns')
        tree_scroll_x.grid(row=1, column=0, sticky='ew')
        
        panel.grid_rowconfigure(0, weight=1)
        panel.grid_columnconfigure(0, weight=1)
        
        # Context menu
        self.tree_menu = tk.Menu(self.tree, tearoff=0)
        self.tree_menu.add_command(label="Add Child Folder", command=self.add_folder)
        self.tree_menu.add_command(label="Edit Folder", command=self.edit_folder)
        self.tree_menu.add_command(label="Delete Folder", command=self.delete_folder)
        self.tree.bind('<Button-3>', self.show_tree_menu)
    
    def create_canvas_panel(self, parent):
        """Create the canvas visualization panel"""
        panel = ttk.LabelFrame(parent, text="Mind Map Visualization")
        panel.pack(fill=tk.BOTH, expand=True)
        
        # Control frame
        control_frame = ttk.Frame(panel)
        control_frame.pack(fill=tk.X)
        
        ttk.Label(control_frame, text="Display Options:").pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(control_frame, text="File Count", variable=self.show_file_count, 
                       command=self.refresh_canvas).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(control_frame, text="File Types", variable=self.show_file_types,
                       command=self.refresh_canvas).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(control_frame, text="Comments", variable=self.show_comments,
                       command=self.refresh_canvas).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(control_frame, text="Colors", variable=self.show_colors,
                       command=self.refresh_canvas).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Refresh", command=self.refresh_canvas).pack(side=tk.RIGHT, padx=5)
        ttk.Button(control_frame, text="Auto Layout", command=self.auto_layout).pack(side=tk.RIGHT, padx=5)
        
        # Canvas with scrollbars
        canvas_frame = ttk.Frame(panel)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white')
        canvas_scroll_y = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        canvas_scroll_x = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=canvas_scroll_y.set, xscrollcommand=canvas_scroll_x.set)
        
        self.canvas.grid(row=0, column=0, sticky='nsew')
        canvas_scroll_y.grid(row=0, column=1, sticky='ns')
        canvas_scroll_x.grid(row=1, column=0, sticky='ew')
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Store node positions for visualization
        self.node_positions: Dict[str, Tuple[int, int]] = {}
        self.node_items: Dict[str, Dict[str, Any]] = {}
    
    def create_action_panel(self, parent):
        """Create the action buttons panel"""
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Organize button
        organize_btn = ttk.Button(action_frame, text="🔄 Organize Files", 
                                 command=self.organize_files)
        organize_btn.pack(side=tk.LEFT, padx=5)
        
        # Preview button
        preview_btn = ttk.Button(action_frame, text="👁️ Preview Changes",
                                command=self.preview_changes)
        preview_btn.pack(side=tk.LEFT, padx=5)
        
        # Keep folders intact option
        self.keep_intact_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(action_frame, text="Keep project folders intact",
                       variable=self.keep_intact_var).pack(side=tk.LEFT, padx=20)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(action_frame, variable=self.progress_var, 
                                           maximum=100, length=300)
        self.progress_bar.pack(side=tk.RIGHT, padx=10)
    
    def show_tree_menu(self, event):
        """Show context menu for tree"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.tree_menu.post(event.x_root, event.y_root)
    
    def populate_tree(self):
        """Populate the tree view with folder structure"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Calculate stats
        if self.target_path:
            self.manager.calculate_stats(self.target_path)
        
        # Add root node
        if self.manager.root_id:
            self._add_tree_nodes(self.manager.root_id, '')
    
    def _add_tree_nodes(self, node_id: str, parent_iid: str):
        """Recursively add nodes to tree"""
        node = self.manager.nodes.get(node_id)
        if not node:
            return
        
        # Get stats
        stats = self.manager.stats.get(node_id, FileStats())
        type_str = ', '.join([ft.value for ft in node.file_types[:2]])
        if len(node.file_types) > 2:
            type_str += '...'
        
        iid = self.tree.insert(parent_iid, 'end', text=node.icon + ' ' + node.name,
                              values=(node.name, type_str, str(stats.total_files), 
                                     node.description[:50]))
        
        for child_id in node.children:
            self._add_tree_nodes(child_id, iid)
    
    def draw_mind_map(self):
        """Draw the mind map visualization on canvas"""
        self.canvas.delete('all')
        self.node_positions.clear()
        self.node_items.clear()
        
        if not self.manager.root_id:
            return
        
        # Calculate layout
        self._layout_nodes(self.manager.root_id, 400, 50, 200, 100)
        
        # Draw connections first (so they're behind nodes)
        for node_id, node in self.manager.nodes.items():
            if node.parent_id and node.parent_id in self.node_positions:
                self._draw_connection(node.parent_id, node_id)
        
        # Draw nodes
        for node_id, pos in self.node_positions.items():
            self._draw_node(node_id, pos)
    
    def _layout_nodes(self, node_id: str, x: int, y: int, x_spacing: int, y_spacing: int):
        """Recursive layout algorithm for mind map"""
        node = self.manager.nodes.get(node_id)
        if not node:
            return
        
        self.node_positions[node_id] = (x, y)
        
        if not node.children:
            return
        
        # Calculate total height needed for children
        num_children = len(node.children)
        total_height = num_children * y_spacing
        
        # Position children
        start_y = y - (total_height // 2)
        
        for i, child_id in enumerate(node.children):
            child_x = x + x_spacing
            child_y = start_y + (i * y_spacing)
            self._layout_nodes(child_id, child_x, child_y, x_spacing // 2, y_spacing)
    
    def _draw_connection(self, parent_id: str, child_id: str):
        """Draw connection line between nodes"""
        if parent_id not in self.node_positions or child_id not in self.node_positions:
            return
        
        x1, y1 = self.node_positions[parent_id]
        x2, y2 = self.node_positions[child_id]
        
        # Draw curved line
        mid_x = (x1 + x2) // 2
        self.canvas.create_line(x1 + 75, y1 + 25, mid_x, y1 + 25, smooth=True, 
                               width=2, fill='#888888')
        self.canvas.create_line(mid_x, y1 + 25, mid_x, y2 + 25, smooth=True,
                               width=2, fill='#888888')
        self.canvas.create_line(mid_x, y2 + 25, x2 - 75, y2 + 25, smooth=True,
                               width=2, fill='#888888')
    
    def _draw_node(self, node_id: str, pos: Tuple[int, int]):
        """Draw a single node on the canvas"""
        node = self.manager.nodes.get(node_id)
        if not node:
            return
        
        x, y = pos
        width, height = 150, 50
        
        # Colors
        fill_color = node.color if self.show_colors.get() else '#FFFFFF'
        text_color = node.text_color if self.show_colors.get() else '#000000'
        
        # Draw rectangle
        rect = self.canvas.create_rectangle(x, y, x + width, y + height,
                                           fill=fill_color, outline='#333333', width=2)
        
        # Draw icon and name
        label = f"{node.icon} {node.name}"
        text = self.canvas.create_text(x + width//2, y + height//2, text=label,
                                       fill=text_color, font=('Arial', 10, 'bold'))
        
        # Store references
        self.node_items[node_id] = {'rect': rect, 'text': text}
        
        # Add additional info if enabled
        if self.show_file_count.get() and node_id in self.manager.stats:
            stats = self.manager.stats[node_id]
            info_text = f"📄 {stats.total_files}"
            self.canvas.create_text(x + width//2, y + height + 15, text=info_text,
                                   fill='#666666', font=('Arial', 8))
        
        if self.show_comments.get() and node.description:
            desc_text = node.description[:40] + '...' if len(node.description) > 40 else node.description
            self.canvas.create_text(x + width//2, y - 15, text=desc_text,
                                   fill='#888888', font=('Arial', 8))
    
    def refresh_canvas(self):
        """Refresh the canvas visualization"""
        self.draw_mind_map()
    
    def auto_layout(self):
        """Automatically adjust layout"""
        self.draw_mind_map()
        # Fit all content in view
        self.canvas.update_idletasks()
        bbox = self.canvas.bbox('all')
        if bbox:
            self.canvas.config(scrollregion=bbox)
    
    def on_canvas_resize(self, event):
        """Handle canvas resize"""
        self.refresh_canvas()
    
    def on_tree_select(self, event):
        """Handle tree selection"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            # Find corresponding node
            # This is simplified - in production would need better mapping
    
    def new_structure(self):
        """Create a new folder structure"""
        if messagebox.askyesno("New Structure", 
                              "Create a new structure? This will clear current structure."):
            self.manager = FolderStructureManager()
            self.manager.create_default_structure()
            self.populate_tree()
            self.refresh_canvas()
            self.status_var.set("New structure created")
    
    def add_folder(self):
        """Add a new folder node"""
        dialog = FolderDialog(self.root, "Add Folder")
        if dialog.result:
            node = FolderNode(
                id=f"folder_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                name=dialog.result['name'],
                description=dialog.result['description'],
                purpose=dialog.result['purpose'],
                file_extensions=dialog.result['extensions'].split(','),
                color=dialog.result['color'],
                parent_id=self.selected_node_id or self.manager.root_id
            )
            self.manager.add_node(node)
            self.populate_tree()
            self.refresh_canvas()
            self.status_var.set(f"Added folder: {node.name}")
    
    def edit_folder(self):
        """Edit selected folder"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a folder to edit")
            return
        
        # Get node ID (simplified - would need proper mapping in production)
        item_values = self.tree.item(selection[0])['values']
        node_name = item_values[0] if item_values else None
        
        if not node_name:
            return
        
        # Find node by name
        node = None
        for n in self.manager.nodes.values():
            if n.name == node_name:
                node = n
                break
        
        if not node:
            return
        
        dialog = FolderDialog(self.root, "Edit Folder", node)
        if dialog.result:
            node.name = dialog.result['name']
            node.description = dialog.result['description']
            node.purpose = dialog.result['purpose']
            node.file_extensions = dialog.result['extensions'].split(',')
            node.color = dialog.result['color']
            
            self.populate_tree()
            self.refresh_canvas()
            self.status_var.set(f"Updated folder: {node.name}")
    
    def delete_folder(self):
        """Delete selected folder"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a folder to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", 
                              "Delete this folder and all subfolders?"):
            # Get node and delete
            item_values = self.tree.item(selection[0])['values']
            node_name = item_values[0] if item_values else None
            
            if node_name:
                for node_id, node in list(self.manager.nodes.items()):
                    if node.name == node_name:
                        self.manager.remove_node(node_id)
                        break
                
                self.populate_tree()
                self.refresh_canvas()
                self.status_var.set("Folder deleted")
    
    def select_source(self):
        """Select source directory"""
        path = filedialog.askdirectory(title="Select Source Directory")
        if path:
            self.source_path = Path(path)
            self.source_var.set(str(self.source_path))
            self.status_var.set(f"Source selected: {self.source_path}")
    
    def select_target(self):
        """Select target directory"""
        path = filedialog.askdirectory(title="Select Target Directory")
        if path:
            self.target_path = Path(path)
            self.target_var.set(str(self.target_path))
            self.status_var.set(f"Target selected: {self.target_path}")
            self.populate_tree()
            self.refresh_canvas()
    
    def organize_files(self):
        """Organize files from source to target"""
        if not self.source_path or not self.target_path:
            messagebox.showerror("Error", "Please select both source and target directories")
            return
        
        if not messagebox.askyesno("Confirm", 
                                  "Start organizing files? This will move/copy files."):
            return
        
        # Run in thread to avoid freezing GUI
        thread = threading.Thread(target=self._organize_files_thread)
        thread.start()
    
    def _organize_files_thread(self):
        """Background thread for file organization"""
        try:
            self.status_var.set("Organizing files...")
            total_files = 0
            processed = 0
            
            # Collect all files
            all_files = []
            for item in self.source_path.rglob('*'):
                if item.is_file():
                    all_files.append(item)
            
            total_files = len(all_files)
            
            for file_path in all_files:
                # Classify file
                file_type, confidence = SmartFileClassifier.classify_file(file_path)
                
                # Check if parent folder should stay intact
                if self.keep_intact_var.get():
                    parent = file_path.parent
                    if SmartFileClassifier.should_keep_folder_intact(parent):
                        # Copy entire folder structure
                        rel_path = parent.relative_to(self.source_path)
                        target_folder = self.target_path / 'projects' / rel_path
                        target_folder.mkdir(parents=True, exist_ok=True)
                        
                        # Copy folder
                        dest = target_folder / file_path.name
                        try:
                            shutil.copy2(file_path, dest)
                        except (IOError, OSError) as e:
                            print(f"Copy error: {e}")
                        continue
                
                # Find best matching folder
                target_node_id = self.manager.find_best_match(file_type, file_path.name)
                if target_node_id:
                    target_node = self.manager.nodes[target_node_id]
                    path_parts = self.manager.get_path_to_node(target_node_id)
                    target_folder = self.target_path / '/'.join(path_parts)
                    target_folder.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    dest = target_folder / file_path.name
                    try:
                        shutil.copy2(file_path, dest)
                        processed += 1
                        progress = (processed / total_files) * 100
                        self.root.after(0, lambda p=progress: self.progress_var.set(p))
                    except (IOError, OSError) as e:
                        print(f"Copy error: {e}")
            
            self.root.after(0, lambda: self.status_var.set(f"Organization complete! Processed {processed}/{total_files} files"))
            self.root.after(0, lambda: self.progress_var.set(100))
            self.root.after(0, self.populate_tree)
            self.root.after(0, self.refresh_canvas)
            
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
    
    def preview_changes(self):
        """Preview what changes would be made"""
        if not self.source_path:
            messagebox.showerror("Error", "Please select source directory")
            return
        
        # Analyze files
        preview_text = "Proposed File Organization:\n\n"
        type_counts = defaultdict(int)
        
        for item in self.source_path.rglob('*'):
            if item.is_file():
                file_type, confidence = SmartFileClassifier.classify_file(item)
                type_counts[file_type.value] += 1
        
        for file_type, count in sorted(type_counts.items()):
            preview_text += f"{file_type}: {count} files\n"
        
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Preview Changes")
        preview_window.geometry("400x300")
        
        text_widget = tk.Text(preview_window)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert('1.0', preview_text)
        text_widget.config(state='disabled')
    
    def export_structure(self):
        """Export structure to file"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filepath:
            # Ask for password
            use_password = messagebox.askyesno("Password Protection",
                                              "Add password protection?")
            password = None
            if use_password:
                password = simpledialog.askstring("Password", "Enter password:", show='*')
            
            if self.manager.export_structure(filepath, password):
                self.status_var.set(f"Structure exported to {filepath}")
                messagebox.showinfo("Success", f"Structure exported successfully!")
            else:
                messagebox.showerror("Error", "Failed to export structure")
    
    def import_structure(self):
        """Import structure from file"""
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filepath:
            # Ask for password
            use_password = messagebox.askyesno("Password Protection",
                                              "Is this file password protected?")
            password = None
            if use_password:
                password = simpledialog.askstring("Password", "Enter password:", show='*')
            
            if self.manager.import_structure(filepath, password):
                self.status_var.set(f"Structure imported from {filepath}")
                self.populate_tree()
                self.refresh_canvas()
                messagebox.showinfo("Success", "Structure imported successfully!")
            else:
                messagebox.showerror("Error", "Failed to import structure")
    
    def run(self):
        """Run the application"""
        self.populate_tree()
        self.refresh_canvas()
        self.root.mainloop()


class FolderDialog(simpledialog.Dialog):
    """Dialog for adding/editing folders"""
    
    def __init__(self, parent, title, node: Optional[FolderNode] = None):
        self.node = node
        self.result = None
        super().__init__(parent, title)
    
    def body(self, master):
        """Create dialog body"""
        ttk.Label(master, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(master, width=40)
        self.name_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(master, text="Description:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.desc_entry = ttk.Entry(master, width=40)
        self.desc_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(master, text="Purpose:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.purpose_entry = ttk.Entry(master, width=40)
        self.purpose_entry.grid(row=2, column=1, pady=5)
        
        ttk.Label(master, text="File Extensions (comma-separated):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.ext_entry = ttk.Entry(master, width=40)
        self.ext_entry.grid(row=3, column=1, pady=5)
        
        ttk.Label(master, text="Color:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.color_btn = ttk.Button(master, text="Choose Color", command=self.choose_color)
        self.color_btn.grid(row=4, column=1, sticky=tk.W, pady=5)
        self.color_preview = tk.Canvas(master, width=30, height=20, bg='#FFFFFF')
        self.color_preview.grid(row=4, column=1, sticky=tk.E, padx=5)
        self.current_color = '#FFFFFF'
        
        if self.node:
            self.name_entry.insert(0, self.node.name)
            self.desc_entry.insert(0, self.node.description)
            self.purpose_entry.insert(0, self.node.purpose)
            self.ext_entry.insert(0, ','.join(self.node.file_extensions))
            self.current_color = self.node.color
            self.color_preview.config(bg=self.current_color)
        
        return self.name_entry
    
    def choose_color(self):
        """Open color chooser"""
        color = colorchooser.askcolor(color=self.current_color)[1]
        if color:
            self.current_color = color
            self.color_preview.config(bg=color)
    
    def apply(self):
        """Apply changes"""
        self.result = {
            'name': self.name_entry.get().strip(),
            'description': self.desc_entry.get().strip(),
            'purpose': self.purpose_entry.get().strip(),
            'extensions': self.ext_entry.get().strip(),
            'color': self.current_color
        }
    
    def validate(self):
        """Validate input"""
        if not self.name_entry.get().strip():
            messagebox.showerror("Error", "Name is required")
            return False
        return True


def main():
    """Main entry point"""
    app = FolderManagerGUI()
    app.run()


if __name__ == "__main__":
    main()
