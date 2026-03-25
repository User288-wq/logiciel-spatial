#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
================================================================================
🚀 LOGICIEL DE CARTOGRAPHIE PROFESSIONNEL V5 - SUPPORT DE TOUS LES FORMATS
================================================================================
Formats supportés :
- ✅ Shapefile (.shp)
- ✅ GeoJSON (.geojson, .json)
- ✅ KML / KMZ (.kml, .kmz) - Google Earth
- ✅ GeoPackage (.gpkg)
- ✅ CSV avec coordonnées (.csv)
- ✅ GeoTIFF (.tif, .tiff) - Images satellites
- ✅ Fichiers vectoriels (GML, DXF, etc.)
================================================================================
"""

import os
import sys
import json
import math
import traceback
import zipfile
import tempfile
from datetime import datetime
from pathlib import Path
from shapely.geometry import Point, LineString, Polygon
import geopandas as gpd
import pandas as pd
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.patches as mpatches
import contextily as ctx

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

os.environ["QT_API"] = "pyside6"

# ============================================================================
# CONSTANTES
# ============================================================================

# Formats supportés avec leurs extensions
SUPPORTED_FORMATS = {
    'Shapefile': ['*.shp'],
    'GeoJSON': ['*.geojson', '*.json'],
    'KML/KMZ': ['*.kml', '*.kmz'],
    'GeoPackage': ['*.gpkg'],
    'CSV avec coordonnées': ['*.csv', '*.txt'],
    'GeoTIFF': ['*.tif', '*.tiff'],
    'GML': ['*.gml', '*.xml'],
    'DXF': ['*.dxf'],
    'Tous fichiers': ['*.*']
}

STYLES = {
    'Point':     {'color': '#FF4444', 'edge': '#CC0000', 'alpha': 0.9, 'marker': 'o', 'size': 8},
    'LineString':{'color': '#FFA500', 'edge': '#FF8C00', 'alpha': 0.8, 'linewidth': 1.5},
    'Polygon':   {'color': '#4CAF50', 'edge': '#2E7D32', 'alpha': 0.4, 'linewidth': 1},
    'MultiPolygon': {'color': '#4CAF50', 'edge': '#2E7D32', 'alpha': 0.4, 'linewidth': 1},
    'region':    {'color': '#4CAF50', 'edge': '#2E7D32', 'alpha': 0.4},
    'departement':{'color': '#FFA500', 'edge': '#FF8C00', 'alpha': 0.3},
    'selected':  {'color': '#FFFF00', 'edge': '#FFAA00', 'alpha': 0.8, 'linewidth': 2},
    'measure':   {'color': '#FF00FF', 'edge': '#FF00AA', 'alpha': 0.9, 'linewidth': 2},
    'raster':    {'color': None, 'alpha': 0.7},
    'default':   {'color': '#888888', 'edge': '#666666', 'alpha': 0.5}
}

LABEL_COLUMNS = ['name', 'NAME', 'NOM', 'admin_level', 'ADMIN1', 'ADMIN2', 'ADMIN3', 'LIBELLE', 'Name', 'Title']

# ============================================================================
# CHARGEUR DE FICHIERS MULTI-FORMATS
# ============================================================================

class FileLoader:
    """Chargeur de fichiers multi-formats"""
    
    @staticmethod
    def load_file(filename):
        """Charge un fichier et retourne un GeoDataFrame"""
        ext = os.path.splitext(filename)[1].lower()
        name = os.path.basename(filename)
        
        print(f"\n📂 Chargement: {name} (extension: {ext})")
        
        try:
            # Shapefile
            if ext == '.shp':
                gdf = gpd.read_file(filename)
                return gdf, "vectoriel"
            
            # GeoJSON
            elif ext in ['.geojson', '.json']:
                gdf = gpd.read_file(filename)
                return gdf, "vectoriel"
            
            # KML / KMZ
            elif ext in ['.kml', '.kmz']:
                return FileLoader.load_kml(filename)
            
            # GeoPackage
            elif ext == '.gpkg':
                gdf = gpd.read_file(filename, layer=0)
                return gdf, "vectoriel"
            
            # CSV avec coordonnées
            elif ext in ['.csv', '.txt']:
                return FileLoader.load_csv(filename)
            
            # GeoTIFF (raster)
            elif ext in ['.tif', '.tiff']:
                return FileLoader.load_raster(filename)
            
            # GML
            elif ext in ['.gml', '.xml']:
                gdf = gpd.read_file(filename)
                return gdf, "vectoriel"
            
            # DXF
            elif ext == '.dxf':
                try:
                    import ezdxf
                    gdf = gpd.read_file(filename)
                    return gdf, "vectoriel"
                except:
                    return None, f"Erreur: ezdxf non installé"
            
            else:
                return None, f"Format non supporté: {ext}"
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            traceback.print_exc()
            return None, str(e)
    
    @staticmethod
    def load_kml(filename):
        """Charge un fichier KML ou KMZ"""
        try:
            import fiona
            import tempfile
            
            # Si KMZ, extraire le KML
            if filename.endswith('.kmz'):
                with tempfile.TemporaryDirectory() as tmpdir:
                    with zipfile.ZipFile(filename, 'r') as kmz:
                        kmz.extractall(tmpdir)
                        kml_files = [f for f in os.listdir(tmpdir) if f.endswith('.kml')]
                        if kml_files:
                            gdf = gpd.read_file(os.path.join(tmpdir, kml_files[0]), driver='KML')
                        else:
                            return None, "Aucun fichier KML trouvé dans l'archive KMZ"
            else:
                gdf = gpd.read_file(filename, driver='KML')
            
            return gdf, "vectoriel"
        except Exception as e:
            return None, f"Erreur KML: {e}"
    
    @staticmethod
    def load_csv(filename):
        """Charge un fichier CSV avec coordonnées"""
        try:
            import pandas as pd
            df = pd.read_csv(filename)
            
            # Chercher les colonnes de coordonnées
            lat_col = None
            lon_col = None
            x_col = None
            y_col = None
            
            for col in df.columns:
                col_lower = col.lower()
                if col_lower in ['lat', 'latitude', 'y']:
                    lat_col = col
                elif col_lower in ['lon', 'long', 'longitude', 'x']:
                    lon_col = col
            
            if lat_col and lon_col:
                # Créer des points
                geometry = [Point(x, y) for x, y in zip(df[lon_col], df[lat_col])]
                gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
                return gdf, "vectoriel"
            else:
                return None, "Aucune colonne de coordonnées trouvée (recherche: latitude, longitude)"
                
        except Exception as e:
            return None, f"Erreur CSV: {e}"
    
    @staticmethod
    def load_raster(filename):
        """Charge un fichier raster GeoTIFF"""
        try:
            import rasterio
            src = rasterio.open(filename)
            return src, "raster"
        except ImportError:
            return None, "rasterio non installé (pip install rasterio)"
        except Exception as e:
            return None, f"Erreur raster: {e}"

# ============================================================================
# DIALOGUE D'IMPORT AVANCÉ
# ============================================================================

class ImportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import avancé de données")
        self.setGeometry(200, 200, 500, 400)
        self.setup_ui()
        self.selected_file = None
        self.import_options = {}
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("📂 IMPORT DE DONNÉES GÉOSPATIALES")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #4CAF50;")
        layout.addWidget(title)
        
        layout.addWidget(QLabel("\nFormats supportés:"))
        formats_text = QTextEdit()
        formats_text.setReadOnly(True)
        formats_text.setMaximumHeight(100)
        formats_html = "<b>• Shapefile</b> (.shp)<br>"
        formats_html += "<b>• GeoJSON</b> (.geojson, .json)<br>"
        formats_html += "<b>• KML/KMZ</b> (.kml, .kmz) - Google Earth<br>"
        formats_html += "<b>• GeoPackage</b> (.gpkg)<br>"
        formats_html += "<b>• CSV avec coordonnées</b> (.csv)<br>"
        formats_html += "<b>• GeoTIFF</b> (.tif, .tiff)<br>"
        formats_html += "<b>• GML</b> (.gml, .xml)<br>"
        formats_html += "<b>• DXF</b> (.dxf)"
        formats_text.setHtml(formats_html)
        layout.addWidget(formats_text)
        
        # Sélection de fichier
        file_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.setReadOnly(True)
        file_layout.addWidget(self.file_path)
        
        self.browse_btn = QPushButton("Parcourir")
        self.browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_btn)
        layout.addLayout(file_layout)
        
        # Options d'import
        options_group = QGroupBox("Options d'import")
        options_layout = QFormLayout(options_group)
        
        self.crs_edit = QLineEdit()
        self.crs_edit.setPlaceholderText("EPSG:4326 (par défaut)")
        options_layout.addRow("Système de projection:", self.crs_edit)
        
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(['utf-8', 'latin1', 'cp1252', 'iso-8859-1'])
        options_layout.addRow("Encodage:", self.encoding_combo)
        
        self.layer_name = QLineEdit()
        self.layer_name.setPlaceholderText("Nom automatique")
        options_layout.addRow("Nom de la couche:", self.layer_name)
        
        layout.addWidget(options_group)
        
        # Aperçu
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(100)
        self.preview_text.setPlaceholderText("Aperçu du fichier...")
        layout.addWidget(self.preview_text)
        
        # Boutons
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
        formats_filter = "Tous les fichiers supportés (*.shp *.geojson *.json *.kml *.kmz *.gpkg *.csv *.tif *.tiff *.gml *.dxf);;"
        formats_filter += "Shapefile (*.shp);;"
        formats_filter += "GeoJSON (*.geojson *.json);;"
        formats_filter += "KML/KMZ (*.kml *.kmz);;"
        formats_filter += "GeoPackage (*.gpkg);;"
        formats_filter += "CSV (*.csv);;"
        formats_filter += "GeoTIFF (*.tif *.tiff);;"
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
        
        if ext in ['.shp', '.geojson', '.json', '.kml', '.kmz', '.gpkg', '.gml']:
            try:
                import fiona
                with fiona.open(filename) as src:
                    preview += f"Type: {src.schema['geometry']}\n"
                    preview += f"Entités: {len(src)}\n"
                    preview += f"Attributs: {', '.join(src.schema['properties'].keys())}"
            except:
                pass
        elif ext in ['.csv']:
            try:
                import pandas as pd
                df = pd.read_csv(filename, nrows=5)
                preview += f"Lignes: {len(df)}\n"
                preview += f"Colonnes: {', '.join(df.columns)}"
            except:
                pass
        
        self.preview_text.setText(preview)

# ============================================================================
# GESTIONNAIRE DE COUCHES (AVEC GLISSER-DÉPOSER)
# ============================================================================

class LayerTreeWidget(QTreeWidget):
    layer_visibility_changed = Signal(str, bool)
    layer_selected = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabel("🗂️ Couches")
        self.setIndentation(15)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setAlternatingRowColors(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.itemClicked.connect(self.on_item_clicked)
        self.itemChanged.connect(self.on_item_changed)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            filename = url.toLocalFile()
            if filename:
                self.parent().load_file(filename)
    
    def add_layer(self, layer_id, name, layer_type, icon='📌'):
        item = QTreeWidgetItem(self)
        item.setText(0, f"{icon} {name}")
        item.setCheckState(0, Qt.Checked)
        item.setData(0, Qt.UserRole, {'id': layer_id, 'type': layer_type})
        self.addTopLevelItem(item)
        return item
    
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
        menu.addAction("🗑️ Supprimer", lambda: self.parent().remove_layer(data['id']))
        menu.exec(self.viewport().mapToGlobal(position))

# ============================================================================
# PANNEAU DE PROPRIÉTÉS (RESTE SIMILAIRE)
# ============================================================================

class PropertiesWidget(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setStyleSheet("background-color: #1a1a2a; color: #00ff00; font-family: 'Courier New'; font-size: 11px;")
    
    def update_properties(self, layer):
        if not layer or layer.gdf is None:
            self.setText("Aucune couche sélectionnée")
            return
        
        gdf = layer.gdf
        geom_type = gdf.geometry.type.iloc[0] if len(gdf) > 0 else 'N/A'
        
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
        
        self.setText(info)

# ============================================================================
# LEGENDE
# ============================================================================

class LegendWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.title = QLabel("📖 LÉGENDE")
        self.title.setStyleSheet("font-weight: bold; color: #4CAF50;")
        layout.addWidget(self.title)
        
        self.legend_layout = QVBoxLayout()
        layout.addLayout(self.legend_layout)
        
        self.update_legend()
    
    def update_legend(self):
        for i in reversed(range(self.legend_layout.count())):
            widget = self.legend_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        entries = [
            ('🟩', 'Régions', '#4CAF50'),
            ('🟧', 'Départements', '#FFA500'),
            ('📍', 'Points', '#FF4444'),
            ('📏', 'Lignes', '#FFA500'),
            ('🔲', 'Polygones', '#4CAF50'),
            ('🟨', 'Sélectionné', '#FFFF00'),
            ('🟪', 'Mesure', '#FF00FF'),
        ]
        
        for icon, name, color in entries:
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(2, 2, 2, 2)
            
            color_label = QLabel(icon)
            layout.addWidget(color_label)
            
            name_label = QLabel(name)
            name_label.setStyleSheet("color: white; font-size: 10px;")
            layout.addWidget(name_label)
            
            layout.addStretch()
            self.legend_layout.addWidget(widget)

# ============================================================================
# MOTEUR CARTOGRAPHIQUE (SIMPLIFIÉ)
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
        self.cid = self.canvas.mpl_connect('button_press_event', self.on_click)
        self.parent_app = parent
    
    def get_style(self, layer, is_selected=False):
        if is_selected:
            return STYLES['selected']
        
        name_lower = layer.name.lower()
        for keyword in ['region', 'departement', 'commune']:
            if keyword in name_lower:
                return STYLES[keyword]
        
        if layer.gdf is not None and len(layer.gdf) > 0:
            geom_type = layer.gdf.geometry.type.iloc[0]
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
                bounds = self.ax.get_xlim() + self.ax.get_ylim()
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
                if label_col:
                    for idx, row in gdf.iterrows():
                        if row.geometry and not row.geometry.is_empty:
                            try:
                                centroid = row.geometry.centroid
                                label = str(row[label_col])[:15]
                                if label and label != 'nan':
                                    color = 'yellow' if hasattr(layer, 'selected') and layer.selected == idx else 'white'
                                    self.ax.text(centroid.x, centroid.y, label,
                                               fontsize=6, color=color,
                                               ha='center', va='center',
                                               bbox=dict(boxstyle="round,pad=0.1",
                                                        facecolor='#1a1a2a',
                                                        alpha=0.6))
                            except:
                                pass
        
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
    
    def zoom_all(self):
        if not self.parent_app.layers:
            self.ax.set_xlim(-20, 20)
            self.ax.set_ylim(0, 25)
            self.canvas.draw()
            return
        
        xmin, ymin, xmax, ymax = float('inf'), float('inf'), float('-inf'), float('-inf')
        for layer in self.parent_app.layers:
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
        """Pour compatibilité avec l'ancien code"""
        return self.data if not self.is_raster else None

