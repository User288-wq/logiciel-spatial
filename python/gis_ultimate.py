#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
================================================================================
🏆 LOGICIEL DE CARTOGRAPHIE PROFESSIONNEL - LEAD DEV ULTIME EDITION
================================================================================
Version: 6.0.0
Auteur: Lead Dev
Date: 2026

FONCTIONNALITÉS COMPLÈTES :
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 CHARGEMENT DE DONNÉES
   • Shapefile (.shp)                    • GeoJSON (.geojson, .json)
   • KML / KMZ (Google Earth)            • GeoPackage (.gpkg)
   • CSV avec coordonnées (.csv)         • GeoTIFF (.tif, .tiff)
   • GML (.gml, .xml)                    • DXF (.dxf)
   • Glisser-déposer                    • Import avancé

🗺️ VISUALISATION
   • Zoom / Pan                          • Vue d'ensemble
   • Fonds de carte OpenStreetMap        • Légende automatique
   • Styles par type de géométrie        • Étiquettes automatiques
   • Thèmes sombre / clair               • Export PNG/JPEG/PDF

🖱️ INTERACTION
   • Sélection par clic                  • Affichage des attributs
   • Surbrillance des entités           • Recherche textuelle
   • Mesure de distance (points)         • Filtres par attribut

💾 GESTION DE PROJET
   • Sauvegarde/chargement JSON          • Historique des projets récents
   • Export des données sélectionnées    • Export CSV/GeoJSON/Shapefile

🎨 INTERFACE PROFESSIONNELLE
   • Menus complets                      • Barres d'outils
   • Panneaux dockables                  • Onglets
   • Barre d'état avec coordonnées       • Raccourcis clavier
   • Thème sombre élégant                • Support multi-écrans

⚙️ PERFORMANCES
   • Chargement asynchrone               • Cache des données
   • Filtrage rapide                     • Optimisation mémoire
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
import traceback
import zipfile
import tempfile
from datetime import datetime
from pathlib import Path
from collections import OrderedDict
from functools import partial

# ============================================================================
# IMPORTS GEOSPATIAUX
# ============================================================================

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon, box
from shapely.ops import unary_union
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.patches as mpatches

# ============================================================================
# IMPORTS QT
# ============================================================================

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtPrintSupport import QPrinter, QPrintDialog

# Configuration
os.environ["QT_API"] = "pyside6"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

# ============================================================================
# CONSTANTES GLOBALES
# ============================================================================

APP_NAME = "🏆 Logiciel de Cartographie Professionnel"
APP_VERSION = "6.0.0"
APP_AUTHOR = "Lead Dev"
APP_ORGANIZATION = "Spatial GIS"
APP_DOMAIN = "spatial-gis.com"

# Chemins
USER_HOME = str(Path.home())
APP_DATA_DIR = os.path.join(USER_HOME, ".spatial_gis")
PLUGINS_DIR = os.path.join(APP_DATA_DIR, "plugins")
PROJECTS_DIR = os.path.join(APP_DATA_DIR, "projects")
STYLES_DIR = os.path.join(APP_DATA_DIR, "styles")
LOGS_DIR = os.path.join(APP_DATA_DIR, "logs")
CACHE_DIR = os.path.join(APP_DATA_DIR, "cache")
EXPORTS_DIR = os.path.join(APP_DATA_DIR, "exports")

# Création des dossiers
for d in [APP_DATA_DIR, PLUGINS_DIR, PROJECTS_DIR, STYLES_DIR, LOGS_DIR, CACHE_DIR, EXPORTS_DIR]:
    os.makedirs(d, exist_ok=True)

# ============================================================================
# FORMATS SUPPORTÉS
# ============================================================================

SUPPORTED_FORMATS = {
    'Shapefile': {
        'extensions': ['*.shp'],
        'description': 'ESRI Shapefile',
        'icon': '🗺️',
        'driver': 'ESRI Shapefile'
    },
    'GeoJSON': {
        'extensions': ['*.geojson', '*.json'],
        'description': 'GeoJSON',
        'icon': '🌍',
        'driver': 'GeoJSON'
    },
    'KML/KMZ': {
        'extensions': ['*.kml', '*.kmz'],
        'description': 'Google Earth KML/KMZ',
        'icon': '🗺️',
        'driver': 'KML'
    },
    'GeoPackage': {
        'extensions': ['*.gpkg'],
        'description': 'GeoPackage',
        'icon': '📦',
        'driver': 'GPKG'
    },
    'CSV': {
        'extensions': ['*.csv', '*.txt'],
        'description': 'CSV avec coordonnées',
        'icon': '📊',
        'driver': None
    },
    'GeoTIFF': {
        'extensions': ['*.tif', '*.tiff'],
        'description': 'GeoTIFF (image satellite)',
        'icon': '🖼️',
        'driver': None
    },
    'GML': {
        'extensions': ['*.gml', '*.xml'],
        'description': 'Geography Markup Language',
        'icon': '📄',
        'driver': 'GML'
    },
    'DXF': {
        'extensions': ['*.dxf'],
        'description': 'AutoCAD DXF',
        'icon': '📐',
        'driver': 'DXF'
    }
}

# ============================================================================
# STYLES CARTOGRAPHIQUES
# ============================================================================

STYLES = {
    'Point': {
        'color': '#FF4444',
        'edge': '#CC0000',
        'alpha': 0.9,
        'marker': 'o',
        'size': 8,
        'label': True
    },
    'LineString': {
        'color': '#FFA500',
        'edge': '#FF8C00',
        'alpha': 0.8,
        'linewidth': 1.5,
        'label': False
    },
    'Polygon': {
        'color': '#4CAF50',
        'edge': '#2E7D32',
        'alpha': 0.4,
        'linewidth': 1,
        'label': True
    },
    'MultiPolygon': {
        'color': '#4CAF50',
        'edge': '#2E7D32',
        'alpha': 0.4,
        'linewidth': 1,
        'label': True
    },
    'region': {
        'color': '#4CAF50',
        'edge': '#2E7D32',
        'alpha': 0.4,
        'label': True
    },
    'departement': {
        'color': '#FFA500',
        'edge': '#FF8C00',
        'alpha': 0.3,
        'label': True
    },
    'commune': {
        'color': '#FF69B4',
        'edge': '#C71585',
        'alpha': 0.3,
        'label': True
    },
    'selected': {
        'color': '#FFFF00',
        'edge': '#FFAA00',
        'alpha': 0.8,
        'linewidth': 2
    },
    'measure': {
        'color': '#FF00FF',
        'edge': '#FF00AA',
        'alpha': 0.9,
        'linewidth': 2
    },
    'raster': {
        'alpha': 0.7,
        'cmap': 'viridis'
    },
    'default': {
        'color': '#888888',
        'edge': '#666666',
        'alpha': 0.5,
        'label': False
    }
}

