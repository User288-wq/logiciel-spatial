# core/project/project_manager.py
"""
================================================================================
💾 GESTIONNAIRE DE PROJET - SAUVEGARDE ET CHARGEMENT
================================================================================
"""

import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class ProjectMetadata:
    """Métadonnées du projet"""
    name: str
    version: str = "1.0"
    created: str = ""
    modified: str = ""
    author: str = ""
    crs: str = "EPSG:4326"
    
    def __post_init__(self):
        if not self.created:
            self.created = datetime.now().isoformat()
        if not self.modified:
            self.modified = datetime.now().isoformat()


class ProjectManager:
    """Gestionnaire de projets"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.current_project: Optional[ProjectMetadata] = None
        self.project_path: Optional[str] = None
        self.recent_projects: List[str] = []
        self._load_recent()
    
    def _load_recent(self):
        """Charge la liste des projets récents"""
        config_dir = os.path.join(os.path.expanduser("~"), ".spatial_gis")
        os.makedirs(config_dir, exist_ok=True)
        config_file = os.path.join(config_dir, "recent.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.recent_projects = data.get('recent', [])
            except:
                pass
    
    def _save_recent(self):
        """Sauvegarde la liste des projets récents"""
        config_dir = os.path.join(os.path.expanduser("~"), ".spatial_gis")
        os.makedirs(config_dir, exist_ok=True)
        config_file = os.path.join(config_dir, "recent.json")
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump({'recent': self.recent_projects[:10]}, f)
        except:
            pass
    
    def new_project(self, name: str = "Nouveau projet") -> ProjectMetadata:
        """Crée un nouveau projet"""
        self.current_project = ProjectMetadata(name=name)
        self.project_path = None
        return self.current_project
    
    def save_project(self, path: str, layers: List[Any]) -> bool:
        """Sauvegarde le projet"""
        if not self.current_project:
            self.new_project()
        
        self.current_project.modified = datetime.now().isoformat()
        
        project_data = {
            'metadata': asdict(self.current_project),
            'layers': []
        }
        
        for layer in layers:
            layer_info = {
                'id': getattr(layer, 'id', ''),
                'name': getattr(layer, 'name', ''),
                'path': getattr(layer, 'path', ''),
                'type': getattr(layer, 'type', 'vector'),
                'is_raster': False,
                'visible': getattr(layer, 'visible', True),
                'style': {}
            }
            project_data['layers'].append(layer_info)
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            
            self.project_path = path
            self.current_project.name = os.path.basename(path)
            
            if path in self.recent_projects:
                self.recent_projects.remove(path)
            self.recent_projects.insert(0, path)
            self._save_recent()
            
            return True
        except Exception as e:
            print(f"Erreur sauvegarde: {e}")
            return False
    
    def load_project(self, path: str) -> Optional[Dict[str, Any]]:
        """Charge un projet"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            metadata = data.get('metadata', {})
            self.current_project = ProjectMetadata(
                name=metadata.get('name', 'Projet'),
                version=metadata.get('version', '1.0'),
                created=metadata.get('created', datetime.now().isoformat()),
                modified=metadata.get('modified', datetime.now().isoformat()),
                author=metadata.get('author', ''),
                crs=metadata.get('crs', 'EPSG:4326')
            )
            
            self.project_path = path
            
            if path in self.recent_projects:
                self.recent_projects.remove(path)
            self.recent_projects.insert(0, path)
            self._save_recent()
            
            return data
        except Exception as e:
            print(f"Erreur chargement: {e}")
            return None
    
    def get_recent_projects(self) -> List[str]:
        return self.recent_projects
    
    def clear_recent(self):
        self.recent_projects = []
        self._save_recent()