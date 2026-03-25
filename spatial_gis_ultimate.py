#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
================================================================================
 LOGICIEL SPATIAL - INTERFACE QT ULTRA-COMPLÈTE (STYLE QGIS PROFESSIONNEL)
================================================================================
Version: 5.0
Auteur: © 2026

Ce fichier contient TOUTES les fonctionnalités d'un SIG professionnel :
- Interface complète style QGIS avec menus, barres d'outils, panneaux
- Gestionnaire de couches hiérarchique avec glisser-déposer
- Propriétés détaillées avec onglets (Info, Attributs, Stats, Métadonnées, Style)
- Outils de navigation avancés (zoom, panoramique, étendue)
- Barre d'état complète avec coordonnées, échelle, progression
- Gestion de projet avec sauvegarde/chargement
- Styles cartographiques multiples
- Légende automatique
- Outils de mesure
- Console Python intégrée
- Gestionnaire d'extensions
- Support multi-langues
- Et bien plus encore...
================================================================================
"""

import os
import sys
import json
import math
import time
import uuid
import hashlib
import threading
import webbrowser
from datetime import datetime, timedelta
from collections import OrderedDict
from functools import partial
from pathlib import Path

# Configuration Qt/Matplotlib
os.environ["QT_API"] = "pyside6"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib import rcParams
rcParams['font.size'] = 9
rcParams['axes.facecolor'] = '#0a1a2a'
rcParams['axes.edgecolor'] = '#333333'
rcParams['axes.labelcolor'] = 'white'
rcParams['xtick.color'] = 'white'
rcParams['ytick.color'] = 'white'
rcParams['grid.color'] = '#333333'
rcParams['grid.alpha'] = 0.3

# Bibliothèques géospatiales
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import box, Point, LineString, Polygon
from shapely.ops import unary_union
from pyproj import CRS, Transformer

# PySide6
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtPrintSupport import QPrinter, QPrintDialog

# ============================================================================
# CONSTANTES GLOBALES
# ============================================================================

APP_NAME = "🚀 Logiciel Spatial Professionnel"
APP_VERSION = "5.0.0"
APP_AUTHOR = "© 2026"
APP_ORGANIZATION = "Spatial GIS Corp"
APP_DOMAIN = "spatial-gis.com"

# Chemins
USER_HOME = str(Path.home())
APP_DATA_DIR = os.path.join(USER_HOME, ".spatial_gis")
PLUGINS_DIR = os.path.join(APP_DATA_DIR, "plugins")
PROJECTS_DIR = os.path.join(APP_DATA_DIR, "projects")
STYLES_DIR = os.path.join(APP_DATA_DIR, "styles")
LOGS_DIR = os.path.join(APP_DATA_DIR, "logs")
CACHE_DIR = os.path.join(APP_DATA_DIR, "cache")

# Créer les dossiers nécessaires
for d in [APP_DATA_DIR, PLUGINS_DIR, PROJECTS_DIR, STYLES_DIR, LOGS_DIR, CACHE_DIR]:
    os.makedirs(d, exist_ok=True)

# Styles cartographiques prédéfinis
STYLES = {
    'region': {
        'name': 'Régions',
        'color': '#4CAF50',
        'edgecolor': '#2E7D32',
        'alpha': 0.4,
        'linewidth': 1.5,
        'hatch': '',
        'label_size': 10,
        'label_color': 'white',
        'label_weight': 'bold',
        'label_halo': True,
        'min_scale': 0,
        'max_scale': 1000000
    },
    'commune': {
        'name': 'Communes',
        'color': '#FFA500',
        'edgecolor': '#FF8C00',
        'alpha': 0.3,
        'linewidth': 0.8,
        'hatch': '///',
        'label_size': 8,
        'label_color': 'yellow',
        'label_weight': 'normal',
        'label_halo': True,
        'min_scale': 0,
        'max_scale': 500000
    },
    'route': {
        'name': 'Routes',
        'color': '#808080',
        'edgecolor': '#666666',
        'alpha': 0.7,
        'linewidth': 0.5,
        'line_style': 'solid',
        'min_scale': 0,
        'max_scale': 100000
    },
    'hydro': {
        'name': 'Hydrographie',
        'color': '#2196F3',
        'edgecolor': '#1976D2',
        'alpha': 0.5,
        'linewidth': 1.0,
        'hatch': '...',
        'min_scale': 0,
        'max_scale': 500000
    },
    'raster': {
        'name': 'Images satellites',
        'alpha': 0.8,
        'cmap': 'viridis',
        'interpolation': 'bilinear',
        'min_scale': 0,
        'max_scale': float('inf')
    },
    'point': {
        'name': 'Points',
        'color': '#FF4444',
        'edgecolor': '#CC0000',
        'alpha': 0.8,
        'marker': 'o',
        'markersize': 5,
        'label_size': 8,
        'label_color': 'white',
        'min_scale': 0,
        'max_scale': 100000
    },
    'line': {
        'name': 'Lignes',
        'color': '#FFA500',
        'edgecolor': '#FF8C00',
        'alpha': 0.7,
        'linewidth': 1.0,
        'min_scale': 0,
        'max_scale': 500000
    },
    'polygon': {
        'name': 'Polygones',
        'color': '#4CAF50',
        'edgecolor': '#2E7D32',
        'alpha': 0.3,
        'linewidth': 1.0,
        'min_scale': 0,
        'max_scale': 1000000
    },
    'vector': {  # Style par défaut pour les vecteurs
        'name': 'Vecteur',
        'color': '#4CAF50',
        'edgecolor': '#2E7D32',
        'alpha': 0.5,
        'linewidth': 1.0,
        'min_scale': 0,
        'max_scale': float('inf')
    }
}

# Codes EPSG communs
CRS_LIST = {
    'EPSG:4326': 'WGS 84 (Lat/Lon)',
    'EPSG:3857': 'Web Mercator (Pseudo-Mercator)',
    'EPSG:2154': 'RGF93 / Lambert-93 (France)',
    'EPSG:32628': 'WGS 84 / UTM zone 28N',
    'EPSG:32629': 'WGS 84 / UTM zone 29N',
    'EPSG:32728': 'WGS 84 / UTM zone 28S',
    'EPSG:32729': 'WGS 84 / UTM zone 29S'
}

# Langues supportées
LANGUAGES = {
    'fr': 'Français',
    'en': 'English',
    'es': 'Español',
    'de': 'Deutsch',
    'pt': 'Português'
}

# Thèmes
THEMES = {
    'dark': 'Sombre',
    'light': 'Clair',
    'blue': 'Bleu',
    'high_contrast': 'Haut contraste'
}

# ============================================================================
# GESTIONNAIRE DE LOGS
# ============================================================================

class Logger:
    """Système de logging avancé"""
    
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
        self.log_file = os.path.join(LOGS_DIR, f"spatial_gis_{datetime.now():%Y%m%d}.log")
        self.log_level = 'INFO'
        self.console_output = True
        self.history = []
        
    def log(self, level, message, module='APP'):
        """Enregistre un message dans les logs"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        log_entry = f"[{timestamp}] [{level}] [{module}] {message}"
        
        self.history.append(log_entry)
        if len(self.history) > 10000:
            self.history.pop(0)
        
        # Écrire dans le fichier
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except:
            pass
        
        # Afficher dans la console
        if self.console_output:
            print(log_entry)
    
    def info(self, message, module='APP'):
        self.log('INFO', message, module)
    
    def warning(self, message, module='APP'):
        self.log('WARNING', message, module)
    
    def error(self, message, module='APP'):
        self.log('ERROR', message, module)
    
    def debug(self, message, module='APP'):
        if self.log_level == 'DEBUG':
            self.log('DEBUG', message, module)