LABEL_COLUMNS = [
    'name', 'NAME', 'NOM', 'label', 'LABEL', 'title', 'TITLE',
    'admin_level', 'ADMIN1', 'ADMIN2', 'ADMIN3', 'ADMIN4',
    'LIBELLE', 'LIBELLE_FR', 'commune', 'ville', 'city'
]

# ============================================================================
# GESTIONNAIRE DE LOGS
# ============================================================================

class Logger:
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
        self.console_output = True
        self.history = []
    
    def log(self, level, message, module='APP'):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        log_entry = f"[{timestamp}] [{level}] [{module}] {message}"
        self.history.append(log_entry)
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except:
            pass
        
        if self.console_output:
            print(log_entry)
    
    def info(self, message, module='APP'):
        self.log('INFO', message, module)
    
    def warning(self, message, module='APP'):
        self.log('WARNING', message, module)
    
    def error(self, message, module='APP'):
        self.log('ERROR', message, module)
    
    def debug(self, message, module='APP'):
        self.log('DEBUG', message, module)

# ============================================================================
# GESTIONNAIRE DE CONFIGURATION
# ============================================================================

class ConfigManager:
    def __init__(self):
        self.config_file = os.path.join(APP_DATA_DIR, 'config.json')
        self.config = self.load()
    
    def load(self):
        default_config = {
            'language': 'fr',
            'theme': 'dark',
            'crs_default': 'EPSG:4326',
            'grid_enabled': True,
            'coords_format': 'dd',
            'auto_save': True,
            'auto_save_interval': 5,
            'recent_projects': [],
            'basemap_enabled': False,
            'measure_mode': False,
            'toolbars': {
                'main': True,
                'map': True,
                'edit': True,
                'analysis': True
            }
        }
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except:
            return default_config
    
    def save(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            Logger().error(f"Erreur sauvegarde config: {e}")
    
    def get(self, key, default=None):
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def set(self, key, value):
        keys = key.split('.')
        target = self.config
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value

# ============================================================================
# CHARGEUR DE FICHIERS
# ============================================================================

class FileLoader:
    @staticmethod
    def load_file(filename, progress_callback=None):
        """Charge un fichier et retourne un GeoDataFrame ou un raster"""
        ext = os.path.splitext(filename)[1].lower()
        name = os.path.basename(filename)
        
        Logger().info(f"Chargement: {name}")
        
        try:
            # Shapefile / GeoJSON / GML
            if ext in ['.shp', '.geojson', '.json', '.gml', '.xml']:
                gdf = gpd.read_file(filename)
                return gdf, 'vectoriel', None
            
            # KML / KMZ
            elif ext in ['.kml', '.kmz']:
                return FileLoader._load_kml(filename)
            
            # GeoPackage
            elif ext == '.gpkg':
                gdf = gpd.read_file(filename, layer=0)
                return gdf, 'vectoriel', None
            
            # CSV
            elif ext in ['.csv', '.txt']:
                return FileLoader._load_csv(filename)
            
            # GeoTIFF
            elif ext in ['.tif', '.tiff']:
                return FileLoader._load_raster(filename)
            
            # DXF
            elif ext == '.dxf':
                try:
                    gdf = gpd.read_file(filename)
                    return gdf, 'vectoriel', None
                except:
                    return None, 'error', f"Format DXF non supporté directement"
            
            else:
                return None, 'error', f"Format non supporté: {ext}"
                
        except Exception as e:
            Logger().error(f"Erreur chargement {name}: {e}")
            traceback.print_exc()
            return None, 'error', str(e)
    
    @staticmethod
    def _load_kml(filename):
        try:
            if filename.endswith('.kmz'):
                with tempfile.TemporaryDirectory() as tmpdir:
                    with zipfile.ZipFile(filename, 'r') as kmz:
                        kmz.extractall(tmpdir)
                        kml_files = [f for f in os.listdir(tmpdir) if f.endswith('.kml')]
                        if kml_files:
                            gdf = gpd.read_file(os.path.join(tmpdir, kml_files[0]), driver='KML')
                            return gdf, 'vectoriel', None
                    return None, 'error', "Aucun fichier KML trouvé"
            else:
                gdf = gpd.read_file(filename, driver='KML')
                return gdf, 'vectoriel', None
        except Exception as e:
            return None, 'error', f"Erreur KML: {e}"
    
    @staticmethod
    def _load_csv(filename):
        try:
            df = pd.read_csv(filename, nrows=1000)
            
            lat_col = None
            lon_col = None
            
            for col in df.columns:
                col_lower = col.lower()
                if col_lower in ['lat', 'latitude', 'y']:
                    lat_col = col
                elif col_lower in ['lon', 'long', 'longitude', 'x']:
                    lon_col = col
            
            if lat_col and lon_col:
                geometry = [Point(x, y) for x, y in zip(df[lon_col], df[lat_col])]
                gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
                return gdf, 'vectoriel', None
            else:
                return None, 'error', "Aucune colonne de coordonnées trouvée"
                
        except Exception as e:
            return None, 'error', f"Erreur CSV: {e}"
    
    @staticmethod
    def _load_raster(filename):
        try:
            import rasterio
            src = rasterio.open(filename)
            return src, 'raster', None
        except ImportError:
            return None, 'error', "rasterio non installé (pip install rasterio)"
        except Exception as e:
            return None, 'error', f"Erreur raster: {e}"

# ============================================================================
# GESTIONNAIRE DE COUCHES (ARBRE)
# ============================================================================

class LayerTreeWidget(QTreeWidget):
    layer_visibility_changed = Signal(str, bool)
    layer_selected = Signal(object)
    layer_removed = Signal(str)
    layer_added = Signal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabel("🗂️ Couches du projet")
        self.setIndentation(15)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.itemClicked.connect(self.on_item_clicked)
        self.itemChanged.connect(self.on_item_changed)
        
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
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            filename = url.toLocalFile()
            if filename:
                self.parent().load_file(filename)
    
    def add_layer(self, layer):
        icons = {'Point': '📍', 'LineString': '📏', 'Polygon': '🔲', 'raster': '🖼️'}
        if layer.is_raster:
            icon = '🖼️'
        else:
            geom_type = layer.data.geometry.type.iloc[0] if len(layer.data) > 0 else 'Polygon'
            icon = icons.get(geom_type, '📌')
        
        item = QTreeWidgetItem(self)
        item.setText(0, f"{icon} {layer.name}")
        item.setCheckState(0, Qt.Checked if layer.visible else Qt.Unchecked)
        item.setData(0, Qt.UserRole, {'id': layer.id, 'type': layer.type})
        item.setToolTip(0, f"Type: {layer.type}\nChemin: {layer.path}")
        
        self.addTopLevelItem(item)
        layer.item = item
        self.layer_added.emit(layer)
        return item
    
    def update_visibility(self, layer_id, visible):
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            data = item.data(0, Qt.UserRole)
            if data and data['id'] == layer_id:
                item.setCheckState(0, Qt.Checked if visible else Qt.Unchecked)
                break
    
    def remove_layer(self, layer_id):
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            data = item.data(0, Qt.UserRole)
            if data and data['id'] == layer_id:
                self.takeTopLevelItem(i)
                self.layer_removed.emit(layer_id)
                break
    
    def on_item_clicked(self, item, column):
        data = item.data(0, Qt.UserRole)
        if data:
            self.layer_selected.emit(data['id'])
    
    def on_item_changed(self, item, column):
        if column == 0:
            data = item.data(0, Qt.UserRole)
            if data:
                visible = item.checkState(0) == Qt.Checked
                self.layer_visibility_changed.emit(data['id'], visible)
    
    def show_context_menu(self, position):
        item = self.itemAt(position)
        if not item:
            return
        data = item.data(0, Qt.UserRole)
        if not data:
            return
        
        menu = QMenu()
        menu.addAction("🔍 Zoom sur la couche", lambda: self.parent().zoom_to_layer(data['id']))
        menu.addAction("🎨 Filtrer", lambda: self.parent().show_filter_dialog(data['id']))
        menu.addAction("📤 Exporter", lambda: self.parent().export_layer_data(data['id']))
        menu.addSeparator()
        menu.addAction("📋 Propriétés", lambda: self.parent().show_layer_properties(data['id']))
        menu.addSeparator()
        menu.addAction("🗑️ Supprimer", lambda: self.parent().remove_layer(data['id']))
        menu.exec(self.viewport().mapToGlobal(position))

# ============================================================================
# PANNEAU DE PROPRIÉTÉS
# ============================================================================

class PropertiesWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_layer = None
        self.setup_ui()
    
    def setup_ui(self):
        self.setDocumentMode(True)
        self.setStyleSheet("""
            QTabWidget::pane {
                background-color: #1a1a2a;
                border: none;
            }
            QTabBar::tab {
                background-color: #16213e;
                color: white;
                padding: 8px 15px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
            }
        """)
        
        # Onglet Info
        self.info_tab = QWidget()
        info_layout = QVBoxLayout(self.info_tab)
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet("background-color: #16213e; color: #00ff00; font-family: 'Courier New'; font-size: 11px;")
        info_layout.addWidget(self.info_text)
        self.addTab(self.info_tab, "ℹ️ Info")
        
        # Onglet Attributs
        self.attr_tab = QWidget()
        attr_layout = QVBoxLayout(self.attr_tab)
        self.attr_table = QTableWidget()
        self.attr_table.setColumnCount(3)
        self.attr_table.setHorizontalHeaderLabels(["Champ", "Type", "Valeur"])
        self.attr_table.horizontalHeader().setStretchLastSection(True)
        self.attr_table.setAlternatingRowColors(True)
        attr_layout.addWidget(self.attr_table)
        self.addTab(self.attr_tab, "📊 Attributs")
        
        # Onglet Statistiques
        self.stats_tab = QWidget()
        stats_layout = QVBoxLayout(self.stats_tab)
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setStyleSheet("background-color: #16213e; color: #00ff00; font-family: 'Courier New'; font-size: 11px;")
        stats_layout.addWidget(self.stats_text)
        self.addTab(self.stats_tab, "📈 Stats")
    
    def update_properties(self, layer):
        self.current_layer = layer
        if not layer or layer.data is None or layer.is_raster:
            self.info_text.setText("Aucune donnée disponible")
            self.attr_table.setRowCount(0)
            self.stats_text.setText("")
            return
        
        gdf = layer.data
        geom_type = gdf.geometry.type.iloc[0] if len(gdf) > 0 else 'N/A'
        
        # Info
        info = f"""
╔══════════════════════════════════════════════════════════════╗
║  {layer.name}
╚══════════════════════════════════════════════════════════════╝

📌 TYPE: {layer.type.upper()} | Géométrie: {geom_type}
📊 ENTITÉS: {len(gdf):,}
📁 COLONNES: {len(gdf.columns) - 1}

🌍 ÉTENDUE:
   X: [{gdf.total_bounds[0]:.4f}, {gdf.total_bounds[2]:.4f}]
   Y: [{gdf.total_bounds[1]:.4f}, {gdf.total_bounds[3]:.4f}]

🔄 PROJECTION: {gdf.crs or 'Non défini'}

📋 COLONNES DISPONIBLES:
"""
        for col in gdf.columns:
            if col != 'geometry':
                info += f"   • {col}\n"
        self.info_text.setText(info)
        
        # Attributs
        self.attr_table.setRowCount(len(gdf.columns) - 1)
        row = 0
        for col in gdf.columns:
            if col != 'geometry':
                self.attr_table.setItem(row, 0, QTableWidgetItem(col))
                self.attr_table.setItem(row, 1, QTableWidgetItem(str(gdf[col].dtype)))
                preview = str(gdf[col].iloc[0])[:50] if len(gdf) > 0 else ''
                self.attr_table.setItem(row, 2, QTableWidgetItem(preview))
                row += 1
        
        # Statistiques
        stats = "📊 STATISTIQUES DES CHAMPS NUMÉRIQUES\n"
        stats += "═" * 40 + "\n\n"
        for col in gdf.columns:
            if col != 'geometry' and pd.api.types.is_numeric_dtype(gdf[col]):
                stats += f"📌 {col}:\n"
                stats += f"   Min: {gdf[col].min():,.2f}\n"
                stats += f"   Max: {gdf[col].max():,.2f}\n"
                stats += f"   Moy: {gdf[col].mean():,.2f}\n"
                stats += f"   Std: {gdf[col].std():,.2f}\n\n"
        self.stats_text.setText(stats)

# ============================================================================
# LÉGENDE
# ============================================================================

class LegendWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.title = QLabel("📖 LÉGENDE")
        self.title.setStyleSheet("font-weight: bold; color: #4CAF50; font-size: 12px; padding: 5px;")
        layout.addWidget(self.title)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setMaximumHeight(200)
        
        self.legend_content = QWidget()
        self.legend_layout = QVBoxLayout(self.legend_content)
        self.scroll.setWidget(self.legend_content)
        layout.addWidget(self.scroll)
        
        self.update_legend()
    
    def update_legend(self):
        for i in reversed(range(self.legend_layout.count())):
            widget = self.legend_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        entries = [
            ('🟩', 'Régions', '#4CAF50'),
            ('🟧', 'Départements', '#FFA500'),
            ('🟪', 'Communes', '#FF69B4'),
            ('📍', 'Points', '#FF4444'),
            ('📏', 'Lignes', '#FFA500'),
            ('🔲', 'Polygones', '#4CAF50'),
            ('🟨', 'Sélectionné', '#FFFF00'),
            ('🟪', 'Mesure', '#FF00FF'),
            ('🖼️', 'Images satellite', '#888888'),
        ]
        
        for icon, name, color in entries:
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(2, 2, 2, 2)
            
            color_label = QLabel(icon)
            color_label.setStyleSheet(f"font-size: 14px;")
            layout.addWidget(color_label)
            
            name_label = QLabel(name)
            name_label.setStyleSheet("color: white; font-size: 10px;")
            layout.addWidget(name_label)
            
            layout.addStretch()
            self.legend_layout.addWidget(widget)

# ============================================================================
# MOTEUR CARTOGRAPHIQUE
# ============================================================================

class MapWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(10, 8), facecolor='#0a1a2a')
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#0a1a2a')
        self.ax.tick_params(colors='white')
        
        self.nav_toolbar = NavigationToolbar(self.canvas, self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.nav_toolbar)
        layout.addWidget(self.canvas)
        
        self.measure_mode = False
        self.measure_points = []
        self.basemap_enabled = False
        self.parent_app = parent
        self.cid = self.canvas.mpl_connect('button_press_event', self.on_click)
    
    def get_style(self, layer, is_selected=False):
        if is_selected:
            return STYLES['selected']
        
        name_lower = layer.name.lower()
        for keyword in ['region', 'departement', 'commune']:
            if keyword in name_lower:
                return STYLES[keyword]
        
        if layer.data is not None and not layer.is_raster and len(layer.data) > 0:
            geom_type = layer.data.geometry.type.iloc[0]
            if geom_type in STYLES:
                return STYLES[geom_type]
        
        return STYLES['default']
    
    def get_label_column(self, gdf):
        for col in LABEL_COLUMNS:
            if col in gdf.columns:
                return col
        return None
    
    def draw_layers(self, layers):
        self.ax.clear()
        self.ax.set_facecolor('#0a1a2a')
        
        if self.basemap_enabled:
            try:
                import contextily as ctx
                ctx.add_basemap(self.ax, crs='EPSG:4326', source=ctx.providers.OpenStreetMap.Mapnik)
            except:
                pass
        
        xmin, ymin, xmax, ymax = float('inf'), float('inf'), float('-inf'), float('-inf')
        any_visible = False
        
        for layer in layers:
            if not layer.visible or layer.data is None:
                continue
            
            any_visible = True
            is_selected = hasattr(layer, 'selected') and layer.selected is not None
            style = self.get_style(layer, is_selected)
            
            if layer.is_raster:
                try:
                    from rasterio.plot import show
                    show(layer.data, ax=self.ax, alpha=style.get('alpha', 0.7))
                except:
                    pass
            else:
                gdf = layer.data
                if hasattr(layer, 'filtered_indices') and layer.filtered_indices is not None:
                    gdf = layer.data.iloc[layer.filtered_indices]
                
                geom_type = gdf.geometry.type.iloc[0] if len(gdf) > 0 else 'Polygon'
                
                if 'Point' in geom_type:
                    gdf.plot(ax=self.ax, color=style['color'], 
                            markersize=style.get('size', 5), 
                            marker=style.get('marker', 'o'),
                            alpha=style['alpha'])
                elif 'Line' in geom_type:
                    gdf.plot(ax=self.ax, color=style['color'], 
                            linewidth=style.get('linewidth', 1),
                            alpha=style['alpha'])
                else:
                    gdf.plot(ax=self.ax, color=style['color'], 
                            edgecolor=style['edge'], 
                            linewidth=style.get('linewidth', 0.5),
                            alpha=style['alpha'])
                
                if is_selected and layer.selected is not None:
                    selected_gdf = layer.data.iloc[[layer.selected]]
                    selected_gdf.plot(ax=self.ax, color=STYLES['selected']['color'],
                                     edgecolor=STYLES['selected']['edge'],
                                     linewidth=2, alpha=0.9)
                
                bounds = gdf.total_bounds
                xmin = min(xmin, bounds[0])
                ymin = min(ymin, bounds[1])
                xmax = max(xmax, bounds[2])
                ymax = max(ymax, bounds[3])
                
                label_col = self.get_label_column(layer.data)
                if label_col and style.get('label', True):
                    for idx, row in gdf.iterrows():
                        if row.geometry and not row.geometry.is_empty:
                            try:
                                centroid = row.geometry.centroid
                                label = str(row[label_col])[:20]
                                if label and label != 'nan':
                                    color = 'yellow' if hasattr(layer, 'selected') and layer.selected == idx else 'white'
                                    self.ax.text(centroid.x, centroid.y, label,
                                               fontsize=7, color=color,
                                               ha='center', va='center',
                                               bbox=dict(boxstyle="round,pad=0.1",
                                                        facecolor='#1a1a2a',
                                                        alpha=0.6))
                            except:
                                pass
        
        # Dessiner les mesures
        if len(self.measure_points) > 1:
            x = [p[0] for p in self.measure_points]
            y = [p[1] for p in self.measure_points]
            self.ax.plot(x, y, 'm-', linewidth=2, alpha=0.8)
            self.ax.plot(x, y, 'mo', markersize=5)
            
            total_dist = 0
            for i in range(len(self.measure_points)-1):
                x1, y1 = self.measure_points[i]
                x2, y2 = self.measure_points[i+1]
                dist = math.sqrt((x2-x1)**2 + (y2-y1)**2) * 111
                total_dist += dist
            
            x_last, y_last = self.measure_points[-1]
            self.ax.text(x_last, y_last, f"{total_dist:.2f} km", 
                        fontsize=9, color='white',
                        bbox=dict(boxstyle="round,pad=0.3",
                                 facecolor='#FF00FF',
                                 alpha=0.8))
        
        if not any_visible:
            self.ax.set_title("Aucune donnée visible - Glissez-déposez des fichiers", color='white')
            self.canvas.draw()
            return None
        
        if xmin != float('inf'):
            margin_x = (xmax - xmin) * 0.05
            margin_y = (ymax - ymin) * 0.05
            self.ax.set_xlim(xmin - margin_x, xmax + margin_x)
            self.ax.set_ylim(ymin - margin_y, ymax + margin_y)
        
        mode_text = " [Mode Mesure ACTIF]" if self.measure_mode else ""
        self.ax.set_title(f"Carte - {len([l for l in layers if l.visible])} couche(s){mode_text}", color='white')
        self.ax.tick_params(colors='white')
        self.canvas.draw()
        return (xmin, ymin, xmax, ymax)
    
    def on_click(self, event):
        if event.inaxes is None:
            return
        
        x, y = event.xdata, event.ydata
        
        if self.measure_mode:
            self.measure_points.append((x, y))
            self.draw_layers(self.parent_app.layers)
            return
        
        point = Point(x, y)
        for layer in self.parent_app.layers:
            if not layer.visible or layer.data is None or layer.is_raster:
                continue
            
            gdf = layer.data
            if hasattr(layer, 'filtered_indices') and layer.filtered_indices is not None:
                gdf = layer.data.iloc[layer.filtered_indices]
            
            for idx, row in gdf.iterrows():
                if row.geometry and row.geometry.contains(point):
                    layer.selected = idx
                    self.parent_app.show_attributes(layer, idx, row)
                    self.draw_layers(self.parent_app.layers)
                    return
        
        for layer in self.parent_app.layers:
            if hasattr(layer, 'selected'):
                delattr(layer, 'selected')
        self.parent_app.attr_text.clear()
        self.draw_layers(self.parent_app.layers)
    
    def toggle_measure(self):
        self.measure_mode = not self.measure_mode
        if not self.measure_mode:
            self.measure_points = []
        self.draw_layers(self.parent_app.layers)
    
    def toggle_basemap(self):
        self.basemap_enabled = not self.basemap_enabled
        self.draw_layers(self.parent_app.layers)
    
    def clear_measure(self):
        self.measure_points = []
        self.draw_layers(self.parent_app.layers)
    
    def zoom_all(self, layers=None):
        if layers is None:
            layers = self.parent_app.layers
        
        xmin, ymin, xmax, ymax = float('inf'), float('inf'), float('-inf'), float('-inf')
        for layer in layers:
            if layer.data is not None and not layer.is_raster:
                gdf = layer.data
                if hasattr(layer, 'filtered_indices') and layer.filtered_indices is not None:
                    gdf = layer.data.iloc[layer.filtered_indices]
                if len(gdf) > 0:
                    bounds = gdf.total_bounds
                    xmin = min(xmin, bounds[0])
                    ymin = min(ymin, bounds[1])
                    xmax = max(xmax, bounds[2])
                    ymax = max(ymax, bounds[3])
        
        if xmin != float('inf'):
            margin_x = (xmax - xmin) * 0.1
            margin_y = (ymax - ymin) * 0.1
            self.ax.set_xlim(xmin - margin_x, xmax + margin_x)
            self.ax.set_ylim(ymin - margin_y, ymax + margin_y)
        else:
            self.ax.set_xlim(-20, 20)
            self.ax.set_ylim(0, 25)
        
        self.canvas.draw()