# ============================================================================
# FENÊTRE PRINCIPALE
# ============================================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 Logiciel de Cartographie Professionnel V5 - Multi-Formats")
        self.setGeometry(100, 100, 1600, 900)
        self.setAcceptDrops(True)
        
        self.layers = []
        self.next_id = 0
        self.project_path = None
        
        self.setup_ui()
        self.setup_menus()
        self.setup_toolbars()
        self.setup_statusbar()
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            filename = url.toLocalFile()
            if filename:
                self.load_file(filename)
    
    def load_file(self, filename):
        """Charge un fichier avec détection automatique du format"""
        data, data_type = FileLoader.load_file(filename)
        
        if data is None:
            QMessageBox.warning(self, "Erreur", f"Impossible de charger {filename}\n{data_type}")
            return
        
        name = os.path.basename(filename)
        is_raster = (data_type == "raster")
        layer_type = 'default'
        name_lower = name.lower()
        for kw in ['region', 'departement', 'commune']:
            if kw in name_lower:
                layer_type = kw
                break
        
        layer_id = str(self.next_id)
        self.next_id += 1
        layer = Layer(layer_id, name, filename, data, layer_type, is_raster)
        
        icons = {'Point': '📍', 'LineString': '📏', 'Polygon': '🔲', 'raster': '🖼️'}
        if is_raster:
            icon = '🖼️'
        else:
            geom_type = data.geometry.type.iloc[0] if len(data) > 0 else 'Polygon'
            icon = icons.get(geom_type, '📌')
        
        item = self.layer_tree.add_layer(layer_id, name, layer_type, icon)
        layer.item = item
        self.layers.append(layer)
        
        self.redraw_map()
        self.zoom_all()
        self.status.showMessage(f"✅ {name} chargé")
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Panneau gauche
        left_panel = QWidget()
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_panel)
        
        # Info glisser-déposer
        info_label = QLabel("💡 Glissez-déposez vos fichiers ici\nFormats: .shp, .geojson, .kml, .kmz, .gpkg, .csv, .tif...")
        info_label.setStyleSheet("background-color: #16213e; color: #ffaa00; padding: 5px; border-radius: 3px;")
        left_layout.addWidget(info_label)
        
        self.layer_tree = LayerTreeWidget(self)
        self.layer_tree.layer_visibility_changed.connect(self.on_layer_visibility_changed)
        self.layer_tree.layer_selected.connect(self.on_layer_selected)
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
        
        file_menu = menubar.addMenu("&Fichier")
        file_menu.addAction("📂 Importer un fichier", self.show_import_dialog, "Ctrl+O")
        file_menu.addSeparator()
        file_menu.addAction("💾 Sauvegarder projet", self.save_project, "Ctrl+S")
        file_menu.addAction("📂 Ouvrir projet", self.load_project, "Ctrl+Shift+O")
        file_menu.addSeparator()
        file_menu.addAction("💾 Exporter la carte", self.export_map, "Ctrl+E")
        file_menu.addSeparator()
        file_menu.addAction("❌ Quitter", self.close, "Ctrl+Q")
        
        tools_menu = menubar.addMenu("&Outils")
        tools_menu.addAction("📏 Mesurer une distance", self.toggle_measure, "Ctrl+M")
        tools_menu.addAction("🔍 Rechercher", self.show_search, "Ctrl+F")
        tools_menu.addAction("🗺️ Fonds de carte OSM", self.toggle_basemap)
        tools_menu.addSeparator()
        tools_menu.addAction("🗑️ Effacer mesure", self.clear_measure)
        tools_menu.addAction("🗑️ Effacer sélection", self.clear_selection, "Ctrl+D")
        
        view_menu = menubar.addMenu("&Affichage")
        view_menu.addAction("🌍 Vue d'ensemble", self.zoom_all, "Ctrl+0")
    
    def setup_toolbars(self):
        toolbar = self.addToolBar("Outils")
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
    
    def setup_statusbar(self):
        self.status = self.statusBar()
        self.coord_label = QLabel("📍 -")
        self.scale_label = QLabel("📏 -")
        self.mode_label = QLabel("")
        self.status.addPermanentWidget(self.coord_label)
        self.status.addPermanentWidget(QLabel("  |  "))
        self.status.addPermanentWidget(self.scale_label)
        self.status.addPermanentWidget(QLabel("  |  "))
        self.status.addPermanentWidget(self.mode_label)
        self.status.showMessage("Prêt - Glissez-déposez vos fichiers !")
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(500)
    
    def update_status(self):
        if hasattr(self.map_widget, 'ax') and self.map_widget.ax.has_data():
            xl, yl = self.map_widget.ax.get_xlim(), self.map_widget.ax.get_ylim()
            lon = (xl[0] + xl[1]) / 2
            lat = (yl[0] + yl[1]) / 2
            self.coord_label.setText(f"📍 {lon:.4f}°, {lat:.4f}°")
        
        if self.map_widget.measure_mode:
            self.mode_label.setText("📏 MODE MESURE ACTIF")
            self.mode_label.setStyleSheet("color: #FF00FF; font-weight: bold;")
        else:
            self.mode_label.setText("")
    
    def show_import_dialog(self):
        dialog = ImportDialog(self)
        if dialog.exec():
            filename = dialog.selected_file
            if filename:
                self.load_file(filename)
    
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
    
    def zoom_all(self):
        self.map_widget.zoom_all()
    
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
    
    def show_filter_dialog(self, layer_id):
        for layer in self.layers:
            if layer.id == layer_id and not layer.is_raster:
                dialog = FilterDialog(layer, self)
                dialog.exec()
                self.redraw_map()
                break
    
    def export_layer_data(self, layer_id):
        for layer in self.layers:
            if layer.id == layer_id and not layer.is_raster:
                filename, _ = QFileDialog.getSaveFileName(
                    self, "Exporter les données", f"{layer.name}_export", 
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
                        
                        self.status.showMessage(f"✅ Exporté: {filename}")
                    except Exception as e:
                        QMessageBox.critical(self, "Erreur", str(e))
                break
    
    def save_project(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Sauvegarder le projet", "", "Projet JSON (*.json)"
        )
        if filename:
            project = {
                'name': os.path.basename(filename),
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
                self.project_path = filename
                self.status.showMessage(f"✅ Projet sauvegardé: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def load_project(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir un projet", "", "Projet JSON (*.json)"
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    project = json.load(f)
                
                for layer in self.layers:
                    self.remove_layer(layer.id)
                
                for layer_info in project['layers']:
                    if os.path.exists(layer_info['path']):
                        self.load_file(layer_info['path'])
                
                self.project_path = filename
                self.status.showMessage(f"✅ Projet chargé: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def remove_layer(self, layer_id):
        for i, layer in enumerate(self.layers):
            if layer.id == layer_id:
                self.layer_tree.takeTopLevelItem(self.layer_tree.indexOfTopLevelItem(layer.item))
                del self.layers[i]
                self.redraw_map()
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
    
    def redraw_map(self):
        self.map_widget.draw_layers(self.layers)
    
    def export_map(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Exporter la carte", "",
            "PNG (*.png);;JPEG (*.jpg);;PDF (*.pdf)"
        )
        if filename:
            self.map_widget.figure.savefig(filename, dpi=300, bbox_inches='tight', facecolor='#0a1a2a')
            self.status.showMessage(f"✅ Carte exportée")

# ============================================================================
# FILTRE DIALOG (simplifié)
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
        
        # Aperçu
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

# ============================================================================
# RECHERCHE DIALOG
# ============================================================================

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

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(18, 18, 18))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.Text, Qt.white)
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())