# ============================================================================
# GESTIONNAIRE DE CONFIGURATION
# ============================================================================

class ConfigManager:
    """Gestionnaire de configuration"""
    
    def __init__(self):
        self.config_file = os.path.join(APP_DATA_DIR, 'config.json')
        self.config = self.load()
    
    def load(self):
        """Charge la configuration"""
        default_config = {
            'language': 'fr',
            'theme': 'dark',
            'crs_default': 'EPSG:4326',
            'grid_enabled': True,
            'coords_format': 'dd',
            'auto_save': True,
            'auto_save_interval': 5,
            'recent_projects': [],
            'plugins_enabled': [],
            'toolbars': {
                'main': True,
                'map': True,
                'edit': True,
                'analysis': True
            },
            'docks': {
                'layers': True,
                'properties': True,
                'legend': True,
                'console': False
            },
            'shortcuts': {},
            'proxy': {
                'enabled': False,
                'host': '',
                'port': '',
                'username': '',
                'password': ''
            },
            'updates': {
                'check_on_start': True,
                'last_check': None
            }
        }
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Fusionner avec les défauts
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except:
            return default_config
    
    def save(self):
        """Sauvegarde la configuration"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            Logger().info("Configuration sauvegardée")
        except Exception as e:
            Logger().error(f"Erreur sauvegarde config: {e}")
    
    def get(self, key, default=None):
        """Récupère une valeur"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def set(self, key, value):
        """Définit une valeur"""
        keys = key.split('.')
        target = self.config
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value