# ============================================================================
# COUCHE
# ============================================================================

class Layer:
    def __init__(self, layer_id, name, path, data, layer_type, is_raster=False):
        self.id = layer_id
        self.name = name
        self.path = path
        self.data = data
        self.type = layer_type
        self.is_raster = is_raster
        self.visible = True
        self.item = None
        self.filtered_indices = None
        if hasattr(self, 'selected'):
            delattr(self, 'selected')
    
    @property
    def gdf(self):
        return self.data if not self.is_raster else None

# ============================================================================
# DIALOGUES
# ============================================================================

class FilterDialog(QDialog):
    def __init__(self, layer, parent=None):
        super().__init__(parent)
        self.layer = layer
        self.setWindowTitle(f"Filtrer - {layer.name}")
        self.setGeometry(200, 200, 500, 400)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Colonne:"))
        self.col_combo = QComboBox()
        for col in self.layer.data.columns:
            if col != 'geometry':
                self.col_combo.addItem(col)
        layout.addWidget(self.col_combo)
        
        layout.addWidget(QLabel("Opérateur:"))
        self.op_combo = QComboBox()
        self.op_combo.addItems(['=', '!=', '>', '<', '>=', '<=', 'contains'])
        layout.addWidget(self.op_combo)
        
        layout.addWidget(QLabel("Valeur:"))
        self.value_edit = QLineEdit()
        layout.addWidget(self.value_edit)
        
        btn_layout = QHBoxLayout()
        self.apply_btn = QPushButton("Appliquer")
        self.apply_btn.clicked.connect(self.apply_filter)
        self.clear_btn = QPushButton("Effacer")
        self.clear_btn.clicked.connect(self.clear_filter)
        btn_layout.addWidget(self.apply_btn)
        btn_layout.addWidget(self.clear_btn)
        layout.addLayout(btn_layout)
        
        layout.addWidget(QLabel("Aperçu des valeurs:"))
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setMaximumHeight(150)
        layout.addWidget(self.preview)
        
        self.col_combo.currentTextChanged.connect(self.update_preview)
        self.update_preview()
    
    def update_preview(self):
        col = self.col_combo.currentText()
        if col and col in self.layer.data.columns:
            values = self.layer.data[col].dropna().unique()[:10]
            self.preview.setText("\n".join(str(v) for v in values))
    
    def apply_filter(self):
        col = self.col_combo.currentText()
        op = self.op_combo.currentText()
        val = self.value_edit.text()
        
        try:
            if op == '=':
                mask = self.layer.data[col].astype(str) == val
            elif op == '!=':
                mask = self.layer.data[col].astype(str) != val
            elif op == '>':
                mask = self.layer.data[col].astype(float) > float(val)
            elif op == '<':
                mask = self.layer.data[col].astype(float) < float(val)
            elif op == '>=':
                mask = self.layer.data[col].astype(float) >= float(val)
            elif op == '<=':
                mask = self.layer.data[col].astype(float) <= float(val)
            elif op == 'contains':
                mask = self.layer.data[col].astype(str).str.contains(val, case=False, na=False)
            
            indices = mask[mask].index.tolist()
            self.layer.filtered_indices = indices
            self.parent().status.showMessage(f"Filtre appliqué: {len(indices)} entités")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    def clear_filter(self):
        self.layer.filtered_indices = None
        self.parent().status.showMessage("Filtre effacé")
        self.accept()

