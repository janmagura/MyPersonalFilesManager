#!/usr/bin/env python3
"""
Core Logic Module - Folder Structure Manager
Contains all non-GUI functionality for file classification and folder management.
This module can be used independently of the GUI.
"""

import os
import json
import hashlib
import shutil
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict


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
                'description': "Files that don't fit other categories",
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
            
            # Note: Password encryption requires cryptography library
            # if password and HAS_CRYPTO:
            #     from cryptography.fernet import Fernet
            #     key = hashlib.sha256(password.encode()).digest()
            #     fernet = Fernet(hashlib.base64.b64encode(key))
            #     json_str = fernet.encrypt(json_str.encode()).decode()
            
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
            
            # Note: Password decryption requires cryptography library
            # if password and HAS_CRYPTO:
            #     from cryptography.fernet import Fernet
            #     key = hashlib.sha256(password.encode()).digest()
            #     fernet = Fernet(hashlib.base64.b64encode(key))
            #     json_str = fernet.decrypt(json_str.encode()).decode()
            
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


def test_classifier():
    """Test the file classifier with sample files"""
    print("Testing SmartFileClassifier...")
    
    test_cases = [
        ("vacation.mp4", FileType.VIDEO),
        ("photo.jpg", FileType.IMAGE),
        ("document.pdf", FileType.DOCUMENT),
        ("song.mp3", FileType.AUDIO),
        ("archive.zip", FileType.ARCHIVE),
        ("script.py", FileType.CODE),
        ("data.csv", FileType.DATA),
        ("program.exe", FileType.EXECUTABLE),
        ("font.ttf", FileType.FONT),
        ("unknown.xyz", FileType.OTHER),
    ]
    
    for filename, expected_type in test_cases:
        result_type, confidence = SmartFileClassifier.classify_file(Path(filename))
        status = "✓" if result_type == expected_type else "✗"
        print(f"  {status} {filename}: {result_type.value} (confidence: {confidence:.0%})")
    
    print("\nTesting folder intact detection...")
    # This would need actual folders to test properly
    print("  ℹ Folder detection requires actual directory structure")
    
    print("\nAll tests completed!")


if __name__ == "__main__":
    test_classifier()