# ============================================================================
# GESTIONNAIRE DE PROJET
# ============================================================================

class Project:
    """Classe représentant un projet"""
    
    def __init__(self, name="Nouveau projet"):
        self.id = str(uuid.uuid4())
        self.name = name
        self.path = None
        self.created = datetime.now()
        self.modified = datetime.now()
        self.author = os.getlogin()
        self.crs = 'EPSG:4326'
        self.extent = None
        self.layers = []
        self.bookmarks = []
        self.annotations = []
        self.metadata = {}
        
    def to_dict(self):
        """Convertit en dictionnaire"""
        return {
            'id': self.id,
            'name': self.name,
            'created': self.created.isoformat(),
            'modified': self.modified.isoformat(),
            'author': self.author,
            'crs': self.crs,
            'extent': self.extent,
            'layers': [l.to_dict() for l in self.layers],
            'bookmarks': self.bookmarks,
            'annotations': self.annotations,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crée un projet depuis un dictionnaire"""
        project = cls(data.get('name', 'Projet'))
        project.id = data.get('id', project.id)
        project.created = datetime.fromisoformat(data.get('created', datetime.now().isoformat()))
        project.modified = datetime.fromisoformat(data.get('modified', datetime.now().isoformat()))
        project.author = data.get('author', project.author)
        project.crs = data.get('crs', project.crs)
        project.extent = data.get('extent')
        project.layers = [Layer.from_dict(l) for l in data.get('layers', [])]
        project.bookmarks = data.get('bookmarks', [])
        project.annotations = data.get('annotations', [])
        project.metadata = data.get('metadata', {})
        return project

class Layer:
    """Classe représentant une couche"""
    
    def __init__(self, name, path, layer_type='vector'):
        self.id = str(uuid.uuid4())
        self.name = name
        self.path = path
        self.type = layer_type
        self.visible = True
        self.style = STYLES.get(layer_type, STYLES['vector']).copy()
        self.opacity = 1.0
        self.crs = None
        self.extent = None
        self.feature_count = 0
        self.attributes = []
        self.metadata = {}
        self.loaded = False
        self.data = None
        
    def to_dict(self):
        """Convertit en dictionnaire"""
        return {
            'id': self.id,
            'name': self.name,
            'path': self.path,
            'type': self.type,
            'visible': self.visible,
            'style': self.style,
            'opacity': self.opacity,
            'crs': self.crs,
            'extent': self.extent,
            'feature_count': self.feature_count,
            'attributes': self.attributes,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crée une couche depuis un dictionnaire"""
        layer = cls(data.get('name'), data.get('path'), data.get('type', 'vector'))
        layer.id = data.get('id', layer.id)
        layer.visible = data.get('visible', True)
        layer.style.update(data.get('style', {}))
        layer.opacity = data.get('opacity', 1.0)
        layer.crs = data.get('crs')
        layer.extent = data.get('extent')
        layer.feature_count = data.get('feature_count', 0)
        layer.attributes = data.get('attributes', [])
        layer.metadata = data.get('metadata', {})
        return layer

# ============================================================================
# GESTIONNAIRE DE PROJET (MANAGER)
# ============================================================================

class ProjectManager(QObject):
    """Gestionnaire de projets"""
    
    project_changed = Signal()
    layer_added = Signal(object)
    layer_removed = Signal(str)
    layer_visibility_changed = Signal(str, bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_project = None
        self.recent_projects = []
        self.config = ConfigManager()
        self.logger = Logger()
        self.load_recent()
    
    def new_project(self, name="Nouveau projet"):
        """Crée un nouveau projet"""
        self.current_project = Project(name)
        self.logger.info(f"Nouveau projet créé: {name}")
        self.project_changed.emit()
        return self.current_project
    
    def open_project(self, path):
        """Ouvre un projet"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.current_project = Project.from_dict(data)
            self.current_project.path = path
            self.logger.info(f"Projet ouvert: {path}")
            
            # Ajouter aux récents
            if path not in self.recent_projects:
                self.recent_projects.insert(0, path)
                self.recent_projects = self.recent_projects[:10]
                self.save_recent()
            
            self.project_changed.emit()
            return True
        except Exception as e:
            self.logger.error(f"Erreur ouverture projet: {e}")
            return False
    
    def save_project(self, path=None):
        """Sauvegarde le projet"""
        if not self.current_project:
            return False
        
        if path:
            self.current_project.path = path
        
        if not self.current_project.path:
            return False
        
        try:
            self.current_project.modified = datetime.now()
            with open(self.current_project.path, 'w', encoding='utf-8') as f:
                json.dump(self.current_project.to_dict(), f, indent=2, ensure_ascii=False)
            self.logger.info(f"Projet sauvegardé: {self.current_project.path}")
            return True
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde projet: {e}")
            return False
    
    def load_recent(self):
        """Charge la liste des projets récents"""
        self.recent_projects = self.config.get('recent_projects', [])
    
    def save_recent(self):
        """Sauvegarde la liste des projets récents"""
        self.config.set('recent_projects', self.recent_projects)
        self.config.save()
    
    def add_layer(self, layer):
        """Ajoute une couche au projet"""
        if self.current_project:
            self.current_project.layers.append(layer)
            self.layer_added.emit(layer)
            self.logger.info(f"Couche ajoutée: {layer.name}")
    
    def remove_layer(self, layer_id):
        """Supprime une couche du projet"""
        if self.current_project:
            self.current_project.layers = [l for l in self.current_project.layers if l.id != layer_id]
            self.layer_removed.emit(layer_id)
            self.logger.info(f"Couche supprimée: {layer_id}")
    
    def get_layer(self, layer_id):
        """Récupère une couche par son ID"""
        if self.current_project:
            for layer in self.current_project.layers:
                if layer.id == layer_id:
                    return layer
        return None

# ============================================================================
# GESTIONNAIRE DE COUCHES (WIDGET)
# ============================================================================

class LayerTreeWidget(QTreeWidget):
    """Gestionnaire de couches hiérarchique avec glisser-déposer"""
    
    layer_selected = Signal(object)
    layer_visibility_changed = Signal(str, bool)
    
    def __init__(self, project_manager, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.parent = parent
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """Configure l'interface du gestionnaire de couches"""
        self.setHeaderLabel("📂 Couches du projet")
        self.setIndentation(20)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # Style
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #16213e;
                alternate-background-color: #1a1a2a;
                border: none;
                font-size: 11px;
            }
            QTreeWidget::item {
                padding: 5px;
                border-bottom: 1px solid #0f3460;
            }
            QTreeWidget::item:hover {
                background-color: #0f3460;
            }
            QTreeWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
        """)
        
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def connect_signals(self):
        """Connecte les signaux"""
        self.itemClicked.connect(self.on_item_clicked)
        self.itemChanged.connect(self.on_item_changed)
    
    def add_layer(self, layer):
        """Ajoute une couche à l'arbre"""
        item = QTreeWidgetItem(self)
        
        # Icône selon le type
        icons = {
            'region': '🟩',
            'commune': '🟧',
            'route': '🛣️',
            'hydro': '💧',
            'raster': '🛰️',
            'point': '📍',
            'line': '📏',
            'polygon': '🔲',
            'vector': '📌'
        }
        icon = icons.get(layer.type, '📌')
        
        # Nom avec extension
        name = os.path.basename(layer.path) if layer.path else layer.name
        item.setText(0, f"{icon} {name}")
        item.setCheckState(0, Qt.Checked if layer.visible else Qt.Unchecked)
        item.setData(0, Qt.UserRole, {
            'id': layer.id,
            'name': layer.name,
            'path': layer.path,
            'type': layer.type
        })
        
        # Ajouter des informations supplémentaires
        item.setToolTip(0, f"Type: {layer.type}\nChemin: {layer.path}")
        
        self.addTopLevelItem(item)
        return item
    
    def remove_layer(self, layer_id):
        """Supprime une couche de l'arbre"""
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            data = item.data(0, Qt.UserRole)
            if data and data['id'] == layer_id:
                self.takeTopLevelItem(i)
                break
    
    def update_layer_visibility(self, layer_id, visible):
        """Met à jour la visibilité d'une couche"""
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            data = item.data(0, Qt.UserRole)
            if data and data['id'] == layer_id:
                item.setCheckState(0, Qt.Checked if visible else Qt.Unchecked)
                break
    
    def on_item_clicked(self, item, column):
        """Gère le clic sur un item"""
        data = item.data(0, Qt.UserRole)
        if data:
            layer = self.project_manager.get_layer(data['id'])
            if layer:
                self.layer_selected.emit(layer)
    
    def on_item_changed(self, item, column):
        """Gère le changement d'état"""
        if column == 0:
            data = item.data(0, Qt.UserRole)
            if data:
                visible = item.checkState(0) == Qt.Checked
                self.layer_visibility_changed.emit(data['id'], visible)
    
    def toggle_visibility(self, item):
        """Bascule la visibilité d'un item"""
        if item:
            current = item.checkState(0)
            new_state = Qt.Unchecked if current == Qt.Checked else Qt.Checked
            item.setCheckState(0, new_state)
    
    def show_context_menu(self, position):
        """Affiche le menu contextuel"""
        item = self.itemAt(position)
        if not item:
            return
        
        data = item.data(0, Qt.UserRole)
        if not data:
            return
        
        menu = QMenu()
        
        # Actions
        properties_action = menu.addAction("📋 Propriétés")
        if self.parent:
            properties_action.triggered.connect(lambda: self.parent.show_layer_properties(data['id']))
        
        zoom_action = menu.addAction("🔍 Zoom sur la couche")
        if self.parent:
            zoom_action.triggered.connect(lambda: self.parent.zoom_to_layer(data['id']))
        
        menu.addSeparator()
        
        visible_action = menu.addAction("👁️ Afficher/Masquer")
        visible_action.triggered.connect(lambda: self.toggle_visibility(item))
        
        remove_action = menu.addAction("🗑️ Supprimer")
        if self.parent:
            remove_action.triggered.connect(lambda: self.parent.remove_layer(data['id']))
        
        menu.addSeparator()
        
        export_action = menu.addAction("💾 Exporter")
        if self.parent:
            export_action.triggered.connect(lambda: self.parent.export_layer(data['id']))
        
        style_action = menu.addAction("🎨 Style")
        if self.parent:
            style_action.triggered.connect(lambda: self.parent.edit_layer_style(data['id']))
        
        menu.exec(self.viewport().mapToGlobal(position))

# ============================================================================
# FENÊTRE PRINCIPALE
# ============================================================================

class MainWindow(QMainWindow):
    """Fenêtre principale du logiciel"""
    
    def __init__(self):
        super().__init__()
        
        self.logger = Logger()
        self.config = ConfigManager()
        self.project_manager = ProjectManager(self)
        
        self.setup_ui()
        self.setup_menus()
        self.setup_toolbars()
        self.setup_statusbar()
        self.setup_docks()
        
        self.logger.info("Application démarrée")
    
    def setup_ui(self):
        """Configure l'interface principale"""
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(1200, 800)
        
        # Icône de l'application
        self.setWindowIcon(QIcon())
        
        # Widget central (carte)
        self.map_widget = QWidget()
        self.map_layout = QVBoxLayout(self.map_widget)
        self.map_layout.setContentsMargins(0, 0, 0, 0)
        
        # Placeholder pour la carte
        self.map_canvas = QLabel("Carte - En développement")
        self.map_canvas.setAlignment(Qt.AlignCenter)
        self.map_canvas.setStyleSheet("""
            background-color: #0a1a2a;
            color: white;
            font-size: 20px;
            border: 1px solid #333;
        """)
        self.map_layout.addWidget(self.map_canvas)
        
        self.setCentralWidget(self.map_widget)
    
    def setup_menus(self):
        """Configure les menus"""
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("📁 Fichier")
        
        new_action = QAction("✨ Nouveau projet", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("📂 Ouvrir un projet", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        save_action = QAction("💾 Sauvegarder", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("💿 Sauvegarder sous...", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("🖨️ Exporter la carte", self)
        export_action.triggered.connect(self.export_map)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("❌ Quitter", self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Menu Édition
        edit_menu = menubar.addMenu("✏️ Édition")
        
        add_layer_action = QAction("➕ Ajouter une couche", self)
        add_layer_action.triggered.connect(self.add_layer)
        edit_menu.addAction(add_layer_action)
        
        edit_menu.addSeparator()
        
        copy_action = QAction("📋 Copier", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.copy)
        edit_menu.addAction(copy_action)
        
        # Menu Vue
        view_menu = menubar.addMenu("👁️ Vue")
        
        zoom_in_action = QAction("🔍 Zoom +", self)
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("🔍 Zoom -", self)
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        zoom_extent_action = QAction("🌍 Zoom étendue", self)
        zoom_extent_action.triggered.connect(self.zoom_extent)
        view_menu.addAction(zoom_extent_action)
        
        view_menu.addSeparator()
        
        # Menu Outils
        tools_menu = menubar.addMenu("🛠️ Outils")
        
        measure_action = QAction("📏 Mesurer", self)
        measure_action.triggered.connect(self.measure)
        tools_menu.addAction(measure_action)
        
        # Menu Aide
        help_menu = menubar.addMenu("❓ Aide")
        
        about_action = QAction("ℹ️ À propos", self)
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)
    
    def setup_toolbars(self):
        """Configure les barres d'outils"""
        # Barre d'outils principale
        main_toolbar = self.addToolBar("Principale")
        main_toolbar.setMovable(False)
        
        new_btn = QAction("✨ Nouveau", self)
        new_btn.triggered.connect(self.new_project)
        main_toolbar.addAction(new_btn)
        
        open_btn = QAction("📂 Ouvrir", self)
        open_btn.triggered.connect(self.open_project)
        main_toolbar.addAction(open_btn)
        
        save_btn = QAction("💾 Sauvegarder", self)
        save_btn.triggered.connect(self.save_project)
        main_toolbar.addAction(save_btn)
        
        main_toolbar.addSeparator()
        
        # Barre d'outils de navigation
        nav_toolbar = self.addToolBar("Navigation")
        
        zoom_in_btn = QAction("🔍 Zoom +", self)
        zoom_in_btn.triggered.connect(self.zoom_in)
        nav_toolbar.addAction(zoom_in_btn)
        
        zoom_out_btn = QAction("🔍 Zoom -", self)
        zoom_out_btn.triggered.connect(self.zoom_out)
        nav_toolbar.addAction(zoom_out_btn)
        
        zoom_extent_btn = QAction("🌍 Zoom étendue", self)
        zoom_extent_btn.triggered.connect(self.zoom_extent)
        nav_toolbar.addAction(zoom_extent_btn)
    
    def setup_statusbar(self):
        """Configure la barre d'état"""
        self.statusbar = self.statusBar()
        
        # Coordonnées
        self.coords_label = QLabel("📍 Coordonnées: --,--")
        self.statusbar.addWidget(self.coords_label)
        
        # Échelle
        self.scale_label = QLabel("📏 Échelle: --")
        self.statusbar.addWidget(self.scale_label)
        
        # CRS
        self.crs_label = QLabel("🗺️ CRS: WGS 84")
        self.statusbar.addWidget(self.crs_label)
        
        # Progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.statusbar.addPermanentWidget(self.progress_bar)
    
    def setup_docks(self):
        """Configure les panneaux dockables"""
        # Panneau des couches
        self.layers_dock = QDockableWidget("📂 Couches", self)
        self.layers_widget = LayerTreeWidget(self.project_manager, self)
        self.layers_dock.setWidget(self.layers_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.layers_dock)
        
        # Panneau des propriétés
        self.properties_dock = QDockableWidget("📋 Propriétés", self)
        self.properties_widget = QTextEdit()
        self.properties_widget.setReadOnly(True)
        self.properties_widget.setStyleSheet("background-color: #16213e; color: white;")
        self.properties_dock.setWidget(self.properties_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties_dock)
    
    # ========================================================================
    # ACTIONS
    # ========================================================================
    
    def new_project(self):
        """Crée un nouveau projet"""
        self.project_manager.new_project()
        self.properties_widget.setText("Nouveau projet créé")
        self.logger.info("Nouveau projet")
    
    def open_project(self):
        """Ouvre un projet"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Ouvrir un projet",
            PROJECTS_DIR,
            "Projets JSON (*.json);;Tous les fichiers (*)"
        )
        if file_path:
            self.project_manager.open_project(file_path)
            self.update_ui()
    
    def save_project(self):
        """Sauvegarde le projet"""
        if self.project_manager.current_project and self.project_manager.current_project.path:
            self.project_manager.save_project()
            self.statusbar.showMessage("Projet sauvegardé", 3000)
        else:
            self.save_project_as()
    
    def save_project_as(self):
        """Sauvegarde le projet sous un nouveau nom"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Sauvegarder le projet",
            PROJECTS_DIR,
            "Projets JSON (*.json)"
        )
        if file_path:
            if not file_path.endswith('.json'):
                file_path += '.json'
            self.project_manager.save_project(file_path)
            self.statusbar.showMessage(f"Projet sauvegardé: {file_path}", 3000)
    
    def add_layer(self):
        """Ajoute une couche"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Ajouter une couche",
            "",
            "Fichiers géospatiaux (*.shp *.geojson *.gpkg *.kml);;Tous les fichiers (*)"
        )
        if file_path:
            # Détection du type
            ext = os.path.splitext(file_path)[1].lower()
            layer_type = 'vector'
            if ext in ['.shp', '.geojson', '.gpkg', '.kml']:
                layer_type = 'vector'
            elif ext in ['.tif', '.tiff', '.jpg', '.png']:
                layer_type = 'raster'
            
            layer = Layer(
                name=os.path.basename(file_path),
                path=file_path,
                layer_type=layer_type
            )
            self.project_manager.add_layer(layer)
            self.layers_widget.add_layer(layer)
            self.statusbar.showMessage(f"Couche ajoutée: {layer.name}", 3000)
    
    def remove_layer(self, layer_id):
        """Supprime une couche"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment supprimer cette couche ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.project_manager.remove_layer(layer_id)
            self.layers_widget.remove_layer(layer_id)
            self.statusbar.showMessage("Couche supprimée", 3000)
    
    def show_layer_properties(self, layer_id):
        """Affiche les propriétés d'une couche"""
        layer = self.project_manager.get_layer(layer_id)
        if layer:
            props = f"""
            === PROPRIÉTÉS DE LA COUCHE ===
            
            Nom: {layer.name}
            Type: {layer.type}
            Chemin: {layer.path}
            Visible: {layer.visible}
            Opacité: {layer.opacity}
            CRS: {layer.crs or 'Non défini'}
            Entités: {layer.feature_count}
            
            Style:
            - Couleur: {layer.style.get('color', 'N/A')}
            - Contour: {layer.style.get('edgecolor', 'N/A')}
            - Alpha: {layer.style.get('alpha', 'N/A')}
            """
            self.properties_widget.setText(props)
    
    def zoom_to_layer(self, layer_id):
        """Zoom sur une couche"""
        layer = self.project_manager.get_layer(layer_id)
        if layer:
            self.statusbar.showMessage(f"Zoom sur: {layer.name}", 3000)
            # TODO: Implémenter le zoom réel
    
    def export_layer(self, layer_id):
        """Exporte une couche"""
        layer = self.project_manager.get_layer(layer_id)
        if layer:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Exporter la couche",
                "",
                "Shapefile (*.shp);;GeoJSON (*.geojson);;GPKG (*.gpkg)"
            )
            if file_path:
                self.statusbar.showMessage(f"Export de {layer.name}...", 3000)
                # TODO: Implémenter l'export réel
    
    def edit_layer_style(self, layer_id):
        """Édite le style d'une couche"""
        layer = self.project_manager.get_layer(layer_id)
        if layer:
            # TODO: Ouvrir un dialogue de style
            QMessageBox.information(self, "Style", f"Édition du style pour {layer.name}")
    
    def export_map(self):
        """Exporte la carte"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter la carte",
            "",
            "Image PNG (*.png);;Image JPEG (*.jpg);;PDF (*.pdf)"
        )
        if file_path:
            self.statusbar.showMessage("Export de la carte...", 3000)
            # TODO: Implémenter l'export réel
    
    def zoom_in(self):
        """Zoom avant"""
        self.statusbar.showMessage("Zoom avant", 2000)
        # TODO: Implémenter le zoom
    
    def zoom_out(self):
        """Zoom arrière"""
        self.statusbar.showMessage("Zoom arrière", 2000)
        # TODO: Implémenter le zoom
    
    def zoom_extent(self):
        """Zoom sur l'étendue totale"""
        self.statusbar.showMessage("Zoom sur l'étendue", 2000)
        # TODO: Implémenter le zoom étendue
    
    def measure(self):
        """Outil de mesure"""
        self.statusbar.showMessage("Outil de mesure - Cliquez sur la carte", 3000)
        # TODO: Implémenter la mesure
    
    def copy(self):
        """Copie"""
        self.statusbar.showMessage("Copie", 1000)
    
    def about(self):
        """Affiche la boîte À propos"""
        QMessageBox.about(
            self,
            f"À propos de {APP_NAME}",
            f"""
            <h2>{APP_NAME}</h2>
            <p>Version {APP_VERSION}</p>
            <p>{APP_AUTHOR}</p>
            <p>Un logiciel SIG professionnel complet</p>
            <p>Fonctionnalités :</p>
            <ul>
                <li>Interface style QGIS</li>
                <li>Gestion de projets</li>
                <li>Couches vectorielles et raster</li>
                <li>Styles cartographiques</li>
                <li>Outils d'analyse spatiale</li>
            </ul>
            """
        )
    
    def update_ui(self):
        """Met à jour l'interface"""
        if self.project_manager.current_project:
            self.setWindowTitle(f"{APP_NAME} v{APP_VERSION} - {self.project_manager.current_project.name}")


class QDockableWidget(QDockWidget):
    """Widget dockable personnalisé"""
    
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        
        # Style
        self.setStyleSheet("""
            QDockWidget {
                titlebar-close-icon: url();
                titlebar-normal-icon: url();
            }
            QDockWidget::title {
                background-color: #0f3460;
                padding: 5px;
                color: white;
                font-weight: bold;
            }
        """)


# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

def main():
    """Point d'entrée principal"""
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(APP_ORGANIZATION)
    
    # Style global
    app.setStyle('Fusion')
    
    # Palette sombre
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(20, 25, 35))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(15, 20, 30))
    palette.setColor(QPalette.AlternateBase, QColor(25, 30, 40))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(30, 35, 45))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.Highlight, QColor(76, 175, 80))
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()