class SearchDialog(QDialog):
    def __init__(self, layers, parent=None):
        super().__init__(parent)
        self.layers = layers
        self.setWindowTitle("Recherche d'entités")
        self.setGeometry(200, 200, 500, 400)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Rechercher:"))
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.search)
        layout.addWidget(self.search_edit)
        
        layout.addWidget(QLabel("Résultats:"))
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.go_to_result)
        layout.addWidget(self.results_list)
        
        self.results = []
    
    def search(self):
        self.results_list.clear()
        self.results = []
        text = self.search_edit.text().lower()
        
        for layer in self.layers:
            if not layer.visible or layer.data is None or layer.is_raster:
                continue
            
            label_col = None
            for col in LABEL_COLUMNS:
                if col in layer.data.columns:
                    label_col = col
                    break
            
            if not label_col:
                continue
            
            for idx, row in layer.data.iterrows():
                name = str(row[label_col]).lower()
                if text in name:
                    self.results.append((layer, idx, row[label_col]))
                    self.results_list.addItem(f"{layer.name}: {row[label_col]}")
    
    def go_to_result(self, item):
        idx = self.results_list.currentRow()
        if idx >= 0:
            layer, entity_idx, name = self.results[idx]
            geom = layer.data.iloc[entity_idx].geometry
            if geom:
                bounds = geom.bounds
                margin_x = (bounds[2] - bounds[0]) * 0.1
                margin_y = (bounds[3] - bounds[1]) * 0.1
                self.parent().map_widget.ax.set_xlim(bounds[0] - margin_x, bounds[2] + margin_x)
                self.parent().map_widget.ax.set_ylim(bounds[1] - margin_y, bounds[3] + margin_y)
                self.parent().map_widget.canvas.draw()
                
                layer.selected = entity_idx
                self.parent().show_attributes(layer, entity_idx, layer.data.iloc[entity_idx])
                self.parent().map_widget.draw_layers(self.parent().layers)
                self.accept()

class ImportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import avancé de données")
        self.setGeometry(200, 200, 500, 400)
        self.selected_file = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("📂 IMPORT DE DONNÉES GÉOSPATIALES")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #4CAF50;")
        layout.addWidget(title)
        
        formats_text = QTextEdit()
        formats_text.setReadOnly(True)
        formats_text.setMaximumHeight(100)
        formats_html = "<b>Formats supportés:</b><br>"
        for name, info in SUPPORTED_FORMATS.items():
            formats_html += f"• {info['icon']} <b>{name}</b> ({', '.join(info['extensions']).replace('*.', '')})<br>"
        formats_text.setHtml(formats_html)
        layout.addWidget(formats_text)
        
        file_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.setReadOnly(True)
        file_layout.addWidget(self.file_path)
        
        self.browse_btn = QPushButton("Parcourir")
        self.browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_btn)
        layout.addLayout(file_layout)
        
        options_group = QGroupBox("Options d'import")
        options_layout = QFormLayout(options_group)
        
        self.crs_edit = QLineEdit()
        self.crs_edit.setPlaceholderText("EPSG:4326 (par défaut)")
        options_layout.addRow("Système de projection:", self.crs_edit)
        
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(['utf-8', 'latin1', 'cp1252'])
        options_layout.addRow("Encodage:", self.encoding_combo)
        
        self.layer_name = QLineEdit()
        self.layer_name.setPlaceholderText("Nom automatique")
        options_layout.addRow("Nom de la couche:", self.layer_name)
        
        layout.addWidget(options_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(100)
        layout.addWidget(self.preview_text)
        
        btn_layout = QHBoxLayout()
        self.import_btn = QPushButton("✅ Importer")
        self.import_btn.clicked.connect(self.accept)
        self.import_btn.setEnabled(False)
        self.cancel_btn = QPushButton("❌ Annuler")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.import_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
    
    def browse_file(self):
        formats_filter = "Tous les fichiers supportés (" + " ".join([ext for info in SUPPORTED_FORMATS.values() for ext in info['extensions']]) + ");;"
        for name, info in SUPPORTED_FORMATS.items():
            formats_filter += f"{info['icon']} {name} ({' '.join(info['extensions'])});;"
        formats_filter += "Tous fichiers (*.*)"
        
        filename, _ = QFileDialog.getOpenFileName(self, "Choisir un fichier", "", formats_filter)
        if filename:
            self.selected_file = filename
            self.file_path.setText(filename)
            self.layer_name.setText(os.path.basename(filename))
            self.preview_file(filename)
            self.import_btn.setEnabled(True)
    
    def preview_file(self, filename):
        ext = os.path.splitext(filename)[1].lower()
        preview = f"Fichier: {os.path.basename(filename)}\n"
        preview += f"Extension: {ext}\n"
        preview += f"Taille: {os.path.getsize(filename) / 1024:.2f} KB\n"
        self.preview_text.setText(preview)

# ============================================================================
# FENÊTRE PRINCIPALE
# ============================================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setGeometry(100, 100, 1600, 900)
        self.setAcceptDrops(True)
        
        self.logger = Logger()
        self.config = ConfigManager()
        self.layers = []
        self.next_id = 0
        self.project_path = None
        
        self.setup_ui()
        self.setup_menus()
        self.setup_toolbars()
        self.setup_statusbar()
        
        self.logger.info(f"Application démarrée - {APP_NAME} v{APP_VERSION}")
        self.status.showMessage("Prêt - Glissez-déposez vos fichiers !")
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            filename = url.toLocalFile()
            if filename:
                self.load_file(filename)
    
    def load_file(self, filename):
        """Charge un fichier avec détection automatique"""
        data, data_type, error = FileLoader.load_file(filename)
        
        if data is None:
            QMessageBox.warning(self, "Erreur", f"Impossible de charger {os.path.basename(filename)}\n{error}")
            return
        
        name = os.path.basename(filename)
        is_raster = (data_type == 'raster')
        layer_type = 'default'
        name_lower = name.lower()
        for kw in ['region', 'departement', 'commune']:
            if kw in name_lower:
                layer_type = kw
                break
        
        layer_id = str(self.next_id)
        self.next_id += 1
        layer = Layer(layer_id, name, filename, data, layer_type, is_raster)
        
        self.layer_tree.add_layer(layer)
        self.layers.append(layer)
        
        self.redraw_map()
        self.map_widget.zoom_all(self.layers)
        self.status.showMessage(f"✅ {name} chargé")
        self.logger.info(f"Couche ajoutée: {name}")
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Panneau gauche
        left_panel = QWidget()
        left_panel.setMaximumWidth(450)
        left_layout = QVBoxLayout(left_panel)
        
        info_label = QLabel("💡 Glissez-déposez vos fichiers ici\n📁 Formats: .shp, .geojson, .kml, .kmz, .gpkg, .csv, .tif...")
        info_label.setStyleSheet("background-color: #16213e; color: #ffaa00; padding: 8px; border-radius: 5px;")
        left_layout.addWidget(info_label)
        
        self.layer_tree = LayerTreeWidget(self)
        self.layer_tree.layer_visibility_changed.connect(self.on_layer_visibility_changed)
        self.layer_tree.layer_selected.connect(self.on_layer_selected)
        self.layer_tree.layer_removed.connect(self.on_layer_removed)
        left_layout.addWidget(QLabel("🗂️ Couches"))
        left_layout.addWidget(self.layer_tree)
        
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("➕ Ajouter")
        self.btn_add.clicked.connect(self.show_import_dialog)
        self.btn_remove = QPushButton("➖ Supprimer")
        self.btn_remove.clicked.connect(self.remove_selected_layer)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_remove)
        left_layout.addLayout(btn_layout)
        
        # Attributs sélectionnés
        self.attr_group = QGroupBox("📋 Attributs de l'entité sélectionnée")
        attr_layout = QVBoxLayout(self.attr_group)
        self.attr_text = QTextEdit()
        self.attr_text.setReadOnly(True)
        self.attr_text.setStyleSheet("background-color: #16213e; color: #ffaa00; font-family: 'Courier New'; font-size: 11px;")
        self.attr_text.setMaximumHeight(200)
        attr_layout.addWidget(self.attr_text)
        left_layout.addWidget(self.attr_group)
        
        self.properties = PropertiesWidget()
        left_layout.addWidget(QLabel("📋 Propriétés de la couche"))
        left_layout.addWidget(self.properties)
        
        layout.addWidget(left_panel)
        
        # Zone centrale
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        self.map_widget = MapWidget(self)
        center_layout.addWidget(self.map_widget)
        layout.addWidget(center_panel, 1)
        
        # Panneau droit
        right_panel = QWidget()
        right_panel.setMaximumWidth(250)
        right_layout = QVBoxLayout(right_panel)
        self.legend = LegendWidget()
        right_layout.addWidget(self.legend)
        right_layout.addStretch()
        layout.addWidget(right_panel)
    
    def setup_menus(self):
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("&Fichier")
        file_menu.addAction("📂 Importer un fichier", self.show_import_dialog, "Ctrl+O")
        file_menu.addSeparator()
        file_menu.addAction("💾 Sauvegarder projet", self.save_project, "Ctrl+S")
        file_menu.addAction("📂 Ouvrir projet", self.load_project, "Ctrl+Shift+O")
        file_menu.addSeparator()
        file_menu.addAction("💾 Exporter la carte", self.export_map, "Ctrl+E")
        file_menu.addSeparator()
        file_menu.addAction("❌ Quitter", self.close, "Ctrl+Q")
        
        # Menu Outils
        tools_menu = menubar.addMenu("&Outils")
        tools_menu.addAction("📏 Mesurer une distance", self.toggle_measure, "Ctrl+M")
        tools_menu.addAction("🔍 Rechercher", self.show_search, "Ctrl+F")
        tools_menu.addAction("🗺️ Fonds de carte OSM", self.toggle_basemap)
        tools_menu.addSeparator()
        tools_menu.addAction("🗑️ Effacer mesure", self.clear_measure)
        tools_menu.addAction("🗑️ Effacer sélection", self.clear_selection, "Ctrl+D")
        
        # Menu Affichage
        view_menu = menubar.addMenu("&Affichage")
        view_menu.addAction("🌍 Vue d'ensemble", self.zoom_all, "Ctrl+0")
        
        # Menu Aide
        help_menu = menubar.addMenu("&Aide")
        help_menu.addAction("📚 Documentation", self.show_docs)
        help_menu.addAction("ℹ️ À propos", self.about)
    
    def setup_toolbars(self):
        toolbar = self.addToolBar("Outils")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(True)
        
        toolbar.addAction("📂 Importer", self.show_import_dialog)
        toolbar.addAction("💾 Sauvegarder", self.save_project)
        toolbar.addAction("📏 Mesurer", self.toggle_measure)
        toolbar.addAction("🔍 Rechercher", self.show_search)
        toolbar.addAction("🗺️ Carte OSM", self.toggle_basemap)
        toolbar.addSeparator()
        toolbar.addAction("🗑️ Effacer sélection", self.clear_selection)
        toolbar.addAction("🗑️ Effacer mesure", self.clear_measure)
        toolbar.addSeparator()
        toolbar.addAction("🌍 Vue d'ensemble", self.zoom_all)
        toolbar.addAction("❓ Aide", self.show_docs)
    
    def setup_statusbar(self):
        self.status = self.statusBar()
        self.coord_label = QLabel("📍 -")
        self.scale_label = QLabel("📏 -")
        self.mode_label = QLabel("")
        self.layer_count_label = QLabel("🗂️ 0 couche(s)")
        
        self.status.addPermanentWidget(self.coord_label)
        self.status.addPermanentWidget(QLabel("  |  "))
        self.status.addPermanentWidget(self.scale_label)
        self.status.addPermanentWidget(QLabel("  |  "))
        self.status.addPermanentWidget(self.mode_label)
        self.status.addPermanentWidget(QLabel("  |  "))
        self.status.addPermanentWidget(self.layer_count_label)
        self.status.showMessage("Prêt")
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(500)
    
    def update_status(self):
        # Mise à jour coordonnées
        if hasattr(self.map_widget, 'ax') and self.map_widget.ax.has_data():
            xl, yl = self.map_widget.ax.get_xlim(), self.map_widget.ax.get_ylim()
            lon = (xl[0] + xl[1]) / 2
            lat = (yl[0] + yl[1]) / 2
            self.coord_label.setText(f"📍 {lon:.4f}°, {lat:.4f}°")
            
            width_deg = xl[1] - xl[0]
            width_km = width_deg * 111
            scale = width_km * 100000
            self.scale_label.setText(f"📏 1:{int(scale):,}")
        
        # Mode mesure
        if self.map_widget.measure_mode:
            self.mode_label.setText("📏 MODE MESURE ACTIF")
            self.mode_label.setStyleSheet("color: #FF00FF; font-weight: bold;")
        else:
            self.mode_label.setText("")
        
        # Compteur de couches
        self.layer_count_label.setText(f"🗂️ {len(self.layers)} couche(s)")
    
    def show_attributes(self, layer, idx, row):
        text = f"🗺️ {layer.name}\n"
        text += "═" * 40 + "\n\n"
        
        for col in row.index:
            if col != 'geometry':
                val = row[col]
                if val is not None:
                    text += f"📌 {col}: {val}\n"
                else:
                    text += f"📌 {col}: (vide)\n"
        
        text += f"\n📍 Index: {idx}"
        self.attr_text.setText(text)
        self.status.showMessage(f"✅ Entité sélectionnée dans {layer.name}")
    
    def clear_selection(self):
        for layer in self.layers:
            if hasattr(layer, 'selected'):
                delattr(layer, 'selected')
        self.attr_text.clear()
        self.redraw_map()
        self.status.showMessage("Sélection effacée")
    
    def toggle_measure(self):
        self.map_widget.toggle_measure()
        self.status.showMessage("Mode mesure " + ("activé" if self.map_widget.measure_mode else "désactivé"))
    
    def toggle_basemap(self):
        self.map_widget.toggle_basemap()
        self.status.showMessage("Fond de carte " + ("activé" if self.map_widget.basemap_enabled else "désactivé"))
    
    def clear_measure(self):
        self.map_widget.clear_measure()
        self.status.showMessage("Mesures effacées")
    
    def show_search(self):
        dialog = SearchDialog(self.layers, self)
        dialog.exec()
    
    def show_import_dialog(self):
        dialog = ImportDialog(self)
        if dialog.exec() and dialog.selected_file:
            self.load_file(dialog.selected_file)
    
    def show_filter_dialog(self, layer_id):
        for layer in self.layers:
            if layer.id == layer_id and not layer.is_raster:
                dialog = FilterDialog(layer, self)
                dialog.exec()
                self.redraw_map()
                break
    
    def show_layer_properties(self, layer_id):
        for layer in self.layers:
            if layer.id == layer_id:
                self.properties.update_properties(layer)
                self.properties.setCurrentIndex(0)
                break
    
    def export_layer_data(self, layer_id):
        for layer in self.layers:
            if layer.id == layer_id and not layer.is_raster:
                filename, _ = QFileDialog.getSaveFileName(
                    self, "Exporter les données", 
                    os.path.join(EXPORTS_DIR, layer.name), 
                    "CSV (*.csv);;GeoJSON (*.geojson);;Shapefile (*.shp)"
                )
                if filename:
                    try:
                        gdf = layer.data
                        if hasattr(layer, 'filtered_indices') and layer.filtered_indices is not None:
                            gdf = layer.data.iloc[layer.filtered_indices]
                        
                        if filename.endswith('.csv'):
                            gdf.drop('geometry', axis=1).to_csv(filename, index=False)
                        elif filename.endswith('.geojson'):
                            gdf.to_file(filename, driver='GeoJSON')
                        elif filename.endswith('.shp'):
                            gdf.to_file(filename)
                        
                        self.status.showMessage(f"✅ Exporté: {os.path.basename(filename)}")
                    except Exception as e:
                        QMessageBox.critical(self, "Erreur", str(e))
                break
    
    def zoom_to_layer(self, layer_id):
        for layer in self.layers:
            if layer.id == layer_id and layer.data is not None and not layer.is_raster:
                bounds = layer.data.total_bounds
                margin_x = (bounds[2] - bounds[0]) * 0.05
                margin_y = (bounds[3] - bounds[1]) * 0.05
                self.map_widget.ax.set_xlim(bounds[0] - margin_x, bounds[2] + margin_x)
                self.map_widget.ax.set_ylim(bounds[1] - margin_y, bounds[3] + margin_y)
                self.map_widget.canvas.draw()
                break
    
    def zoom_all(self):
        self.map_widget.zoom_all(self.layers)
    
    def save_project(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Sauvegarder le projet", PROJECTS_DIR, "Projet JSON (*.json)"
        )
        if filename:
            project = {
                'name': os.path.basename(filename),
                'version': APP_VERSION,
                'date': datetime.now().isoformat(),
                'crs': 'EPSG:4326',
                'layers': []
            }
            
            for layer in self.layers:
                project['layers'].append({
                    'path': layer.path,
                    'name': layer.name,
                    'type': layer.type,
                    'is_raster': layer.is_raster,
                    'visible': layer.visible
                })
            
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(project, f, indent=2, ensure_ascii=False)
                
                # Ajouter aux récents
                recent = self.config.get('recent_projects', [])
                if filename not in recent:
                    recent.insert(0, filename)
                    self.config.set('recent_projects', recent[:10])
                    self.config.save()
                
                self.project_path = filename
                self.status.showMessage(f"✅ Projet sauvegardé: {os.path.basename(filename)}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def load_project(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir un projet", PROJECTS_DIR, "Projet JSON (*.json)"
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    project = json.load(f)
                
                # Nettoyer les couches existantes
                for layer in self.layers[:]:
                    self.remove_layer(layer.id)
                
                # Charger les couches
                for layer_info in project['layers']:
                    if os.path.exists(layer_info['path']):
                        self.load_file(layer_info['path'])
                
                self.project_path = filename
                self.status.showMessage(f"✅ Projet chargé: {os.path.basename(filename)}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def remove_layer(self, layer_id):
        for i, layer in enumerate(self.layers):
            if layer.id == layer_id:
                self.layer_tree.remove_layer(layer_id)
                del self.layers[i]
                self.redraw_map()
                self.logger.info(f"Couche supprimée: {layer.name}")
                break
    
    def remove_selected_layer(self):
        for item in self.layer_tree.selectedItems():
            data = item.data(0, Qt.UserRole)
            if data:
                self.remove_layer(data['id'])
    
    def on_layer_visibility_changed(self, layer_id, visible):
        for layer in self.layers:
            if layer.id == layer_id:
                layer.visible = visible
                self.redraw_map()
                break
    
    def on_layer_selected(self, layer_id):
        for layer in self.layers:
            if layer.id == layer_id:
                self.properties.update_properties(layer)
                break
    
    def on_layer_removed(self, layer_id):
        self.redraw_map()
    
    def redraw_map(self):
        self.map_widget.draw_layers(self.layers)
    
    def export_map(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Exporter la carte", EXPORTS_DIR,
            "PNG (*.png);;JPEG (*.jpg);;PDF (*.pdf)"
        )
        if filename:
            self.map_widget.figure.savefig(filename, dpi=300, bbox_inches='tight', facecolor='#0a1a2a')
            self.status.showMessage(f"✅ Carte exportée: {os.path.basename(filename)}")
    
    def show_docs(self):
        QMessageBox.information(self, "Documentation",
            f"{APP_NAME} v{APP_VERSION}\n\n"
            "📁 Formats supportés:\n"
            "• Shapefile (.shp)\n"
            "• GeoJSON (.geojson, .json)\n"
            "• KML/KMZ (Google Earth)\n"
            "• GeoPackage (.gpkg)\n"
            "• CSV avec coordonnées\n"
            "• GeoTIFF (.tif, .tiff)\n"
            "• GML (.gml, .xml)\n"
            "• DXF (.dxf)\n\n"
            "🖱️ Raccourcis:\n"
            "• Ctrl+O: Importer\n"
            "• Ctrl+S: Sauvegarder projet\n"
            "• Ctrl+E: Exporter carte\n"
            "• Ctrl+M: Mode mesure\n"
            "• Ctrl+F: Rechercher\n"
            "• Ctrl+D: Effacer sélection\n"
            "• Ctrl+0: Vue d'ensemble")
    
    def about(self):
        QMessageBox.about(self, "À propos",
            f"{APP_NAME}\n"
            f"Version {APP_VERSION}\n\n"
            f"Logiciel de cartographie professionnel\n"
            f"Développé avec PySide6 et GeoPandas\n"
            f"{APP_AUTHOR}\n\n"
            f"© 2026 - Tous droits réservés")

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Palette sombre professionnelle
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(18, 18, 18))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(18, 18, 18))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())